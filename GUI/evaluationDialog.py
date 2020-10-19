from PyQt5.QtWidgets import QLabel, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5 import QtWidgets

from PyQt5 import QtCore

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from indexing import index, evaluation


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
            if key != 'limit' and key != 'group':
                text += '<b>'+str(key)+'</b>: '+str(value)+', &nbsp; &nbsp; &nbsp;'
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
        r_prec = self.evaluator.Rprecision()
        e_meas = self.evaluator.computeEmeasure(b=1.5)
        f_meas = self.evaluator.computeFmeasure()

        data = {}
        for query in e_meas:
            data[query] = []
            data[query].append(ndcg[query])
            data[query].append(r_prec[query])
            data[query].append(e_meas[query])
            data[query].append(f_meas[query])

        data = dict(sorted(data.items()))

        return self.createTable(['Query', 'NDCG', 'R-PRECISION', 'E-MEASURE', 'F_MEASURE'], data)


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
        res = self.evaluator.averagePrecisionAtRecall()
        recall = list(res.keys())
        precision = list(res.values())

        graphWidget = pg.PlotWidget()

        graphWidget.setTitle("Average Precison at recall level:", color="k", size="18pt")
        graphWidget.setBackground('w')

        styles = {"color": "#000000", "font-size": "15px"}
        graphWidget.setLabel('left', 'Precision', **styles)
        graphWidget.setLabel('bottom', 'Recall', **styles)

        graphWidget.showGrid(x=True, y=True)
        graphWidget.setXRange(0, 1.02, padding=0)
        graphWidget.setYRange(0, 1.05, padding=0)

        pen = pg.mkPen(color=(255, 0, 0), width=5, style=QtCore.Qt.SolidLine)
        graphWidget.plot(recall, precision, 
                        pen=pen, symbol='o',symbolSize=8, symbolBrush=('b'))
        return graphWidget