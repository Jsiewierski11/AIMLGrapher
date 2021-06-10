from PyQt5.QtWidgets import QGraphicsView, QApplication, QGraphicsSceneMouseEvent, QPushButton
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from GUI.Node.QDM.GraphicsSocket import QDMGraphicsSocket
from GUI.Node.QDM.GraphicsEdge import QDMGraphicsEdge
from GUI.Node.Edge import Edge, EDGE_TYPE_BEZIER
from GUI.Node.QDM.GraphicsCutline import QDMCutLine
from Utils.ErrorMessage import handleError


MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3

EDGE_DRAG_START_THRESHOLD = 10


DEBUG = False


class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene

        self.initUI()

        self.setScene(self.grScene)

        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        # cutline
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)

    def initUI(self):
        try:
            if DEBUG: print("in GraphicsView - initUI()")
            self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

            self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

            # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setDragMode(QGraphicsView.RubberBandDrag)
        except Exception as ex:
            print("Exception caught in GraphicsView - initUI()")
            print(ex)
            handleError(ex)

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.MiddleButton:
                self.middleMouseButtonPress(event)
            elif event.button() == Qt.LeftButton:
                self.leftMouseButtonPress(event)
            elif event.button() == Qt.RightButton:
                self.rightMouseButtonPress(event)
            else:
                super().mousePressEvent(event)
        except Exception as ex:
            print("Exception caught in GraphicsView - mousePressEvent()")
            print(ex)
            handleError(ex)

    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.MiddleButton:
                self.middleMouseButtonRelease(event)
            elif event.button() == Qt.LeftButton:
                self.leftMouseButtonRelease(event)
            elif event.button() == Qt.RightButton:
                self.rightMouseButtonRelease(event)
            else:
                super().mouseReleaseEvent(event)
        except Exception as ex:
            print("Exception caught in GraphicsView - mouseReleaseEvent()")

    def middleMouseButtonPress(self, event):
        try:
            releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                    Qt.LeftButton, Qt.NoButton, event.modifiers())
            super().mouseReleaseEvent(releaseEvent)
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                    Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
            super().mousePressEvent(fakeEvent)
        except Exception as ex:
            print("Exception caught in GraphicsView - middleMouseButtonPress()")
            print(ex)
            handleError(ex)

    def middleMouseButtonRelease(self, event):
        try:
            fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                    Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
            super().mouseReleaseEvent(fakeEvent)
            self.setDragMode(QGraphicsView.RubberBandDrag)
        except Exception as ex:
            print("Exception caught in GraphicsView - middleMouseButtonRelease()")
            print(ex)
            handleError(ex)

    def leftMouseButtonPress(self, event):
        try:
            # get item which we clicked on
            item = self.getItemAtClick(event)

            # we store the position of last LMB click
            self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

            # if DEBUG: print("LMB Click on", item, self.debug_modifiers(event))

            # logic
            if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
                if event.modifiers() & Qt.ShiftModifier:
                    event.ignore()
                    fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                            Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                            event.modifiers() | Qt.ControlModifier)
                    super().mousePressEvent(fakeEvent)
                    return

            if type(item) is QDMGraphicsSocket:
                if self.mode == MODE_NOOP:
                    self.mode = MODE_EDGE_DRAG
                    self.edgeDragStart(item)
                    return

            if self.mode == MODE_EDGE_DRAG:
                res = self.edgeDragEnd(item)
                if res: return

            if item is None:
                if event.modifiers() & Qt.ControlModifier:
                    self.mode = MODE_EDGE_CUT
                    fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                            Qt.LeftButton, Qt.NoButton, event.modifiers())
                    super().mouseReleaseEvent(fakeEvent)
                    QApplication.setOverrideCursor(Qt.CrossCursor)
                    return
                else:
                    self.rubberBandDraggingRectangle = True

            super().mousePressEvent(event)
        except Exception as ex:
            print("Exception caught in GraphicsView - leftMouseButtonPress()")
            print(ex)
            handleError(ex)

    def leftMouseButtonRelease(self, event):
        try:
            # get item which we release mouse button on
            item = self.getItemAtClick(event)

            # logic
            if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
                if event.modifiers() & Qt.ShiftModifier:
                    event.ignore()
                    fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                            Qt.LeftButton, Qt.NoButton,
                                            event.modifiers() | Qt.ControlModifier)
                    super().mouseReleaseEvent(fakeEvent)
                    return

            if self.mode == MODE_EDGE_DRAG:
                if self.distanceBetweenClickAndReleaseIsOff(event):
                    res = self.edgeDragEnd(item)
                    if res: return

            if self.mode == MODE_EDGE_CUT:
                self.cutIntersectingEdges()
                self.cutline.line_points = []
                self.cutline.update()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.mode = MODE_NOOP
                return

            if self.rubberBandDraggingRectangle:
                self.grScene.scene.history.storeHistory("Selection changed")
                self.rubberBandDraggingRectangle = False

            super().mouseReleaseEvent(event)
        except Exception as ex:
            print("Exception caught in GraphicsView - leftMouseButtonRelease()")

    def rightMouseButtonPress(self, event):
        try:
            super().mousePressEvent(event)

            item = self.getItemAtClick(event)

            # moving the center of the screen to mouse coordinates
            try:
                coor = event.pos()
                self.grScene.update(coor.x(), coor.y(), self.grScene.scene.scene_width, self.grScene.scene.scene_height)
            except Exception as ex:
                print("Exception caught in GraphicsView - rightMouseButtonPress()")
                print(ex)

            if DEBUG:
                if isinstance(item, QDMGraphicsEdge): print('RMB DEBUG:', item.edge, ' connecting sockets:',
                                                item.edge.start_socket, '<-->', item.edge.end_socket)
                if type(item) is QDMGraphicsSocket: print('RMB DEBUG:', item.socket, 'has edge:', item.socket.edge)

                if item is None:
                    print('SCENE:')
                    print('  Nodes:')
                    for node in self.grScene.scene.nodes: print('    ', node)
                    print('  Edges:')
                    for edge in self.grScene.scene.edges: print('    ', edge)
        except Exception as ex:
            print("Exception caught in GraphicsView - rightMouseButtonPress()")
            print(ex)
            handleError(ex)


    def rightMouseButtonRelease(self, event):
        try:
            super().mouseReleaseEvent(event)
        except Exception as ex:
            print("Exception caught in GraphicsView - rightMouseButtonRelease()")
            print(ex)
            handleError(ex)

    def mouseMoveEvent(self, event):
        try:
            if self.mode == MODE_EDGE_DRAG:
                pos = self.mapToScene(event.pos())
                self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
                self.dragEdge.grEdge.update()

            if self.mode == MODE_EDGE_CUT:
                pos = self.mapToScene(event.pos())
                self.cutline.line_points.append(pos)
                self.cutline.update()

            self.last_scene_mouse_position = self.mapToScene(event.pos())

            self.scenePosChanged.emit(
                int(self.last_scene_mouse_position.x()), int(self.last_scene_mouse_position.y())
            )

            super().mouseMoveEvent(event)
        except Exception as ex:
            print("Exception caught in GraphicsView - mouseMoveEvent()")
            print(ex)
            handleError(ex)

    def keyPressEvent(self, event):
        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.saveToFile("graph.json.txt")
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.loadFromFile("graph.json.txt")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.redo()
        # elif event.key() == Qt.Key_H:
        #     print("HISTORY:     len(%d)" % len(self.grScene.scene.history.history_stack),
        #           " -- current_step", self.grScene.scene.history.history_current_step)
        #     ix = 0
        #     for item in self.grScene.scene.history.history_stack:
        #         print("#", ix, "--", item['desc'])
        #         ix += 1
        # else:
        super().keyPressEvent(event)

    def cutIntersectingEdges(self):
        try:
            for ix in range(len(self.cutline.line_points) - 1):
                p1 = self.cutline.line_points[ix]
                p2 = self.cutline.line_points[ix + 1]

                for edge in self.grScene.scene.edges:
                    if edge.grEdge.intersectsWith(p1, p2):
                        edge.remove()
            self.grScene.scene.history.storeHistory("Delete cutted edges", setModified=True)
        except Exception as ex:
            print("Exception caught in GraphicsView - cutIntersectingEdges()")
            print(ex)
            handleError(ex)

    def deleteSelected(self):
        try:
            for item in self.grScene.selectedItems():
                if isinstance(item, QDMGraphicsEdge):
                    item.edge.remove()
                elif hasattr(item, 'node'):
                    item.node.remove()
            self.grScene.scene.history.storeHistory("Delete selected", setModified=True)
        except Exception as ex:
            print("Exception caught in GraphicsView - deleteSelected()")
            print(ex)
            handleError(ex)

    def debug_modifiers(self, event):
        try:
            out = "MODS: "
            if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
            if event.modifiers() & Qt.ControlModifier: out += "CTRL "
            if event.modifiers() & Qt.AltModifier: out += "ALT "
            return out
        except Exception as ex:
            print("Exception caught in GraphicsView - debug_modifiers()")
            print(ex)
            handleError(ex)

    def getItemAtClick(self, event):
        try:
            """ return the object on which we've clicked/release mouse button """
            pos = event.pos()
            obj = self.itemAt(pos)
            return obj
        except Exception as ex:
            print("Exception caught in GraphicsView - getItemAtClick()")
            print(ex)
            handleError(ex)

    def edgeDragStart(self, item):
        try:
            if DEBUG: print('View::edgeDragStart ~ Start dragging edge')
            if DEBUG: print('View::edgeDragStart ~   assign Start Socket to:', item.socket)
            self.previousEdge = item.socket.edge
            self.last_start_socket = item.socket
            self.dragEdge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
            if DEBUG: print('View::edgeDragStart ~   dragEdge:', self.dragEdge)
        except Exception as ex:
            print("Exception caught in GraphicsView - edgeDragStart()")
            print(ex)
            handleError(ex)

    def edgeDragEnd(self, item):
        try:
            """ return True if skip the rest of the code """
            self.mode = MODE_NOOP

            if type(item) is QDMGraphicsSocket:
                if item.socket != self.last_start_socket:
                    if DEBUG: print('View::edgeDragEnd ~   previous edge:', self.previousEdge)
                    if item.socket.hasEdge():
                        item.socket.edge.remove()
                    if DEBUG: print('View::edgeDragEnd ~   assign End Socket', item.socket)
                    if self.previousEdge is not None: self.previousEdge.remove()
                    if DEBUG: print('View::edgeDragEnd ~  previous edge removed')
                    self.dragEdge.start_socket = self.last_start_socket
                    self.dragEdge.end_socket = item.socket
                    self.dragEdge.start_socket.setConnectedEdge(self.dragEdge)
                    self.dragEdge.end_socket.setConnectedEdge(self.dragEdge)
                    if DEBUG: print('View::edgeDragEnd ~  reassigned start & end sockets to drag edge')
                    self.dragEdge.updatePositions()
                    self.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)
                    return True

            if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
            self.dragEdge.remove()
            self.dragEdge = None
            if DEBUG: print('View::edgeDragEnd ~ about to set socket to previous edge:', self.previousEdge)
            if self.previousEdge is not None:
                self.previousEdge.start_socket.edge = self.previousEdge
            if DEBUG: print('View::edgeDragEnd ~ everything done.')

            return False
        except Exception as ex:
            print("Exception caught in GraphicsView - edgeDragEnd()")
            print(ex)
            handleError(ex)

    def distanceBetweenClickAndReleaseIsOff(self, event):
        try:
            """ measures if we are too far from the last LMB click scene position """
            new_lmb_release_scene_pos = self.mapToScene(event.pos())
            dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
            edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD*EDGE_DRAG_START_THRESHOLD
            return (dist_scene.x()*dist_scene.x() + dist_scene.y()*dist_scene.y()) > edge_drag_threshold_sq
        except Exception as ex:
            print("Exception caught in GraphicsView - distanceBetweenClickAndReleaseIsOff()")
            print(ex)
            handleError(ex)

    def wheelEvent(self, event):
        try:
            # calculate our zoom Factor
            zoomOutFactor = 1 / self.zoomInFactor

            # calculate zoom
            if event.angleDelta().y() > 0:
                zoomFactor = self.zoomInFactor
                self.zoom += self.zoomStep
            else:
                zoomFactor = zoomOutFactor
                self.zoom -= self.zoomStep

            clamped = False
            if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
            if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

            # set scene scale
            if not clamped or self.zoomClamp is False:
                self.scale(zoomFactor, zoomFactor)
        except Exception as ex:
            print("Exception caught in GraphicsView - wheelEvent()")
            print(ex)
            handleError(ex)