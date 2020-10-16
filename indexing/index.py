#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 15:24:26 2020

@author: gabrielesavoia
"""

import os, os.path

from whoosh import index, scoring, qparser
from whoosh.fields import SchemaClass, TEXT, ID, STORED, KEYWORD, NUMERIC
from whoosh.qparser import QueryParser

import shutil  

from .xmlParsing import saxReader

from .analysis.analyzers import LemmatizingAnalyzer, AdvancedStemmingAnalyzer, NounSelectionAnalyzer, StemmingWithStopwordAnalyzer
from .searching.searcher import WikiSearcher

from .pageRank.graph import WikiGraph, WikiPageRanker 

# https://github.com/iwasingh/Wikoogle/tree/master/src

class WikiSchema(SchemaClass):
    """
    DOCS : https://whoosh.readthedocs.io/en/latest/schema.html
    DOCS : https://github.com/mchaput/whoosh/blob/main/src/whoosh/fields.py
    
    Definizione dello schema per l'indice.
    Tutti i Field ereditano da FieldType.
    Ogni Field ha un certo Format, che indica come salvare la posting list (se salvare le pos, la freq..)
    
    TEXT -> usa il Format 'Position' se 'phrase=true' (default) --> (WORD-BASED) con anche il numero delle 
            volte in cui si ripete il token nel documento
    """
    id_page = ID(stored=True, unique=True)
    text = TEXT(analyzer=AdvancedStemmingAnalyzer(), stored=True)     #phrase=False per ridurre index
    title = TEXT(analyzer=AdvancedStemmingAnalyzer(), stored=True)
    

class WikiIndex:
    
    def __init__(self, args_paths):
        """
        Inizializzazione classe.

        :param dict_paths : dictionary con i path che servono all'indice
        """
        self.args_paths = args_paths
        
        self.__index = None
        self.__page_ranker = None
        self.__searcher = None
        
    @classmethod 
    def getSchema(cls):
        """
        :param self
        return dello schema dell'indice.
        """
        return WikiSchema


    def openOrBuild(self):
        """
        Apre un indice già esistente oppure se non esiste ne crea uno nuovo.
        
        :param self
        """
        if index.exists_in(self.args_paths.index_dir):
            print('  Lettura indice da file..')
            try:
                self.__index = index.open_dir(self.args_paths.index_dir)
                self.__afterBuild()

                return True
            except Exception as e:
                raise(e)
                print('! Errore caricamento indice dal path: '+self.args_paths.index_dir)
                return False
        else:
            print('  Creazione indice dal dump..')
            return self.build() 
    

    def build(self): 
        """
        DOCS : https://whoosh.readthedocs.io/en/latest/indexing.html
        
        Creazione di un nuovo indice situato nella directory settata nell'__init__ della classe.
        Se esistente, la cartella dell'indice viene eliminata per poi esssere ricreata con il 
        nuovo indice.
        Viene creato il writer, per poi leggere il file xml di wikipedia e ogni volta che una pagina è 
        letta correttamente, viene chiamata la funzione '__addWikiPage' per poi eseguire il commit
        del writer una volta che ho letto tutto il file.
        
        TUNING   DOCS : https://whoosh.readthedocs.io/en/latest/batch.html
        # limitmb : default=128 sono i mega usati per l'index pool. Più è alto più è veloce
                    Se uso multiprocessor è la memoria per ogni processore.
        # procs : n proc che vengono usati. Vengono creati sub-writer per ogni processsore.
                  Per fare il marge dei segmenti creati da ogni processore però
                  viene comunque usato un singlo processo.
                  Se non specificato quindi avviene il merge dei segmenti -> DISPENDIOSO
        # multisegment: se True fa in modo che ogni sub-writer crei segmenti 
                        separati senza fare il merge.
                        Vengono creati n-segmenti se sono abilitati n processori.        
        
        :param self
        """
        
        if os.path.exists(self.args_paths.index_dir):
            shutil.rmtree(self.args_paths.index_dir)  
        os.mkdir(self.args_paths.index_dir)

        graph = WikiGraph(self.args_paths)
        
        self.__index = index.create_in(self.args_paths.index_dir, WikiIndex.getSchema())

        writer = self.__index.writer(limitmb=2048, procs=4, multisegment=True)  

        try:     
            import time
            start_build = time.time()

            print('Lettura file xml ...')
            start = time.time()
            saxReader.readXML(self.args_paths, self.__addWikiPage, graph, writer)
            end = time.time()
            print('Tempo di lettura file xml : '+str(round(end-start, 5)))

            print('Commit indice ...')
            start = time.time()
            writer.commit()
            end = time.time()
            print('Tempo di commit indice : '+str(round(end-start, 5)))

            print('Calcolo pagerank ...')
            start = time.time()
            graph.end()
            end = time.time()
            print('Tempo calcolo pagerank : '+str(round(end-start, 5)))

            self.__afterBuild()  
            end_build = time.time()
            print('Tempo totale : '+str(round(end_build-start_build, 5)))


            return True           
        except Exception as e: 
            raise(e)
            print('! Errore durante la creazione indice.')
            return False   


    def __afterBuild(self):
        """
        Funzione che deve essere chiamata dopo che l'indice è stato creato oppure caricato da file.
        Configura il page_ranker e il searcher.

        :param self
        """
        print('Caricamento in memoria del file di pagerank e searcher ...')

        self.__page_ranker = WikiPageRanker(self.args_paths)
        self.__searcher = WikiSearcher(self.__index, self.__page_ranker)

        print('* Creazione / caricamento indice avvenuta con successo')

        
    def __addWikiPage(self, graph, writer, **data_parsed):
        """
        Questa funzione viene chiamata quando viene letta una pagina valida dal dump xml.

        Per poter 

        
        :param graph: instanza di grafo per il page rank
        :param writer: writer per poter aggiungere all'index la pagina di wikipedia letta dal dump
        :param data_parsed: dati letti e filtrati che sono stati ritornati dopo la lettura del dump xml
        """
        if self.__index is not None and writer is not None:
            title = data_parsed['title']
            text = data_parsed['text']
            id_page = data_parsed['id']
            link = data_parsed['internal_link']

            writer.add_document(text=text, title=title, id_page=id_page)
            graph.addPage(id_page, title, link)
        else:
            print('! Problemi durante indicizzazione pagina wikipedia')
            
            
    def getFieldInfo(self, field):
        """
        Ottengo le informazioni riferite al field.
        Funzione utile in fase di debug.
        
        :param field: field di cui voglio le informazioni
        return dict con le info del field specificato
        """
        return self.__searcher.getFieldInfo(field)
    
    
    def getGeneralInfo(self):
        """
        Ottengo le informazioni generali riferite all'indice.
        Funzione utile in fase di debug.
        
        :param self:
        return dict con le info
        """
        return self.__searcher.getGeneralInfo()
        
        
    def query(self, text, **settings): 
        """
        Viene fatto il parsing della query e poi tramite l'utilizzo di modelli
        di information retrieval, vengono estratti dall'indice i documenti
        più rilevanti per la query.
        
        :param text: testo da parsare per ottenere la query vera e propria
        :param settings: sono i settaggi del searcher 
        :return dict con il tempo di esecuzione della query, i documneti totali
                        e il riferimento ai documenti interi (url)
        """
        if self.__index is not None:
            return self.__searcher.search(text, **settings)
        else:
            return None

