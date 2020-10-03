#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 15:54:36 2020

@author: gabrielesavoia
"""

from whoosh.qparser import MultifieldParser
from whoosh.searching import Searcher as WhooshSearcher
from whoosh import scoring, qparser

from .queryElaboration import expansion

#from analysis.analyzers import LemmatizingAnalyzer

class WikiSearcher:
    
    def __init__(self, index, weighting='BM25F', group='AND', text_boost=1.0, 
                 title_boost=1.0):
        """
        PARSER 
            - MULTIFIELD così effettuo ricerca sia nel titolo che nel testo.
                         Il parser utilizza un analizzatore per analizzare la query.
                         Se ho definito 2 analyzer diversi per titolo e testo, questi vengono
                         usati rispettivamente per parsare la query per il titolo e per il testo.
                         ES: testo con stemmer e titolo senza stemmer:
                             query: 'fortified' --> query parsata :'(text:fortifi OR title:fortified)'
                             
            - GROUP default concatena i token con 'AND'. Specificando 'OrGroup' concatena con OR.
                    Utilizzando il FACTORY, do un punteggio maggiore ai documenti in cui un certo termine
                    ha una frequenza più alta. Senza FACTORY non ho questo effetto.
                    
            - FIELDBOOST associa un valore di boost ai fields.        
        """
        self.index = index
        
        self.weighting=scoring.BM25F
        if weighting == 'TF_IDF':
            self.weighting=scoring.TF_IDF
        
        if group == 'OR':
            group = {'group': qparser.OrGroup}
        else:
            group = {}
            
        self.parser = MultifieldParser(["text", "title"], 
                                       fieldboosts={'text': text_boost, 'title': title_boost},
                                       schema=index.schema,
                                       **group)
        
    
    def search(self, text, limit=10, exp=True):
        """
        
        """
        if exp:
            list_token_expanded = expansion(text)
            expandend = ' OR ( '+' OR '.join(list_token_expanded)+' )'
            text = '( '+text+' )'+expandend
            
        query = self.parser.parse(text)
        
        print('\n')
        print(query)
        
        get_link = lambda title: 'https://en.wikipedia.org/wiki/'+title.replace(" ", "_")
        
        res = {}
        with self.index.searcher(weighting=self.weighting) as searcher:
            results = searcher.search(query, limit=limit)
            
            res['time_second'] = results.runtime 
            res['expanded'] = list_token_expanded if exp else []
            res['n_res'] = results.estimated_length()
            res['docs'] = [{'link': get_link(result['title']),
                            'title': result['title'], 
                            'text': result['text'],
                            'highlight': result.highlights("text", top=2),
                            'score': result.score} for result in results]
        return res
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        