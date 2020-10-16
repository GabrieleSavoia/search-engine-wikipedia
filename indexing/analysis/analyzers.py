#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 10:00:58 2020

@author: gabrielesavoia
"""
from whoosh.analysis import StemmingAnalyzer, RegexTokenizer, LowercaseFilter, StopFilter, StemFilter
from whoosh.analysis.filters import STOP_WORDS, CharsetFilter
from whoosh.analysis.tokenizers import default_pattern
from whoosh.support.charset import accent_map

from .filters import LemmatizerFilter, NounSelectionFilter
from .tokenizers import NltkTokenizerWithPOStag


"""
DOCS : src whoosh -> https://github.com/mchaput/whoosh/blob/main/src/whoosh/analysis/analyzers.py

ANALIZZATORE = TOKENIZZATORE + FILTRO + ... + FILTRO
        
ANALIZZATORE : è una funzione o un callable, che prende in input una stringa unicode
                e ritorna un generatore che fa yield dei token filtrati.
                E' composto da un TOKENIZZATORE e da FILTRI
TOKENIZZATORE : funzione o callable che prende in input una stringa unicode e 
                fa yield di token non filtrati.
FILTRO : prende in input token e ritorna token filtrato.
TOKEN : è una classe di Whoosh che contiene tutte le informazioni che servono per indicizzare  
                    
FORMAT : è riferito ad ogni field. Può essere ad esempio 'Existence', 'Positions', 'Frequency'.
        Questo chiama l'analizzatore passandogli al costruttore i campi necessari.
        L'analizzatore chiama a sua volta il tokenizzatore che imposta i valori di setting dei token.
        Perchè se ad esempio un field con il format 'positions' deve passare all'analizzatore:
            positions=True
        Questo a sua volta chiama il tokenizzatore passandogli i valori settati
        ovvero scrive nei settings del token che è necessario memorizzare la posizione di ognuno.
        
"""  
    

def NounSelectionAnalyzer():
    """
    Non uso questo analizzatore nel progetto ma è stato sviluppato per finalità di test.

    Analizzatore mediante il quale avviene la tokenizzazione con NLTK, e 
    contemporaneamente avviene anche il POS tagging per poi andare a rimuovere
    i token categorizzati come 'non-nomi'. 
    E' presente anche una serie di filtri per la normalizzazione.
    """
    return NltkTokenizerWithPOStag() | LowercaseFilter() \
            | NounSelectionFilter() | StopFilter() | StemFilter()
            
            
def LemmatizingAnalyzer(expression=default_pattern, stoplist=STOP_WORDS,
                     minsize=2, maxsize=None, gaps=False):
    """
    Analizzatore mediante il quale effettuo una tokenizzazione, il lowercase,
    eliminazione delle stopword ed infine effettuo la lemmatizzazione.
    
    :param expression: espressione regolare usata per estrarre i token
    :param stoplist: lisat di stopword. E' possibile effettuare l'unione con altre un altra lista
    :param minsize: Parole più piccole di questo valore vengono eliminate
    :param maxsize: parole più grandi di questo valore vengono eliminate
    :param gaps: se true, avviene lo split piuttosto che l'eliminazione
    """

    ret = RegexTokenizer(expression=expression, gaps=gaps)
    chain = ret | LowercaseFilter()
    if stoplist is not None:
        chain = chain | StopFilter(stoplist=stoplist, minsize=minsize,
                                   maxsize=maxsize)
    return chain | LemmatizerFilter()


def AdvancedStemmingAnalyzer(stoplist=STOP_WORDS):
    """
    Analizzatore mediante il quale effettuo la tokenizzazione, il lowercase, 
    l'eliminazione delle stopword ,lo stemming e inoltre se sono presenti lettere
    con particolari accenti, queste vengono ricondotte ad una 'forma base'.
    'accent folding'
    ES: 'cafè' -> 'cafe'
    
    :param stoplist: lista di stopword. E' possibile effettuare l'unione con altre di un altra lista
    :cachesize: numero max di parole 'stemmate' da mantenere in cache. Più questo 
                numero è alto più è veloce la fase di stemming ma maggiore è anche
                la memoria occupata 
                -1 per definire la cache 'unbound' per lo stemming così da velocizzare l'indicizzazione.
    """
    return StemmingAnalyzer(stoplist=stoplist, cachesize=-1) \
            | CharsetFilter(accent_map)


def StemmingWithStopwordAnalyzer(stoplist=[',', '.', ':', ';']):
    """
    Analizzatore mediante il quale effettuo la tokenizzazione, il lowercase, 
    l'eliminazione delle stopword ,lo stemming e inoltre se sono presenti lettere
    con particolari accenti, queste vengono ricondotte ad una 'forma base'.
    'accent folding'
    ES: 'cafè' -> 'cafe'
    
    :param stoplist: lista di stopword. E' possibile effettuare l'unione con altre di un altra lista
    :cachesize: numero max di parole 'stemmate' da mantenere in cache. Più questo 
                numero è alto più è veloce la fase di stemming ma maggiore è anche
                la memoria occupata 
                -1 per definire la cache 'unbound' per lo stemming così da velocizzare l'indicizzazione.
    """
    return StemmingAnalyzer(stoplist=stoplist, cachesize=-1) \
            | CharsetFilter(accent_map)
            
        
             
                
                
                
                
                
                