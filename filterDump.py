from indexing.xmlParsing.saxReader import filterXML
from indexing.searching.searcher import WikiSearcher
from indexing import testSet

import dicttoxml

from xml.dom.minidom import parseString

import json, os, re

import argparse


class FilterDump():

    def __init__(self, path_google_links, path_origin, path_end, total_docs_noise):
        """
        Dall'xml di partenza, crea l'xml filtrato.

        :param path_origin: path del dump
        :parma path_end: path del file filtrato
        :param titles_to_select: iterabile contenente i titoli da selezionare
        :param total_docs_noise: numero di documenti per creare disturbo
        """

        self.path_origin = path_origin
        self.path_end = path_end

        self.total_docs_noise = total_docs_noise
        self.titles_to_select = FilterDump.getTitlesToSelect(path_google_links)

        self.file = None


    def __fileSetup(self):
        """
        Setup del file xml filtrato.

        :param self
        """
        self.file = open(self.path_end, "wt")
        self.file.write("<wikimedia>\n")


    def __fileClose(self):
        """
        Chiusura del file xml filtrato.

        :param self
        """
        self.file.write("</wikimedia>")
        self.file.close()


    @classmethod
    def getTitlesToSelect(cls, path_google_links):
        """
        Ricavo un set contenente i titoli da selezionare.

        :param self
        return: titoli da selezionare
        """
        google_links = testSet.loadTestSet(path_google_links)

        if not google_links:
            raise FileNotFoundError

        return set(testSet.getLinkToFilter(google_links))


    def writePage(self, **info_page):
        """
        Scrittura di una pagina letta dal dump.

        :param self
        """
        xml = dicttoxml.dicttoxml(info_page, custom_root='page', attr_type=False)
        dom = parseString(xml).toprettyxml().replace('<?xml version="1.0" ?>\n', "")
        self.file.write(dom)


    def startFilter(self):
        """
        Fa partire il filtraggio del file xml.

        :param self
        """
        self.__fileSetup()
        filterXML(self.path_origin, self.total_docs_noise ,self.titles_to_select, self.writePage)
        self.__fileClose()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Script per filtrare per titolo file xml in base ai titoli presenti nel file google_links.json')
    p.add_argument(
        '--source',
        type=str,
        default=None,
        help='File xml da filtrare')
    p.add_argument(
        '--dest',
        type=str,
        default='files/filtered.xml',
        help='File xml filtrato')
    p.add_argument(
        '--google_link',
        type=str,
        default='files/google_links.json',
        help='File json che contiene il dict con le query e i rispettivi link.')
    p.add_argument(
        '--noise',
        type=int,
        default=450,
        help='Pagine di rumore.')

    args = p.parse_args()

    if args.source is None:
        print('Specificare il file xml da parsare')
    else:
        f = FilterDump(args.google_link, args.source, args.dest, args.noise)
        f.startFilter()










