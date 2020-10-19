import math
import json

import os, os.path, re

from . import testSet

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
    
    def __init__(self, index, settings):
        """
        
        """
        self.index = index
        self.settings = settings
        self.settings['limit'] = 10       # per l'evaluation lo considero sempre a 10
        
        self.queries = set(('DNA', 'Apple', 'Epigenetics', 'Hollywood', 'Maya',
                           'Microsoft', 'Precision', 'Tuscany', '99 balloons',
                           'Computer Programming', 'Financial meltdown',
                           'Justin Timberlake', 'Least Squares', 'Mars robots',
                           'Page six', 'Roman Empire', 'Solar energy', 'Statistical Significance',
                           'Steve Jobs', 'The Maya', 'Triple Cross', 'US Constitution',
                           'Eye of Horus', 'Madam I’m Adam', 'Mean Average Precision', 
                           'Physics Nobel Prizes', 'Read the manual', 'Spanish Civil War',
                           'Do geese see god', 'Much ado about nothing'))
        
        self.google_set = self.__computeTestSet(30, 10)
        self.retrieval_set = self.__computeRetrievalSet()

        
    def __computeTestSet(self, n_per_query, n_relevant):
        """
        Per ognuna delle 30 query fornite, eseguo una richiesta a Google, dalla quale mi salvo i primi 30 
        documenti rilevanti per ognuna (escludendo link non importanti). Per l'evaluation considero
        solo i primi n documenti come rilevanti e gli altri irrilevanti.
        Il calcolo dei 900 link lo eseguo una sola volta e mi salvo i risultati in un file.

        :param n: numero documenti rilevanti
        return dict con nome query e lista di n link rilevanti
        """
        google_set = testSet.loadTestSet(self.index.args_paths.google_links, n_relevant)
        if not google_set:
            google_set = testSet.computeTestSet(self.queries, self.index.args_paths.google_links, 
                                                self.index.args_paths.interwiki_links, 
                                                n_per_query, n_relevant)
        return google_set

    

    def __computeRetrievalSet(self):
        """
            Viene utilizzato il nostro modello IR per ricavare i documenti in base ad una data query.
            :return docs dizionario dei documenti ricavati dal nostro modello IR.
        """
        docs = {}
        for query in self.queries:
            docs[query] = [doc['link'] for doc in self.index.query(query, **self.settings)['docs']]

        return docs


    def precisonAtLevel(self, recall_level, query):
        """

        """
        relevant = 0

        if recall_level == 0: recall_level=1

        for count_retrieved, retrieved in enumerate(self.retrieval_set[query], 1):
            if retrieved in self.google_set[query]:
                relevant += 1

                if relevant == recall_level:
                    return relevant/count_retrieved
        return 0


    def averagePrecisionAtRecall(self, round_precision=3):
        """

        """
        res = {}
        tot_queries = len(self.queries)

        for recall_level in range(11):  # 0...10
            precision = round(sum([self.precisonAtLevel(recall_level, q) for q in self.queries]) / tot_queries,
                              round_precision)
            recall = recall_level / 10
            res[recall] = precision

        return res

    
    def MAP(self, round_map=3):
        """
        - Ogni query ha lo stesso peso
        - Assume che utente sia interessato a ritornare il maggior numero di documenti rilevanti per la query
        """
        return round( sum([len(set(self.google_set[query]) & set(self.retrieval_set[query])) / 
                      len(self.retrieval_set[query]) for query in self.queries if len(self.retrieval_set[query]) != 0]) / len(self.queries), round_map)
    
    
    def Rprecision(self, r=10, round_precision=3):
        """
        :param r: 
        """
        res = {}

        for query in self.queries:
            first_r_relevants = len(set(self.google_set[query]) & set(self.retrieval_set[query][:r]))
            res[query] = round(first_r_relevants/r, round_precision) 
        
        return res


    def Emeasure(self, query, b):

        ra = len(set(self.google_set[query]) & set(self.retrieval_set[query]))

        try:
            recall = ra / len(self.google_set[query])
        except ZeroDivisionError:
            recall = 0

        try:
            precision = ra / len(self.retrieval_set[query])
        except ZeroDivisionError:
            precision = 0

        try:
            res = 1-( (1+pow(b, 2)) / ( (pow(b, 2)/recall) + (1/precision) ) )
        except ZeroDivisionError:
            res = 0

        return res


    def computeEmeasure(self, b, round_emeasure=3):

        return {query: round(self.Emeasure(query, b), round_emeasure) for query in self.queries}


    def Fmeasure(self, query):

        ra = len(set(self.google_set[query]) & set(self.retrieval_set[query]))

        try:
            recall = ra / len(self.google_set[query])
        except ZeroDivisionError:
            recall = 0

        try:
            precision = ra / len(self.retrieval_set[query])
        except ZeroDivisionError:
            precision = 0

        try:
            res = (2*(precision*recall)) / precision+recall
        except ZeroDivisionError:
            res = 0

        return res


    def computeFmeasure(self, round_fmeasure=3):

        return {query: round(self.Fmeasure(query), round_fmeasure) for query in self.queries}


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
            
                
    def NDCG(self, round_ndcg=3):
        """
        Valore del DCG normalizzato.
        """
    
        return {query : round(Evaluator.DCG(self.getRelevanceVector(query)) / 
                              Evaluator.DCG(self.getRelevanceVector(query, gt=True)), round_ndcg) 
                            for query in self.queries}
 
       
    
    
    