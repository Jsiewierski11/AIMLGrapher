from collections import OrderedDict
from GUI.Node.Utils.Serializable import Serializable
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal, Qt, pyqtBoundSignal
from GUI.QLabel_Clickable import *
from Model.Data import *
from GUI.Node.Node import *
from PyQt5 import QtCore
from Utils.ErrorMessage import handleError

DEBUG = False


class QDMNodeContentWidget(QWidget, Serializable):

    catClicked = pyqtSignal(Tag)
    childClicked = pyqtSignal(Tag)

    def __init__(self, node, parent=None):
        self.node = node
        self.wdg_label = LabelClickable()
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        try:
            self.layout = QVBoxLayout()
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(self.layout)

            self.layout.addWidget(self.wdg_label)
            
            # Setting connections for when a node is clicked
            self.wdg_label.templateLabel.catClicked.connect(self.categoryClicked)
            self.wdg_label.patternLabel.catClicked.connect(self.categoryClicked)
            self.wdg_label.thatLabel.catClicked.connect(self.categoryClicked)
        except Exception as ex:
            print("Exception caught in ContentWidget - initUI()")
            print(ex)
            handleError(ex)

    def setEditingFlag(self, value):
        try:
            self.node.scene.grScene.views()[0].editingFlag = value
        except Exception as ex:
            print("Exception caught in ContentWidget - seEditingFlag()")
            print(ex)
            handleError(ex)

    def serialize(self):
        return OrderedDict([

        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        return False

    @pyqtSlot()
    def categoryClicked(self):
        if DEBUG: print("slot in ContentWidget - categoryClicked()")
        if DEBUG: print(self.node.category)
        try:
            if self.node.category.cat_id == "":
                if DEBUG: print("id is empty string")
                cat_id = QUuid()
                cat_id = cat_id.createUuid()
                cat_id = cat_id.toString()
                self.node.category.cat_id = cat_id
                if DEBUG: print(self.node.category.cat_id)
                try:
                    self.catClicked.emit(self.node.category) # emitting signal up to Editor Widget
                    if DEBUG: print("signal emitted")
                except Exception as ex:
                    print("Exception caught in ContentWidget - categoryClicked()")
                    print(ex)
            else:
                if DEBUG: print("id exists")
                if DEBUG: print(self.node.category.cat_id)
                try:
                    self.catClicked.emit(self.node.category) # emitting signal up to Editor Widget
                    if DEBUG: print("signal emitted")
                except Exception as ex:
                    print("Exception caught in ContentWidget - categoryClicked()")
                    print(ex)
        except Exception as ex:
            print("Exception caught in ContentWidget - categoryClicked()")
            print(ex)
            handleError(ex)

class QDMTextEdit(QTextEdit):
    def __init__(self, input):
        try:
            super().__init__(input)
            # self.setGeometry(QtCore.QRect(90, 30, 291, 21))
        except Exception as ex:
            print("Exception caught in ContentWidget - QDMTextEdit __init__()")
            print(ex)
            handleError(ex)

    def focusInEvent(self, event):
        if DEBUG: print("in focusInEvent()")
        try:
            self.parentWidget().setEditingFlag(True)
            super().focusInEvent(event)
        except Exception as ex:
            print("Exception caught in ContentWidget - focusInEvent()")
            print(ex)
            handleError(ex)

    def focusOutEvent(self, event):
        if DEBUG: print("in focusOutEvent()")
        try:
            self.parentWidget().setEditingFlag(False)
            super().focusOutEvent(event)
        except Exception as ex:
            print("Exception caught in ContentWidget - focusOutEvent()")
            print(ex)
            handleError(ex)