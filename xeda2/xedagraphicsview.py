# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
import re


class XedaGraphicsView(QtGui.QGraphicsView):

    def __init__(self, *args, **kwargs):
        super(XedaGraphicsView, self).__init__(*args, **kwargs)

        self.setCursor(QtCore.Qt.BlankCursor)
        # self.unsetCursor()  #para mostrar o cursor denovo...
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.HighQualityAntialiasing|QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        # self.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setMouseTracking(True)
        self.scale(.1, -.1)

        self.guide = QtGui.QColor(255, 255, 255)

        self._pan_pos = None
        self._mouse_pos = QtCore.QPointF(0, 0)

    def setScene(self, scene):
        super(XedaGraphicsView, self).setScene(scene)
        # self.setSceneRect(QtCore.QRectF(0.0, 0.0, 20000.0, 20000.0))
        scene.setSceneRect(0, 0, scene.cfg.dim[0], scene.cfg.dim[1])
        self.setSceneRect(0, 0, scene.cfg.dim[0], scene.cfg.dim[1])

    def drawBackground(self, paint, rect):

            paint.fillRect(rect, QtGui.QColor(*self.scene().cfg.colors.back))

            def doGrid(color, size):
                s = self.transform().m11()
                if size*s < 5: return     #grid is too small, so ignore it

                left = int(rect.left()-(rect.left()%size))
                top = int(rect.top()-(rect.top()%size))
                lines = []
                for x in xrange(left, int(rect.right()), size):
                    lines.append(QtCore.QLineF(x, rect.top(), x, rect.bottom()))
                for y in xrange(top, int(rect.bottom()), size):
                    lines.append(QtCore.QLineF(rect.left(), y, rect.right(), y))

                paint.setPen(QtGui.QPen(QtGui.QColor(*color), int(self.scene().cfg.weakgrid)))
                paint.drawLines(lines)

            if self.scene().cfg.grid1: doGrid(self.scene().cfg.colors.grid1, self.scene().cfg.grid1)
            if self.scene().cfg.grid2: doGrid(self.scene().cfg.colors.grid2, self.scene().cfg.grid2)

    def drawForeground(self, paint, rect):
        paint.setPen(QtGui.QPen(self.guide))
        paint.drawLine(rect.left(), self._mouse_pos.y(), rect.right(), self._mouse_pos.y())
        paint.drawLine(self._mouse_pos.x(), rect.top(), self._mouse_pos.x(), rect.bottom())

    def wheelEvent(self, event):
        d = event.delta()

        if event.orientation() == QtCore.Qt.Orientation.Vertical:
            factor = 1.25

            s = self.transform().m11()
            if d > 0:  #in
                if s < 1.5: self.scale(factor, factor)
            else:
                if s > .04: self.scale(1/factor, 1/factor)

            event.accept()
        else:
            event.ignore()

    def mousePressEvent(self, event):
        super(XedaGraphicsView, self).mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_pos = event.pos()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        super(XedaGraphicsView, self).mouseMoveEvent(event)
        self._mouse_pos = self.mapToScene(event.pos())
        self.scene().invalidate()
        i = self.items(event.pos())
        if i:
            pass
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
        super(XedaGraphicsView, self).mouseReleaseEvent(event)
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_pos = None
            event.accept()
        else:
            event.ignore()

    def mouseDoubleClickEvent(self, event):
        i = self.items(event.pos())
        if i:
            if isinstance(i[0], BaseXedaItem):
                i[0].inspect()

    def keyPressEvent(self, event):
        print event.text(), event.key(), event.modifiers(), event.type()

        for f, k in self.scene().cfg.shortcuts._d.iteritems():
            if isinstance(k, (list, tuple)):
                k = k[0]
            if k == event.text().upper():
                self.scene().processShortcut(f)





from dlg_grid_ui import *
import smartside.signal as smartsignal


class GridDialog(QtGui.QDialog, Ui_dlg_grid, smartsignal.SmartSignal):

    def __init__(self, data, parent=None):
        super(GridDialog, self).__init__(parent)
        self.setupUi(self)
        self.auto_connect()

    def _on_edt_snap_comp__textChanged(self):
        self.sel_snap_comp.setCurrentIndex(1)
    def _on_edt_snap_all__textChanged(self):
        self.sel_snap_all.setCurrentIndex(1)
    def _on_edt_grid1__textChanged(self):
        self.sel_grid1.setCurrentIndex(1)
    def _on_edt_grid2__textChanged(self):
        self.sel_grid2.setCurrentIndex(1)

    @staticmethod
    def execute(data, parent=None):
        dialog = GridDialog(data, parent)
        result = dialog.exec_()
        return (result == QtGui.QDialog.Accepted), dialog.dump()














class BaseXedaScene(QtGui.QGraphicsScene):

    def __init__(self, config=None, *args, **kwargs):
        super(BaseXedaScene, self).__init__(*args, **kwargs)

        self.cfg = config

        self.procNames = {
            'grid': self.setGrid,
            'clearsel': self.clearSelection,
            'setorigin': self.setOrigin,
            'resetorigin': self.resetOrigin,
            # 'rotate': self.
            # 'delete': self.
            }

    def processShortcut(self, name):
        print name
        if name in self.procNames:
            self.procNames[name](shortcut=True)

    def setGrid(self, **kwargs):
        ok, grid = GridDialog.execute(self)
        if ok:
            print 1

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











class SCHScene(BaseXedaScene):

    def __init__(self, *args, **kwargs):
        super(SCHScene, self).__init__(*args, **kwargs)

    # def addPart(self, i):
    #     print 'addPart'
    # def addPower(self, i):
    #     print 'addPower'
    # def addText(self, i):
    #     print 'addText'
    # def addLine(self, i):
    #     print 'addLine'
    # def addArc(self, i):
    #     print 'addArc'
    # def addJunction(self, i):
    #     print 'addJunction'
    # def addTrace(self, i):
    #     print 'addTrace'









class BaseXedaItem(QtGui.QGraphicsItem):

    def __init__(self):
        super(BaseXedaItem, self).__init__()

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)

        self._x_selected = False

    def boundingRect(self):
        raise NotImplementedError()

    def paint(self, painter, option, widget):
        raise NotImplementedError()

    def inspect(self):
        raise NotImplementedError()

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

    def getbyname(self, name):
        o = getattr(self, name, None)
        if o:
            if isinstance(o, QtGui.QWidget):
                return o
        return None

    def _toBase(self, val):
        g = re.match(r'^\s*([+-]?\d+[,.]?\d*|[+-]?[.,]\d+)\s*(mm|in|mils?|cm)?\s*$', val)
        if g:
            v = float(g.group(1))
            unit = g.group(2)
            if unit == 'mil' or unit == 'mils': return int(v)
            if unit == 'in': return int(v*1000.0)
            if unit == 'mm': return int(v*39.37)
            if unit == 'cm': return int(v*393.7)
            return 0

    def _fromBase(self, val, dest='mil'):
        if val:
            v = float(val)
            if dest == 'mil' or dest == 'mils': return '{:.0f} mil'.format(v)
            if dest == 'in': return '{:.0f} in'.format(v/1000.0)
            if dest == 'mm': return '{:.3f} mm'.format(v/39.37)
            if dest == 'cm': return '{:.3f} cm'.format(v/393.7)
        return ''

    def populate(self, data):
        print data
        self._data = data
        for t, f, ui in self._UI_XO:
            print ui, f, data[f]
            if t == 1: #absolute position
                self.getbyname(ui).setText(self._fromBase(data[f]))
            elif t == 2: #mm or mil dim
                self.getbyname(ui).setText(self._fromBase(data[f]))
            elif t == 3: #boolean
                self.getbyname(ui).setChecked(data[f])
            elif t == 4: #net
                pass
            elif t == 5: #layer
                pass
            elif t == 6: #
                pass

    def dump(self):
        for t, f, ui in self._UI_XO:
            if t == 1: #absolute position
                self._data[f] = self._toBase(self.getbyname(ui).text())
            elif t == 2: #mm or mil dim
                self._data[f] = self._toBase(self.getbyname(ui).text())
            elif t == 3: #boolean
                self._data[f] = self.getbyname(ui).isChecked()
            elif t == 4: #net
                pass
            elif t == 5: #layer
                pass
            elif t == 6: #
                pass
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

    def __init__(self, data, parent=None):
        super(PCBViaInspector, self).__init__(parent)
        self.setupUi(self)
        # self.setFixedSize(self.size())

        self.populate(data)

    @staticmethod
    def inspect(data, parent=None):
        dialog = PCBViaInspector(data, parent)
        result = dialog.exec_()
        return (result == QtGui.QDialog.Accepted), dialog.dump()









class PCBViaItem(BaseXedaItem):

    _x_name = 'VIA'

    def __init__(self):
        super(PCBViaItem, self).__init__()

        self._x_od = 50
        self._x_id = 28
        self._x_plated = False
        self._x_net = None
        self._x_start = 1
        self._x_end = 32
        self._x_tent = False
        self._x_mask = None

    def boundingRect(self):
        return QtCore.QRectF(-self._x_od/2, -self._x_od/2, self._x_od, self._x_od)

    def paint(self, painter, option, widget):
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200, 127), (self._x_od-self._x_id)/2))
        r = self._x_od-(self._x_od-self._x_id)/2
        painter.drawEllipse(QtCore.QRectF(-r/2, -r/2, r, r))

    def inspect(self):
        ok, data = PCBViaInspector.inspect(self.pack())
        if ok:
            self.unpack(data)
