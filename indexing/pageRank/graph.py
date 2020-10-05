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
	Viene sovrascritto il contenuto del file specificato.
	Viene creato il file se non esiste.

	:param enitity: oggetto da salvare
	:param file_name: nome del file dove salvare l'entità
	"""
	f_out = snap.TFOut(file_name)
	to_save.Save(f_out)
	f_out.Flush()


def snapLoad(to_load, file_name):
	"""
	Caricamento da file.

	:param enitity: oggetto da caricare
	:param file_name: nome del file da dove caricare l'entità
	"""
	f_in = snap.TFIn(file_name)
	to_load.Load(f_in) 



class WikiTableTitle(snap.TTableContext):
	"""
	DOCS : https://snap.stanford.edu/snappy/doc/reference/table.html#ttablecontext

	Mappatura dei titoli dei testi di Wikipedia con un numero univoco.
	"""
	file_name = 'id_title.tablecontext'

	def __init__(self):
		super().__init__()
	

	def getId(self, title):
		"""
		:param title: titolo della pagina
		return ID (intero univoco) a partire da una stringa.
		"""
		return self.AddStr(title)


	def getTitle(self, id_page):
		"""
		:param id_page: id della pagina di cui voglio ritornare il titolo
		return titolo della pagina
		"""
		return self.GetStr(id_page)


class WikiGraph():
	"""
	DOC : https://snap.stanford.edu/snappy/doc/reference/graphs.html

	Gestisce la creazione del grafo delle pagine di Wikipedia.
	"""

	t_graph = {'TUNGraph': snap.TUNGraph,   # grafo unidirezionale -> NO attributi su archi e nodi
											# 						  (A---B)
			   'TNGraph': snap.TNGraph,		# grafo diretto        -> NO attributi su archi e nodi			   								
											#						  (A-->B) O (A<--B)
			   'TNEANet': snap.TNEANet,		# network              -> SI attributi su archi e nodi
				}			   								

	def __init__(self, t_graph='TNGraph', dir_storage='indexing/pageRank/'):
		"""
		Inizializzazione della classe.

		:param t_graph: tipologia grafo.
		:param dir_storage: directory per lo storage dei file associati al grafo.
		"""
		self.dir_storage = dir_storage
		self.graph = WikiGraph.t_graph.get(t_graph, snap.TNGraph).New()
		self.table_title = WikiTableTitle()


	def addPage(self, title_page, titles_page_linked=[]):
		"""
		Aggiunge una pagina al grafo.

		:param title_page: titolo della pagina da aggiungere 
		:param titles_page_linked: lista di titoli delle pagine di wikipedia linkate dalla pagina corrente
		"""
		id_page = self.table_title.getId(title_page)
		if not self.graph.IsNode(id_page): self.graph.AddNode(id_page)  # O(1)

		for title_page_linked in titles_page_linked:
			id_page_linked = self.table_title.getId(title_page_linked)
			if not self.graph.IsNode(id_page_linked): self.graph.AddNode(id_page_linked)
			self.graph.AddEdge(id_page, id_page_linked)


	def end(self):
		"""	
		Salvataggio della table per la mappatura tra id e titoli delle pagine.
		Non salvo il grafo intero.
		Eseguo il pagerank.

		:param self
		"""
		snapSave(self.table_title, self.dir_storage+WikiTableTitle.file_name)
		WikiPageRanker.computePageRank(self.graph, self.dir_storage)


class WikiPageRanker():
	"""
	DOC : https://snap.stanford.edu/snappy/doc/reference/GetPageRank.html
		  https://snap.stanford.edu/snappy/doc/reference/composite.html#thash
	"""
	file_name = 'table.rank'

	def __init__(self, dir_storage='indexing/pageRank/'):
		"""
		Inizializzazione della classe.
		Errore se i file non esistono.

		:param self
		:param dir_storage: directory per lo storage della tabella del page rank.
		"""
		self.table_rank = snap.TIntFltH()
		snapLoad(self.table_rank, dir_storage+WikiPageRanker.file_name)

		self.table_title = WikiTableTitle()
		snapLoad(self.table_title, dir_storage+WikiTableTitle.file_name)


	@classmethod
	def computePageRank(cls, graph, dir_storage):
		"""
		Calcolo del page rank sull'intero grafo.
		Utilizzo un Hashtable che ha come chiave l'id della pagina e come valore il page rank (float).
		Hashtable salvata su file.

		:param cls
		:param graph: grafo su cui calcolare il page rank
		:dir_storage: dove salvare la table del page rank
		"""
		params = {'C': 0.85,
				  'Eps': 1e-4,
				  'MaxIter': 100}

		table_rank = snap.TIntFltH()
		snap.GetPageRank(graph, table_rank, *[val for val in params.values()])
		snapSave(table_rank, dir_storage+WikiPageRanker.file_name)
		return table_rank


	def getRank(self, filter_title):
		"""
		Ritorna un dict che ha come chiavi i titoli che sono stati passati nel filtro 
		e che sono presenti nell'Hashtable del page rank e come valore il 
		valore di page rank della pagina corrispondente.

		:param self
		:param filter_title: lista di filtri di cui mi interessa il rank
		return: python dict con i rank riferiti solo ai titoli passati nel filtro
		"""	
		return {title: self.table_rank[self.table_title.getId(title)] 
				for title in filter_title if self.table_rank.IsKey(self.table_title.getId(title))}


