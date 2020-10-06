
import re
from . import urlRequest

#INTERWIKI_PREFIX = urlRequest.getInterwikiMap()

INTERWIKI_PREFIX = ('')

def getLinkAndCategory(text, title, link_file=False):
    """
    # DOCS   https://www.mediawiki.org/wiki/Help:Links#Internal_links
    # DOCS   https://www.mediawiki.org/wiki/Help:Categories
    # DOCS   https://www.mediawiki.org/wiki/Help:Images   alla fine per le diff tra ':File' 'File' ..
    # DOCS   https://meta.wikimedia.org/wiki/Help:Interwiki_linking   INTERWIKI
    
    Rilevamento dei link e delle categorie del testo presenti nella stringa del campo 'text'.
    Abbiamo deciso di usare una singola funzione perchè per definire le categorie che appartengono
    ad un certo testo si usa la stessa struttura dei link, ovveo [[Category:]], ma senza i ':' iniziali.
    Alcuni tipi di link non vengono considerati dato che li abbiamo considerati NON RILEVANTI
    per la link analysis.
    in questi casi viene comunque implementata la condizione ma viene imposto res a Null, così si predispone
    per eventuali estensioni future.
    
    IMPORTANTE : il salvataggio dei link e categorie è sottoforma di stringhe con spazi, 
                questi andranno trasformati in '_' se voglio avere il link vero e proprio.
    
    NOTA = 'Interwiki links' per poter essere identificati, è necessario eseguire una richiesta 
           al server di WikiMedia che contiene una table con tutti i prefissi con i relativi url
           risolti in base al prefisso. Abbiamo deciso di non considerarli per la link analysis dato
           che si riferiscono spesso a link esterni. INTERWIKI_PREFIX contiene 
           SOLO I PREFISSI e li abbiamo salvati in un SET chiamato 'interwiki_prefix', così che la
           ricerca sia O(1), a discapito però di un maggior impiego di memoria rispetto che ad una 
           lista.
    
    :param text: il testo da cui estrarre i link
    :param title: il titolo del teso, che corrisponde al link della pagina 
    :param link_file: bool per decidere se è opportuno considerare i link a file multimediali
    
    return res_dict: dizionario con 2 liste, una per le categorie e una per i link
    
    """
    res_dict ={'links': [], 'categories': []}
    
    # prima usavo questa (.+?)  ma è meglio  ([^\]]+)
    pattern = re.compile(r'\[\[([^\]]+?)\]\]') 
    
    for match in re.finditer(pattern, text):
        res = match.group(1).split("|")[0].strip()   # strip rimuove spazi inizio o fine IMPORTANTE!
        
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
                
            # Si tratta di LINK a PAGINE DI CATEGORIE. Questo NON significa che il documento 
            # corrente fa parte della categoria linkata. 
            elif res.startswith(':Category'):
                res = res[1:]                    # tolgo primo carattere ':'                    
                
            # Link TESTUALE (NON E' IMMAGINE) che punta AD UNA PAGINA WIKIPEDIA contenente l'IMMAGINE
            # le sue caratteristiche e in più UN ELENCO DI TUTTE LE PAGINE CHE LA USANO.
            # Questo elenco è sotto forma di lista di link a pagine.
            elif res.startswith(':File'):
                if link_file: 
                    res = res[1:]
                else:
                    res = None
                
            # E' un'IMMAGINE che contiene un link. Questo link può essere customizzato ma abbiamo
            # deciso che non è opportuno salvarselo per lo scopo di questo progetto. 
            elif (res.startswith('Media:') or 
                  res.startswith('File:') or 
                  res.startswith('Image:')):
                if not link_file:
                    res = None
            
            # Pagine personali degli utenti oppure a specifiche revisioni 
            # specificando il numero di revisione.
            # Non serve salvarsi i link.
            elif res.startswith('Special:'):
                res = None
            
            # Abbiamo deciso di non risolvere il valore di queste variabili in link dato che 
            # servono principalmente per riferirsi a Talk pages oppure risolvere link di
            # help pages per ricondursi a link di base.
            elif res.startswith('{{'):
                res = None
                
            # Controlla se è un 'interwiki' link.
            # Se lo è lo ignoro.
            # IMPORTANTE : questa regola è molto generica e tienila in basso così se 'res' soddisfa 
            # regole più specifiche (scritte sopra) qua non entra.
            elif re.search(r'^:?[^:]+?:', res) is not None:
                pref = re.search(r'^:?[^:]+?:', res)[0]
                pref = re.sub(r':', '', pref) 
                if pref in INTERWIKI_PREFIX:
                    res = None                    
                
            # Se res == None --> tipo di link non gestito e non faccio niente
            if res is not None:
                if is_category:
                    res_dict['categories'].append(res)
                else:
                    res_dict['links'].append(res)
    return res_dict 


def getCleaned(text):
    """
    # DOCS   https://www.mediawiki.org/wiki/Help:Magic_words
    
    Eseguo una pulizia del testo dalle parti che sicuramente non sono importanti ai fini del
    progetto come i tag html, i link esterni..
    Mantengo invece i link interni perchè potrebbero contenere parole che possono dare un maggiore
    significato al documento.
    Esistono moltissimi tipi di tag, variabili e funzioni che potrebbero essere filtrati in modo 
    da ottnere un testo più pulito ma abbiamo ritenuto non necessario coprire tutti i possibili casi.
    
    In questa fase NON vengono eliminati i caratteri non attinenti come '[(..' dato che è il 
    compito dell'analizzatore.
    
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
        (r'\shttp.+?\s', ''),          # rimuovo link esterni  -> NON FUNZIONA SE url è inizio stringa !! 
        (r'\s[^\s]+\.com\s?', ''),     # rimuovo ogni parola che termina con '.com' |
        (r'\s[^\s]+\.org\s?', ''),     # rimuovo ogni parola che termina con '.org' |
        (r'\s[^\s]+\.it\s?', ''),      # rimuovo ogni parola che termina con '.it'  | --> Li elimino perchè sono link esterni a wikipedia e non li considero importanti per l'applicazione
        (r'\s[^\s]+\.en\s?', ''),      # rimuovo ogni parola che termina con '.en'  |
        
                                     
        (r'<gallery.*?</gallery>', ''),   # Qua vengono di solito messe le liste di file che non salvo
        (r'\[\[File:.*?\]\]', ''),        # Se non è presente '|' , CANCELLO FINO A '\n'
        (r'\[\[Media:.*?\]\]', ''),       # da 'Media:...|txt_name' -> rimane 'txt_name'
        
        (r'<[^<]*?>', ''),           # rimuovo tag html TIENI ALLA FINE 

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
                    
                    
                    
                    
                    
                    
                    
                    