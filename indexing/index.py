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

# https://github.com/iwasingh/Wikoogle/tree/master/src

class WikiSchema(SchemaClass):
    """
    DOCS : https://whoosh.readthedocs.io/en/latest/schema.html
    DOCS : https://github.com/mchaput/whoosh/blob/main/src/whoosh/fields.py
    
    Definizione dello schema per l'indice.
    Tutti i Field ereditano da FieldType.
    Ogni Field ha un certo Format, che indica come salvare la posting list (se salvare le pos, la freq..)
    
    FUNZIONAMENTO: passo ad esempio il testo di wikipedia ricavato dall'xml al
                    Field chiamato 'text', questo lo passa al suo corrispettivo 
                    oggetto Format (salvato come attributo nella classe Field), che
                    a sua volta chiama l'analizzatore settato in fase di definiszione 
                    dello schema, per poi salvarlo sul disco in base al tipo di 
                    Format.
    
    TEXT : usa il Format 'Position' se 'phrase=true' (default) --> (WORD-BASED) con anche il numero delle 
            volte in cui si ripete il token nel documento
    """
    text = TEXT(analyzer=AdvancedStemmingAnalyzer(), stored=True)
    title = TEXT(analyzer=LemmatizingAnalyzer(), stored=True)
    

class WikiIndex:
    
    def __init__(self, name_index_dir, corpus_path):
        """
        :param name_index_dir : nome della cartella dove memorizzare l'indice
        :param corpus_path : path per il corpus
        """
        self.name_index_dir = name_index_dir
        self.corpus_path = corpus_path
        
        self.__index = None
        
        
    def getSchema(self):
        """
        return dello schema dell'indice.
        """
        return WikiSchema
    

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
                    Se uso multiprocessor è la memoria per ogni processore !!
        # procs : n proc che vengono usati. Vengono creati sub-writer per ogni processsore.
                  Per fare il marge dei segmenti creati da ogni processore però
                  viene comunque usato un singlo processo.
                  Se non specificato quindi avviene il merge dei segmenti -> DISPENDIOSO
        # multisegment: se True fa in modo che ogni sub-writer crei segmenti 
                        separati senza fare il merge.
                        Vengono creati n-segmenti se sono abilitati n processori.        
        
        :param self
        """
        
        if os.path.exists(self.name_index_dir):
            shutil.rmtree(self.name_index_dir)  
        
        os.mkdir(self.name_index_dir)
        
        self.__index = index.create_in(self.name_index_dir, self.getSchema())
        writer = self.__index.writer(limitmb=256, procs=2, multisegment=True)       
        
        saxReader.readXML(self.corpus_path, self.__addWikiPage, writer)
        
        writer.commit()
        
        
    def openOrBuild(self):
        """
        Apre un indice già esistente oppure se non esiste ne crea uno nuovo.
        
        :param self
        """
        if self.__index is not None and self.__index.exists_in(self.name_index_dir):
            self.__index = index.open_dir(self.name_index_dir)
        else:
            self.build()        
        
        
    def __addWikiPage(self, writer, **data_parsed):
        """
        Indicizza la pagina letta.
        E' necessario controllare che l'indice esista e che il writer sia valido.
        Questa funzione viene chiamata dal SAX (lettore xml) ogni volta che una pagina è stata letta
        in modo completo dal dump xml.
        
        NOTA: 'writer' lo passo come parametro alla funzione. Avrei potuto ricavarlo direttamente
              all'interno di questa funzione per poi eseguire il commit sempre all'interno. Questo però
              risulta essere più costoso dato che sarebbero operazioni da svolgere per ogni pagina letta.
              Quindi abbiamo deciso di delegare il controllo del writer al di fuori di questa funzione.
        
        :param writer: writer per poter aggiungere all'index la pagina di wikipedia letta dal dump
        :param data_parsed: dati letti e filtrati che sono stati ritornati dopo la lettura del dump xml
        """
        if self.__index is not None and writer is not None:
            writer.add_document(text=data_parsed['text'], title=data_parsed['title'])
        else:
            print('Problemi durante indicizzazione pagina wikipedia')
            
            
    def getFieldInfo(self, field):
        """
        Ottengo le informazioni riferite al field.
        Funzione utile in fase di debug.
        
        :param field: field di cui voglio le informazioni
        return dict con le info del field specificato
        """
        if self.__index is None:
            return None
        
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
        if self.__index is None:
            return None        
        
        res = {}
        with self.__index.searcher() as searcher:
            res['doc_count'] = searcher.doc_count()
        
        return res
        
        
    
    def query(self, text, limit=10, weighting='BM25F', group='AND',text_boost=1.0, 
                 title_boost=1.0, exp=True): 
        """
        Viene fatto il parsing della query e poi tramite l'utilizzo di modelli
        di information retrieval, vengono estratti dall'indice i documenti
        più rilevanti per la query.
        
        - Parser   --> riferito ad un certo field. Serve per definire la 
                        STRUTTURA SINTATTICA della query. 
                        E' necessario quindi eseguire un'analizzatore per effettuare
                        la tokenizzazione con eventuali filtri.
                        L'ANALIZZATORE usato è quello associato al field dello schema.
                        Il parser si occupa di defnire le regole sintattiche come
                        gli 'and' oppure gli 'or' tra i token.
                        Di default i token vengono messi in 'and', ma si può settare OrGroup.
                       
        - Searcher --> esegue la ricerca della query parsata. Qua viene definito:
                        - limit    --> è il numero di risultati in risposta
                        - IR model --> default è BM25F
                        - numero HITS di dafault a 20 
                        - len(result) -> numero di docs che fanno MATCH (UNSCORED)
                        - 
        
        :param query: query dell'utente non ancora parsata 
        :return dict con il tempo di esecuzione della query, i documneti totali
                        e il riferimento ai documenti interi (url)
        """
        
        if self.__index is not None:
            searcher = WikiSearcher(self.__index, 
                                    weighting=weighting, 
                                    group=group,
                                    text_boost=text_boost,
                                    title_boost=title_boost)
            return searcher.search(text, limit=limit, exp=exp)
        else:
            return None
    
#i = WikiIndex()
#i.build() 
#i.query('cafè')
#print(i.getFieldInfo('text'))


















