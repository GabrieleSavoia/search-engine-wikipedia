#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 14:13:56 2020

@author: gabrielesavoia
"""
import xml
from xml.sax import ContentHandler
from xml.sax.xmlreader import Locator

from . import filterText

import sys


class SaxContentHandler(ContentHandler):
    """
    Sottoclasse di xml.sax.ContentHandler
    """
    
    def __init__(self, fn, *args_fn, **kwargs_fn):
        """
        Inizializzazione variabili di instanza.
        """
        self.fn = fn
        self.args_fn = args_fn
        self.kwargs_fn = kwargs_fn
        
        self.current_tag = ""
        self.block_tag = 'page'
        
        self.title = ''
        self.text = ''
        
        self.valid_block = True

        self.filter = filterText.FilterWikiText()
                            

    def startElement(self, tag, attributes):
        """
        Ogni volta che inizia un ELEMENTO (<TAG>) viene chiamata questa funzione.
        
        :param self
        :param tag: ovvero il nome dell'elemento es: ' <movie> </movie> ' -> tag è 'movie'
        :attributes: ovvero gli attributi riferiti ad un certo elemento.
                        E' un DICT in cui ci si accede passando il nome degli attributi.
        """
        self.current_tag = tag
        
       
    def characters(self, content):
        """
        Ogni volta che il contenuto di un ELEMENTO viene letto (<TAG> Nome film </TAG>) 
        questa funzione viene chiamata.
        In questo caso 'content' = 'Nome Film'.
        Il content si riferisce al tag corrispondente a 'self.currentTag', ovvero
        l'ULTIMO TAG aperto e non ancora chiuso.
        
        : param self
        :param content: contenuto di un elemento.
        """
        if self.valid_block:
            
            if self.current_tag == 'title':
                self.title += content.strip()
                
            elif self.current_tag == 'ns':
                self._checkValidNs(content)
                
            elif self.current_tag == 'text' and self._validText(content):
                self.text += content
                
                
    def _checkValidNs(self, ns):
        """
        Controlla che il namespace sia valido.
        Non è valido se ha uno dei valori qua scritti.
        
        :param self
        :param ns: numero del namespace        
        """
        if ns==6 or ns==7:
            self.valid_block = False
        return self.valid_block                 
                
                
    def _validText(self, text):
        """
        Controlla che il testo sia valido.
        Non è valido se contiene un redirect
        
        :param self
        :param text: testo da controllare
        """        
        if text.startswith('#REDIRECT'):
            self.valid_block = False
        return self.valid_block                           


    def endElement(self, tag):
        """
        Ogni volta che termina un ELEMENTO (</TAG>) viene chiamata questa funzione.
        Aggiungo un documento all'indice nel caso in cui il tag chiuso sia una
        pagina, ovvero ho letto tutte le informazioni di una pagina e le voglio
        indicizzare.
        In questo caso svolgo anche il filtraggio del testo dell'xml ricavando gli elementi che 
        mi servono come i link e le categorie a cui appartiene la pagina.
        
        :param self
        :param tag : ovvero il nome dell'elemento es: ' <movie> </movie> ' -> tag è 'movie'
        """
        if tag == self.block_tag and self.valid_block:
            
            # Filtraggio
            res ={}
            filtered = self.filter.performFiltering(self.text, self.title)
            res['internal_link'] = filtered['links']
            res['text'] = filtered['text_filtered']
            res['title'] = self.title

            # Usa il risultatao
            self.fn(*self.args_fn, **self.kwargs_fn, **res)
            
            # Reset
            self.title = ''
            self.text = ''
            
        
def readXML(path_file, fn, *args_fn, **kwargs_fn):
    """
    Definisco il parser, instanzio il mio ContentHandler e poi eseguo il vero e proprio parsing.
    
    :param path_file: il path relativo per il file xml.
    :param fn: la funzione da eseguire quando il parser ha riconosciuto 
                una certo blocco che mi interessa
    :param args_fn: argomenti da passare alla funzione
    :param kwargs_fn: argomenti da passare alla funzione
    """
       
    parser = xml.sax.make_parser() 
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    
    handler = SaxContentHandler(fn, *args_fn, **kwargs_fn)
    parser.setContentHandler(handler)
       
    parser.parse(path_file)
    
    
    
    
    
    
    
    
    
    




