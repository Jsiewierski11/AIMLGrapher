from PyQt5.QtWidgets import QLabel, QDockWidget, QTextEdit, \
                            QGridLayout, QLineEdit, QWidget, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSlot

from Utils.ErrorMessage import *

DEBUG = False


class Toolbar(QDockWidget):

    # Adding signal
    # catClicked = pyqtSignal(Tag)

    def __init__(self, window=None, parent=None, scene=None):
        super().__init__(parent)
        self.scene = scene
        self.stylesheet_filename = 'GUI/style/nodestyle.qss'
        self.loadStylesheet(self.stylesheet_filename)

        self.create_buttons()
        self.init_items()


    def create_buttons(self):
        # Creating unhighlight button to deselect clicked nodes
        self.unhighlight = QPushButton("Un-highlight")
        self.unhighlight.clicked.connect(self.unhighlight_clicked)

    def init_items(self):
        # Disabling close button
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)

        # initializing content inside widget
        self.setWindowTitle("Tool Bar")

        # Create Widget that contains fields, it get's added to dockable widget
        widgetToDock = QWidget()
        self.setWidget(widgetToDock)

        # formatting content in widget
        widgetToDock.setLayout(QGridLayout())
        widgetToDock.layout().addWidget(self.unhighlight, 1, 0)


    def unhighlight_clicked(self):
        # TODO: Have this function reset the scene. Below is code used in editor widget to reset all the nodes.
        """
        # Resetting all nodes to original style sheet
        self.scene.nodes = list(map(self.setNodeStyleSheet, self.scene.nodes))
        """
        print("HERE!")
        # Resetting all nodes to original style sheet
        self.scene.nodes = list(map(self.setNodeStyleSheet, self.scene.nodes))

    def setNodeStyleSheet(self, node):
        node.content.setStyleSheet(self.stylesheet_filename)
        return node

    def loadStylesheet(self, filename):
        try:
            if DEBUG: print('STYLE loading:', filename)
            file = QFile(filename)
            file.open(QFile.ReadOnly | QFile.Text)
            stylesheet = file.readAll()
            QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
        except Exception as ex:
            print("Exception caught in EditorWidget - loadStylesheet()")
            print(ex)
            handleError(ex)
