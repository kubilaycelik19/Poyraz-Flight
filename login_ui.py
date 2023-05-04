# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
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
from PySide6.QtWidgets import (QApplication, QLineEdit, QMainWindow, QPushButton,
    QSizePolicy, QWidget)
import img_rc

class Ui_login(object):
    def setupUi(self, login):
        if not login.objectName():
            login.setObjectName(u"login")
        login.resize(950, 535)
        login.setMinimumSize(QSize(949, 530))
        login.setMaximumSize(QSize(9999, 9999))
        font = QFont()
        font.setFamilies([u"Favela-Medium"])
        font.setPointSize(10)
        login.setFont(font)
        icon = QIcon()
        icon.addFile(u":/envanter/images/icon/poyrazLogo.ico", QSize(), QIcon.Normal, QIcon.Off)
        login.setWindowIcon(icon)
        login.setStyleSheet(u"#centralwidget{\n"
"	background-image: url(:/envanter/images/img/loginBG1.jpg);\n"
"	background-repeat: no-repeat;\n"
"}")
        self.centralwidget = QWidget(login)
        self.centralwidget.setObjectName(u"centralwidget")
        self.idtext = QLineEdit(self.centralwidget)
        self.idtext.setObjectName(u"idtext")
        self.idtext.setGeometry(QRect(310, 240, 331, 31))
        font1 = QFont()
        font1.setFamilies([u"Favela-Medium"])
        font1.setPointSize(11)
        self.idtext.setFont(font1)
        self.idtext.setStyleSheet(u"background-color: rgba(0,0,0,0);\n"
"border: none;\n"
"color: rgba(32,123,255,255);")
        self.passtext = QLineEdit(self.centralwidget)
        self.passtext.setObjectName(u"passtext")
        self.passtext.setGeometry(QRect(310, 300, 331, 31))
        font2 = QFont()
        font2.setFamilies([u"Favela-Medium"])
        font2.setPointSize(12)
        font2.setStyleStrategy(QFont.PreferDefault)
        self.passtext.setFont(font2)
        self.passtext.setFocusPolicy(Qt.StrongFocus)
        self.passtext.setStyleSheet(u"background-color: rgba(0,0,0,0);\n"
"border: none;\n"
"color: rgba(32,123,255,255);")
        self.passtext.setEchoMode(QLineEdit.Password)
        self.girisbtn = QPushButton(self.centralwidget)
        self.girisbtn.setObjectName(u"girisbtn")
        self.girisbtn.setGeometry(QRect(340, 360, 271, 31))
        font3 = QFont()
        font3.setFamilies([u"Favela-Medium"])
        font3.setPointSize(14)
        self.girisbtn.setFont(font3)
        self.girisbtn.setStyleSheet(u"background-color: rgba(32,123,255,255);\n"
"border-radius: 12px;\n"
"")
        login.setCentralWidget(self.centralwidget)

        self.retranslateUi(login)

        QMetaObject.connectSlotsByName(login)
    # setupUi

    def retranslateUi(self, login):
        login.setWindowTitle(QCoreApplication.translate("login", u"MainWindow", None))
        self.idtext.setPlaceholderText(QCoreApplication.translate("login", u" ID", None))
        self.passtext.setInputMask("")
        self.passtext.setPlaceholderText(QCoreApplication.translate("login", u" Password", None))
        self.girisbtn.setText(QCoreApplication.translate("login", u"G\u0130R\u0130S", None))
#if QT_CONFIG(shortcut)
        self.girisbtn.setShortcut(QCoreApplication.translate("login", u"Return", None))
#endif // QT_CONFIG(shortcut)
    # retranslateUi

