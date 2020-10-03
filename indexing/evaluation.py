#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 14:46:17 2020

@author: gabrielesavoia
"""

# https://stackoverflow.com/questions/37083058/programmatically-searching-google-in-python-using-custom-search
# https://programmablesearchengine.google.com/cse/setup/basic?cx=5fcf76f44c6462b11
from googleapiclient.discovery import build

# https://www.geeksforgeeks.org/performing-google-search-using-python-code/    
import googlesearch

import math

"""
my_api_key = "AIzaSyAPH6BrV0tw9ZB9evu0cx6bQlQ3Wriq-OY" #The API_KEY you acquired
my_cse_id = "5fcf76f44c6462b11" #The search-engine-ID you created
def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']['link']
results = google_search('dna', my_api_key, my_cse_id, num=10)
for result in results:
    print(result['link'])    
print('\n')  


# FORMULAZIONE ALTERNATIVA DCG

    @classmethod
    def DCG_(cls, rel_vector, rank=None, log_base=2):
        #Formulazione alternativa del DCG
        
        if rank is None or rank > len(rel_vector):
            rank = len(rel_vector) 
        elif rank<0:
            rank = 0            
        
        return sum([ ((2**rel_i)-1)/
                     math.log(2+i,log_base) 
                   for i, rel_i in enumerate(rel_vector) if i < rank])  
"""
    
    
class Evaluator:
    """
    
    """
    
    def __init__(self, ir_system, n_docs_per_query=10):
        """
        
        """
        self.ir_system = ir_system
        self.n_docs_per_query = n_docs_per_query
        self.queries = set(('DNA', 'apple', 'Epigenetics', 'Hollywood', 'Maya',
                           'Microsoft', 'Precision', 'Tuscany', '99 balloons',
                           'Computer Programming', 'Financial meltdown',
                           'Justin Timberlake', 'Least Squares', 'Mars robots',
                           'Page six', 'Roman Empire', 'Solar energy', 'Statistical Significance',
                           'Steve Jobs', 'The Maya', 'Triple Cross', 'US Constitution',
                           'Eye of Horus', 'Madam I’m Adam', 'Mean Average Precision', 
                           'Physics Nobel Prizes', 'Read the manual', 'Spanish Civil War',
                           'Do geese see god', 'Much ado about nothing'))
        self.queries = set(('dna', 'apple'))
        
        self.test_set = self.__computeTestSet()
        self.retrieval_set = self.__computeRetrievalSet()
        
        
    def __computeTestSet(self):
        """
        
        """
        docs = {}
        
        for query in self.queries:
            docs[query] = []
            for doc in googlesearch.search(query, tld="com", num=self.n_docs_per_query, 
                                           stop=self.n_docs_per_query, 
                                           pause=2, lang='en'): 
                docs[query].append(doc) 
                
        return docs
    
    
    def __computeRetrievalSet(self):
        """
        
        """
        docs = {}
        
        for query in self.queries:
            docs[query] = [doc['link'] for doc in self.ir_system(query)]
            
        return docs
    
    
    def MAP_(self):
        """
        
        """
        return sum([len(set(self.test_set.keys()) & set(self.retrieval_set.keys())) / 
                    len(self.retrieval_set) for _ in self.queries]) / len(self.queries)
    
    
    def getRelevanceVector(self, query, gt=False):
        """
        
        """
        rel_gt = [6,5,4,3,2,1,1,1,1,1]
        
        if gt:
            return rel_gt
        
        doc_rel_gt = {doc:rel_gt[pos] for pos, doc in enumerate(self.test_set[query])}
         
        return [doc_rel_gt[doc] if doc_rel_gt.get(doc, None) is not None else 0 
                            for doc in self.retrieval_set[query]]
        
        
    @classmethod
    def DCG(cls, rel_vector, rank=None, log_base=2):
        """
        Formulazione classica del DCG
        """
        if rank is None or rank > len(rel_vector):
            rank = len(rel_vector)  
        elif rank<0:
            rank = 0
            
        if len(rel_vector)==0:
            return 0
        
        if len(rel_vector)==1:
            return rel_vector[0]
        
        return rel_vector[0]+sum([ rel_i /
                                   math.log(i,log_base) 
                                 for i, rel_i in enumerate(rel_vector[1:], 2) if i <= rank])         
            
                
    def NDCG(self):
        """
        Valore del DCG normalizzato.
        """
    
        return {query : Evaluator.DCG(self.getRelevanceVector(query)) / 
                        Evaluator.DCG(self.getRelevanceVector(query, gt=True)) 
                            for query in self.queries}
 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    