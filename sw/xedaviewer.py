# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
import re
import config
from collections import namedtuple





layersId = {
    0: 'top',
    1: 'l1',
    2: 'l2',
    3: 'l3',
    4: 'l4',
    5: 'l5',
    6: 'l6',
    32: 'bottom',
    33: 'tpaste',
    34: 'bpaste',
    35: 'tglue',
    36: 'bglue',
    37: 'tsilk',
    38: 'bsilk',
    39: 'tmask',
    40: 'bmask',
    41: 'edge',
    42: 'aux1',
    43: 'aux2',
    44: 'aux3',
    45: 'aux4',
    46: 'aux5',
    47: 'keepout'
    }

layersId.update({v: k for k, v in layersId.iteritems()})


Point = namedtuple('Point', 'x y')


class XedaViewer(QtGui.QWidget):

    moveEvent = QtCore.Signal(tuple)
    hoverEvent = QtCore.Signal(tuple)

    def __init__(self, *args, **kwargs):
        super(XedaViewer, self).__init__(*args, **kwargs)

        self.setCursor(QtCore.Qt.BlankCursor)
        # self.unsetCursor()  #para mostrar o cursor denovo...
        self.setMouseTracking(True)
        # self.scale(.1, -.1)

        self._pan_pos = None
        self._mouse_pos = None
        self.doSnap = True
        self._snap_pos = None

        self.scene = None

        self.viewSize = QtCore.QSize(0, 0)
        self.viewRect = QtCore.QRect(0, 0, 0, 0)

        self.previousRect = None

        self.scale = .1

    def setScene(self, scene):
        self.scene = scene
        self.viewSize = QtCore.QSize(scene.cfg.dim[0], scene.cfg.dim[1])
        self.scene.setSceneSize(self.viewSize)

    def paintEvent(self, e):
        # qp = QtGui.QPainter(self)
        qp = QtGui.QPainter()
        qp.begin(self)
        self.viewRect.setWidth(e.rect().width()/self.scale),
        self.viewRect.setHeight(e.rect().height()/self.scale)
        t = QtGui.QTransform(self.scale, 0, 0, self.scale, -self.viewRect.left(), -self.viewRect.top())

        if self.previousRect != self.viewRect:
            self.previousRect = QtCore.QRect(self.viewRect)
            self._gridImage = QtGui.QPixmap(e.rect().width(), e.rect().height())
            p = QtGui.QPainter(self._gridImage)
            p.setTransform(t)
            self._drawGrid(p, self.viewRect)
        qp.drawPixmap(0, 0, self._gridImage)

        qp.setTransform(t)
        qp.setPen(QtGui.QPen(QtGui.QColor(128, 128, 255, 127),
                  20,
                  QtCore.Qt.SolidLine,
                  QtCore.Qt.RoundCap,
                  QtCore.Qt.RoundJoin))
        qp.drawLine(1000, 1000, 2000, 3000)
        self._drawCursor(qp, self.viewRect)
        qp.end()

    def _drawGrid(self, paint, rect):
        print 'dezenhando o fundo....', rect
        paint.fillRect(rect, QtGui.QColor(*self.scene.cfg.colors.back))

        def doGrid(color, size):
            if size*self.scale > 5:    #grid is too small, so ignore it
                lines = []
                x = rect.left()-(rect.left()%size)
                end = rect.right()
                while x < end:
                    lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
                    x += size
                y = rect.top()-(rect.top()%size)
                end = rect.bottom()
                while y < end:
                    lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))
                    y += size

                paint.setPen(QtGui.QPen(QtGui.QColor(*color), int(self.scene.proj.weakgrid)))
                paint.drawLines(lines)

        if self.scene.proj.grid1: doGrid(self.scene.cfg.colors.grid1, self.scene.proj.grid1)
        if self.scene.proj.grid2: doGrid(self.scene.cfg.colors.grid2, self.scene.proj.grid2)


    def _drawCursor(self, paint, rect):
        if self._snap_pos:
            paint.setPen(QtGui.QPen(QtGui.QColor(*self.scene.cfg.colors.guide)))
            pos = self._snap_pos if self.doSnap else self._mouse_pos
            paint.drawLine(rect.left(), pos.y(), rect.right(), pos.y())
            paint.drawLine(pos.x(), rect.top(), pos.x(), rect.bottom())

    def mapToScene(self, point):
        return QtCore.QPoint(point.x()/self.scale+self.viewRect.left(),
                             point.y()/self.scale+self.viewRect.top()
                             )

    def wheelEvent(self, event):
        d = event.delta()

        if event.orientation() == QtCore.Qt.Orientation.Vertical:
            factor = 1.25

            if d > 0:  #in
                if self.scale < 1.6: self.scale *= factor
            else:
                if self.scale > .04: self.scale /= factor

            self.repaint()

            event.accept()
        else:
            event.ignore()

    def leaveEvent(self, event):
        super(XedaViewer, self).leaveEvent(event)
        self._snap_pos = None
        self.repaint()

    def mousePressEvent(self, event):
        super(XedaViewer, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            i = self._discoverItem(None)
            #TODO quando tiver mas de um item isso sera assincrono.... fudeu

            #TODO prepara para arrastar....
            #se item selecionado faz parte de uma selecao tem que mover toda ela
        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_pos = event.pos()
            event.accept()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            pass
            #TODO mostra algum menu
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        super(XedaViewer, self).mouseMoveEvent(event)
        # self._mouse_pos = Point._make(self.mapToScene(event.pos()).toTuple())
        # self._mouse_pos = Point(*self.mapToScene(event.pos()).toTuple())
        self._mouse_pos = self.mapToScene(event.pos())
        n = self.scene.proj.snap
        self._snap_pos = QtCore.QPoint((self._mouse_pos.x()//n)*n, (self._mouse_pos.y()//n)*n)
        # self.moveEvent.emit(self._mouse_pos)
        self.moveEvent.emit(self._snap_pos)
        self.repaint()
        #self._discoverItem(None) #TODO quando tiver mas de um item isso sera assincrono.... fudeu
        if self._pan_pos:
            p = event.pos()-self._pan_pos
            self._pan_pos = event.pos()
            self.viewRect.setLeft(min(self.viewSize.width()-self.viewRect.width(),
                                      max(0, self.viewRect.left()-p.x()/self.scale)))
            self.viewRect.setTop(min(self.viewSize.height()-self.viewRect.height(),
                                     max(0, self.viewRect.top()-p.y()/self.scale)))
            print self.viewRect
            self.repaint()
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        super(XedaViewer, self).mouseReleaseEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pass
            #TODO solta o que estava arrastando...
        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_pos = None
            event.accept()
        # elif event.button() == QtCore.Qt.MouseButton.RightButton:
        #     pass
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        i = self._discoverItem(None) #TODO quando tiver mas de um item isso sera assincrono.... fudeu
        if i:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                if isinstance(i, BaseXedaItem):
                    i.inspect()

    def keyPressEvent(self, event):
        print event.text(), event.key(), event.modifiers(), event.type()








class BaseXedaScene(object):

    def __init__(self, config, project, *args, **kwargs):
        super(BaseXedaScene, self).__init__(*args, **kwargs)

        self.cfg = config
        self.proj = project

        self.items = []

        self.procNames = {
            # 'grid': self.setGrid,
            # 'clearsel': self.clearSelection,
            # 'setorigin': self.setOrigin,
            # 'resetorigin': self.resetOrigin,
            # 'rotate': self.
            # 'delete': self.
            }

    def setSceneSize(self, size):
        print size

    def addItem(self, item):
        self.items.append(item)

    def setOrigin(self, **kwargs):
        print 'setOrigin'
    def resetOrigin(self, **kwargs):
        print 'resetOrigin'
    def clearSelection(self, **kwargs):
        print 'clearSelection'
    # def removeItem(self, item):
    #     print 'removeItem'
    # def rotateItem(self, item):
    #     print 'rotateItem'







class SCHScene(BaseXedaScene):
    pass

class PCBScene(BaseXedaScene):

    def __init__(self, *args, **kwargs):
        super(PCBScene, self).__init__(*args, **kwargs)

        self.procNames.update({
            # 'text': self.
            # 'pad': self.
            # 'via': self.
            # 'line': self.
            # 'arc': self.
            # 'area': self.
            # 'trace': self.
            'place': self.cmdPlace,
            })

    def cmdPlace(self, **kwargs):
        print 'place!!!'

    # def addText(self, i):
    #     print 'addText'
    # def addVia(self, i):
    #     print 'addVia'
    # def addPad(self, i):
    #     print 'addPad'
    # def addLine(self, i):
    #     print 'addLine'
    # def addArc(self, i):
    #     print 'addArc'
    # def addArea(self, i):
    #     print 'addArea'
    # def addPart(self, i):
    #     print 'addPart'
    # def setLayer(self, i):
    #     print 'setLayer'
    # def addTrace(self, i):
    #     print 'addTrace'














class BaseXedaItem(object):

    def __init__(self, data=None):
        super(BaseXedaItem, self).__init__()

        self._x_selected = False

        if data:
            self.unpack(data)

    def bounding(self):
        raise NotImplementedError()

    def paint(self, painter, option, widget):
        raise NotImplementedError()

    def inspect(self):
        ok, data = self.myInspector.inspect(self.pack())
        if ok:
            self.unpack(data)

    def setPos(self, x, y):
        pass
        # print x, y

    def pack(self):
        d = {}
        for m in dir(self):
            if m.startswith('_x_'):
                d[m[3:]] = getattr(self, m)
        d['x'] = self.x()
        d['y'] = self.y()
        return d

    def unpack(self, data):
        self.setPos(data['x'], data['y'])
        del data['x']
        del data['y']
        for k, v in data.items():
            setattr(self, '_x_'+k, v)
        # self.invalidate()

    def toGerber(self):
        raise NotImplementedError()

    # def setPos(self, x, y):
    #     super(BaseXedaItem, self).setPos(x, y)
    #     self._x_x = x
    #     self._x_y = y








class BaseXedaInspector(QtGui.QDialog):

    def __init__(self, data, parent=None):
        super(BaseXedaInspector, self).__init__(parent)
        self.setupUi(self)

        self.populate(data)

    def getByName(self, name):
        o = getattr(self, name, None)
        if o:
            if isinstance(o, QtGui.QWidget):
                return o
        return None

    def populate(self, data):
        print data
        self._data = data
        for t, f, ui in self._UI_XO:
            print ui, f, data[f]
            if t == 1: #absolute position
                self.getByName(ui).setDim('{}mil'.format(data[f]), 'mm')
            elif t == 2: #mm or mil dim
                self.getByName(ui).setDim('{}mil'.format(data[f]), 'mm')
            elif t == 3: #boolean
                self.getByName(ui).setChecked(data[f])
            elif t == 4: #net
                pass
            elif t == 5: #layer
                pass
            elif t == 6: #
                pass
            elif t == 7: #string
                self.getByName(ui).setText(data[f])

    def dump(self):
        for t, f, ui in self._UI_XO:
            if t == 1: #absolute position
                self._data[f] = self.getByName(ui).getDim()
            elif t == 2: #mm or mil dim
                self._data[f] = self.getByName(ui).getDim()
            elif t == 3: #boolean
                self._data[f] = self.getByName(ui).isChecked()
            elif t == 4: #net
                pass
            elif t == 5: #layer
                pass
            elif t == 6: #
                pass
            elif t == 7: #string
                self._data[f] = self.getByName(ui).text()
        print self._data
        return self._data










from ins_via_ui import *

class PCBViaInspector(BaseXedaInspector, Ui_dlg_via):

    _UI_XO = (
        (2, 'od', 'edt_od'),
        (2, 'id', 'edt_id'),
        (3, 'plated', 'chk_plated'),
        (4, 'net', 'sel_net'),
        (5, 'start', 'sel_start'),
        (5, 'end', 'sel_end'),
        (3, 'tent', 'chk_tent'),
        (2, 'mask', 'edt_mask'),
        (1, 'x', 'edt_x'),
        (1, 'y', 'edt_y')
        )

    @staticmethod
    def inspect(data, parent=None):
        dialog = PCBViaInspector(data, parent)
        result = dialog.exec_()
        return (result == QtGui.QDialog.Accepted), dialog.dump()








class PCBViaItem(BaseXedaItem):

    _x_name = 'VIA'
    myInspector = PCBViaInspector

    def __init__(self, *args, **kwargs):

        self._x_od = 50
        self._x_id = 28
        self._x_plated = False
        self._x_net = None
        self._x_start = 1
        self._x_end = 32
        self._x_tent = False
        self._x_mask = None

        super(PCBViaItem, self).__init__(*args, **kwargs)

    def bounding(self):
        return QtCore.QRectF(-self._x_od/2, -self._x_od/2, self._x_od, self._x_od)

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200, 127), (self._x_od-self._x_id)/2))
        r = self._x_od-(self._x_od-self._x_id)/2
        painter.drawEllipse(QtCore.QRectF(-r/2, -r/2, r, r))

