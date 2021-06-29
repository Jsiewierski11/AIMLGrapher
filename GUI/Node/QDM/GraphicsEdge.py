import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from Utils.ErrorMessage import handleError
from GUI.Node.Utils.Socket import *


DEBUG = False

EDGE_CP_ROUNDNESS = 100


class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        if DEBUG: print("In QDMGraphicsEdge constructor")
        try:
            super().__init__(parent)

            self.edge = edge

            self._color = QColor("#000066")
            self._color_selected = QColor("#800000")
            self._pen = QPen(self._color)
            self._pen_selected = QPen(self._color_selected)
            self._pen_dragging = QPen(self._color)
            self._pen_dragging.setStyle(Qt.DashLine)
            self._pen.setWidthF(2.0)
            self._pen_selected.setWidthF(2.0)
            self._pen_dragging.setWidthF(2.0)

            self.setFlag(QGraphicsItem.ItemIsSelectable)

            self.setZValue(-1)

            self.posSource = [0, 0]
            self.posDestination = [200, 100]
        except Exception as ex:
            print("Exception caught in GraphicsEdge - __init__()")
            print(ex)
            handleError(ex)

    def setSource(self, x, y):
        if DEBUG: print("In setSource()")
        try:
            self.posSource = [x, y]
        except Exception as ex:
            print("Exception caught in GraphicsEdge - setSource()")
            print(ex)
            handleError(ex)

    def setDestination(self, x, y):
        if DEBUG: print("In setDestination()")
        try:
            self.posDestination = [x, y]
        except Exception as ex:
            print("Exception caught in GraphicsEdge - setDestination()")
            print(ex)
            handleError(ex)

    def boundingRect(self):
        if DEBUG: print("In boundingRect() GraphicsEdge")
        try:
            return self.shape().boundingRect()
        except Exception as ex:
            print("Exception caught in GraphicsEdge - boundingRect()")
            print(ex)
            handleError(ex)

    def shape(self):
        if DEBUG: print("In shape()")
        try:
            return self.calcPath()
        except Exception as ex:
            print("Exception caught in GraphicsEdge - shape()")
            print(ex)
            handleError(ex)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if DEBUG: print("In paint()")
        try:
            self.setPath(self.calcPath())

            if self.edge.end_socket is None:
                painter.setPen(self._pen_dragging)
            else:
                painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.path())
        except Exception as ex:
            print("Exception caught in GraphicsEdge - paint()")
            print(ex)
            handleError(ex)

    def intersectsWith(self, p1, p2):
        if DEBUG: print("In intersectsWith()")
        try:
            cutpath = QPainterPath(p1)
            cutpath.lineTo(p2)
            path = self.calcPath()
            return cutpath.intersects(path)
        except Exception as ex:
            print("Exception caught in GraphicsEdge - intersectsWith()")
            print(ex)
            handleError(ex)

    def calcPath(self):
        try:
            """ Will handle drawing QPainterPath from Point A to B """
            if DEBUG: print("In calcPath Abstract function")
            raise NotImplemented("This method has to be overridden in a child class")
        except Exception as ex:
            print("Exception caught in GraphicsEdge - calcPath() Abstract")
            print(ex)
            handleError(ex)


class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def calcPath(self):
        if DEBUG: print("In calcPath() Direct")
        try:
            path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
            path.lineTo(self.posDestination[0], self.posDestination[1])
            if DEBUG: print("returning direct path")
            return path
        except Exception as ex:
            print("Exception caught in GraphicsEdge - calPath() Direct")
            print(ex)
            handleError(ex)


class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def calcPath(self):
        if DEBUG: print("In calcPath() Bezier")
        try:
            s = self.posSource
            d = self.posDestination
            dist = (d[0] - s[0]) * 0.5

            cpx_s = +dist
            cpx_d = -dist
            cpy_s = 0
            cpy_d = 0

            if self.edge.start_socket is not None:
                sspos = self.edge.start_socket.position

                if (s[0] > d[0] and sspos in (RIGHT_TOP, RIGHT_BOTTOM)) or (s[0] < d[0] and sspos in (LEFT_BOTTOM, LEFT_TOP)):
                    cpx_d *= -1
                    cpx_s *= -1

                    cpy_d = (
                        (s[1] - d[1]) / math.fabs(
                            (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                        )
                    ) * EDGE_CP_ROUNDNESS
                    cpy_s = (
                        (d[1] - s[1]) / math.fabs(
                            (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                        )
                    ) * EDGE_CP_ROUNDNESS


            path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
            path.cubicTo( s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDestination[0], self.posDestination[1])

            return path
        except Exception as ex:
            print("Exception caught in GraphicsEdge - calPath() Bezier")
            print(ex)
            handleError(ex)