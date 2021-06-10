from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Utils.ErrorMessage import handleError


DEBUG = False


class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, socket, socket_type=1):
        if DEBUG: print("In Graphics Socket constructor")
        try:
            self.socket = socket
            super().__init__(socket.node.grNode)

            self.radius = 6.0
            self.outline_width = 1.0
            self._colors = [
                QColor("#FFFF7700"),
                QColor("#FF52e220"),
                QColor("#FF0056a6"),
                QColor("#FFa86db1"),
                QColor("#FFb54747"),
                QColor("#FFdbe220"),
            ]
            self._color_background = self._colors[socket_type]
            self._color_outline = QColor("#FF000000")

            self._pen = QPen(self._color_outline)
            self._pen.setWidthF(self.outline_width)
            self._brush = QBrush(self._color_background)
        except Exception as ex:
            print("Exception caught in GraphicsSocket - __init__()")
            print(ex)
            handleError(ex)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        if DEBUG: print("In GraphicsSocket - paint()")
        try:
            # painting circle
            painter.setBrush(self._brush)
            painter.setPen(self._pen)
            painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)
        except Exception as ex:
            print("Exception caught in GraphicsSocket - paint()")
            print(ex)
            handleError(ex)

    def boundingRect(self):
        if DEBUG: print("In GraphicsSocket - boundingRect()")
        try:
            return QRectF(
                - self.radius - self.outline_width,
                - self.radius - self.outline_width,
                2 * (self.radius + self.outline_width),
                2 * (self.radius + self.outline_width),
            )
        except Exception as ex:
            print("Exception caught in GraphicsSocket - boundingRect()")
            print(ex)
            handleError(ex)