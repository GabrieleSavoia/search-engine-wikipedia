import nltk 

from whoosh.analysis import Filter
      

class LemmatizerFilter(Filter):
    """
    Filtro che effettua la lemmatizzazione dei token con nltk.
    """

    def __init__(self):
        """
        Inizializzazione del lemmatizer.

        :param self
        """
        self.lemmatizer = nltk.WordNetLemmatizer()

    
    def __call__(self, tokens):
        """
        Generatore di token lemmatizzati.

        :param self
        :param tokens: tokens da lemmatizzare
        yield: token lemmatizzato 
        """
        for token in tokens:
            token.text = self.lemmatizer.lemmatize(token.text)
            yield token