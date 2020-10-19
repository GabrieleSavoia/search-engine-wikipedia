
#import sys
#from PyQt5 import QtWidgets, uic
  
#app = QtWidgets.QApplication(sys.argv)

#window = uic.loadUi("GUI/search_form.ui")
#window.show()
#app.exec()

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem, QWidget

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from GUI import mainWindow, delegates          # comando :  pyuic5 mainWindow.ui -o mainWindow.py
from GUI.evaluationDialog import EvaluationDialog

from indexing import index, evaluation
from indexing.searching.searcher import WikiSearcher

import sys  
import argparse
import time


class MainWindow(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):

    def __init__(self, wiki_index, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setupUi(self) # Presente nel file mainWindow.Ui_MainWindow

        self.wiki_index = wiki_index
        
        self.setFixedSize(833, 711)
        
        self.resultWidgetList.setItemDelegate(delegates.HTMLDelegate())
        
        self.setupEvent()
        
        self.statusbar.showMessage('Indexed docs : {}    |    '\
                                   'Field \'title\' length : {}    |    '\
                                   'Field \'text\' length : {}'.
                                   format(self.wiki_index.getGeneralInfo()['doc_count'],
                                          self.wiki_index.getFieldInfo('title')['length'],
                                          self.wiki_index.getFieldInfo('text')['length']))
        
        
        list_group = WikiSearcher.group.keys()
        self.groupCombo.addItems(list_group)
        list_weighting = WikiSearcher.weighting.keys()
        self.weighting_combo.addItems(list_weighting)  
        
        self.setupQuerySettings() 

        self.w = QWidget()


    def setupEvent(self):
        self.search_button.clicked.connect(self.startSearchEvent)
        self.resultWidgetList.itemDoubleClicked.connect(self.openDocument)
        self.query_setting_restore_button.clicked.connect(self.setupQuerySettings) 
        self.evaluation.clicked.connect(self.computeEvaluation)


    def computeEvaluation(self):
        dlg = EvaluationDialog(self.w, self.wiki_index, self.getSettings())  
        
        
    def setupQuerySettings(self):
        self.limit_spin.setValue(10)
        
        self.weighting_combo.setCurrentText('BM25F')
        self.groupCombo.setCurrentText('AND')
        
        self.text_boost_spin.setValue(1.0)
        self.title_boost_spin.setValue(1.0)  
        
        self.expansion_checkBox.setChecked(True)
        self.page_rank_checkbox.setChecked(False)


    def getSettings(self):
    	return  {'limit': self.limit_spin.value(), 
                    'exp' : self.expansion_checkBox.isChecked(), 
                    'page_rank' : self.page_rank_checkbox.isChecked(),
                    'text_boost' : self.text_boost_spin.value(),
                    'title_boost' : self.title_boost_spin.value(),
                    'weighting' : self.weighting_combo.currentText(),
                    'group' : self.groupCombo.currentText(),
                    }
        
        
    def startSearchEvent(self):
        # sender = self.sender()     ottengo oggetto che ha generato l'evento
        
        self.res_link = []
        
        text = self.search_query.text()

        settings = self.getSettings()
        
        query_results = self.wiki_index.query(text, **settings)

        self.updateResultWidgetList(settings, query_results)
        self.updateInfoSearch(query_results)
        self.updateExpandedTerms(settings, query_results)
        

    def updateResultWidgetList(self, settings, query_results):
        self.resultWidgetList.clear()
        
        if len(query_results['docs']) == 0:
            self.resultWidgetList.insertItem(0, 'Nessun documento compatibile con la ricerca.')
            it = self.resultWidgetList.item(0)
            it.setFlags(QtCore.Qt.NoItemFlags)  # Non selezionabile
        else:
            for pos, result in enumerate(query_results['docs']):
                title = '<p><b>'+result['title']+'</b></p>'
                p_r = str(result['page_rank']) if settings.get('page_rank') else 'Disabled'
                score = '<p><i>Final Score</i> : '+str(round(result['final_score'],3))+' ---> <i>Score</i> : '+str(round(result['score'],3))+' | <i>Page rank</i> : '+p_r+'</p>'
                link =  '<p><i>Link</i> : <u>'+result['link']+'</u></p>'
                highlight = '<p><i>highlight</i> : ... '+result['highlight'].replace('...', ' ... | ... ')+' ...</p>'
                self.res_link.append(result['link'])
                self.resultWidgetList.insertItem(pos, title+score+highlight)
                
                if (pos % 2) == 0: 
                    self.resultWidgetList.item(pos).setBackground(QColor('#f5f5f5'))


    def updateInfoSearch(self, query_results):
        seconds = query_results['time_second']
        n_res = query_results['n_res']
        retrieved = len(query_results['docs'])

        self.info_search_label.setText('Time : {}s        |        '\
                                       'Retrieved {} of {} matched'\
                                       .format(round(seconds, 4),
                                               retrieved, 
                                               n_res))


    def updateExpandedTerms(self, settings, query_results):
        if settings.get('exp', True):
            if len(query_results['expanded'])>0:
                self.expandedTerms.setText(', '.join(query_results['expanded']))
            else:
                self.expandedTerms.setText('No expansion term found.')    
        else:
            self.expandedTerms.setText('Query expansion DISABLED.')

        
    def openDocument(self):
        import webbrowser 
        
        row = self.resultWidgetList.currentRow()
        link = self.res_link[row]
        
        if len(self.res_link) >= row and row>=0:
            try:
                webbrowser.open(link, new=2)
            except Exception:
                print('Errore durante apertura del link '+ link)
            
        
def main(args_paths):
    app = QtWidgets.QApplication(sys.argv)

    wiki_index = index.WikiIndex(args_paths)

    if wiki_index.openOrBuild():
        main = MainWindow(wiki_index)
        main.show()
        sys.exit(app.exec_())


if __name__ == '__main__':

    p = argparse.ArgumentParser(description='Creazione Wiki Search Engine con interfaccia grafica.')
    p.add_argument(
        '--index_dir',
        type=str,
        default='files/indexdir',
        help='Folder indice whoosh.')
    p.add_argument(
        '--corpus',
        type=str,
        default='files/filtered.xml',
        help='File xml filtrato.')
    p.add_argument(
        '--google_links',
        type=str,
        default='files/google_links.json',
        help='File json che contiene il dict con le query di google e i rispettivi links.')
    p.add_argument(
        '--interwiki_links',
        type=str,
        default='files/interwiki.prefix',
        help='File per gli interwiki links.')
    p.add_argument(
        '--pagerank',
        type=str,
        default='files/table.rank',
        help='File dove salvo il pagerank calcolato')

    args_paths = p.parse_args()   

    main(args_paths)

