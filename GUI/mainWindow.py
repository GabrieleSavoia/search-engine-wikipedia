# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(833, 711)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setToolTip("")
        MainWindow.setStatusTip("")
        MainWindow.setWhatsThis("")
        MainWindow.setAccessibleName("")
        MainWindow.setAccessibleDescription("")
        MainWindow.setAutoFillBackground(False)
        MainWindow.setWindowFilePath("")
        MainWindow.setUnifiedTitleAndToolBarOnMac(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 240, 811, 441))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.result_Layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.result_Layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.result_Layout.setContentsMargins(0, 0, 0, 0)
        self.result_Layout.setObjectName("result_Layout")
        self.resultWidgetList = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.resultWidgetList.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.resultWidgetList.setObjectName("resultWidgetList")
        self.result_Layout.addWidget(self.resultWidgetList)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 210, 811, 31))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.info_Layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.info_Layout.setContentsMargins(0, 0, 0, 0)
        self.info_Layout.setObjectName("info_Layout")
        self.info_search_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.info_search_label.setAlignment(QtCore.Qt.AlignCenter)
        self.info_search_label.setObjectName("info_search_label")
        self.info_Layout.addWidget(self.info_search_label)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(10, 10, 811, 201))
        self.scrollArea.setAutoFillBackground(True)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 809, 199))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.search_query = QtWidgets.QLineEdit(self.scrollAreaWidgetContents)
        self.search_query.setGeometry(QtCore.QRect(230, 20, 341, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_query.sizePolicy().hasHeightForWidth())
        self.search_query.setSizePolicy(sizePolicy)
        self.search_query.setBaseSize(QtCore.QSize(0, 0))
        self.search_query.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.search_query.setInputMask("")
        self.search_query.setText("")
        self.search_query.setFrame(True)
        self.search_query.setObjectName("search_query")
        self.search_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.search_button.setGeometry(QtCore.QRect(570, 20, 101, 41))
        self.search_button.setObjectName("search_button")
        self.label_search = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_search.setGeometry(QtCore.QRect(370, 0, 81, 16))
        self.label_search.setObjectName("label_search")
        self.limit_spin = QtWidgets.QSpinBox(self.scrollAreaWidgetContents)
        self.limit_spin.setGeometry(QtCore.QRect(10, 110, 71, 24))
        self.limit_spin.setObjectName("limit_spin")
        self.query_setting_label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.query_setting_label.setGeometry(QtCore.QRect(360, 70, 121, 16))
        self.query_setting_label.setObjectName("query_setting_label")
        self.limit_labe = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.limit_labe.setGeometry(QtCore.QRect(10, 90, 41, 16))
        self.limit_labe.setObjectName("limit_labe")
        self.weighting_label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.weighting_label.setGeometry(QtCore.QRect(120, 90, 61, 21))
        self.weighting_label.setObjectName("weighting_label")
        self.weighting_combo = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.weighting_combo.setGeometry(QtCore.QRect(120, 110, 101, 26))
        self.weighting_combo.setObjectName("weighting_combo")
        self.groupCombo = QtWidgets.QComboBox(self.scrollAreaWidgetContents)
        self.groupCombo.setGeometry(QtCore.QRect(260, 110, 71, 26))
        self.groupCombo.setObjectName("groupCombo")
        self.groupLabel = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.groupLabel.setGeometry(QtCore.QRect(260, 90, 41, 21))
        self.groupLabel.setObjectName("groupLabel")
        self.text_boost_labe = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.text_boost_labe.setGeometry(QtCore.QRect(10, 150, 71, 16))
        self.text_boost_labe.setObjectName("text_boost_labe")
        self.title_boost_label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.title_boost_label.setGeometry(QtCore.QRect(120, 150, 71, 16))
        self.title_boost_label.setObjectName("title_boost_label")
        self.text_boost_spin = QtWidgets.QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.text_boost_spin.setGeometry(QtCore.QRect(10, 170, 68, 24))
        self.text_boost_spin.setSingleStep(0.1)
        self.text_boost_spin.setObjectName("text_boost_spin")
        self.title_boost_spin = QtWidgets.QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.title_boost_spin.setGeometry(QtCore.QRect(120, 170, 68, 24))
        self.title_boost_spin.setSingleStep(0.1)
        self.title_boost_spin.setObjectName("title_boost_spin")
        self.query_setting_restore_button = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.query_setting_restore_button.setGeometry(QtCore.QRect(720, 160, 91, 41))
        self.query_setting_restore_button.setObjectName("query_setting_restore_button")
        self.expandedTerms = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.expandedTerms.setGeometry(QtCore.QRect(390, 130, 251, 61))
        self.expandedTerms.setObjectName("expandedTerms")
        self.expansion_checkBox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.expansion_checkBox.setGeometry(QtCore.QRect(390, 110, 131, 20))
        self.expansion_checkBox.setObjectName("expansion_checkBox")
        self.page_rank_checkbox = QtWidgets.QCheckBox(self.scrollAreaWidgetContents)
        self.page_rank_checkbox.setGeometry(QtCore.QRect(260, 170, 91, 20))
        self.page_rank_checkbox.setObjectName("page_rank_checkbox")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Wiki Search Engine"))
        self.info_search_label.setText(_translate("MainWindow", "Time : ... s        |        Results : ...   "))
        self.search_query.setPlaceholderText(_translate("MainWindow", "Write your query here"))
        self.search_button.setText(_translate("MainWindow", "Search"))
        self.label_search.setText(_translate("MainWindow", "SEARCHING"))
        self.query_setting_label.setText(_translate("MainWindow", "QUERY SETTINGS"))
        self.limit_labe.setText(_translate("MainWindow", "Limit"))
        self.weighting_label.setText(_translate("MainWindow", "Weighting"))
        self.groupLabel.setText(_translate("MainWindow", "Group"))
        self.text_boost_labe.setText(_translate("MainWindow", "Text Boost"))
        self.title_boost_label.setText(_translate("MainWindow", "Title Boost"))
        self.query_setting_restore_button.setText(_translate("MainWindow", "Restore All"))
        self.expansion_checkBox.setText(_translate("MainWindow", "Expansion terms"))
        self.page_rank_checkbox.setText(_translate("MainWindow", "Page Rank"))

