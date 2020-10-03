#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 08:13:44 2020

@author: gabrielesavoia
"""
import requests

def getInterwikiMap():
    """
    DOCS   https://www.mediawiki.org/wiki/Manual:Interwiki
    
    Ritorna un SET (775 elem) con tutti i link di tipo Interwiki.
    Abbaimo deciso di salvarci solo il prefisso e non anche la loro risoluzione in url
    dato che essendo link che puntano a siti esterni, non ci servono per la link analysy.
    
    Questi chiaramente occupano memoria però abbiamo deciso di utilizzare i SET in modo tale che 
    il costo di ricerca sia O(1).
    
    return set di prefissi
    """
    
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
    
    return pref