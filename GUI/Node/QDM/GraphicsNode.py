from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from Model.Data import *
from Utils.ErrorMessage import handleError

DEBUG = False

class QDMGraphicsNode(QGraphicsItem):

    handleBottomRight = 8

    handleSize = +8.0
    handleSpace = -4.0

    handleCursors = {
        handleBottomRight: Qt.SizeFDiagCursor
    }

    def __init__(self, node, parent=None):
        try:
            super().__init__(parent)
            self.node = node
            self.content = self.node.content

            self._title_color = Qt.green
            self._title_font = QFont("Ubuntu", 10)

            self.rect = QRectF(
                0,
                0,
                430,
                540
            )
            self.edge_size = 10.0
            self.title_height = 35.0
            self._padding = 4.0

            self._pen_default = QPen(QColor("#7F000000"))
            self._pen_selected = QPen(QColor("#FFFFA637"))

            self._brush_title = QBrush(QColor("#FF313131"))
            self._brush_background = QBrush(QColor("#E3212121"))

            # init title
            self.initTitle()
            self.title = self.node.title

            # init sockets
            self.initSockets()

            # init content
            self.initContent()

            self.initUI()
            self.wasMoved = False

            self.handles = {}
            self.handleSelected = None
            self.mousePressPos = None
            self.mousePressRect = None
            self.handle = QRectF(self.rect.right() - self.handleSize,
                                self.rect.bottom() - self.handleSize, self.handleSize, self.handleSize)
        except Exception as ex:
            print("Exception caught in GraphicsNode - __init__()")
            print(ex)
            handleError(ex)

    def boundingRect(self):
        if DEBUG: print("In GraphicsNode - boundingRect()")
        try:
            if DEBUG: print(f"\t> GraphicsNode - self.rect: {self.rect}")
            if DEBUG: print(f"\t> Category ID: {self.node.category.cat_id}")
            return self.rect
        except Exception as ex:
            print("Exception caught in GraphicsNode - boundingRect()")
            print(ex)
            handleError(ex)

    def hoverMoveEvent(self, moveEvent):
        try:
            """
            Executed when the mouse moves over the shape (NOT PRESSED).
            """
            if self.isSelected():
                handle = None
                if self.handle.contains(moveEvent.pos()):
                    handle = "k"  # something not None
                cursor = Qt.ArrowCursor if handle is None else Qt.SizeFDiagCursor
                self.setCursor(cursor)
            super().hoverMoveEvent(moveEvent)
        except Exception as ex:
            print("Exception caught in GraphicsNode - hoverMouseEvent")
            print(ex)
            handleError(ex)

    def hoverLeaveEvent(self, moveEvent):
        try:
            """
            Executed when the mouse leaves the shape (NOT PRESSED).
            """
            self.setCursor(Qt.ArrowCursor)
            super().hoverLeaveEvent(moveEvent)
        except Exception as ex:
            print("Exception caught in GraphicsNode - hoverLeaveEvent()")
            print(ex)
            handleError(ex)

    def mousePressEvent(self, mouseEvent):
        try:
            """
            Executed when the mouse is pressed on the item.
            """
            if DEBUG: print("\nMOUSE PRESS ON NODE\n")

            if self.handle.contains(mouseEvent.pos()):
                self.handleSelected = "Bottom Right"
            if self.handleSelected:
                self.mousePressPos = mouseEvent.pos()
                self.mousePressRect = self.rect
            super().mousePressEvent(mouseEvent)
        except Exception as ex:
            print("Exception caught in GraphicsNode - mousePressEvent()")
            print(ex)
            handleError(ex)

    def mouseMoveEvent(self, event):
        try:
            if DEBUG: print("MOVING NODE!!")
            # optimize me! just update the selected nodes
            for node in self.scene().scene.nodes:
                if node.grNode.isSelected():
                    node.updateConnectedEdges()
            self.wasMoved = True

            if self.handleSelected is not None:
                self.interactiveResize(event.pos())
            else:
                super().mouseMoveEvent(event)
        except Exception as ex:
            print("Exception caught in GraphicsNode - mouseMoveEvent()")
            print(ex)
            handleError(ex)

    def mouseReleaseEvent(self, event):
        if DEBUG: print("\nMOUSE RELEASED\n")
        try:
            super().mouseReleaseEvent(event)

            if self.wasMoved:
                self.wasMoved = False
                self.node.scene.history.storeHistory(
                    "Node moved", setModified=True)

            self.handleSelected = None
            self.mousePressPos = None
            self.mousePressRect = None
            self.update()
        except Exception as ex:
            print("Exception caught in GraphicsNode - mouseReleaseEvent()")
            print(ex)

    @property
    def title(self): 
        try:
            return self._title
        except Exception as ex:
            print("Exception caught in GraphicsNode - title() @property")
            print(ex)
            handleError(ex)

    @title.setter
    def title(self, value):
        try:
            self._title = value
            self.title_item.setPlainText(self._title)
        except Exception as ex:
            print("Exception caught in GraphicsNode - title() @setter")
            print(ex)
            handleError(ex)

    @property
    def width(self): 
        try:
            return self.rect.width()
        except Exception as ex:
            print("Exception caught in GraphicsNode - width() @property")
            print(ex)
            handleError(ex)

    @width.setter
    def width(self, value):
        try:
            self.rect.setWidth(value)
        except Exception as ex:
            print("Exception caught in GraphicsNode - width() @setter")
            print(ex)
            handleError(ex)

    @property
    def height(self): 
        try:
            return self.rect.height()
        except Exception as ex:
            print("Exception caught in GraphicsNode - height() @property")
            print(ex)
            handleError(ex)

    @height.setter
    def height(self, value):
        try:
            self.rect.setheight(value)
        except Exception as ex:
            print("Exception caught in GraphicsNode - height() @setter")
            print(ex)
            handleError(ex)

    def initUI(self):
        try:
            self.setFlag(QGraphicsItem.ItemIsSelectable)
            self.setFlag(QGraphicsItem.ItemIsMovable)
            self.setAcceptHoverEvents(True)
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        except Exception as ex:
            print("Exception caught in GraphicsNode - initUI()")
            print(ex)
            handleError(ex)

    def interactiveResize(self, mousePos):
        try:
            """
            Perform shape interactive resize.
            """
            rect = QRectF(self.rect)
            self.prepareGeometryChange()
            if self.handleSelected:
                fromX = self.mousePressRect.right()
                fromY = self.mousePressRect.bottom()
                toX = fromX + mousePos.x() - self.mousePressPos.x()
                toY = fromY + mousePos.y() - self.mousePressPos.y()
                rect.setRight(toX)
                rect.setBottom(toY)
                self.rect = rect
                self.setContentGeo()
                self.node.updateSocketPos()
                # self.setRect(self.rect)

            self.handle = QRectF(self.rect.right() - self.handleSize,
                                self.rect.bottom() - self.handleSize, self.handleSize, self.handleSize)
        except:
            print("Exception caught in GraphicsNode - interactiveResize()")
            print(ex)
            handleError(ex)

    def initTitle(self):
        try:
            self.title_item = QGraphicsTextItem(self)
            self.title_item.node = self.node
            self.title_item.setDefaultTextColor(self._title_color)
            self.title_item.setFont(self._title_font)
            self.title_item.setPos(self._padding, 0)
            self.title_item.setTextWidth(
                self.width
                - 2 * self._padding
            )
        except Exception as ex:
            print("Exception caught in GraphicsNode - initTitle()")
            print(ex)
            handleError(ex)

    def initContent(self):
        try:
            self.grContent = QGraphicsProxyWidget(self)
            self.content.setGeometry(self.edge_size, self.title_height + self.edge_size,
                                    self.rect.width() - 2*self.edge_size, self.rect.height() - 2*self.edge_size-self.title_height)
            self.grContent.setWidget(self.content)
        except Exception as ex:
            print("Exception caught in GraphicsNode - initContent()")
            print(ex)
            handleError(ex)

    def setContentGeo(self):
        try:
            self.content.setGeometry(self.edge_size, self.title_height + self.edge_size,
                                    self.rect.width() - 2*self.edge_size, self.rect.height() - 2*self.edge_size-self.title_height)
        except Exception as ex:
            print("Exception caught in GraphicsNode - setContentGeo()")
            print(ex)
            handleError(ex)

    def initSockets(self):
        pass

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        try:
            # title
            path_title = QPainterPath()
            path_title.setFillRule(Qt.WindingFill)
            path_title.addRoundedRect(0, 0, self.rect.width(
            ), self.title_height, self.edge_size, self.edge_size)
            path_title.addRect(0, self.title_height -
                            self.edge_size, self.edge_size, self.edge_size)
            path_title.addRect(self.rect.width() - self.edge_size, self.title_height -
                            self.edge_size, self.edge_size, self.edge_size)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._brush_title)
            painter.drawPath(path_title.simplified())

            # content
            path_content = QPainterPath()
            path_content.setFillRule(Qt.WindingFill)
            path_content.addRoundedRect(0, self.title_height, self.rect.width(),
                                        self.rect.height() - self.title_height, self.edge_size, self.edge_size)
            path_content.addRect(0, self.title_height,
                                self.edge_size, self.edge_size)
            path_content.addRect(self.rect.width() - self.edge_size,
                                self.title_height, self.edge_size, self.edge_size)
            painter.setPen(Qt.NoPen)
            painter.setBrush(self._brush_background)
            painter.drawPath(path_content.simplified())

            # outline
            path_outline = QPainterPath()
            path_outline.addRoundedRect(
                0, 0, self.rect.width(), self.rect.height(), self.edge_size, self.edge_size)
            painter.setPen(self._pen_default if not self.isSelected()
                        else self._pen_selected)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path_outline.simplified())

            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
            painter.setPen(QPen(QColor(0, 0, 0, 255), 1.0,
                                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawEllipse(self.handle)
        except Exception as ex:
            print("Exception caught in GraphicsNode - paint()")
            print(ex)
            handleError(ex)