from collections import OrderedDict
from GUI.Node.Utils.Serializable import Serializable
from GUI.Node.QDM.GraphicsEdge import *
from Utils.ErrorMessage import handleError


EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

DEBUG = False


class Edge(Serializable):
    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):
        if DEBUG: print("In Edge constructor")
        try:
            super().__init__()
            self.scene = scene

            self.start_socket = start_socket
            self.end_socket = end_socket
            self.edge_type = edge_type

            self.scene.addEdge(self)
        except Exception as ex:
            print("Exception caught in Edge - __init__()")
            print(ex)
            handleError(ex) 

    def __str__(self):
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    @property
    def start_socket(self): 
        if DEBUG: print("in start_socket() @property")
        try:
            return self._start_socket
        except Exception as ex:
            print("Exception caught in Edge - start_socket() @property")
            print(ex)
            handleError(ex)

    @start_socket.setter
    def start_socket(self, value):
        if DEBUG: print("in start_socket() @property")
        try:
            self._start_socket = value
            if self.start_socket is not None:
                self.start_socket.edge = self
        except Exception as ex:
            print("Exception caught in Edge - start_socker() setter")

    @property
    def end_socket(self): 
        try:
            if DEBUG: print("In end_socket() @property")
            return self._end_socket
        except Exception as ex:
            print("Exception caught in Edge - end_socket() @property")
            print(ex)
            handleError(ex)

    @end_socket.setter
    def end_socket(self, value):
        if DEBUG: print("In end_socket() setter")
        try:
            self._end_socket= value
            if self.end_socket is not None:
                self.end_socket.edge = self
        except Exception as ex:
            print("Exception caught in Edge - end_socket() setter")
            print(ex)
            handleError(ex)

    @property
    def edge_type(self): 
        if DEBUG: print("In edge_type() @property")
        try:
            return self._edge_type
        except Exception as ex:
            print("Exception caught in Edge - edge_type() @property")
            print(ex)
            handleError(ex)

    @edge_type.setter
    def edge_type(self, value):
        if DEBUG: print("In edge_type() setter")
        try:
            if hasattr(self, 'grEdge') and self.grEdge is not None:
                self.scene.grScene.removeItem(self.grEdge)

            self._edge_type = value
            if self.edge_type == EDGE_TYPE_DIRECT:
                self.grEdge = QDMGraphicsEdgeDirect(self)
            elif self.edge_type == EDGE_TYPE_BEZIER:
                self.grEdge = QDMGraphicsEdgeBezier(self)
            else:
                self.grEdge = QDMGraphicsEdgeBezier(self)

            self.scene.grScene.addItem(self.grEdge)

            if self.start_socket is not None:
                self.updatePositions()
        except Exception as ex:
            print("Exception caught in Edge - edge_type() setter")
            print(ex)
            handleError(ex)

    def updatePositions(self):
        if DEBUG: print("In updatePositions()")
        try:
            source_pos = self.start_socket.getSocketPosition()
            source_pos[0] += self.start_socket.node.grNode.pos().x()
            source_pos[1] += self.start_socket.node.grNode.pos().y()
            self.grEdge.setSource(*source_pos)
            if self.end_socket is not None:
                end_pos = self.end_socket.getSocketPosition()
                end_pos[0] += self.end_socket.node.grNode.pos().x()
                end_pos[1] += self.end_socket.node.grNode.pos().y()
                self.grEdge.setDestination(*end_pos)
            else:
                self.grEdge.setDestination(*source_pos)
            self.grEdge.update()
        except Exception as ex:
            print("Exception caught in Edge - updatePositions()")
            print(ex)
            handleError(ex)

    def remove_from_sockets(self):
        if DEBUG: print("In remove_from_sockets()")
        try:
            if self.start_socket is not None:
                self.start_socket.edge = None
            if self.end_socket is not None:
                self.end_socket.edge = None
            self.end_socket = None
            self.start_socket = None
        except Exception as ex:
            print("Exception caught in Edge - remove_from_sockets()")
            print(ex)
            handleError(ex)

    def remove(self):
        try:
            if DEBUG: print("# Removing Edge", self)
            if DEBUG: print(" - remove edge from all sockets")
            self.remove_from_sockets()
            if DEBUG: print(" - remove grEdge")
            self.scene.grScene.removeItem(self.grEdge)
            self.grEdge = None
            if DEBUG: print(" - remove edge from scene")
            try:
                self.scene.removeEdge(self)
            except ValueError:
                pass
            if DEBUG: print(" - everything is done.")
        except Exception as ex:
            print("Exception caught in Edge - remove()")
            print(ex)
            handleError(ex)

    def serialize(self):
        return OrderedDict([
            ('id', self.objId),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.objId),
            ('end', self.end_socket.objId),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.objId = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']