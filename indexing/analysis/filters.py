#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:42:15 2020

@author: gabrielesavoia
"""
import nltk 

from whoosh.analysis import Filter

class NounSelectionFilter(Filter):
    """ Selezione dei nomi ed eliminazione del resto.
        E' una metodologia per ridurre la grandezza dell'iverted index considerando 
        il fatto che questi rappresentano le parti del testo con maggiore 
        significato.
    """
    
    def __init__(self, renumber=True):
        """
        Per poter funzionare è necessario che i token forniti abbiano 
        l'attributo TAG, ovvero che venga usato il tokenizzatore :
            NltkTokenizerWithPOStag
        
        :param renumber: se True aggiorna la 'pos' dei vari token considerati 
                            in seguito all'eliminazione di uno di essi.
        """
        
        self.renumber = renumber
        
    def __eq__(self, other):
        """
        Da definire per permettere la comparazione degli oggetti 'Schema'.
        """
        return (other
                and self.__class__ is other.__class__
                and self.renumber == other.renumber)        
    
    def __call__(self, tokens):
        """
        Rimozione dei vari token che non sono dei nomi.
        Non è presente la marcatura di essi come nel caso della rimozione
        delle stopword.
        
        IMPORTANTE : se il token non è un nome, questo non viene restituito. 
                     Ovvero non c'è marcatura.
        
        :param tokens : ovvero i token provenienti dal tokenizzatore che 
                    possono essere o meno filtrati
        """

        renumber = self.renumber       
    
        pos = None
        for token in tokens:
            if not token.stopped and token.tag == 'NN':
                # Se è un nome e token.positions=True con renumber=True
                if renumber and token.positions:
                    if pos is None:
                        pos = token.pos
                    else:
                        pos += 1
                        token.pos = pos 
                yield token
                                

class LemmatizerFilter(Filter):
    """
    Filtro che effettua la lemmatizzazione del testo del token
    """
    
    def __call__(self, tokens):
        for token in tokens:
            token.text = nltk.WordNetLemmatizer().lemmatize(token.text)
            yield token
  