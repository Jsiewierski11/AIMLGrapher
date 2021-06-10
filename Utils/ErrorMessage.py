from PyQt5.QtWidgets import QErrorMessage
from PyQt5.QtWidgets import QMessageBox


def handleError(error):
    em = QErrorMessage.qtHandler()
    em.showMessage(str(error))

def handleCompileMsg():
    msg_box = QMessageBox(QMessageBox.Warning, 'Compile Code!', 'There are changes to your code that have not been compiled.\
    If you do not compile your code before exporting you will lose those changes. Would you like to compile before you export?')

    msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.No | QMessageBox.Yes)
    
    retval = msg_box.exec_()
    return retval

def compileSuccessful():
    msg_box = QMessageBox()
    msg_box.setText("Compile Succesful!")
    msg_box.exec_()

def exportSuccessful():
    msg_box = QMessageBox()
    msg_box.setText("Export Succesful!")
    msg_box.exec_()

def importSuccessful():
    msg_box = QMessageBox()
    msg_box.setText("Import Succesful!")
    msg_box.exec_()