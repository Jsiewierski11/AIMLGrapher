from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from Utils.ErrorMessage import handleError

DEBUG = False


class QDMCutLine(QGraphicsItem):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)

            self.line_points = []

            self._pen = QPen(Qt.white)
            self._pen.setWidthF(2.0)
            self._pen.setDashPattern([3, 3])

            self.setZValue(2)
        except Exception as ex:
            print("Exception caught in GraphicsCutline - __init__()")
            print(ex)
            handleError(ex)

    def boundingRect(self):
        try:
            if DEBUG: print("In GraphicsCutline - boundingRect()")
            return self.shape().boundingRect()
        except Exception as ex:
            print("Exception caught in GraphicsCutline - boundingRect()")
            print(ex)
            handleError(ex)

    def shape(self):
        try:
            if DEBUG: print("In GraphicsCutline - shape()")
            poly = QPolygonF(self.line_points)

            if len(self.line_points) > 1:
                path = QPainterPath(self.line_points[0])
                for pt in self.line_points[1:]:
                    path.lineTo(pt)
            else:
                path = QPainterPath(QPointF(0,0))
                path.lineTo(QPointF(1,1))

            return path
        except Exception as ex:
            print("Exception caught in GraphicsCutline - shape()")
            print(ex)
            handleError(ex)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        try:
            if DEBUG: print("In GraphicsCutline - paint()")
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(self._pen)

            poly = QPolygonF(self.line_points)
            painter.drawPolyline(poly)
        except Exception as ex:
            print("Exception caught in GraphicsCutline - paint()")
            print(ex)
            handleError(ex)