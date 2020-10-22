# https://www.geeksforgeeks.org/performing-google-search-using-python-code/ 
from googlesearch import search 

# .
from .xmlParsing import interwikiLink
from .xmlParsing.saxReader import NS_NOT_VALID
from .searching.searcher import WikiSearcher

import os, json, re, time
from urllib.request import url2pathname

"""
Modulo composto dalle funzioni necessarie per poter ricavare il test set del progetto.
E' possibile inoltre 

"""

def getRelevantPerQuery(google_links, n_relevant):
    """
    Pero ogni query considero solo i primi n_relevant link trovati da Google.

    :param google_links: dict con TUTTI (> n_relevant) links per query
    :param n_relevant: per ogni query eleziono solo i primi n_relevant links
    return dict con tutte le query e per ognuna ci sono n_relevant links
    """
    return {query:list_link[:n_relevant] for query, list_link in google_links.items()}


def prepareValidatorLink(interwiki_file_path):
    """
    Ritorna la funzione di validazione del link.
    In questa closure definisco 'interwiki' che calcolo una sola volta (perchè è il caricamento
    in memoria di file e non voglio farlo per ogni link da analizzare).

    """
    interwiki = interwikiLink.getPrefixSet(interwiki_file_path)

    def validatorLink(link, already_saved_links):
        """
        Controllo se il link ricavato da Google è compatibile con i documenti
        del progetto.

        :param link: link di Google
        :param already_saved_links: lista (riferita ad una singola query) dei link già salvati
        return: True se link è valido, False altrimenti
        """

        if link in already_saved_links:
            return False

        if not link.startswith(WikiSearcher.base_url):
            return False 

        # Condizione necessaria perchè negli interwiki link non è presente 'Wikitionary'
        if 'Wiktionary:' in link:
            return False

        link_no_site_name = link[len(WikiSearcher.base_url):]
        pref = re.search(r'^:?[^:]+?:', link_no_site_name)

        if pref is not None:
            pref = re.sub(r':', '', pref[0])
            ns_not_valid = set(NS_NOT_VALID.values())

            if pref in interwiki:
                return False

            if pref in ns_not_valid:
                return False
            
        return True

    return validatorLink


def computeTestSet(queries, google_file_path, interwiki_file_path, n_per_query, n_relevant=None):
    """
    Per ognuna delle 30 query fornite, eseguo una richiesta a Google, dalla quale mi salvo i primi 30 
    documenti rilevanti per ognuna (escludendo link non importanti). Per l'evaluation considero
    solo i primi n documenti come rilevanti e gli altri irrilevanti.
    Il calcolo dei 900 link lo eseguo una sola volta e mi salvo i risultati in un file.

    :param n: numero documenti rilevanti
    :param n_relevant: per ogni query eleziono solo i primi n_relevant links
    return dict con nome query e lista di n link rilevanti
    """
    n_google_res = int(n_per_query * 1.5)  # n_google_res deve essere > di n_per_query dato che poi effettuo un filtraggio dei link

    print('Calcolo i risultati del test set eseguendo richieste da Google ...')
    validatorLink = prepareValidatorLink(interwiki_file_path)

    google_links = {}
    for query in queries:
        google_links[query] = []
        google_res = search(query+' site:en.wikipedia.org', 
                                tld="com", pause=2, lang='en', num=n_google_res)

        for link in google_res:
            link = re.sub('#.*$', '', url2pathname(link))

            if validatorLink(link, google_links[query]):    
                google_links[query].append(link) 

            if len(google_links[query]) == n_per_query:
                break

            time.sleep(2)
    
    with open(google_file_path, 'w') as fp:
        json.dump(google_links, fp)

    print('Terminazione del calcolo dei risultati di Google.')

    if n_relevant is None:
        return google_links
    return getRelevantPerQuery(google_links, n_relevant)


def loadTestSet(google_file_path, n_relevant=None):
    """
    Caricamento del test set salvato su file.

    :param n_relevant: per ogni query eleziono solo i primi n_relevant links

    return del dict con i links di Google, False se il fle non è presente
    """
    if os.path.exists(google_file_path):
        with open(google_file_path, 'r') as fp:
            google_links = json.load(fp)
            if n_relevant is None:
                return google_links
            return getRelevantPerQuery(google_links, n_relevant)
    else:
        return False


def getLinkToFilter(google_links):
    """
    Dato il dict 'google_links', che ha come chiavi tutte le query e come valori i links ritornati
    da Google, ritorno un'unica lista contenente tutti i links. Questa lista serve per poter 
    filtrare le pagine dal dump.
    E' quindi necessario che dal link tolga il 'base_url' e i '_' diventino spazi.

    return: set di links
    """
    links = []
    for list_link in google_links.values():
        for link in list_link: 
            link = link[len(WikiSearcher.base_url):].replace("_", " ")
            links.append(link)

    return links









