#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 08:13:44 2020

@author: gabrielesavoia
"""
import requests
import os, os.path
import pickle

def getPrefixSet(path_interwiki_links):
    """
    DOCS   https://www.mediawiki.org/wiki/Manual:Interwiki
    
    Ritorna un SET (775 elem) con tutti i link di tipo Interwiki.
    Abbaimo deciso di salvarci solo il prefisso e non anche la loro risoluzione in url
    dato che essendo link che puntano a siti esterni, non ci servono per la link analysy.
    
    Questi chiaramente occupano memoria però abbiamo deciso di utilizzare i SET in modo tale che 
    il costo di ricerca sia O(1).

    Il set viene salvato su file. Se questo file non esiste, allora eseguo la richiesta url da wikipedia.
    Se il file esiste non avviene la richiesta url e leggo il file.
    
    return set di prefissi
    """

    if os.path.exists(path_interwiki_links):
        with open(path_interwiki_links, 'rb') as fp: 
            return set(pickle.load(fp))
    
    url = 'https://www.mediawiki.org/w/api.php'
    
    params = dict(
        action='query',
        meta='siteinfo',
        siprop='interwikimap',
        format='json',
    )
    
    resp = requests.get(url=url, params=params).json()
    
    pref = set()
    for i in resp['query']['interwikimap']:
        pref.add(i['prefix'])

    with open(path_interwiki_links, 'wb') as fp: 
        pickle.dump(pref, fp)
    
    return pref

    