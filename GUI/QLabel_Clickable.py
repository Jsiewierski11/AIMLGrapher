from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QMessageBox, QScrollArea, QVBoxLayout, QWidget
import xml.etree.ElementTree as ET
from Model.Data import *
from Utils.ErrorMessage import *


class QLabelClickable(QLabel):

    # initializing signal for click or double click events
    catClicked = pyqtSignal()

    def __init__(self, parent=None):
        super(QLabelClickable, self).__init__(parent)
        self.labelFont = QFont("Sanserif", 13)
        self.setFont(self.labelFont)

        self.setAlignment(Qt.AlignTop)

    def mousePressEvent(self, event):
        self.last = "Click"

    def mouseReleaseEvent(self, even):
        if self.last == "Click":
            QTimer.singleShot(QApplication.instance().doubleClickInterval(), self.performSingleClickAction)
        else:
            # emmits to Editor Widget categoryClicked()
            print("mouseReleaseEvent() - label clicked")
            self.catClicked.emit()

    def mouseDoubleClickEvent(self, event):
        self.last = "Double Click"

    def performSingleClickAction(self):
        if self.last == "Click":
            # emmits to Editor Widget categoryClicked()
            print("performSingleClickAction() - label clicked")
            self.catClicked.emit()


class LabelClickable(QWidget):
    def __init__(self, parent=None):
        super(LabelClickable, self).__init__(parent)

        self.setWindowTitle("Category")
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(350, 450)

        self.templateText = ""
        self.patternText = ""

        self.initUI()

    def initUI(self):
        self.patternLabel = QLabelClickable(self)
        self.patternLabel.setWordWrap(True)
        self.patternLabel.setGeometry(0, 0, 350, 50)
        self.patternLabel.setCursor(Qt.PointingHandCursor)
        self.patternLabel.setStyleSheet("QLabel {background-color: black; color: white; border: 1px solid "
                                         "#01DFD7; border-radius: 5px;}")

        self.thatLabel = QLabelClickable(self)
        self.thatLabel.setWordWrap(True)
        self.thatLabel.setGeometry(0, 60, 350, 50)
        self.thatLabel.setCursor(Qt.PointingHandCursor)
        self.thatLabel.setStyleSheet("QLabel {background-color: black; color: white; border: 1px solid "
                                         "#01DFD7; border-radius: 5px;}")

        self.templateLabel = QLabelClickable(self)
        self.templateLabel.setWordWrap(True)
        self.templateLabel.setGeometry(0, 120, 350, 270)
        self.templateLabel.setToolTip("Edit category")
        self.templateLabel.setCursor(Qt.PointingHandCursor)
        self.templateLabel.setStyleSheet("QLabel {background-color: black; color: white; border: 1px solid "
                                         "#01DFD7; border-radius: 5px;}")

        # Making labels scrollable
        layout = QVBoxLayout()
        templateArea = QScrollArea()
        templateArea.setMaximumSize(350, 270)
        templateArea.setWidget(self.templateLabel)

        layout.addWidget(self.patternLabel)
        layout.addWidget(self.thatLabel)
        layout.addWidget(templateArea)

        self.setLayout(layout)

    def displayVisuals(self, category):
        try:
            self.clear()
            template = category.findTag("template")
            pattern = category.findTag("pattern")
            that = category.findTag("that")

            # adding text to appropriate fields
            self.patternLabel.setText(pattern.getContents())
            if that is not None:
                self.thatLabel.setText(that.getContents())
            self.templateLabel.setText(template.getContents())

            # making sure tags don't have unnecessary attributes
            category.attrib = []
        except Exception as ex:
            print("exception caught in display visuals!")
            print(ex)
            handleError(ex)

    def clear(self):
        self.templateLabel.clear()
        self.patternLabel.clear()
        self.thatLabel.clear()
