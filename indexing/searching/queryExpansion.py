#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 26 15:21:04 2020

@author: gabrielesavoia
"""

import nltk    
from nltk.corpus import wordnet as wn  
from nltk.wsd import lesk

class Disambiguator():

    @classmethod
    def leskDisambiguate(cls, *args, **kwargs):
        """
        DOC: https://www.nltk.org/_modules/nltk/wsd.html
        
        """
        return lesk(*args, **kwargs)

    @classmethod
    def nounSenseDisambiguate(cls, tokens, index_term, *args):
        """
        Avviene la disambiguazione (ovvero ritorno il significato più pertinente) in riferimento
        al token 'index_term' nell'insieme 'tokens'.
        
        Per ogni index_term Tx, devo assegnarli il proprio significato corretto in base 
        al contesto in cui si trova.
        Per ogni suo significato TxSi, calcolo uno score score_TxSi :
            1) per ogni termine Ty != Tx mi ricavo il max_score ovvero il valore max 
               di similarità tra TxSi e OGNI significato TySz di Ty
            2) sommo il max_score di ogni Ty e ottengo lo score score_TxSi di TxSi
        A questo punto ho che ogni significato Tsi ha un proprio score score_TxSi e quindi
        assegno come significato al termine Tx quello che ha score maggiore (best_score).

        :param cls
        :param tokens: ovvero il testo tokenizzato
        :param index_term: termine da disambiguare
        return: significato del token disambiguato
        """
        Tx = index_term

        if len(wn.synsets(Tx, wn.NOUN)) == 0:  # se token non riconosciuto
            return None
        best_sense = wn.synsets(Tx, wn.NOUN)[0]
        best_score = 0.0
        for TxSi in wn.synsets(Tx, wn.NOUN):
            score_TxSi = 0.0            
            for Ty in tokens:
                if Ty==Tx:
                    continue
                max_score = 0.0   
                for TySz in wn.synsets(Ty, wn.NOUN):
                    tmp_score = TxSi.wup_similarity(TySz)
                    if tmp_score > max_score:
                        max_score = tmp_score
                score_TxSi += max_score
            if score_TxSi > best_score:
                best_score = score_TxSi
                best_sense = TxSi
        return best_sense


class Expander():
    """
    Callable che mi ritorna l'espanzione della query.
    """

    disambiguate_fn_map = {'lesk': Disambiguator.leskDisambiguate,
                           'noun_sense': Disambiguator.nounSenseDisambiguate,
                           }


    def __init__(self, disambiguate_fn='lesk'):
        """
        Inizializzazione classe in cui specifico la funzione che voglio usare per la
        disambiguazione.

        :param self
        :param disambiguate_fn: funzione usata per la disambiguazione
        """
        self.disambiguate_fn = Expander.disambiguate_fn_map[disambiguate_fn]
        self.stopword = nltk.corpus.stopwords.words('english')


    def stopwordRemove(self, tokens):
        """
        Rimozione stopword da lista di token.
        
        :param self
        :param tokens: lista di token da cui rimuovere le stopword
        retrun: lista di token senza stopword
        """
        return [t for t in tokens if t not in self.stopword]


    def getRelatedTerms(self, best_sense):
        """
        Dato il significato di un token mi ritorna i termini pertinenti.

        :param self
        :param best_sense: significato del token
        return: termini pertinenti/relativi 
        """
        if best_sense is not None:
            return self.stopwordRemove(best_sense.lemma_names())
        return []


    def expansion(self, text):
        """
        Query expansion basata sui sinonimi dei nomi della query. 
        
        Ricavo i nomi dalla query, per poi effettuare una disambiguazione tra essi 
        e salvarmi i primi n sinonimi trovati per ogni nome.

        Per ogni sinonimo tolgo gli eventuali trattini (questo può portare al fatto che un singolo sinonimo
        abbia più token).
        Elimino inoltre i sinonimi che sono già presenti nella query.
        
        :param n: per ogni nome vengono salvati al più n sinonimi
        """
        tokens = self.stopwordRemove(nltk.word_tokenize(text))

        res=[]
        for token in tokens:
            best_sense = self.disambiguate_fn(tokens, token, 'n')

            related_terms = self.getRelatedTerms(best_sense)

            for related_term in related_terms:
                related_term = related_term.lower().replace(token.lower(), "")
                related_term = related_term.replace('_', " ")
                related_term = related_term.replace('-', " ")
                related_term = related_term.strip()

                splitted_term = related_term.split()

                for term in splitted_term:  
                    if term not in res and len(term)>2 and term.strip()!='':
                        res.append(term)
        return res

    def __call__(self, text):
        """
        Ritorna il testo espanso.

        :param self
        :param text: testo da cui fare espansione
        return: testo espanso in cui ho imposto regole sintattiche
        """
        list_token_expanded = self.expansion(text)
        expandend = ' OR ( '+' OR '.join(list_token_expanded)+' )'
        return ('( '+text+' )'+expandend, list_token_expanded)


