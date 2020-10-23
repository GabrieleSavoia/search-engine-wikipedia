from whoosh.analysis import SimpleAnalyzer, StandardAnalyzer, StemmingAnalyzer, RegexTokenizer, LowercaseFilter, StopFilter, StemFilter
from whoosh.analysis.filters import STOP_WORDS, CharsetFilter
from whoosh.analysis.tokenizers import default_pattern
from whoosh.support.charset import accent_map

from .filters import LemmatizerFilter

"""
DOCS : src whoosh -> https://github.com/mchaput/whoosh/blob/main/src/whoosh/analysis/analyzers.py 

"""   

def SimpleAnalyzer_():
    """
    Analizzatore che effettua tokenizzazione e lowercase.
    """
    return SimpleAnalyzer()


def StandardAnalyzer_():
    """
    Analizzatore che effettua tokenizzazione, lowercase e rimozione stopword.
    """
    return StandardAnalyzer()  


def StemmingAnalyzer_(stoplist=STOP_WORDS):
    """
    Analizzatore che effettua tokenizzazione, lowercase, rimozione stopword e stemming.
    
    :param stoplist: lista di stopword. E' possibile effettuare l'unione con altre di un altra lista
    """
    return StemmingAnalyzer(stoplist=stoplist, cachesize=-1)  


def AccentStemmingAnalyzer(stoplist=STOP_WORDS):
    """
    Analizzatore che effettua tokenizzazione, lowercase, rimozione stopword e stemming. 
    Inoltre se sono presenti token con particolari accenti, queste vengono ricondotte ad una 'forma base'.
    ES: 'cafè' -> 'cafe'
    
    :param stoplist: lista di stopword. E' possibile effettuare l'unione con altre di un altra lista
    """
    return StemmingAnalyzer(stoplist=stoplist, cachesize=-1) \
            | CharsetFilter(accent_map)  
     

def LemmatizingAnalyzer(stoplist=STOP_WORDS, minsize=2, maxsize=None):
    """
    Analizzatore che effettua tokenizzazione, lowercase, rimozione stopword e lemmatizzazione.
    
    :param stoplist: lista di stopword. E' possibile effettuare l'unione con altre un altra lista
    :param minsize: Parole più piccole di questo valore vengono eliminate
    :param maxsize: parole più grandi di questo valore vengono eliminate
    """
    ret = RegexTokenizer(expression=default_pattern, gaps=False)
    chain = ret | LowercaseFilter()
    if stoplist is not None:
        chain = chain | StopFilter(stoplist=stoplist, minsize=minsize,
                                   maxsize=maxsize)
    return chain | LemmatizerFilter()

                