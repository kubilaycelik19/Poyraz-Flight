# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'flightHistory.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_flightWindow(object):
    def setupUi(self, flightWindow):
        flightWindow.setObjectName("flightWindow")
        flightWindow.resize(1900, 950)
        flightWindow.setMinimumSize(QtCore.QSize(1180, 800))
        flightWindow.setMaximumSize(QtCore.QSize(1900, 950))
        font = QtGui.QFont()
        font.setUnderline(False)
        flightWindow.setFont(font)
        flightWindow.setWindowOpacity(0.94)
        flightWindow.setStyleSheet("")
        self.centralwidget = QtWidgets.QWidget(flightWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mapWidget = QtWidgets.QWidget(self.centralwidget)
        self.mapWidget.setGeometry(QtCore.QRect(0, 0, 1901, 951))
        self.mapWidget.setObjectName("mapWidget")
        flightWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(flightWindow)
        QtCore.QMetaObject.connectSlotsByName(flightWindow)

    def retranslateUi(self, flightWindow):
        _translate = QtCore.QCoreApplication.translate
        flightWindow.setWindowTitle(_translate("flightWindow", "MainWindow"))
import img_rc


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    flightWindow = QtWidgets.QMainWindow()
    ui = Ui_flightWindow()
    ui.setupUi(flightWindow)
    flightWindow.show()
    sys.exit(app.exec_())
