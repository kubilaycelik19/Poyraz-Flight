from PyQt5.QtWidgets import QApplication
from login import loginPage

app = QApplication([])
loginPencere = loginPage()
loginPencere.show()
app.processEvents()
app.exec_()
