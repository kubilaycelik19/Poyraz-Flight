import sys
from PyQt5.QtWidgets import *
from login_python import Ui_login
from HomePage import hpPage


class loginPage(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.loginForm = Ui_login() 
        self.loginForm.setupUi(self)
        self.homeAc = hpPage()
        self.loginForm.girisbtn.clicked.connect(self.girisYap)
        
        
          
        
    def girisYap(self):
        # """id = self.loginForm.idtext.text()
        # self.homeAc.homeForm.idLabel.setText(id)"""
        # password = self.loginForm.passtext.text()
        # sifre = "poyraz"
        # if password != sifre:
        #     uyari = QMessageBox
        #     uyari.about(self,"HATA","HATALİ GİRİS")
        # elif password == sifre:   
        self.close()
        self.homeAc.showMaximized()
        self.homeAc.show()
        
            
        