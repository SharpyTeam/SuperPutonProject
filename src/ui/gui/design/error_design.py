# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'D:\Documents\Projects\HSE\SuperPutonProject\ui_src\error.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ErrorOccurredWindow(object):
    def setupUi(self, ErrorOccurredWindow):
        ErrorOccurredWindow.setObjectName("ErrorOccurredWindow")
        ErrorOccurredWindow.resize(800, 600)
        ErrorOccurredWindow.setWindowTitle("Произошла ошибка")
        self.centralwidget = QtWidgets.QWidget(ErrorOccurredWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.error_occured_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(16)
        self.error_occured_label.setFont(font)
        self.error_occured_label.setToolTip("")
        self.error_occured_label.setText("Произошла ошибка!")
        self.error_occured_label.setAlignment(QtCore.Qt.AlignCenter)
        self.error_occured_label.setObjectName("error_occured_label")
        self.verticalLayout.addWidget(self.error_occured_label)
        self.error_details_label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.error_details_label.setFont(font)
        self.error_details_label.setObjectName("error_details_label")
        self.verticalLayout.addWidget(self.error_details_label)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.textBrowser.setFont(font)
        self.textBrowser.setAcceptDrops(False)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.exit_button = QtWidgets.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.exit_button.setFont(font)
        self.exit_button.setObjectName("exit_button")
        self.verticalLayout.addWidget(self.exit_button)
        ErrorOccurredWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ErrorOccurredWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        ErrorOccurredWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ErrorOccurredWindow)
        self.statusbar.setObjectName("statusbar")
        ErrorOccurredWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ErrorOccurredWindow)
        QtCore.QMetaObject.connectSlotsByName(ErrorOccurredWindow)

    def retranslateUi(self, ErrorOccurredWindow):
        _translate = QtCore.QCoreApplication.translate
        self.error_details_label.setText(_translate("ErrorOccurredWindow", "Подробности: -"))
        self.exit_button.setText(_translate("ErrorOccurredWindow", "Закрыть программу"))


