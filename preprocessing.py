#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 15:45:09 2020

@author: gabrielesavoia
""" 

# http://www.nltk.org/book/
            
import nltk        
from nltk.corpus import wordnet as wn  

# IMPORTANTE : guarda RAKE per la keyword extraction automatica.

text = "I'm booking hotel"

# 1 tokenizzazione
tokens = nltk.word_tokenize(text)   

print(nltk.pos_tag(tokens))

for i in tokens:
    print(nltk.pos_tag([i]))


# 2 noun selection (tagging), eliminazione stopwords e case lettere.
#   POSTAG funziona bene se gli passi l'insieme di token e non la singola parola
#   cap 5 parte 1
candidates_tokens = [token[0].lower() for token in nltk.pos_tag(tokens)
                      if token[1][0:2] == 'NN' and
                      token[0] not in nltk.corpus.stopwords.words('english')]
#print(candidates_tokens)
    
# 3.1 stemming Porter     cap 3 parte 3.6   USO SOLO QUESTO
#     Uso il Porter se voglio indicizzare del testo e fare ricerca usando parole alternative.
porter = nltk.PorterStemmer()
tokens_stemmed1 = [porter.stem(token) for token in candidates_tokens]
#print(tokens_stemmed1) 

# 3.2 stemming Lancaster
porter = nltk.LancasterStemmer()
tokens_stemmed2 = [porter.stem(token) for token in candidates_tokens]
#print(tokens_stemmed2)    

# 3.3 lemmatizing che sembra funzionare meglio.
#     Funziona meglio che gli stemmer.
#     adatto ad applicazioni in cui mi interessa avere correttezza del lemma
wnl = nltk.WordNetLemmatizer()
lemmatized_tokens = [wnl.lemmatize(token) for token in candidates_tokens]
#print(lemmatized_tokens)


# Metodo slide non funziona bene
no_stopwords = [token.lower() for token in tokens
                if token not in nltk.corpus.stopwords.words('english')]
porter = nltk.LancasterStemmer()
tokens_stemmed = [porter.stem(token) for token in no_stopwords]
tokens_noun_selected = [token[0].lower() for token in nltk.pos_tag(tokens_stemmed)
                        if token[1][0:2] == 'NN']
#print(tokens_noun_selected)



# SIMILARITY

# PATH-DISTANCE --> non considera l'antenato comune probabilmente non è preciso

# WU-PALMER     --> considera antenato comune e distanza tra i significati
cat = wn.synset('cat.n.01')
computer = wn.synset('computer.n.01')
cat.wup_similarity(computer)

# RESNICK
brown_ic = nltk.corpus.wordnet_ic.ic('ic-brown.dat')
computer.res_similarity(cat,brown_ic)

def wordSenseDisambiguate(index_terms):
    """
    index_terms : sono i termini del contesto che devo disambiguare.
    
    Per ogni index_term Tx, devo assegnarli il proprio significato corretto in base 
    al contesto in cui si trova.
    Per ogni suo significato TSi, calcolo uno score :
        1) per ogni termine Ty != Tx mi ricavo il max_score ovvero il valore max 
           di similarità tra TSi e OGNI significato di Ty
        2) sommo il max_score di ogni Ty e ottengo lo score di TSi
    A questo punto ho che ogni significato Tsi ha un proprio score e quindi
    assegno come significato al termine Tx quello che ha score maggiore.
    """
    try:
        len(index_terms)
    except TypeError:
        print('La funzione accetta solo una lista di token')
        
    res = []
        
    for index_term in index_terms:
        best_sense = wn.synsets(index_term, wn.NOUN)[0]
        best_score = 0.0
        for candidate_sense in wn.synsets(index_term, wn.NOUN):
            score = 0.0            
            for other_term in index_terms:
                if other_term==index_term:
                    continue
                max_score = 0.0   
                for possible_sense in wn.synsets(other_term, wn.NOUN):
                    tmp_score = candidate_sense.wup_similarity(possible_sense)
                    if tmp_score > max_score:
                        max_score = tmp_score
                score += max_score
            if score > best_score:
                best_score = score
                best_sense = candidate_sense
        res.append({'word': index_term, 'sense': best_sense, 'score':best_score})
    return res

for d in wordSenseDisambiguate(['mouse', 'computer']):
    #print(d['word'] + ': ' + d['sense'].definition())
    break

def queryExpansionV1(index_terms, n=2):
    """
    Dati gli index_terms della query, fornisce n SINONIMI per ogni termine. 
    Dai sinonimi vengono tolte le parole uguali agli index_term.
    """
    res = []
    for term_disambiguated in wordSenseDisambiguate(index_terms):
        for synonym in term_disambiguated['sense'].lemma_names()[:n]:
            to_add = True
            for term in index_terms:
                if synonym == term:
                    to_add = False
            if to_add:
                res.append(synonym)
    return res
        
print(queryExpansionV1(['computer', 'cat', 'dog']))































