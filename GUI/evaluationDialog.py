from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QGridLayout
from PyQt5 import QtWidgets

from PyQt5.QtWidgets import QWidget

from PyQt5 import QtCore

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from indexing import index, evaluation
from indexing.searching import searcher


class EvaluationDialog(QDialog):

    def __init__(self, parent, wiki_index, settings):
        super(EvaluationDialog, self).__init__(parent)

        self.setModal(0)

        self.wiki_index = wiki_index
        self.evaluator = evaluation.Evaluator(self.wiki_index, settings)

        # MAP
        self.textMAP = QLabel('<b>'+'MAP: '+'</b>'+str(self.evaluator.MAP()))

        # GRAPH
        self.graph = self.createAveragePrecisonGraph()

        # Settings
        self.text_settings = QLabel()
        text = ''
        for key, value in settings.items():
            if key == 'exp':
                key = 'expansion'
            if key != 'group':
                if key == 'text_boost' or key == 'title_boost': 
                    value = round(value, 3)
                text += '<b>'+str(key)+'</b>: '+str(value)+', &nbsp; &nbsp;'
            if key == 'group':
                text += '<b>'+str(key)+'</b>: '+str(value)
        self.text_settings.setText(text)


        self.table = self.createEvaluationTable()


        layout = QVBoxLayout()

        # Settings
        layout.addWidget(self.text_settings)

        # GRAPH add
        layout.addWidget(self.graph)

        # MAP add
        layout.addWidget(self.textMAP)

        # Table
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.setWindowTitle("Evaluation")

        self.setMinimumSize(870, 610)

        self.show() 


    def createEvaluationTable(self):
        ndcg = self.evaluator.NDCG()
        r = 10
        r_prec = self.evaluator.Rprecision(r=r)
        b = 1.0
        e_meas = self.evaluator.Emeasure(b=b)
        f_meas = self.evaluator.Fmeasure()

        data = {}
        for query in e_meas:
            data[query] = []
            data[query].append(ndcg[query])
            data[query].append(r_prec[query])
            data[query].append(e_meas[query])
            data[query].append(f_meas[query])

        data = dict(sorted(data.items()))

        #return self.createTable(['Query', 'NDCG', 'PRECISION@'+str(r), 'E-MEASURE (b='+str(b)+')', 'F_MEASURE'], data)
        return EvaluationTableWidget(['Query', 'NDCG', 'PRECISION@'+str(r), 'E-MEASURE (b='+str(b)+')', 'F_MEASURE'], 
                                        data, self.evaluator)


    def createTable(self, title_col, data):
        tableWidget = QTableWidget()
        tableWidget.setRowCount(len(data.keys()))
        tableWidget.setColumnCount(len(title_col))
        tableWidget.setHorizontalHeaderLabels(title_col)
        for count, query in enumerate(data):
            tableWidget.setItem(count, 0, self.cell(query))
            for pos, val in enumerate(data[query], 1):
                tableWidget.setItem(count, pos, self.cell(str(val)))

        header = tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        for i in range(len(title_col)):     
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        tableWidget.setMinimumHeight(230)
        return tableWidget  


    def cell(self, var=""):
        item = QTableWidgetItem()
        item.setText(var)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        return item    


    def createAveragePrecisonGraph(self):
        res = self.evaluator.averagePrecisionAtLevel()
        recall = list(res.keys())
        precision = list(res.values())

        graphWidget = pg.PlotWidget()

        graphWidget.setTitle("Average Precison at recall level:", color="k", size="18pt")
        graphWidget.setBackground('w')

        styles = {"color": "#000000", "font-size": "15px"}
        graphWidget.setLabel('left', 'Precision', **styles)
        graphWidget.setLabel('bottom', 'Recall', **styles)

        graphWidget.showGrid(x=True, y=True)
        graphWidget.setXRange(0.08, 1.02, padding=0)
        graphWidget.setYRange(0, 1.05, padding=0)

        pen = pg.mkPen(color=(255, 0, 0), width=5, style=QtCore.Qt.SolidLine)
        graphWidget.plot(recall, precision, 
                        pen=pen, symbol='o',symbolSize=8, symbolBrush=('b'))
        return graphWidget



class EvaluationTableWidget(QWidget):

    def __init__(self, title_col, data, evaluator):
        super().__init__()

        self.evaluator = evaluator

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(data.keys()))
        self.tableWidget.setColumnCount(len(title_col))
        self.tableWidget.setHorizontalHeaderLabels(title_col)

        for count, query in enumerate(data):
            self.tableWidget.setItem(count, 0, self.cell(query))
            for pos, val in enumerate(data[query], 1):
                self.tableWidget.setItem(count, pos, self.cell(str(val)))

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        for i in range(len(title_col)):     
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.tableWidget.setMinimumHeight(230)

        self.tableWidget.viewport().installEventFilter(self)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        

    def cell(self, var=""):
        item = QTableWidgetItem()
        item.setText(var)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        return item   


    def eventFilter(self, source, event):
        if(event.type() == QtCore.QEvent.MouseButtonPress and
           event.buttons() == QtCore.Qt.LeftButton and
           source is self.tableWidget.viewport()):
            item = self.tableWidget.itemAt(event.pos())
            if item is not None:
                query = self.tableWidget.item(item.row(), 0).text()
                results = self.evaluator.results(query)
                dialog_result = CompareResultsDialog(query, results)
                dialog_result.exec_()
        return super(EvaluationTableWidget, self).eventFilter(source, event)      

class CompareResultsDialog(QDialog):

    def __init__(self, query, results):
        super(CompareResultsDialog, self).__init__()

        self.setWindowTitle("Query Detail")

        #self.query = QLabel('<b>'+'Query: '+'</b>'+str(query))
        self.query = QLabel('<html><head/><body><p align=\'center\'>'+'<b>'+'Query: '+'</b>'+str(query)+'</p></body></html>')
        self.results = results

        grid = QGridLayout()
        grid.addWidget(QLabel('<b>'+'R-Set:'+'</b>'), 0, 0)
        grid.addWidget(QLabel('<b>'+'A-Set:'+'</b>'), 0, 1)

        max_len = max( len(self.results['r']), len(self.results['a']) )

        for counter in range(0, max_len):
            r_label, a_label = self.getLabels(counter)

            grid.addWidget(r_label, counter+1, 0)
            grid.addWidget(a_label, counter+1, 1)


        layout = QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(self.query)
        layout.addLayout(grid)
        self.setLayout(layout)


    def getLabels(self, counter):

        try:
            r_link = self.results['r'][counter]
            if (r_link in self.results['a']):
                r_title = '<b>('+str(counter+1)+')</b> &nbsp;'+r_link[len(searcher.WikiSearcher.base_url):]
            else:
                r_title = '('+str(counter+1)+') &nbsp; <b></b>'+r_link[len(searcher.WikiSearcher.base_url):]
        except:
            r_link = ''
            r_title = ''

        try:
            a_link = self.results['a'][counter]
            a_title = a_link[len(searcher.WikiSearcher.base_url):]
        except:
            a_link = ''
            a_title = ''

        r_label = QLabel(str(r_title))
        a_label = QLabel(str(a_title))

        if (a_link != '') and (a_link in self.results['r']):
            index = self.results['r'].index(a_link)

            a_label.setText(str(a_title)+' &nbsp; &nbsp; <b> ('+ str(index+1) + ')</b>')
            a_label.setStyleSheet("background-color: yellow;")

        return r_label, a_label 






