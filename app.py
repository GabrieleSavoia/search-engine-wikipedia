
#import sys
#from PyQt5 import QtWidgets, uic
  
#app = QtWidgets.QApplication(sys.argv)

#window = uic.loadUi("GUI/search_form.ui")
#window.show()
#app.exec()

from PyQt5 import QtWidgets
from PyQt5 import QtCore

from PyQt5.QtGui import QColor

from GUI import mainWindow, delegates  # comando :  pyuic5 mainWindow.ui -o mainWindow.py

from indexing import index

import sys  


class MainWindow(QtWidgets.QMainWindow, mainWindow.Ui_MainWindow):

    def __init__(self, name_index_dir='indexing/indexdir', 
                 corpus_path='indexing/xmlParsing/xml/wiki_fake.xml', 
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setupUi(self) # Presente nel file mainWindow.Ui_MainWindow
        
        self.setFixedSize(833, 711)
        
        self.resultWidgetList.setItemDelegate(delegates.HTMLDelegate())
        
        self.setupEvent()
        
        self.wiki_index = index.WikiIndex(name_index_dir, corpus_path)
        self.wiki_index.build()
        
        self.statusbar.showMessage('Indexed docs : {}    |    '\
                                   'Field \'title\' length : {}    |    '\
                                   'Field \'text\' length : {}'.
                                   format(self.wiki_index.getGeneralInfo()['doc_count'],
                                          self.wiki_index.getFieldInfo('title')['length'],
                                          self.wiki_index.getFieldInfo('text')['length']))
        
        
        list_group = ['AND', 'OR']
        self.groupCombo.addItems(list_group)
        list_weighting = ['BM25F', 'TF_IDF']
        self.weighting_combo.addItems(list_weighting)  
        
        self.setupQuerySettings()     
        
        
    def setupQuerySettings(self):
        self.limit_spin.setValue(10)
        
        self.weighting_combo.setCurrentText('BM25F')
        self.groupCombo.setCurrentText('AND')
        
        self.text_boost_spin.setValue(1.0)
        self.title_boost_spin.setValue(1.0)  
        
        self.expansion_checkBox.setChecked(True)
        
        
    def setupEvent(self):
        self.search_button.clicked.connect(self.startSearchEvent)
        self.resultWidgetList.itemDoubleClicked.connect(self.openDocument)
        self.query_setting_restore_button.clicked.connect(self.setupQuerySettings)
        
        
    def startSearchEvent(self):
        # sender = self.sender()     ottengo oggetto che ha generato l'evento
        self.resultWidgetList.clear()
        self.res_link = []
        
        text = self.search_query.text()
        limit = self.limit_spin.value()
        weighting = self.weighting_combo.currentText()
        group = self.groupCombo.currentText()
        title_boost = self.title_boost_spin.value()
        text_boost = self.text_boost_spin.value()
        exp = self.expansion_checkBox.isChecked()
        page_rank = self.page_rank_checkbox.isChecked()
        
        query_results = self.wiki_index.query(text, 
                                              limit=limit, 
                                              weighting=weighting,
                                              group=group,
                                              title_boost=title_boost,
                                              text_boost=text_boost,
                                              exp=exp,
                                              page_rank=page_rank)
        
        seconds = query_results['time_second']
        n_res = query_results['n_res']
        retrieved = len(query_results['docs'])
        
        if len(query_results['docs']) == 0:
            self.resultWidgetList.insertItem(0, 'Nessun documento compatibile con la ricerca.')
            it = self.resultWidgetList.item(0)
            it.setFlags(QtCore.Qt.NoItemFlags)  # Rendilo non selezionabile
        else:
            for pos, result in enumerate(query_results['docs']):
                title = '<p><b>'+result['title']+'</b></p>'
                p_r = str(result['page_rank']) if page_rank else 'Disabled'
                score = '<p><i>Final Score</i> : '+str(round(result['final_score'],3))+' ---> <i>Score</i> : '+str(round(result['score'],3))+' | <i>Page rank</i> : '+p_r+'</p>'
                #link =  '<p><i>Link</i> : <u>'+result['link']+'</u></p>'
                highlight = '<p><i>highlight</i> : ... '+result['highlight'].replace('...', ' ... | ... ')+' ...</p>'
                self.res_link.append(result['link'])
                self.resultWidgetList.insertItem(pos, title+score+highlight)
                
                if (pos % 2) == 0: 
                    self.resultWidgetList.item(pos).setBackground(QColor('#f5f5f5'))
            
        self.info_search_label.setText('Time : {}s        |        '\
                                       'Retrieved {} of {} matched'\
                                       .format(round(seconds, 4),
                                               retrieved, 
                                               n_res))
        
        if exp:
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
            
        
def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':      
    main()

