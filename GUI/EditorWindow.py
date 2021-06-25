import os
import json
from PyQt5.QtWidgets import QMainWindow, QLabel, QAction, QMessageBox, QApplication, QFileDialog, QTextEdit, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, pyqtSlot, QFileInfo
from Model.Data import *
import Utils.Storage as Storage
from GUI.QLabel_Clickable import *
from GUI.EditorWidget import EditorWidget
from GUI.Node.QDM.GraphicsScene import *
from Utils.ErrorMessage import handleError, handleCompileMsg, compileSuccessful, exportSuccessful, importSuccessful
from GUI.Node.Scene.Scene import Scene
from GUI.Node.Node import Node


DEBUG = True


class EditorWindow(QMainWindow):

    # Adding signal
    catCreated = pyqtSignal(Tag)
    catClicked = pyqtSignal(Tag)
    childClicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.filename = None
        self.editSpace = QWidget() # Used for displaying source code
        self.graphview = None # Used for graphing out categories
        self.aiml = AIML()
        self.setCentralWidget(self.editSpace)
        self.initUI()


    def createAct(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act

    def initUI(self):
        menubar = self.menuBar()
        
        # initialize Menu
        fileMenu = menubar.addMenu('&File')
        
        fileMenu.addAction(self.createAct('&Export', 'Ctrl+Shift+E', 'Export File', self.onFileExport))
        fileMenu.addAction(self.createAct('&Import', 'Ctrl+Shift+I', 'Import File', self.onFileImport))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Find', 'Ctrl+F', 'Find Word in File', self.onFind))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('E&xit', 'Ctrl+Q', "Exit application", self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createAct('&Undo', 'Ctrl+Z', "Undo last operation", self.onEditUndo))
        editMenu.addAction(self.createAct('&Redo', 'Ctrl+Shift+Z', "Redo last operation", self.onEditRedo))
        editMenu.addAction(self.createAct('Cu&t', 'Ctrl+X', "Cut to clipboard", self.onEditCut))
        editMenu.addAction(self.createAct('&Copy', 'Ctrl+C', "Copy to clipboard", self.onEditCopy))
        editMenu.addAction(self.createAct('&Paste', 'Ctrl+V', "Paste from clipboard", self.onEditPaste))

        compileMenu = menubar.addMenu('Compile')
        compileMenu.addAction(self.createAct('Compile project', 'Ctrl+Shift+C', 'Compile project to export', self.onCompile))

        themeMenu = menubar.addMenu('Color Theme')
        # themeMenu.addAction(self.createAct('Dark Theme', 'Ctrl+Shift+D', 'Switch Text Editor to Dark Theme', self.switchToDark))
        # themeMenu.addAction(self.createAct('Light Theme', 'Ctrl+Shift+L', 'Switch Text Editor to Light Theme', self.switchToLight))

        self.add_graphview()

        # status bar
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")
        self.statusBar().addPermanentWidget(self.status_mouse_pos)

        # set window properties
        self.setWindowTitle("Program-R AIML Editor")
        self.showMaximized()

        # Setting main editing area where Files will be displayed and can be edited
        # create node editor widget (visualization of categories)
        self.editSpace.graphview.scene.addHasBeenModifiedListener(self.changeTitle)

    # slot function for a category being created and displaying on editSpace
    @pyqtSlot(Tag)
    def categoryCreated(self, cat):
        if DEBUG: print("slot in EditorWindow - categoryCreated()")
        if DEBUG: print(str(cat))
        # emitting signal to send category received from docker to EditorWidget slot
        self.catCreated.emit(cat) 


    @pyqtSlot(Tag)
    def categoryClicked(self, cat):
        if DEBUG: print("slot in EditorWindow - categoryClicked()")
        self.catClicked.emit(cat) # emitting signal to send category to docker to repopulate fields

    def add_graphview(self):
        self.editSpace.layout = QGridLayout(self)

        # Setting of backdrop for view categories as nodes.
        self.editSpace.graphview = EditorWidget(self)

        # Adding widgets to layout
        self.layout = QGridLayout(self)
        self.editSpace.layout.addWidget(self.graphview, 1, 0, 4, 3)

        # Setting layout
        self.editSpace.setLayout(self.editSpace.graphview.layout)

    def create_category_graph_view(self, cat):
        try:
            if cat.type == "topic":
                # Iterate through topic and place categories
                for category in cat.tags:
                    thatToCheck = self.editSpace.graphview.getLastSentence(category)
                    if DEBUG: print("got last sentence of category: {}".format(thatToCheck))
                    title = "Category: " + category.cat_id
                    aNode = Node(self.editSpace.graphview.scene, title, category)
                    aNode.content.wdg_label.displayVisuals(category)

                    if thatToCheck is not None:
                        for that in thatToCheck:
                            self.editSpace.graphview.findChildNodes(aNode, that)
                    
                    # NOTE: Nodes get placed if there are <that> tags otherwise get stacked vertically from default place.
                    self.editSpace.graphview.findParentNodes(aNode)
                    self.editSpace.graphview.placeNodes(self.editSpace.graphview.scene.nodes)

                    for node in self.editSpace.graphview.scene.nodes:
                        node.updateConnectedEdges()

                    # connecting signals coming from Content Widget
                    aNode.content.catClicked.connect(self.editSpace.graphview.categoryClicked)

            elif cat.type == "comment":
                print("Comment found, don't display comments on graphview.")
            else:
                thatToCheck = self.editSpace.graphview.getLastSentence(cat)
                if DEBUG: print("got last sentence of category: {}".format(thatToCheck))
                title = "Category: " + cat.cat_id
                aNode = Node(self.editSpace.graphview.scene, title, cat)
                aNode.content.wdg_label.displayVisuals(cat)

                if thatToCheck is not None:
                    for that in thatToCheck:
                        self.editSpace.graphview.findChildNodes(aNode, that)
                
                # NOTE: Nodes get placed if there are <that> tags otherwise get stacked vertically from default place.
                self.editSpace.graphview.findParentNodes(aNode)
                self.editSpace.graphview.placeNodes(self.editSpace.graphview.scene.nodes)

                for node in self.editSpace.graphview.scene.nodes:
                    node.updateConnectedEdges()

                # connecting signals coming from Content Widget
                aNode.content.catClicked.connect(self.editSpace.graphview.categoryClicked)
                    
        except Exception as ex:
            print("Exception caught in TabController - create_category_graph_view()")
            print(ex)
            handleError(ex)

    def changeTitle(self):
        title = "Node Editor - "
        if self.filename is None:
            title += "New"
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().graphview.scene.has_been_modified:
            title += "*"

        self.setWindowTitle(title)

    # def switchToDark(self):
    #     if DEBUG: print("switching to dark theme")
    #     self.editSpace.tab1.layout.removeWidget(self.editSpace.editSpace)
    #     self.editSpace.editSpace = QCodeEditor(self.editSpace, theme_color='dark')
    #     self.editSpace.tab1.layout.addWidget(self.editSpace.editSpace)
    #     self.editSpace.editSpace.setPlainText(str(self.editSpace.aiml))
    
    # def switchToLight(self):
    #     if DEBUG: print("switching to light theme")
    #     self.editSpace.tab1.layout.removeWidget(self.editSpace.editSpace)
    #     self.editSpace.editSpace = QCodeEditor(self.editSpace, theme_color='light')
    #     self.editSpace.tab1.layout.addWidget(self.editSpace.editSpace)
    #     self.editSpace.editSpace.setPlainText(str(self.editSpace.aiml))

    def closeEvent(self, event):
        if DEBUG: print("closeEvent")
        # if self.maybeSave():
        #     event.accept()
        # else:
        #     event.ignore()

    def isModified(self):
        return self.centralWidget().graphview.scene.has_been_modified

    def maybeSave(self):
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "About to loose your work?",
                "The document has been modified.\n Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
              )

        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False

        return True

    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText("Scene Pos: [%d, %d]" % (x, y))

    def onFind(self):
        if DEBUG: print("Find command called")
        finder = Find(self.editSpace.editSpace)
        finder.show()

    def onFileNew(self):
        self.editSpace.aiml = AIML()
        self.editSpace.clear()
        # if self.maybeSave():
        #     self.centralWidget().scene.clear()
        #     self.filename = None
        #     self.changeTitle()

    def onFileOpen(self):
        try:
            if self.maybeSave():
                fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
                if fname == '':
                    return
                if os.path.isfile(fname):
                    if DEBUG: print("found file")
                    self.filename = os.path.splitext(fname)[0]  # removing extension from path name
                    self.editSpace.graphview.scene.loadFromFile(self.filename)
                    for node in self.editSpace.graphview.scene.nodes:
                        self.editSpace.aiml.append(node.category)
                        node.content.catClicked.connect(self.editSpace.categoryClicked)
                    if DEBUG: print("Opened file successfully")
        except Exception as ex:
            handleError(ex)
            print("Exception caught in onFileOpen!")
            print(ex)

    def onFileSave(self):
        try:
            if self.filename is None: return self.onFileSaveAs()
            self.editSpace.graphview.scene.saveToFile(self.filename)
            # Storage.save(self.filename, self.editSpace.aiml)  # save as a pickle file
            self.statusBar().showMessage("Successfully saved %s" % self.filename)
            return True
        except Exception as ex:
            print("Exception caught trying to save to file")
            print(ex)
            handleError(ex)

    def onFileExport(self):
        # Check for uncompiled changes
        retval = None
        if self.editSpace.up_to_date is False:
            if DEBUG: print("Code is not compiled. Compile before export.")
            retval = handleCompileMsg()

        if retval == QMessageBox.Cancel:
            return
        
        if retval == QMessageBox.Yes:
            if DEBUG: print('Compiling code before exporting')
            try:
                self.onCompile()
            except Exception as ex:
                print('Couldn\'t compile before exporting')
                return
        try:
            fname, filter = QFileDialog.getSaveFileName(self, 'Export to file')
            if fname == "":
                if DEBUG: print("Cancel clicked")
                return
            Storage.exportAIML(fname, self.editSpace.aiml) # save as an aiml file

            # Display Dialog
            exportSuccessful()
        except Exception as ex:
            print("Exception caught trying to export")
            print(ex)
            handleError(ex)

    def onFileImport(self):
        try:
            fname, filter = QFileDialog.getOpenFileName(self, "Import File")

            if fname == "":
                if DEBUG: print("Cancel was clicked")
                return
                
            yoffset = -4000
            if DEBUG: print("fname: " + fname)
            self.filename = os.path.splitext(fname)[0]  # removing extension from path name
            aiml = Storage.importAIML(self.filename) # import the aiml file
            numCats = 0
            topics = []

            # Adding all categories to the scene
            for cat in aiml.tags:
                self.create_category_graph_view(cat)
                numCats = numCats + 1

            # # Add any categories inside topics to the scene
            for cat in topics:
                self.create_category_graph_view(cat)
                numCats = numCats + 1

            if DEBUG: print("Finished creating " + str(numCats) + " categories")
            if DEBUG: print("file import successful")
            importSuccessful()
        except Exception as ex:
            handleError(ex)
            print(ex)

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')
        if fname == '':
            return False
        self.filename = fname
        # Storage.save(self.filename, self.editSpace.scene)  # save as a pickle file
        self.onFileSave()
        return True

    def onEditUndo(self):
        self.centralWidget().graphview.scene.history.undo()

    def onEditRedo(self):
        self.centralWidget().graphview.scene.history.redo()

    def onEditDelete(self):
        self.centralWidget().graphview.scene.grScene.views()[0].deleteSelected()

    def onEditAdd(self):
        widget = self.centralWidget().graphview
        assert isinstance(widget, EditorWidget)
        widget.addNode("new", [0], [0], 0, 0)

    def onEditCut(self):
        data = self.centralWidget().graphview.scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        data = self.centralWidget().graphview.scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        raw_data = QApplication.instance().clipboard().text()

        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting of not valid json data!", e)
            return

        # check if the json data is correct
        if 'nodes' not in data:
            if DEBUG: print("JSON does not contain any nodes!")
            return

        self.centralWidget().graphview.scene.clipboard.deserializeFromClipboard(data)

    def onCompile(self):
        if DEBUG: print("Compile Pressed!!!")
        try:
            if DEBUG: print("Clearing scene")
            self.editSpace.graphview.scene.clear()
            self.editSpace.graphview.scene.grScene.clear()

            # Display dialog
            compileSuccessful()
        except Exception as ex:
            print("Exception caught trying to compile project")
            print(ex)
            handleError(ex)