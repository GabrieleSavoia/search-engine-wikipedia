
# https://www.geeksforgeeks.org/performing-google-search-using-python-code/    
from googlesearch import search 

import math
import time
import json

"""
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
    
    def __init__(self, ir_system, settings):
        """
        
        """
        self.ir_system = ir_system
        self.settings = settings
        
        self.queries = set(('DNA', 'Apple', 'Epigenetics', 'Hollywood', 'Maya',
                           'Microsoft', 'Precision', 'Tuscany', '99 balloons',
                           'Computer Programming', 'Financial meltdown',
                           'Justin Timberlake', 'Least Squares', 'Mars robots',
                           'Page six', 'Roman Empire', 'Solar energy', 'Statistical Significance',
                           'Steve Jobs', 'The Maya', 'Triple Cross', 'US Constitution',
                           'Eye of Horus', 'Madam I’m Adam', 'Mean Average Precision', 
                           'Physics Nobel Prizes', 'Read the manual', 'Spanish Civil War',
                           'Do geese see god', 'Much ado about nothing'))
        
        self.google_set = self.__computeTestSet()
        self.retrieval_set = self.__computeRetrievalSet()

        
    def __computeTestSet(self):
        """
            site:en.wikipedia.org
            docs = {}

            for query in self.queries:
                docs[query] = []
                for doc in search(query+' site:en.wikipedia.org', tld="com", pause=2, lang='en'):
                    if "Category:" in doc or "User:" in doc:
                        pass
                    else:
                        docs[query].append(doc) 
                    if len(docs[query]) == 10:
                        break
                    time.sleep(2)

            print(docs)
            
            with open('google_links.json', 'w') as fp:
                json.dump(docs, fp)

            Abbiamo utilizzato la funzione qua sopra per ricavare i primi 10 risultati di google per ogni query.
            I risultati ottenuti sono link a pagine che sono presenti anche nel nostro dump di wikipedia.
            Viene infine salvato il dizionario ottenuto in un file .json per motivi di velocità.

            :return docs dizionario dei documenti ricavati da google.
        """

        with open('files/google_links.json', 'r') as fp:
            docs = json.load(fp)

        return docs
    

    def __computeRetrievalSet(self):
        """
            Viene utilizzato il nostro modello IR per ricavare i documenti in base ad una data query.
            :return docs dizionario dei documenti ricavati dal nostro modello IR.
        """
        docs = {}
        
        for query in self.queries:
            docs[query] = [doc['link'] for doc in self.ir_system.query(query, **self.settings)['docs']]

        return docs
    
    
    def MAP(self):
        """
        
        """
        return sum([len(set(self.google_set[query]) & set(self.retrieval_set[query])) / 
                    len(self.retrieval_set[query]) for query in self.queries if len(self.retrieval_set[query]) != 0]) / len(self.queries)
    
    
    def getRelevanceVector(self, query, gt=False):
        """
        
        """
        rel_gt = [6,5,4,3,2,1,1,1,1,1]
        
        if gt:
            return rel_gt
        
        doc_rel_gt = {doc:rel_gt[pos] for pos, doc in enumerate(self.google_set[query])}
         
        return [doc_rel_gt[doc] if doc_rel_gt.get(doc, None) is not None else 0 
                            for doc in self.retrieval_set[query]]
        
        
    @classmethod
    def DCG(cls, rel_vector, rank=None, log_base=2):
        """
        Formulazione classifica del DCG
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
 
       
    
    
    