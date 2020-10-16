#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 09:00:43 2020

@author: gabrielesavoia
"""

import snap


def snapSave(to_save, file_name):
    """
    Salvataggio in formato binario.
    Viene sovrascritto il contenuto del file specificato se già esistente.
    Viene creato il file se non esiste.

    :param to_save: oggetto da salvare
    :param file_name: nome del file dove salvare l'oggetto
    """
    f_out = snap.TFOut(file_name)
    to_save.Save(f_out)
    f_out.Flush()


def snapLoad(to_load, file_name):
    """
    Caricamento da file.

    :param to_load: oggetto da caricare
    :param file_name: nome del file da caricare
    """
    f_in = snap.TFIn(file_name)
    to_load.Load(f_in) 


class WikiGraph():
    """
    DOC : https://snap.stanford.edu/snappy/doc/reference/graphs.html

    Gestisce la creazione del grafo delle pagine di Wikipedia.
    """

    t_graph = {'TUNGraph': snap.TUNGraph,   # grafo unidirezionale -> NO attributi su archi e nodi
                                            #                         (A---B)
               'TNGraph': snap.TNGraph,     # grafo diretto        -> NO attributi su archi e nodi                                          
                                            #                         (A-->B) O (A<--B)
               'TNEANet': snap.TNEANet,     # network              -> SI attributi su archi e nodi
                }                                           

    def __init__(self, args_paths, t_graph='TNGraph'):
        """
        Inizializzazione della classe.

        In 'compact_struct' salvo un dict contente n chiavi (titoli), dove n = numeri nodi del grafo, in 
        cui ciascuna è associata ad una tupla (x, y) con x = id pagina, y = set di link a cui punta (uso un 
        set per togliere duplicati dei link, quindi non è possibile che una pagina punti più volte ad
        un'altra)

        Questa struttra di supporto mi serve dato che in fase di scrittura dei nodi nel grafo, non 
        ho conoscienza dell' id dei link a cui punta una pagina dato che potrebbero rappresentare pagine
        non ancora lette o che non esisteranno nel grafo completo.

        :param sel
        :param args_paths: per determinare i path
        :param t_graph: tipologia grafo
        """
        self.args_paths = args_paths
        self.graph = WikiGraph.t_graph.get(t_graph, snap.TNGraph).New()

        self.compact_struct = {}


    def addPage(self, id_page, title_page, titles_page_linked=[]):
        """
        Aggiungo una pagina al grafo e aggiorno il compact_struct con la pagina 
        corrente e i suoi link. Per descrizione della compact_struct vedere commenti nell'__init__.

        :param self
        :param id_page: id della pagina da aggiungere
        :param title_page: titolo della pagina da aggiungere
        :param titles_page_linked: link a cui la pagina corrente punta
        """
        id_page = int(id_page)

        if self.graph.IsNode(id_page) :
            print('La pagina con id: '+id_page+' e titolo: '+title_page+' è già presente nel grafo.')
            return False

        self.graph.AddNode(id_page)

        self.compact_struct[title_page] = tuple((id_page, set()))
        for linked_page in titles_page_linked:
            self.compact_struct[title_page][1].add(linked_page)


    def computeEdges(self):
        """
        Per ogni pagina (page_from), ricavo il suo id (id_page_from) e il suo set di titoli 
        corrispondenti ai link a cui punta. Per ognuno di questi titoli, guardo se è presente nel grafo 
        (page_to not None) e in caso affermativo ricavo il suo id id_page_to, per poi creare l'edge
        dato da (page_from, page_to).

        In tutti gli edges (a,b) che creo, 'a' e 'b' sono entrambi presenti nel grafo.

        :param self
        """
        for page_from in self.compact_struct.values():
            id_page_from = page_from[0]
            links_out = page_from[1]

            for link in links_out:
                page_to = self.compact_struct.get(link, None)
                if page_to is not None:
                    id_page_to = page_to[0]

                    self.graph.AddEdge(id_page_from, id_page_to)


    def end(self):
        """ 
        Questa funzione viene chiamata nel momento in cui ho terminato la creazione del grafo,
        ovvero quando ho aggiunto tutti le pagine (nodi) ad esso.

        Qua eseguo il 'computeEdges()' che mi calcola tutti i possibili edges che 
        compongono il grafo, per poi effettuare il pagerank.

        Non viene salvato il grafo ma solo il file corrispondente alla table del pagrank.

        :param self
        """
        self.computeEdges()
        WikiPageRanker.computePageRank(self.graph, self.args_paths)


class WikiPageRanker():
    """
    DOC : https://snap.stanford.edu/snappy/doc/reference/GetPageRank.html
          https://snap.stanford.edu/snappy/doc/reference/composite.html#thash
    """

    def __init__(self, args_paths):
        """
        Caricamento da file della table (id_page, value_pagerank).
        Genera eccezione se il file non esiste.

        :param self
        :param args_paths: path dello storage della tabella del page rank.
        """
        self.table_rank = snap.TIntFltH()
        snapLoad(self.table_rank, args_paths.pagerank)


    @classmethod
    def computePageRank(cls, graph, args_paths):
        """
        Calcolo del page rank sull'intero grafo.
        La funzione di page rank prende in input un hashtable vuota (int, float) e la riempie con i valori
        calcolati.
        Una volta calcolato il pagerank, lo salvo su file.

        :param cls
        :param graph: grafo su cui calcolare il pagerank
        :parma args_paths: dove salvare la table del page rank
        """
        params = {'C': 0.85,
                  'Eps': 1e-4,
                  'MaxIter': 100}

        table_rank = snap.TIntFltH()
        snap.GetPageRank(graph, table_rank, *params.values())

        snapSave(table_rank, args_paths.pagerank)


    def getRank(self, filter_ids, round_rank):
        """
        Ritorna un dict che ha come chiavi i titoli che sono stati passati nel filtro 
        e che sono presenti nell'Hashtable del page rank e come valore il 
        valore di page rank della pagina corrispondente, diviso per una costante per il motivo
        spiegato precedentemente.

        :param self
        :param filter_ids: lista di id da filtare dalla table 
        return: python dict con i rank riferiti solo agli id passati nel filtro
        """ 
        return {id_page: round(self.table_rank[int(id_page)], round_rank) for id_page in filter_ids}



