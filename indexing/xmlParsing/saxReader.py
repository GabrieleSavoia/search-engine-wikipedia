#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 14:13:56 2020

@author: gabrielesavoia
"""
import xml
from xml.sax import ContentHandler
from xml.sax.xmlreader import Locator

from xml.sax.expatreader import ExpatParser

from . import filterText

import sys

import os

# https://en.wikipedia.org/wiki/Wikipedia:Namespace

NS_NOT_VALID = {'-2': 'Media', 
                '-1': 'Special', 
                '1': 'Talk', 
                '2': 'User' , 
                '3': 'User_talk', 
                '4': 'Wikipedia',
                '5': 'Wikipedia_talk', 
                '6': 'File', 
                '7': 'File_talk',
                '8': 'MediaWiki', 
                '9': 'MediaWiki_talk', 
                '10': 'Template',
                '11': 'Template_talk', 
                '12': 'Help', 
                '13': 'Help_talk', 
                '14': 'Category', 
                '15': 'Category_talk', 
                '100': 'Portal',
                '101': 'Portal_talk', 
                '108': 'Book',
                '109': 'Book_talk', 
                '118': 'Draft',
                '119': 'Draft_talk', 
                '446': 'Education_Program',
                '447': 'Education_Program_talk', 
                '710': 'TimedText',
                '711': 'TimedText_talk', 
                '828': 'Module',
                '829': 'Module_talk', 
                '2300': 'Gadget',
                '2301': 'Gadget_talk',
                '2302': 'Gadget_definition',
                '2303': 'Gadget_definition_talk',
                }


class BaseContentHandler(ContentHandler):
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
        
        self.current_tag = ''
        self.block_tag = 'page'
        
        self.title = ''
        self.id_page = ''
        self.text = ''
        
        self.valid_block = True
        self.valid_id_page = True
                            

    def startElement(self, tag, attributes):
        """
        Ogni volta che inizia un ELEMENTO (<TAG>) viene chiamata questa funzione.
        
        :param self
        :param tag: ovvero il nome dell'elemento es: ' <movie> </movie> ' -> tag è 'movie'
        :attributes: ovvero gli attributi riferiti ad un certo elemento.
                        E' un DICT in cui ci si accede passando il nome degli attributi.
        """
        self.current_tag = tag

        if self.current_tag == 'revision':
            self.valid_id_page = False
        
       
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
                self.valid_block = self.__validNs(content)

            elif self.current_tag == 'id':
                if self.__validId():
                    self.id_page += content
                
            elif self.current_tag == 'text':
                self.valid_block = self.__validText(content)
                if self.valid_block:
                    self.text += content 

                
    def __validNs(self, ns):
        """
        Controlla che il namespace sia valido.
        Non è valido se ha uno dei valori qua scritti.
        
        :param self
        :param ns: numero del namespace        
        """
        if ns in NS_NOT_VALID.keys():
            return False
        return True


    def __validId(self):
        """
        Controllo che l'id non si riferisca alla sezione di revision ma sia l'id della pagina.

        :param self:
        """
        return self.valid_id_page              
                
                
    def __validText(self, text):
        """
        Controlla che il testo sia valido.
        Non è valido se contiene un redirect
        
        :param self
        :param text: testo da controllare
        """        
        if text.startswith('#REDIRECT'):
            return False
        return True                     


    def endElement(self, tag):
        """
        Da implementare per ogni instanza.
        
        :param self
        :param tag : ovvero il nome dell'elemento es: ' <movie> </movie> ' -> tag è 'movie'
        """
        raise NotImplementedError

    def reset(self):
        """
        Reset delle variabili dopo aver completato la lettura di una pagina.

        :param self
        """
        self.title = ''
        self.id_page = ''
        self.text = ''

        self.valid_block = True
        self.valid_id_page = True


class EndFilterDumpException(Exception):
    """
    Eccezione creata per terminare la lettura del xml usando il 'FilterDumpHandler'.
    """
    pass


class FilterDumpHandler(BaseContentHandler):
    """
    Sottoclasse di xml.sax.ContentHandler
    """
    
    def __init__(self, total_docs_noise, titles_to_select, fn, *args_fn, **kwargs_fn):
        """
        Inizializzazione variabili di instanza.
        """
        super().__init__(fn, *args_fn, **kwargs_fn)

        self.total_docs_noise = total_docs_noise
        self.curr_docs_noise = 0

        self.titles_to_select = titles_to_select
        self.curr_selected = 0


    def checkAndSelect(self):
        """
        Controllo se la pagina è selezionabile e in caso affermativo la seleziono, se no 
        ritorno False

        :param self
        return dict con i valori della pagina se è selezionabile, False atrimenti
        """
        res = {'title': self.title,
               'id': self.id_page,
               'text': self.text,
              }

        if self.title in self.titles_to_select:
            self.curr_selected += 1
            return res

        elif self.curr_docs_noise < self.total_docs_noise:
            self.curr_docs_noise += 1
            return res

        else:
            return False


    def noMoreSelectable(self):
        """
        Controllo se non ci sono più elementi selezionabili nel dump.

        :param self
        return True se non ci sono più elementi selezionabili, False se ce ne sono
        """
        return (self.curr_selected == len(self.titles_to_select)) and \
               (self.curr_docs_noise == self.total_docs_noise)
                

    def endElement(self, tag):
        """
        Ogni volta che termina un ELEMENTO (</TAG>) viene chiamata questa funzione.
        Aggiungo un documento all'indice nel caso in cui il tag chiuso sia una
        pagina, ovvero ho letto tutte le informazioni di una pagina e le voglio
        indicizzare.
        In questo caso svolgo anche il filtraggio del testo dell'xml ricavando gli elementi che 
        mi servono.
        
        :param self
        :param tag : ovvero il nome dell'elemento es: ' <movie> </movie> ' -> tag è 'movie'
        """
        if tag == self.block_tag: 
            if self.valid_block:
                res = self.checkAndSelect()

                if res:
                    self.fn(*self.args_fn, **self.kwargs_fn, **res)

            if self.noMoreSelectable():
                raise EndFilterDumpException

            self.reset()  


class WikiDumpHandler(BaseContentHandler):
    """
    Sottoclasse di xml.sax.ContentHandler
    """
    
    def __init__(self, path_interwiki_links, fn, *args_fn, **kwargs_fn):
        """
        Inizializzazione variabili di instanza.
        """
        super().__init__(fn, *args_fn, **kwargs_fn)

        self.filter = filterText.FilterWikiText(path_interwiki_links)


    def endElement(self, tag):
        """
        Ogni volta che termina un ELEMENTO (</TAG>) viene chiamata questa funzione.
        Aggiungo un documento all'indice nel caso in cui il tag chiuso sia una
        pagina, ovvero ho letto tutte le informazioni di una pagina e le voglio
        indicizzare.
        In questo caso svolgo anche il filtraggio del testo dell'xml ricavando gli elementi che 
        mi servono.
        
        :param self
        :param tag : ovvero il nome dell'elemento es: ' <movie> </movie> ' -> tag è 'movie'
        """
        if tag == self.block_tag: 
            if self.valid_block:

                filtered = self.filter.startFilter(self.text, self.title)
        
                res ={'title': self.title,
                      'id': self.id_page.strip(),
                      'text': filtered['text'],
                      'internal_link': filtered['links'],
                      }

                # Usa il risultato
                self.fn(*self.args_fn, **self.kwargs_fn, **res)

            self.reset() 


def startParse(path_file, handler):  
    parser = xml.sax.make_parser() 
    parser.setFeature(xml.sax.handler.feature_namespaces, 0) 

    parser.setContentHandler(handler) 
    parser.parse(path_file)        
        
            
def readXML(args_paths, fn, *args_fn, **kwargs_fn):
    """
    Definisco il parser, instanzio il mio ContentHandler e poi eseguo il vero e proprio parsing.
    
    :param path_file: il path relativo per il file xml.
    :param fn: la funzione da eseguire quando il parser ha riconosciuto 
                una certo blocco che mi interessa
    :param args_fn: argomenti da passare alla funzione
    :param kwargs_fn: argomenti da passare alla funzione
    """
    handler = WikiDumpHandler(args_paths.interwiki_links, fn, *args_fn, **kwargs_fn)

    startParse(args_paths.corpus, handler)


def filterXML(path_file, total_docs_noise, titles_to_select, fn, *args_fn, **kwargs_fn):
    """
    Definisco il parser, instanzio il mio ContentHandler e poi eseguo il vero e proprio parsing.
    
    :param path_file: il path relativo per il file xml
    :param total_docs_noise: num totale di doc di rumore
    :param titles_to_select: iterabile di titoli da filtrare
    :param fn: la funzione da eseguire quando il parser ha riconosciuto 
                una certo blocco che mi interessa
    :param args_fn: argomenti da passare alla funzione
    :param kwargs_fn: argomenti da passare alla funzione
    """
    handler = FilterDumpHandler(total_docs_noise, titles_to_select,
                                fn, *args_fn, **kwargs_fn)

    try:    
        startParse(path_file, handler)
    except EndFilterDumpException:
        pass
