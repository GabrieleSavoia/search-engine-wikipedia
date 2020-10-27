import math
import json

import os, os.path, re

from . import testSet
#import testSet
  
class Evaluator:
    """
    Classe per l'evaluation del sistema.
    """
    
    def __init__(self, index, settings):
        """
        Inizializzazione della classe. Qua definisco le query e calcolo i set per l'evaluation.

        :param self
        :param index: index su cui fare l'evaluation
        :param settings: dict che contiene i settings con cui eseguire le query
        """
        self.queries = set(('DNA', 'Apple', 'Epigenetics', 'Hollywood', 'Maya',
                           'Microsoft', 'Precision', 'Tuscany', '99 balloons',
                           'Computer Programming', 'Financial meltdown',
                           'Justin Timberlake', 'Least Squares', 'Mars robots',
                           'Page six', 'Roman Empire', 'Solar energy', 'Statistical Significance',
                           'Steve Jobs', 'The Maya', 'Triple Cross', 'US Constitution',
                           'Eye of Horus', 'Madam I’m Adam', 'Mean Average Precision', 
                           'Physics Nobel Prizes', 'Read the manual', 'Spanish Civil War',
                           'Do geese see god', 'Much ado about nothing'))
        
        self.R_set = self.__computeTestSet(index, 30, 10)
        self.A_set = self.__computeRetrievalSet(index, settings)

        """
        self.queries = set(('q1', 'q2'))

        self.R_set = {'q1': ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'l'], 
                      'q2': ['m', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v']}

        self.A_set = {'q1': ['x', 'b', 'v', 'd', 'p', 'f', 's', 'u', 't', 'v'], 
                      'q2': ['m', 'n', 'd', 'f', 'b', 'g', 'v', 't', 'a', 'l']}
        """

        
    def __computeTestSet(self, index, n_per_query, n_relevant):
        """
        Per ognuna delle 30 query fornite, eseguo una richiesta a Google, dalla quale mi salvo i primi 30 
        documenti rilevanti per ognuna (escludendo link non importanti). Per l'evaluation considero
        solo i primi n documenti come rilevanti e gli altri irrilevanti.
        Il calcolo dei 900 link lo eseguo una sola volta e mi salvo i risultati in un file.

        :param n: numero documenti rilevanti
        return dict con nome query e lista di n link rilevanti per ogni query
        """
        google_set = testSet.loadTestSet(index.args_paths.google_links, n_relevant)
        if not google_set:
            google_set = testSet.computeTestSet(self.queries, index.args_paths.google_links, 
                                                index.args_paths.interwiki_links, 
                                                n_per_query, n_relevant)
        return google_set

    
    def __computeRetrievalSet(self, index, settings):
        """
        Viene utilizzato il nostro modello IR per ricavare i documenti in base ad una data query.
        return: docs dizionario dei documenti ricavati dal nostro modello IR.
        """
        if settings['limit'] <= 0:
            settings['limit'] = 10      

        docs = {}
        for query in self.queries:
            docs[query] = [doc['link'] for doc in index.query(query, **settings)['docs']]

        return docs


    def __getPrecsionAndRecall(self, query, rank_pos=10):
        """
        Calcolo della precision e della recall per una determinata query ad una certa 
        posizione nel ranking.

        :param self
        :param query: query su cui calcolare precision e recall
        :param rank_pos: posizione del rank su cui calcolare precision e recall
        return precision, recall
        """
        if rank_pos > len(self.A_set[query]):
            print('Valore di rank_pos troppo grande.')
            rank_pos = len(self.A_set[query])

        a = len(self.A_set[query][:rank_pos])

        r = len(self.R_set[query])

        ra = len(set(self.R_set[query]) & set(self.A_set[query][:rank_pos]))

        try:
            precision = ra / a
        except ZeroDivisionError:
            precision = 0

        try:
            recall = ra / r
        except ZeroDivisionError:
            recall = 0

        return precision, recall


    def __precisonAtLevel(self, query, recall_level):
        """
        Viene calcolata la precision ad un determinato livello di recall, in riferimento ad una certa query.

        :param self
        :param query: la query in riferimento (suppongo che esista)
        :param recall_level: livello recall su cui calcolare precision (0...10) per semplicità
        return: precisione ad un certo livello di recall
        """
        relevants_retrieved = 0

        # recall_level parte da 1

        for count_retrieved, retrieved in enumerate(self.A_set[query], 1):
            if retrieved in self.R_set[query]:
                relevants_retrieved += 1

                if relevants_retrieved == recall_level:
                    return relevants_retrieved/count_retrieved  # count_retrieved parte da 1 e non è mai 0
        return 0


    def averagePrecisionAtLevel(self, round_precision=3):
        """
        Viene calcolata l'average precision (di tutte le query) per ogni livello (1...10) di recall.
        Per lo scopo di questo progetto, non è necessario gestire un numero di livelli di recall != da 10.
        Questi valori vengono poi rappresentati su grafico. 
        Determino così una curva precision-recall, che risulta essere importante per poter
        confrontare due sistemi, infatti la curva che è più vicina all'angolo in altro a destra
        del grafico, è quella che approssima il comportamento del sistema più performante. 

        :param self
        :param round_precision: arrotondamento dei valori di precision
        return: dict con chiavi i valori di recall e come valori le precision (per ogni livello di recall)
        """
        res = {}
        tot_queries = len(self.queries)
        levels = 10                     

        for level in range(1, levels+1):  # 1...10 compresi
            sum_precisions_at_level = sum([self.__precisonAtLevel(q, level) for q in self.queries])
            avg_precision_at_level = round( sum_precisions_at_level/tot_queries, round_precision)
            recall_level = level / levels
            res[recall_level] = avg_precision_at_level

        print('avgAtRecall: ', res)

        return res

    
    def MAP(self, round_map=3):
        """
        Mean Average Precision
        Si tratta di un singolo valore che ha lo scopo di fornire una stima sull'efficacia del sistema.
        Più documenti rilevanti vengono ritornati, più questo valore è alto.

        :param round_map: approssimazione del MAP 
        return: MAP calcolato (single value)     
        """
        avg_precisions_per_query = []
        tot_queries = len(self.queries)
        levels = 10

        for query in self.queries:
            sum_precisions_at_levels = sum( [self.__precisonAtLevel(query, level) for level in range(1, levels+1)] )
            avg_precision = sum_precisions_at_levels / levels
            avg_precisions_per_query.append(avg_precision)

        return round( sum(avg_precisions_per_query)/tot_queries ,round_map)

    
    def Rprecision(self, r=10, round_precision=3):
        """
        Per ogni query, calcolo la precison alla r-esima posizione nel ranking.

        :param r: r-esima posizione su cui calcolare la precision
        return: dict che ha come chiavi le query e come valori la r-precision
        """
        res = {}

        if r <= 0:
            print('Valore di \'r\' deve essere >0.')
            return None

        for query in self.queries:
            if r > len(self.A_set[query]):
                res[query] = 'error'
            else:
                relevants_in_r_retrieved = len(set(self.R_set[query]) & set(self.A_set[query][:r]))
                res[query] = round(relevants_in_r_retrieved/r, round_precision) 

        print('R-precision: ', res)
        
        return res


    def Emeasure(self, b, rank_pos=10, round_measure=3):
        """
        Permette all'utente di decidere se è più interessato a precision o recall cambiando il valore
        di 'b'.

        :param b: parametro per preferire recall o precision:
                    b=1 -> complementa F measure
                    b>1 -> enfatizza precision
                    b<1 -> enfatizza recall
        :param round_measure: approssimazione valore di e-measure
        return: dict con chiavi le query e valori la e-measure di ogni query 
        """

        e_measure = {}

        for query in self.queries:
            precision, recall = self.__getPrecsionAndRecall(query, rank_pos)
            try:
                res = round( 1-( (1+pow(b, 2)) / ( (pow(b, 2)/recall) + (1/precision) ) ), round_measure)
            except ZeroDivisionError:
                res = 0.0
            e_measure[query] = res

        print('e-measure: ', e_measure)

        return e_measure


    def Fmeasure(self, rank_pos=10, round_measure=3):
        """
        Media Armonica
        Valore elevato quando sia precision che recall sono alte.
        Compreso nell'intervallo [0,1]. 0 se non torno doc rilevanti, 1 se sono tutti rilevanti.

        :param self
        :param round_measure: arrotondamento de valore
        return: dict con chiavi le query e valori la f-measure di ogni query
        """

        f_measure = {}

        for query in self.queries:
            precision, recall = self.__getPrecsionAndRecall(query, rank_pos)
            try:
                res = round( (2*precision*recall) / (precision+recall), round_measure)
            except ZeroDivisionError:
                res = 0.0
            f_measure[query]= res

        print('f-measure: ', f_measure)

        return f_measure


    def getRelevanceVector(self, query, gt=False):
        """
        Assumiamo come ground truth per la query q i risultati in self.R_set[q].
        Ad ognuno di questi documenti associo un valore di rilevanza [6,5,4,3,2,1,1,1,1,1].
        Es: val 6 al primo doc ritornato, 5 al secondo ... Questa corrispondenza la salvo in 'doc_rel_gt'.

        Il relevance vector associato al sistema da valutare, è costruito prima di tutto calcolando il 
        relevance vector del ground truth, per poi scorrere ogni documento ritornato dal sistema, e
        se questo è presente in 'doc_rel_gt' allora gli associo il valore di rilevanza corrispondente,
        se no la rilevanza è 0.
        
        :param self
        :param query:
        :param gt: True se voglio che la funzione ritorni il relevance vector del Ground Truth
        return: lista di valori di rilevanza
        """
        rel_gt = [6,5,4,3,2,1,1,1,1,1]
        
        if gt:
            return rel_gt
        
        doc_rel_gt = {doc:rel_gt[pos] for pos, doc in enumerate(self.R_set[query])}
         
        return [doc_rel_gt[doc] if doc_rel_gt.get(doc, None) is not None else 0 
                            for doc in self.A_set[query]]
        
        
    @classmethod
    def DCG(cls, rel_vector, rank=10, log_base=2):
        """
        Formulazione classifica del DCG.
        Documenti rilevanti è preferibile che si trovino in posizioni di ranking alte.
        Documenti rilevanti che si trovano alla fine del ranking hanno un impatto minore sul valore 
        di DCG totale.

        :param cls
        :param rel_vector: vettore di rilevanza
        :param rank: livello di ranking
        :param log_base: base del logaritmo
        return: valore dcg calcolato
        """
        if rank > len(rel_vector):
            rank = len(rel_vector)  
        elif rank<0:
            rank = 0
            
        if len(rel_vector)==0:
            return 0
        
        if len(rel_vector)==1:
            return rel_vector[0]
        
        return rel_vector[0]+sum([ rel_i / math.log(i,log_base)         # rel_vector[1:] --> elem 1 compreso
                                   for i, rel_i in enumerate(rel_vector[1:], 2) if i <= rank])         
            
                
    def NDCG(self, round_ndcg=3):
        """
        Valore del DCG normalizzato rispetto al ranking ideale.

        :param elf
        :param round_ndcg: arrotondamento valore ndcg
        return: valore ndcg
        """
        rank = 10

        res = {query : round(Evaluator.DCG(self.getRelevanceVector(query), rank) / 
                              Evaluator.DCG(self.getRelevanceVector(query, gt=True), rank), round_ndcg) 
                            for query in self.queries}

        avg = sum([v for v in res.values()]) / len(res.values())
        print('AVG NDCG, ',avg)
    
        return res


    def results(self, query):
        """
        Ritorna un dict con tutti i documenti ritornati da Google e quelli ritornati dal sistema,
        in riferimento ad una certa query.

        :param self
        :param query
        """
        return {'r': self.R_set.get(query, None), 'a': self.A_set.get(query, None)}
 
 
"""
e = Evaluator(None, None)  

avg_prec_at_recall = e.averagePrecisionAtRecall()

print('avg_prec_at_recall: ', avg_prec_at_recall)
e.MAP(avg_prec_at_recall)

r_prec = e.Rprecision()

print('r-prec: ', r_prec)

e.Emeasure(1.5)

e.Fmeasure()

print('ndcg: ', e.NDCG())
"""







    
    
    