
import re
from . import interwikiLink, saxReader

class FilterWikiText():

    def __init__(self, path_interwiki_links):
        """
        Inizializzazione interwiki_prefix_set che corrisponde ad un set contenente tutti i prefix 
        degli interwiki link.
        
        :param self
        :param dir_storage: directory dove salvare i prefix degli interwiki link
        """
        self.interwiki_prefix_set = interwikiLink.getPrefixSet(path_interwiki_links)


    def getLinkAndCategory(self, text, title):
        """
        # DOCS   https://www.mediawiki.org/wiki/Help:Links#Internal_links
        # DOCS   https://www.mediawiki.org/wiki/Help:Categories
        # DOCS   https://www.mediawiki.org/wiki/Help:Images   
        # DOCS   https://meta.wikimedia.org/wiki/Help:Interwiki_linking   INTERWIKI
        
        Rilevamento dei link e delle categorie del testo presenti nella stringa del campo 'text'.
        Abbiamo deciso di usare una singola funzione perchè per definire le categorie che appartengono
        ad un certo testo si usa la stessa struttura dei link.
        L'obbiettivo è quello di ricavare i link interni ad altre pagine wikipedia. 
        Questa funzione ha principalmente 2 scopi:
            - RISOLUZIONE LINK: nel testo i link possono non essere scritti per intero ma usare regole di abbreviazione. Quindi mi devo 
                                occupare di risolvere queste abbreviazioni
            - FILTRAGGIO: seleziono solo i link che mi interessano.
                            Ad esempio non considero gli INTERWIKI LINK e link a NAMESPACE che ho considerato non validi.
        
        Questa funzione mi permette di ridurre considerevolmente i link associati a questa pagina e 
        quindi viene ottimizzato il pagerank.

        Le categorie non sono state usate ai fini del progetto.

        :param self
        :param text: il testo da cui estrarre i link
        :param title: il titolo del teso, che corrisponde al link della pagina 
        
        return res_dict: dizionario con 2 liste, una per le categorie e una per i link
        """
        res_dict ={'links': [], 'categories': []}
        
        # reg exp per determinare i link da text wiki '[[link]]'
        pattern = re.compile(r'\[\[([^\]]+?)\]\]') 
        
        for match in re.finditer(pattern, text):
            # [[Link name| display name]]   -->  res = 'Link name'   -> non considero il display name perchè non fa parte del link
            res = match.group(1).split("|")[0].strip() 
            
            # link a una sezione nella stessa pagina non lo considero (startswith('#'))
            # se il link è uguale a titolo delle pagina, allora NON è un link ma viene solo messo in grassetto il testo in fase di visualizzazione
            if not res.startswith('#') and res!=title :
                is_category = False                  
                                  
                # Da fare sempre se link valido                  
                res = re.sub(r'#.*', '', res)        # elimina da '#' fino alla fine SE '#' PRESENTE
                res = re.sub(r'/\s*?$', '', res)     # elimina ultimo '/' nell'url SE PRESENTE 
                
                # link alla sotto-pagina e quindi devo aggiungere come prefisso il titolo della 
                # pagina corrente                                     
                if res.startswith('/'):
                    res = title+res
                    
                # Data la pag 'p/test1' --> 'test1 è sotto-pagina di 'p'. 
                # Nella pag 'p/test1' ho un link che inizia con '../test2', questo significa che 
                # il link risultante deve essere 'p/test2'
                elif res.startswith('../'):
                    father_page = re.sub(r'/[^/]+?$', '', title)    # da 'p/test1' a 'p/' oopure da 'p/test1/test2' a       'p/test1
                    res = father_page + re.sub(r'..', '', res)      # Se link è '../test3' tolgo solo '..' così diventa --> 'p/test1/test3
                    
                # Se definito, indica una delle categorie di cui fa parte la pagina corrente, quindi
                # la aggiungo alla lista delle categorie
                elif res.startswith('Category'):
                    is_category = True

                # NON risolviamo link che contengono variabili {{''}} dato che 
                # servono principalmente per riferirsi a Talk pages oppure risolvere link di
                # help pages per ricondursi a link di base
                elif res.startswith('{{'):
                    res = None

                # Prefissi che non sono NAMESPACE non li considero
                elif res.startswith('Image:') or res.startswith('Manual:') or res.startswith('Extension:'):
                    res = None

                # match_ è NOT NONE se il link ha queste forme :   ':x:y'  o  'x:y'  o  ':x:y:z'  o  'x:y:z'  ...
                # ovvero se è un candidato INTERWIKI LINK o LINK a pagine in cui è specificato il NAMESAPCE.
                # Se è NOT NONE allora ricavo il prefix :   ':x:y:z' --> 'x'  o  'x:y' --> 'x'    (toglie ':')
                  # Una volta ricavata la 'x' (prefix), controllo se 
                    #  1) è un INTERWIKI LINK  --> res = None
                    #  2) è link a pagina che ha NAMESPACE non valido  -->  res = None
                    #  Se non soddisfa 1) e 2) allora significa che è un link che ha ':' nel titolo ma non corrisponde a interwiki o namespace non validi --> link valido
                # Se invece match_ è NONE, significa che il link non è INTERWIKILINK e non fa parte di NAMESPACE non validi --> link PROBABILMENTE valido
                else:
                    match_ = re.search(r'^:?[^:]+?:', res)
                    if match_ is not None:
                        pref = re.sub(r':', '', match_[0]) 
                        if pref in self.interwiki_prefix_set:
                            res = None
                        else:
                            for ns_not_valid in saxReader.NS_NOT_VALID.values():  
                                if pref == ns_not_valid.replace("_", " "):
                                    res = None
                    
                # Se res == None --> tipo di link non considerato e non faccio niente
                # Se non è una categoria, è possibile che un titolo inizi con ':', ma il titolo effettivo è senza ':', quindi li tolgo.
                # es :   [[:Article]] è equivalente con [[Article]], ma mi salvo solo 'Article'
                if res is not None:
                    if is_category:
                        res_dict['categories'].append(res)
                    else:
                        res = re.sub(r':', '', res)  
                        res_dict['links'].append(res)
        return res_dict 


    @classmethod
    def getCleaned(cls, text):
        """
        # DOCS   https://www.mediawiki.org/wiki/Help:Magic_words
        
        Eseguo una pulizia del testo dalle parti che sicuramente non sono importanti ai fini del
        progetto come i tag html, i link esterni..
        Mantengo invece i link interni perchè potrebbero contenere parole che possono dare un maggiore
        significato al documento.
        Esistono moltissimi tipi di tag, variabili e funzioni che potrebbero essere filtrati in modo 
        da ottnere un testo più pulito ma abbiamo ritenuto non necessario coprire tutti i possibili casi.
        
        In questa fase vengono eliminati i caratteri non attinenti come '[({..' in modo da ottenere
        highlights dei documenti ritornati più puliti.
        
        :param cls
        :param text: testo da pulire
        
        return testo pulito
        """
        
        replacements = [
            
            (r'{{[^}{]*?url=.*?}}', ''),      # rimuovo {{..url=..}}
            (r'{{[^}{]*?lang.*?}}', ''),      # rimuovo {{..lang..}}
            (r'{{[^}{]*?reflist.*?}}', ''),   # rimuovo {{..ref..}}
            (r'{{[^}{]*?commons.*?}}', ''),   # rimuovo {{..commons..}}
            (r'{{[^}{]*?coord.*?}}', ''),     # rimuovo {{..coord..}}
        
            (r'\[http.+?\]', ''),          # rimuovo link esterni [http..]
            (r'\shttp.+?\s', ''),          # rimuovo link esterni
            (r'\s[^\s]+\.com\s?', ''),     # rimuovo ogni parola che termina con '.com' |
            (r'\s[^\s]+\.org\s?', ''),     # rimuovo ogni parola che termina con '.org' |
            (r'\s[^\s]+\.it\s?', ''),      # rimuovo ogni parola che termina con '.it'  | --> Li elimino perchè sono link esterni a wikipedia e non li considero importanti per l'applicazione
            (r'\s[^\s]+\.en\s?', ''),      # rimuovo ogni parola che termina con '.en'  |
            
                                         
            (r'<gallery.*?</gallery>', ''),   # Qua vengono di solito messe le liste di file che non salvo
            (r'\[\[File:.*?\]\]', ''),        # Se non è presente '|' , CANCELLO FINO A '\n'
            (r'\[\[Media:.*?\]\]', ''),       # da 'Media:...|txt_name' -> rimane 'txt_name'
            
            (r'<[^<]*?>', ''),           # rimuovo tag html 

            (r'\[', ''),            # Rimuovo [
            (r'\]', ''),            # Rimuovo ]
            (r'\{', ''),            # Rimuovo {
            (r'\}', ''),            # Rimuovo }
            (r'\/', ''),            # Rimuovo /
            (r'\:', ' '),           # Rimuovo :
            (r'\|', ' '),           # Rimuovo |
            (r'\=', ' '),           # Rimuovo =
            (r'\*', ''),            # Rimuovo *
        ]
        res = text
        for old, new in replacements:
            res = re.sub(old, new, res, flags=re.DOTALL) # perchè il '.' non fa match con newline 

        return res  


    def startFilter(self, text, title):
        """
        Effettuo filtraggio completo della pagina di wikipedia.

        :param self
        :param text: testo della pagina
        :parma title: titolo della pagina
        """
        res = self.getLinkAndCategory(text, title)
        res['text'] = FilterWikiText.getCleaned(text)
        return res

                    
                    
                    
                    
                    
                    