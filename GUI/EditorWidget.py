from PyQt5.QtWidgets import QWidget, QTextEdit, QGraphicsItem,\
    QApplication, QVBoxLayout, QPushButton, QBoxLayout, QMainWindow
from PyQt5.QtGui import QBrush, QPen, QFont, QColor
from PyQt5.QtCore import QFile, Qt, pyqtSlot, pyqtSignal
from Utils.ErrorMessage import *
from Model.Data import *
from GUI.QLabel_Clickable import *
from GUI.Node.Node import Node
from GUI.Node.Scene.Scene import Scene
from GUI.Node.Edge import Edge, EDGE_TYPE_BEZIER
from GUI.Node.QDM.GraphicsView import QDMGraphicsView
from GUI.Node.QDM.GraphicsNode import *
from GUI.Node.Utils.Socket import *

DEBUG = True


class EditorWidget(QWidget):

    # Adding signal
    catCreated = pyqtSignal(Tag)
    catClicked = pyqtSignal(Tag)
    childClicked = pyqtSignal(str)

    def __init__(self, window, parent=None):
        try:
            super().__init__(parent)
            self.stylesheet_filename = 'GUI/style/nodestyle.qss'
            self.loadStylesheet(self.stylesheet_filename)
            self.responseTable = None
            self.initUI(window)
        except Exception as ex:
            print("Exception caught in EditorWidget - __init__()")
            print(ex)
            handleError(ex)

    def initUI(self, window):
        try:
            self.layout = QBoxLayout(QBoxLayout.LeftToRight)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(self.layout)

            # crate graphics scene
            self.scene = Scene()
            self.grScene = self.scene.grScene

            # create graphics view
            self.view = QDMGraphicsView(self.scene.grScene, self)
            self.layout.addWidget(self.view)
        except Exception as ex:
            print("Exception caught in EditorWidget - initUI()")
            print(ex)
            handleError(ex)

    def addNode(self, title, inputs, outputs, posx, posy):
        try:
            print("Adding node")
            node1 = Node(self.scene, title=title, inputs=inputs, outputs=outputs)
            node1.setPos(posx, posy)
        except Exception as ex:
            print("Exception caught in EditorWidget - addNode()")
            print(ex)
            handleError(ex)

    def updateNode(self, cat):
        try:
            if DEBUG: print("updating node in display")
            for node in self.scene.nodes:
                if node.category.cat_id == cat.cat_id:
                    if DEBUG: print("found node to update")
                    node.category = cat
                    if DEBUG: print(str(node.category))
                    
                    # Displaying updated content on node.
                    node.content.wdg_label.clear()
                    node.content.wdg_label.displayVisuals(cat)
        except Exception as ex:
            print("EXCEPTION CAUGHT! In EditorWidget - updateNode()")
            print(ex)
            handleError(ex)

    def addDebugContent(self):
        try:
            greenBrush = QBrush(Qt.green)
            outlinePen = QPen(Qt.black)
            outlinePen.setWidth(2)

            rect = self.grScene.addRect(-100, -100, 80,
                                        100, outlinePen, greenBrush)
            rect.setFlag(QGraphicsItem.ItemIsMovable)

            text = self.grScene.addText(
                "This is my Awesome text!", QFont("Ubuntu"))
            text.setFlag(QGraphicsItem.ItemIsSelectable)
            text.setFlag(QGraphicsItem.ItemIsMovable)
            text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))

            widget1 = QPushButton("Hello World")
            proxy1 = self.grScene.addWidget(widget1)
            proxy1.setFlag(QGraphicsItem.ItemIsMovable)
            proxy1.setPos(0, 30)

            widget2 = QTextEdit()
            proxy2 = self.grScene.addWidget(widget2)
            proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
            proxy2.setPos(0, 60)

            line = self.grScene.addLine(-200, -200, 400, -100, outlinePen)
            line.setFlag(QGraphicsItem.ItemIsMovable)
            line.setFlag(QGraphicsItem.ItemIsSelectable)
        except Exception as ex:
            print("Exception caught in EditorWidget - addDebugContent()")
            print(ex)
            handleError(ex)

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


    """
    Determine if the condition or random table has text afterwards.
    """
    def tableContainsTail(self, template):
        try:
            for tag in reversed(template.tags):
                if DEBUG: print("Beginning of loop")
                if DEBUG: print(f"Current tag: {tag}")

                if isinstance(tag, str) is True:
                    if DEBUG: print("String found before Condition or Random. Return True.")
                    return True, tag
                # Check for <oob> tag
                elif tag.type == "oob":
                    if DEBUG: print("oob found, keep searching.")
                elif tag.type == "condition" or tag.type == "random":
                    if DEBUG: print("Condition or Random found before String. Return False.")
                    return False, None
            # Made it to end without finding anything
            if DEBUG: print("Made it to end without finding anything. This should not happen!")
            return False, None
        except Exception as ex:
            print("Exception caught in EditorWidget - tableContainsTail()")
            print(ex)
            handleError(ex)

    """
    Determine if the set tag has text afterwards.
    """
    def setContainsTail(self, template):
        try:
            print("In setContainsTail()")
            for index, tag in enumerate(reversed(template.tags)):
                if index == 0:
                    if tag.type == "set":
                        return False
                    else:
                        return True
        except Exception as ex:
            print("Exception caught in EditorWidget - setContainsTail()")
            print(ex)
            handleError(ex)


    """
    Function to find the sentence to be used for <that> tag of potential children.
    Returns a list of strings of last sentences in the <template> tag.
    Sentences will only contain more than 1 element if there is a <random> or
    <condition> tag. Sentences will then have a string for each <li> tag.
    """
    def getLastSentence(self, cat):
        if DEBUG: print("In getLastSentence()")
        try:
            template = cat.findTag("template")
            sentences = []

            # Check for empty template
            if template is None:
                if DEBUG: print("Template is empty")
                return None

            # Check for condition or random blocks
            condition = template.findTag("condition")
            random = template.findTag("random")
            if condition is None and random is None:
                if DEBUG: print("no random or condition tag found in template")
                # if DEBUG: print(str(template))

                tempString = template.findTag("text")
                if DEBUG: print(f"tempString: {tempString}")

                # Check for empty template string
                if tempString is None:
                    if DEBUG: print("No sentence in category")
                    return None

                set_tag = template.findTag("set")
                if set_tag is not None:
                    sentences.append(set_tag.findTag("text"))

                sentences = self.findPunctuation(tempString, sentences)

                # If we made it to end of array without finding another punctiation mark, return full text in template.
                if len(sentences) is 0:
                    if DEBUG: print(f"appending: {tempString}")
                    sentences.append(tempString)
                return sentences
            else:
                if DEBUG: print("template contains either a random or condition tag")
                # if DEBUG: print(str(template))

                contains_tail, tail = self.tableContainsTail(template)
                if contains_tail is True:
                    sentences.append(tail)
                    return sentences
                else:
                    if DEBUG: print("Random or Condition tag is the last thing in the template")
                    if condition is not None:
                        if DEBUG: print("table contains condition table")
                        for li in condition.tags:
                            liText = li.findTag("text")
                            if DEBUG: print("text inside condition: " + liText)

                            # Checking for set tag
                            set_tag = li.findTag("set")
                            setHasTail = True
                            if set_tag is not None:
                                print("Found set tag in condition block")
                                setHasTail = self.setContainsTail(li)
                                if not setHasTail:
                                    print("Set tag is last sentence, appending: {}".format(set_tag.findTag("text")))
                                    sentences.append(set_tag.findTag("text"))
                            else:
                                setHasTail = False
                                
                            punctuationExists = False
                            sentences = self.findPunctuation(liText, sentences)
                                    
                            # If made it to end of array without finding another punctiation mark. return full text in tag
                            if punctuationExists is False and setHasTail is True:
                                sentences.append(liText)
                        return sentences
                    else:
                        if DEBUG: print("table contains random table")
                        for li in random.tags:
                            liText = li.findTag("text")
                            if DEBUG: print("text inside random: " + liText)

                            # Checking for set tag
                            set_tag = li.findTag("set")
                            setHasTail = True
                            if set_tag is not None:
                                print("Found set tag in random block")
                                setHasTail = self.setContainsTail(li)
                                if not setHasTail:
                                    print("Set tag is last sentence, appending: {}".format(set_tag.findTag("text")))
                                    sentences.append(set_tag.findTag("text"))
                            else:
                                setHasTail = False

                            punctuationExists = False
                            sentences = self.findPunctuation(liText, sentences)

                            # If at the end of array without finding another punctiation mark. return full text in tag
                            if punctuationExists is False and setHasTail is True:
                                if DEBUG: print(f"appending: {liText}")
                                sentences.append(liText)
                        return sentences
        except Exception as ex:
            print("Exception caught in EditorWidget - getLastSentence()")
            print(ex)
            # handleError(ex)
            return sentences


    """
    Helper function for findLastSentence that finds where the last punctuation is.
    """
    def findPunctuation(self, tempString, sentences):
        tempArr = tempString.split()
        index = 0
        for word in reversed(tempArr):
            if "." in word or "?" in word or "!" in word:
                if index == 0:
                    if DEBUG: print("Found last punctuation mark on very first word: \"{}\". Keep searching.".format(word))
                else:
                    if DEBUG: print("Found the start of the last sentence: \"{}\"".format(word))
                    arrSize = len(tempArr)
                    start = arrSize - (index)
                    lastSentence = tempArr[start:arrSize]
                    lastSentence = " ".join(lastSentence)
                    # if DEBUG: print(f"appending: {lastSentence}")
                    sentences.append(lastSentence)
            index = index + 1

        return sentences

    """
    Find child nodes in the scene and add edges based off of <that> tags
    """
    def findChildNodes(self, newnode, thatStr):
        try:
            if DEBUG: print("looking for child nodes")
            xOffset = 0
            for node in self.scene.nodes:
                thatTag = node.category.findTag("that")
                if DEBUG: print(f"Current Category:\n{node.category}")
                if DEBUG: print(f"that: {str(thatTag)}")
                if newnode == node:
                    if DEBUG: print("looking at node just created. Do nothing")
                elif thatTag is None:
                    if DEBUG: print("no that tag found in category: " + str(node.category))
                else:
                    # That tag was found, add an edge
                    if DEBUG: print("that tag was found in category: " + str(node.category))
                    thatText = thatTag.findTag("text")
                    if DEBUG: print(f"Return type of findTag(\"text\"): {type(thatText)}")
                    if DEBUG: print(f"{thatText}")
                    if DEBUG: print(f"Data type of parameter thatStr: {type(thatStr)}")
                    if DEBUG: print(f"{thatStr}")
                    if thatText.lower() == thatStr.lower():
                        if DEBUG: print("FOUND CHILD!")
                        self.updateChildSockets(newnode, node)
                    else:
                        if DEBUG: print("Not a match for a child")

            if DEBUG: print("No child found in scene")
        except Exception as ex:
            print("Exception caught in EditorWidget when looking for child nodes")
            print(ex)
            handleError(ex)


    """
    Find parent nodes in the scene and add edges based off of <that> tags.
    """
    def findParentNodes(self, newnode):
        try:
            if DEBUG: print("looking for parent nodes")
            mythatTag = newnode.category.findTag("that")
            if mythatTag is None:
                if DEBUG: print("no that tag so node will not have any parents")
                return
            thatText = mythatTag.findTag("text")
            if DEBUG: print("Text of That Tag to look for: " + thatText)
            xOffset = 0
            for node in self.scene.nodes:
                if node == newnode:
                    if DEBUG: print("looking at node just created, do nothing")
                else:
                    if DEBUG: print("looking at node with category: " + str(node.category))
                    self.updateParentSockets(newnode, node, thatText)
        except Exception as ex:
            print("Exception caught in EditorWidget - findParentNodes()")
            print(ex)
            handleError(ex)

    
    """
    Function to update the edges connecting to child nodes.
    """
    def updateChildSockets(self, newnode, node):
        try:
            parentsocket = Socket(newnode, position=RIGHT_BOTTOM, socket_type=2)
            newnode.inputs.append(parentsocket) # outputs is children

            if node not in newnode.children:
                newnode.children.append(node)

            childsocket = Socket(node)
            node.outputs.append(childsocket)

            if newnode not in node.parents:
                node.parents.append(newnode)

            edge = Edge(self.scene, parentsocket, childsocket)
            
            return edge
        except Exception as ex:
            print("Exception caught in EditorWidget - updateChildSockets()")
            print(ex)
            handleError(ex)


    """
    Function to update the edges connecting to parent nodes.
    """
    def updateParentSockets(self, newnode, node, thatText):
        try:
            templateText = self.getLastSentence(node.category)
            for text in templateText:
                if thatText.lower() == text.lower():
                    if DEBUG: print("Found parent node!")
                    parentsocket = Socket(node, position=RIGHT_BOTTOM, socket_type=2)
                    node.inputs.append(parentsocket)

                    # need to check if node exists in list before appending
                    if newnode not in node.children:
                        node.children.append(newnode)

                    childsocket = Socket(newnode)
                    newnode.outputs.append(childsocket)

                    if node not in newnode.parents:
                        newnode.parents.append(node)

                    edge = Edge(self.scene, parentsocket, childsocket)
                else:
                    if DEBUG: print("Not a match for a parent")
        except Exception as ex:
            print("Exception caught in EditorWidget - updateParentSockets()")
            print(ex)
            handleError(ex)
  

    """
    Function to organize nodes based on parents and children
    """
    def placeNodes(self, nodes, depth=0, xOffset=0, yOffset=0):
        # TODO: Recursively look through children. Place parents on top, children below.
        try:
            if DEBUG: print("placing nodes")
            if depth > 15:
                if DEBUG: print("reached max depth")
                return

            parentXOffset = 0
            
            for i, node in enumerate(nodes):
                if len(node.parents) is 0 and len(node.children) is 0:
                    if DEBUG: print("Node has no parents or children (Root level node)")
                    if DEBUG: print(f"Placing category:\n{node.category}")
                    node.setPos(parentXOffset, 0)
                    # parentXOffset = (abs(parentXOffset) + 425)
                    if i % 2 == 0: 
                        parentXOffset = parentXOffset * -1
                    else:
                        # parentXOffset = (abs(parentXOffset) + 425)
                        parentXOffset = node.grNode.x() + 425

                if len(node.parents) is 0 and len(node.children) > 0:
                    if DEBUG: print("Node has no parents, only children (Root level node)")
                    if DEBUG: print(f"Placing category:\n{node.category}")
                    node.setPos(parentXOffset, 0 + (300*(depth)))

                    if i % 2 == 0: 
                        parentXOffset = parentXOffset * -1
                    else:
                        parentXOffset = node.grNode.x() + 425
                else:
                    if DEBUG: print("Node has parents and children")
                    yOffset = 0
                    for child in node.children:
                        depth = depth + 1
                        y = node.grNode.y()
                        child.setPos(xOffset, y + (300*(depth)))
                        
                        if DEBUG: print(f"Placing category:\n{node.category}")
                        self.placeNodes(child.children, depth)
                    
                    if i % 2 == 0: 
                        parentXOffset = parentXOffset * -1
                    else:
                        parentXOffset = node.grNode.x() + 425
                    
                    # Setting position for first child node
                    y = node.grNode.y()
                    node.setPos(parentXOffset, y + (100 * ((depth*.02)+1)))
                
        except Exception as ex:
            print("Exception caught placing nodes!")
            print(ex)
            handleError(ex)

    def setNodeStyleSheet(self, node):
        node.content.setStyleSheet(self.stylesheet_filename)
        return node

    @pyqtSlot(Tag)
    def categoryClicked(self, cat):
        if DEBUG: print("slot in EditorWidget - categoryClicked()")
        
        # Resetting all nodes to original style sheet
        self.scene.nodes = list(map(self.setNodeStyleSheet, self.scene.nodes))
        
        try:
            # FIXME: Optimize by maybe storing parent and children nodes in something other than lists, maybe an unordered set?
            for node in self.scene.nodes:
                if DEBUG: print("Searching for correct node")
                if node.category.cat_id == cat.cat_id:
                    node.content.setStyleSheet("QDMNodeContentWidget { background: #ffff1a; }")
                    for child in node.children:
                        if DEBUG: print("Changing background of child")
                        child.content.setStyleSheet("QDMNodeContentWidget { background: #f82f04; }")

                    for parent in node.parents:
                        if DEBUG: print("Changing background of parent")
                        parent.content.setStyleSheet("QDMNodeContentWidget { background: #0cfdd8; }")
        except Exception as ex:
            print("Exception caught when category is clicked.")
            print(ex)
            handleError(ex)