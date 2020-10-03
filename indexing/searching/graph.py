#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 09:00:43 2020

@author: gabrielesavoia
"""

import snap

class WikiGraph():
	"""
	DOC : https://snap.stanford.edu/snappy/doc/reference/index-ref.html

	"""

	t_graph = {'TUNGraph': snap.TUNGraph,   # grafo unidirezionale -> NO attributi su archi e nodi
											# 						  ID 'int' solo su nodi
											# 						  SI self-loop
											# 						  Liste di adj ordinata
											# 						  nodo : adj1,adj2,..,adjN 
											# 						  (A---B)
			   'TNGraph': snap.TNGraph,		# grafo diretto        -> NO attributi su archi e nodi
			   								# 						  ID 'int' solo su nodi
			   								# 						  SI self-loop.
											# 						  Liste di adj ordinata
											# 						  nodo : adj1,adj2,..,adjN 			   								
											#						  (A-->B) O (A<--B)
			   'TNEANet': snap.TNEANet,		# network              -> SI attributi su archi e nodi
			   								# 						  ID 'int' su nodi e su archi
											# 						  Liste di adj ordinata
											# 						  nodo : adj1,adj2,..,adjN 
				}			   								

	def __init__(self, t_graph='TNGraph', file_name='wiki.graph'):
		"""
		DOCS :  https://snap.stanford.edu/snappy/doc/reference/table.html#ttablecontext
				https://snap.stanford.edu/snappy/doc/reference/composite.html#thash

		Inizializzazione della classe.

		:param t_graph:
		:param file_name:
		"""
		self.file_name = file_name

		self.t_graph = WikiGraph.t_graph[t_graph]
		self.graph = self.t_graph.New()

		self.table_context = snap.TTableContext()  
		self.table_rank = snap.TIntFltH()


	def __getIdPage(self, title_page):
		"""
		:param title_page: titolo della pagina
		return ID (intero univoco) a partire da una stringa.
		"""
		return self.table_context.AddStr(title_page)


	def __getTitlePage(self, id_page):
		"""
		:param id_page: id della pagina di cui voglio ritornare il titolo
		return titolo della pagina
		"""
		return self.table_context.GetStr(id_page)


	def addPage(self, title_page, titles_page_linked=[]):
		"""
		Aggiunge una pagina al grafo.

		:param page_title: titolo della pagina da aggiungere 
		:param pages_linked: titoli delle pagine di wikipedia linkate dalla pagina corrente
		"""
		id_page = self.__getIdPage(title_page)
		if not self.graph.IsNode(id_page): self.graph.AddNode(id_page)  # O(1)

		for title_page_linked in titles_page_linked:
			id_page_linked = self.__getIdPage(title_page_linked)
			if not self.graph.IsNode(id_page_linked): self.graph.AddNode(id_page_linked)
			self.graph.AddEdge(id_page, id_page_linked)
			#if not self.graph.IsEdge(id_page, id_page_linked) self.graph.AddEdge(id_page, id_page_linked)	


	def getRank(self, filter_title):
		"""
		Ritorna un dict che ha come chiavi i titoli che sono stati passati nel filtro 
		e che sono presenti nell'Hashtable del page rank e come valore il 
		valore di page rank della pagina corrispondente.

		:param filter_title: lista di filtri di cui mi interessa il rank
		return: python dict con i rank riferiti solo ai titoli passati nel filtro
		"""	
		return {title: self.table_rank[self.__getIdPage(title)] 
				 for title in filter_title if self.table_rank.IsKey(self.__getIdPage(title))}


	def computePageRank(self):
		"""
		DOC : https://snap.stanford.edu/snappy/doc/reference/GetPageRank.html

		Calcolo del page rank sull'intero grafo.
		Utilizzo un Hashtable che ha come chiave l'id della pagina e come valore il page rank (float).

		:param self
		"""
		params = {'C': 0.85,
				  'Eps': 1e-4,
				  'MaxIter': 100}

		snap.GetPageRank(self.graph, self.table_rank, *[val for val in params.values()])


	def load(self):
		"""
		Caricamento grafo da file.

		:param file_name: nome del file da dove caricare il grafo
		"""
		f_in = snap.TFIn(self.file_name)
		self.graph = snap.TNGraph.Load(f_in)


	def save(self):
		"""
		Salvataggio grafo in formato binario.
		Viene sovrascritto il contenuto del file specificato.
		Viene creato il file se non esiste.

		:param file_name: nome del file dove salvare il grafo
		"""
		f_out = snap.TFOut(self.file_name)
		G2.Save(f_out)
		f_out.Flush()


g = WikiGraph()
g.addPage('page1', ['page2', 'page3', 'page3'])
g.addPage('page2', ['page7'])
g.addPage('page3', ['page4', 'page6'])
g.addPage('page4', ['page1'])
g.addPage('page5')
g.addPage('page6', ['page7'])

g.computePageRank()




