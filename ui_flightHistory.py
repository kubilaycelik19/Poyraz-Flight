# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'flightHistory.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QSizePolicy, QWidget)
import img_rc

class Ui_flightWindow(object):
    def setupUi(self, flightWindow):
        if not flightWindow.objectName():
            flightWindow.setObjectName(u"flightWindow")
        flightWindow.resize(1180, 630)
        flightWindow.setMinimumSize(QSize(1180, 630))
        flightWindow.setMaximumSize(QSize(1180, 630))
        font = QFont()
        font.setUnderline(False)
        flightWindow.setFont(font)
        flightWindow.setWindowOpacity(0.940000000000000)
        flightWindow.setStyleSheet(u"")
        self.centralwidget = QWidget(flightWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.mapWidget = QWidget(self.centralwidget)
        self.mapWidget.setObjectName(u"mapWidget")
        self.mapWidget.setGeometry(QRect(0, 0, 1180, 630))
        flightWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(flightWindow)

        QMetaObject.connectSlotsByName(flightWindow)
    # setupUi

    def retranslateUi(self, flightWindow):
        flightWindow.setWindowTitle(QCoreApplication.translate("flightWindow", u"MainWindow", None))
    # retranslateUi

