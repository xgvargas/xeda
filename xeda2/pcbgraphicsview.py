# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui

class BaseXedaView(QtGui.QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(BaseXedaView, self).__init__(*args, **kwargs)

        self.setCursor(QtCore.Qt.BlankCursor)
        # self.unsetCursor()  #para mostrar o cursor denovo...
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setSceneRect(QtCore.QRectF(0.0, 0.0, 20000.0, 20000.0))
        self.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.HighQualityAntialiasing|QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)
        self.scale(.1, -.1)

        self.guide = QtGui.QColor(255, 255, 255)
        self.background = QtGui.QColor(0, 0, 0)
        self.grids = [(100, QtGui.QColor(64, 64, 64)), (1000, QtGui.QColor(255, 255, 255))]

        self._pan_pos = None
        self._mouse_pos = QtCore.QPointF(0, 0)

    def _drawGrid(self, p, rect, pen, size):
        s = self.transform().m11()
        if size*s < 5: return     #grid is too small, so ignore it

        left = int(rect.left()-(rect.left()%size))
        top = int(rect.top()-(rect.top()%size))
        lines = []
        for x in xrange(left, int(rect.right()), size):
            lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
        for y in xrange(top, int(rect.bottom()), size):
            lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))

        p.setPen(pen)
        p.drawLines(lines)

    def drawBackground(self, paint, rect):
        paint.fillRect(rect, self.background)

        for g in self.grids:
            p = QtGui.QPen(g[1], 0)
            self._drawGrid(paint, rect, p, g[0])

    def drawForeground(self, paint, rect):
        paint.setPen(QtGui.QPen(self.guide))
        paint.drawLine(rect.left(), self._mouse_pos.y(), rect.right(), self._mouse_pos.y())
        paint.drawLine(self._mouse_pos.x(), rect.top(), self._mouse_pos.x(), rect.bottom())

    def wheelEvent(self, event):
        d = event.delta()

        if event.orientation() == QtCore.Qt.Orientation.Vertical:
            factor = 1.15

            s = self.transform().m11()
            if d > 0:  #in
                if s < 1.5: self.scale(factor, factor)
            else:
                if s > .04: self.scale(1/factor, 1/factor)

            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        super(BaseXedaView, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_pos = event.pos()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        super(BaseXedaView, self).mouseMoveEvent(event)
        self._mouse_pos = self.mapToScene(event.pos())
        self.scene().invalidate()
        i = self.items(event.pos())
        if i:
            print i
        if self._pan_pos:
            p = event.pos()-self._pan_pos
            self._pan_pos = event.pos()
            v = self.verticalScrollBar()
            v.setValue(v.value()-p.y())
            h = self.horizontalScrollBar()
            h.setValue(h.value()-p.x())
            # self.translate(p.x(), p.y())    isso nao funciona aqui!
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        super(BaseXedaView, self).mouseReleaseEvent(event)
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_pos = None
            event.accept()
        else:
            event.ignore()

class PCBGraphicsView(BaseXedaView):
    pass

class SCHGraphicsView(BaseXedaView):

    def __init__(self, *args, **kwargs):
        super(SCHGraphicsView, self).__init__(*args, **kwargs)

        self.guide = QtGui.QColor(0, 0, 0)
        self.background = QtGui.QColor(245, 239, 191)
        self.grids = [(100, QtGui.QColor(226, 223, 208)), (1000, QtGui.QColor(171, 169, 129))]


class PCBViaItem(QtGui.QGraphicsItem):

    def boundingRect(self):
        do = 50
        di = 28
        return QtCore.QRectF(-do/2, -do/2, do, do)

    def paint(self, painter, option, widget):
        do = 50
        di = 28
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200, 127), (do-di)/2))
        r = do-(do-di)/2
        painter.drawEllipse(QtCore.QRectF(-r/2, -r/2, r, r))
