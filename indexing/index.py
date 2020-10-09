#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 10 15:24:26 2020

@author: gabrielesavoia
"""

import os, os.path

from whoosh import index, scoring, qparser
from whoosh.fields import SchemaClass, TEXT, ID, STORED
from whoosh.qparser import QueryParser

import shutil  

from .xmlParsing import saxReader

from .analysis.analyzers import LemmatizingAnalyzer, AdvancedStemmingAnalyzer, NounSelectionAnalyzer
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
    text = TEXT(analyzer=AdvancedStemmingAnalyzer(), stored=False, phrase=False) #phrase=False per ridurre index
    title = TEXT(analyzer=AdvancedStemmingAnalyzer(), stored=True, phrase=False)
    

class WikiIndex:

    name_index = 'indexdir'
    name_corpus = 'wiki_fake.xml'
    
    def __init__(self, dir_storage):
        """
        Inizializzazione classe.

        :param dir_storage : nome della cartella dove è presente la cartella dell'indice 'indexdir'
        """
        self.dir_storage = dir_storage
        self.index_path = self.dir_storage+WikiIndex.name_index

        self.corpus_path = self.dir_storage+WikiIndex.name_corpus
        
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
        if index.exists_in(self.index_path):
            print('  Lettura indice da file..')
            try:
                self.__index = index.open_dir(self.index_path)
                self.__afterBuild()

                return True
            except Exception as e:
                print(e)
                print('! Errore caricamento indice dal path: '+self.index_path)
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
        
        if os.path.exists(self.index_path):
            shutil.rmtree(self.index_path)  
        os.mkdir(self.index_path)

        graph = WikiGraph(self.dir_storage)
        
        self.__index = index.create_in(self.index_path, WikiIndex.getSchema())

        writer = self.__index.writer(limitmb=256, procs=2, multisegment=True)  

        try:     
            saxReader.readXML(self.corpus_path, self.__addWikiPage, graph, writer)
            writer.commit()
            graph.end()
            self.__afterBuild()  

            return True           
        except Exception as e: 
            print(e)
            print('! Errore durante la creazione indice.')
            return False   


    def __afterBuild(self):
        """
        Funzione che deve essere chiamata dopo che l'indice è stato creato oppure caricato da file.
        Configura il page_ranker e il searcher.

        :param self
        """
        self.__page_ranker = WikiPageRanker(self.dir_storage)
        self.__searcher = WikiSearcher(self.__index, self.__page_ranker)
        print('* Creazione / caricamento indice avvenuta con successo')

        
    def __addWikiPage(self, graph, writer, **data_parsed):
        """
        Indicizza la pagina letta.
        E' necessario controllare che l'indice esista e che il writer sia valido.
        Questa funzione viene chiamata dal SAX (lettore xml) ogni volta che una pagina è stata letta
        in modo completo dal dump xml.
        
        :param graph: instanza di grafo per il page rank
        :param writer: writer per poter aggiungere all'index la pagina di wikipedia letta dal dump
        :param data_parsed: dati letti e filtrati che sono stati ritornati dopo la lettura del dump xml
        """
        if self.__index is not None and writer is not None:
            title = data_parsed['title']
            text = data_parsed['text']
            link = data_parsed['internal_link']

            writer.add_document(text=text, title=title)
            graph.addPage(title, link)
        else:
            print('! Problemi durante indicizzazione pagina wikipedia di titolo: '+title)
            
            
    def getFieldInfo(self, field):
        """
        Ottengo le informazioni riferite al field.
        Funzione utile in fase di debug.
        
        :param field: field di cui voglio le informazioni
        return dict con le info del field specificato
        """
        if self.__index is None: return None
        
        res = {}
        with self.__index.searcher() as searcher:
            res['lexicon'] = list(searcher.lexicon(field))
            res['length'] = searcher.field_length(field)
            res['avg-length'] = searcher.avg_field_length(field)
        
        return res
    
    
    def getGeneralInfo(self):
        """
        Ottengo le informazioni generali riferite all'indice.
        Funzione utile in fase di debug.
        
        :param self:
        return dict con le info
        """
        if self.__index is None: return None        
        
        res = {}
        with self.__index.searcher() as searcher:
            res['doc_count'] = searcher.doc_count()
        
        return res
        
        
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

