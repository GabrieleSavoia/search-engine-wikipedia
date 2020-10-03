#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:44:24 2020

@author: gabrielesavoia
"""
import nltk

from whoosh.analysis import Tokenizer, Token
         
class NltkTokenizerWithPOStag(Tokenizer):
    """
    La tokenizzazione è fatta tramite nltk e contemporaneamente avviene
    anche il POS tag per ogni token.
    Questo viene aggiunto come attributo della classe Token.
    
    Eseguo il POS tagging in fase di tokenizzazione perchè 'nltk.pos_tag'
    ha un funzionamento corretto solo se gli passo insieme tutti i token da 
    elaborare.
    Infatti se provo a passargli singolarmente le varie parole il tagging 
    può risultare scorretto.
    ESEMPIO:
        1)  QUA VA BENE :
            tokens = nltk.word_tokenize("born")  
            
            print(nltk.pos_tag(tokens))          # 'born' -> 'NN' -> OK
            
            for i in tokens:
                print(nltk.pos_tag([i]))         # 'born' -> 'NN' -> OK
                
        2)  MA QUA NO :
            tokens = nltk.word_tokenize("I was born")  
            
            print(nltk.pos_tag(tokens))          # 'born' -> 'VB' -> OK
            
            for i in tokens:
                print(nltk.pos_tag([i]))         # 'born' -> 'NN' -> NO perchè in questo 
                                                                    è verbo
            
    """
    
    def __eq__(self, other):
        """
        Da defnire per permettere la comparazione degli oggetti 'Schema'.
        """
        return (other 
                and self.__class__ is other.__class__)
    
    
    def __call__(self, value, positions = False, chars = False,
                 keeporiginal = False, removestops = True,
                 start_pos = 0, start_char = 0, mode = '', **kwargs):
        """
        Eseguo tokenizzazione con nltk e post tag.
        
        :param value: La stringa unicode da tokenizzare
        :param positions: Se salvarsi le posizioni
        :param chars: Se salvarsi indice dei caratteri
        :param keeporiginal: Se salvarsi il token originale no filtrato
        :param removestops: se eliminare le stopword (True)
        :param start_pos: offset per la posizione iniziale
            se start_pos=2, i token saranno numerati 2,3,4,...
            invece di 0,1,2,...
        :param start_char: offset per l'indice inizale dei caratteri. 
            se start_char=2, il testo "aaa bbb"
            avrà (2,5),(6,9) invece di (0,3),(4,7).
        """
        
        assert isinstance(value, str), "%r is not unicode" % value
        
        tagged_tokens = [token for token in nltk.pos_tag(nltk.word_tokenize(value))]
        
        t = Token(positions, chars, removestops=removestops, mode=mode)

        count_char = 0
        for counter, token in enumerate(tagged_tokens):
            t.text = token[0]
            t.tag = token[1][0:2]
            t.boost = 1.0
            if keeporiginal:
                t.original = t.text
            t.stopped = False
            if positions:
                t.pos = start_pos + counter
            if chars:
                t.startchar = start_char + count_char 
                t.endchar = start_char + (count_char + len(t.text))
                count_char += len(t.text)+1
            yield t 
  
