from collections import OrderedDict
from GUI.Node.Utils.Serializable import Serializable
from GUI.Node.QDM.GraphicsSocket import QDMGraphicsSocket
from Utils.ErrorMessage import handleError


LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4


DEBUG = False


class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1):
        try:
            super().__init__()

            self.node = node
            self.index = index
            self.position = position
            self.socket_type = socket_type

            if DEBUG:
                print("Socket -- creating with", self.index,
                    self.position, "for node", self.node)

            self.grSocket = QDMGraphicsSocket(self, self.socket_type)

            self.grSocket.setPos(*self.node.getSocketPosition(index, position))

            self.edge = None
        except Exception as ex:
            print("Exception caught in Socket - __init__()")
            print(ex)
            handleError(ex)

    def __str__(self):
        return "<Socket %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    def getSocketPosition(self):
        try:
            if DEBUG:
                print("  GSP: ", self.index, self.position, "node:", self.node)
            res = self.node.getSocketPosition(self.index, self.position)
            if DEBUG:
                print("  res", res)
            return res
        except Exception as ex:
            print("Exception caught in Socket - getSocketPosition()")
            print(ex)
            handleError(ex)

    def setSocketPosition(self):
        if DEBUG: print("In setSocketPosition()")
        try:
            self.grSocket.setPos(
                *self.node.getSocketPosition(self.index, self.position))
        except Exception as ex:
            print("Exception caught in Socket - setSocketPosition()")
            print(ex)
            handleError(ex)

    def setConnectedEdge(self, edge=None):
        if DEBUG: print("In setConnectedEdge()")
        try:
            self.edge = edge
        except Exception as ex:
            print("Exception caught in Socket - setConnectedEdge()")
            print(ex)
            handleError(ex)

    def hasEdge(self):
        if DEBUG: print("In hasEdge()")
        try:
            return self.edge is not None
        except Exception as ex:
            print("Exception caught in Socket - hasEdge()")
            print(ex)
            handleError(ex)

    def serialize(self):
        return OrderedDict([
            ('id', self.objId),
            ('index', self.index),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id:
            self.objId = data['id']
        hashmap[data['id']] = self
        return True
