# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui
import re
import config
from collections import namedtuple
import math
import time


# tpaste
# tglue
# tpeel  - areas aqui definem local de cobertura plastica removivel para protecao durante a solda
# theatsink  - areas aqui definemcobertura com tinta condutora termica
# tsilk
# tcarbon  - linhas aqui incluem: trilha no top, abertura no mask e no carbon propriamente
# tmask
# top

layersId = {
    0: 'edge',
    1: 'keepout',
    2: 'tpaste',
    3: 'tglue',
    4: 'tsilk',
    5: 'tmask',
    6: 'drill',
    10: 'top',
    11: 'l1',
    12: 'l2',
    13: 'l3',
    14: 'l4',
    15: 'l5',
    16: 'l6',
    42: 'bottom',
    43: 'bmask',
    44: 'bsilk',
    45: 'bglue',
    46: 'bpaste',
    47: 'mec1',
    48: 'mec2',
    49: 'mec3',
    50: 'mec4',
    51: 'mec5'
    }

layersId.update({v: k for k, v in layersId.items()})


Point = namedtuple('Point', 'x y')


def dimConvert(val, out='mils', default=None):

    if not default:
        default = 'mils'   #TODO ler isso da configuracao!!!!

    if isinstance(val, str):
        g = re.match(r'^\s*([+-]?\d+[,.]?\d*|[+-]?[.,]\d+)\s*(mm|in|mils?|cm)?\s*$', val)
        if g:
            v = float(g.group(1))
            unit = g.group(2) if g.group(2) else default
        else:
            return 0
    else:
        v = float(val)
        unit = default

    if unit == 'mil' or unit == 'mils': pass
    elif unit == 'in': v *= 1000.0
    elif unit == 'mm': v *= 39.37
    elif unit == 'cm': v *= 393.7
    else: v = 0

    if out == 'mil' or out == 'mils': return v
    elif out == 'in': return v/1000.0
    elif out == 'mm': return v/39.37
    elif out == 'cm': return v/393.7

    return 0

def dimConvertText(val, out='mils'):
    return '{:.2f} {}'.format(dimConvert(val, out), out)









class XedaViewer(QtGui.QWidget):

    moveEvent = QtCore.Signal(tuple)
    hoverEvent = QtCore.Signal(tuple)
    commandEvent = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setCursor(QtCore.Qt.BlankCursor)
        # self.unsetCursor()  #para mostrar o cursor denovo...
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setMouseTracking(True)

        self._pan_pos = None
        self._mouse_pos = None
        self.doSnap = True
        self._snap_pos = None

        self.scene = None

        self.origin = QtCore.QPoint(2000, 1000)

        self._rulerOrigin = None

        self.viewSize = QtCore.QSize(0, 0)
        self.viewRect = QtCore.QRectF(0, 0, 0, 0)

        self.previousRect = None

        self.scale = .1

        self.forcePaint = True   #ignore all cache in next paint

    def setScene(self, scene):
        self.scene = scene
        self.viewSize = QtCore.QSize(scene.cfg.dim[0], scene.cfg.dim[1])
        self.scene.setSceneSize(self.viewSize)
        self.initShortcuts()

    def repaint(self, force=False):
        self.forcePaint = force
        super().repaint()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        # qp.setRenderHint(QtGui.QPainter.Antialiasing)

        t1 = time.time()

        self.viewRect.setWidth(e.rect().width()/self.scale),
        self.viewRect.setHeight(e.rect().height()/self.scale)

        t = QtGui.QTransform(self.scale, 0, 0, self.scale,
                             -self.viewRect.left()*self.scale,
                             -self.viewRect.top()*self.scale)

        if self.previousRect != self.viewRect or self.forcePaint:
            self.previousRect = QtCore.QRectF(self.viewRect)
            self._gridImage = QtGui.QPixmap(e.rect().width(), e.rect().height())
            p = QtGui.QPainter(self._gridImage)
            # p.setRenderHint(QtGui.QPainter.Antialiasing)
            p.setTransform(t)
            p.translate(self.origin)
            self._drawGrid(p, self.viewRect.translated(-self.origin))
        qp.drawPixmap(0, 0, self._gridImage)

        t2 = time.time()

        # qp.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        for l in self.scene.proj.layers.active:
            qp.drawPixmap(0, 0, self.scene.renderLayer(t, l, self.viewRect, e.rect(), self.forcePaint))

        t3 = time.time()

        qp.setTransform(t)
        # qp.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
        self._drawCursor(qp, self.viewRect)

        t4 = time.time()

        qp.end()

        # print('grid= {:f}, layers= {:f}, cursor= {:f}, total= {:f}'.format(t2-t1, t3-t2, t4-t3, t4-t1))

        self.forcePaint = False

    def _drawGrid(self, paint, rect):
        paint.fillRect(rect, QtGui.QColor(*self.scene.cfg.colors.back))

        def doGrid(color, size):
            if size*self.scale > 5:    # if grid is too small, ignore it
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

        paint.setPen(QtGui.QPen(QtGui.QColor(*self.scene.cfg.colors.origin), 0))
        paint.setBrush(QtGui.QBrush(QtGui.QColor(*self.scene.cfg.colors.origin)))
        paint.drawEllipse(QtCore.QRectF(-25, -25, 50, 50))


    def _drawCursor(self, paint, rect):
        if self._snap_pos:
            paint.setPen(QtGui.QPen(QtGui.QColor(*self.scene.cfg.colors.guide)))
            pos = self._snap_pos if self.doSnap else self._mouse_pos
            paint.drawLine(rect.left(), pos.y(), rect.right(), pos.y())
            paint.drawLine(pos.x(), rect.top(), pos.x(), rect.bottom())

            if self._rulerOrigin:
                paint.setFont(QtGui.QFont('Helvetica', 10/self.scale))
                unit = self.scene.proj.units

                paint.setPen(QtGui.QPen(QtGui.QColor('red'), 0))
                paint.drawLine(self._rulerOrigin.x(), self._rulerOrigin.y(), self._snap_pos.x(), self._rulerOrigin.y())
                dx = self._snap_pos.x()-self._rulerOrigin.x()
                paint.drawText(rect.left()+5/self.scale, rect.top()+10/self.scale, '{:.2f} {}'.format(dimConvert(abs(dx), unit), unit))

                paint.setPen(QtGui.QPen(QtGui.QColor('cyan'), 0))
                paint.drawLine(self._rulerOrigin.x(), self._rulerOrigin.y(), self._rulerOrigin.x(), self._snap_pos.y())
                dy = self._snap_pos.y()-self._rulerOrigin.y()
                paint.drawText(rect.left()+5/self.scale, rect.top()+25/self.scale, '{:.2f} {}'.format(dimConvert(abs(dy), unit), unit))

                paint.setPen(QtGui.QPen(QtGui.QColor('green'), 0))
                paint.drawLine(self._rulerOrigin.x(), self._rulerOrigin.y(), self._snap_pos.x(), self._snap_pos.y())
                paint.drawText(rect.left()+5/self.scale, rect.top()+40/self.scale, '{:.2f} {}'.format(dimConvert(pow(pow(dx, 2)+pow(dy, 2), .5), unit), unit))

                paint.setPen(QtGui.QPen(QtGui.QColor('yellow'), 0))
                a = abs(math.degrees(math.atan2(dy, dx)))%90
                #TODO desenhar um pie
                paint.drawText(rect.left()+5/self.scale, rect.top()+55/self.scale, '{:.2f} \u00b0'.format(a))

                paint.setPen(QtGui.QPen(QtGui.QColor('magenta'), 0))
                #TODO desenhar um pie
                paint.drawText(rect.left()+5/self.scale, rect.top()+70/self.scale, '{:.2f} \u00b0'.format(90-a))

    def mapToScene(self, point):
        return QtCore.QPoint(point.x()/self.scale+self.viewRect.left(),
                             point.y()/self.scale+self.viewRect.top()
                             )

    def mapFromScene(self, point):
        p = QtCore.QPoint((point.x()-self.viewRect.left())*self.scale, (point.y()-self.viewRect.top())*self.scale)
        if self.geometry().contains(p):
            return p
        return None

    def wheelEvent(self, event):
        if event.orientation() == QtCore.Qt.Orientation.Vertical:
            if event.delta() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
            event.accept()
        else:
            event.ignore()

    def enterEvent(self, event):
        self.setFocus()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self._snap_pos = None
        self.repaint()
        self.clearFocus()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            i = self._discoverItem(None)
            #TODO quando tiver mas de um item isso sera assincrono.... fudeu

            # um click sem nada abaixo inicia um rubber para selecionar items
            # com um item abaixo coloca ele em modo de destaque
            # com um item abaixo e shift alterna estado dele na selecao
            # com um item e move sem soltar, move o item ou a selecao caso ele faca parte delta
            # se tiver mais de um item entao motra menu perguntando qual
            # ignora tal menu se algum dos items estiver na lista de prioridades



        elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._pan_pos = event.pos()
            event.accept()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            m = QtGui.QMenu(self)
            m.addAction('texte')
            m.addAction('texte')
            m.addSeparator()
            m.addAction('teste com xix??')
            m.exec_(event.globalPos())
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self._mouse_pos = self.mapToScene(event.pos())
        n = self.scene.proj.snap
        self._snap_pos = QtCore.QPoint((self._mouse_pos.x()//n)*n, (self._mouse_pos.y()//n)*n)
        # self.moveEvent.emit(self._mouse_pos)
        self.moveEvent.emit(self._snap_pos-self.origin)
        self.repaint()
        #self._discoverItem(None) #TODO quando tiver mas de um item isso sera assincrono.... fudeu
        if self._pan_pos:
            p = event.pos()-self._pan_pos
            self._pan_pos = event.pos()
            self.viewRect.setLeft(min(self.viewSize.width()-self.viewRect.width(),
                                      max(0, self.viewRect.left()-p.x()/self.scale)))
            self.viewRect.setTop(min(self.viewSize.height()-self.viewRect.height(),
                                     max(0, self.viewRect.top()-p.y()/self.scale)))
            self.repaint()
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
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
            elif event.button() == QtCore.Qt.MouseButton.MiddleButton:
                pass

                #TODO mostra uma regua, com hip e angulo

    def initShortcuts(self):
        self.shortcuts = []
        for f, k in self.scene.cfg.shortcuts._d.items():
            if k:
                if isinstance(k, (list, tuple)):
                    k = k[0]
                self.shortcuts.append( (f, QtGui.QKeySequence(k)) )
                print(f,k)

    def keyPressEvent(self, event):
        # print(event.text(), event.key(), event.modifiers(), event.type())

        if event.key() == QtCore.Qt.Key_Escape:
            self._rulerOrigin = None
            self.repaint()
        elif event.key() == QtCore.Qt.Key_Up: pass
        elif event.key() == QtCore.Qt.Key_Down: pass
        elif event.key() == QtCore.Qt.Key_Left:
            if self._snap_pos.x() > 0:
                self._snap_pos.setX(max(0, self._snap_pos.x()-self.scene.proj.snap))
                QtGui.QCursor.setPos(self.mapToGlobal(self._snap_pos))
                self.repaint()
        elif event.key() == QtCore.Qt.Key_Right: pass
        else:
            k = QtGui.QKeySequence(event.modifiers()|event.key())
            try:
                print(k.toString())
            except: pass
            for f, s in self.shortcuts:
                if s.matches(k):
                    print ('foi:', f, s.toString())
                    if hasattr(self, f):
                        getattr(self, f)()
                    elif hasattr(self.scene, f):
                        getattr(self.scene, f)()
                    else:
                        self.commandEvent.emit(f)

    def setOrigin(self, pos=None):
        if pos is -1:
            pos = QtCore.QPoint(0, 0)
        elif not pos:
            pos = self._snap_pos
        self.origin = pos
        self.repaint(True)
        self.moveEvent.emit(self._snap_pos-self.origin)

    def resetOrigin(self):
        self.setOrigin(-1)

    def matchPoints(self, scene, widget):
        self.viewRect.setLeft(min(self.viewSize.width()-self.viewRect.width(),
                                  max(0, scene.x()-widget.x()/self.scale)))
        self.viewRect.setTop(min(self.viewSize.height()-self.viewRect.height(),
                                 max(0, scene.y()-widget.y()/self.scale)))
        self.repaint()

    def zoomIn(self):
        if self.scale < 1.6:
            self.scale *= 1.25
            cursor = self.mapFromGlobal(QtGui.QCursor.pos())
            if not self.contentsRect().contains(cursor):
                cursor = self.contentsRect().center()
            self.matchPoints(self._mouse_pos, cursor)

    def zoomOut(self):
        if self.scale > .04:
            self.scale /= 1.25
            cursor = self.mapFromGlobal(QtGui.QCursor.pos())
            if not self.contentsRect().contains(cursor):
                cursor = self.contentsRect().center()
            self.matchPoints(self._mouse_pos, cursor)

    def zoomFit(self):
        #TODO ajustar a escala....
        self.matchPoints(self.scene.getBounding().center(), self.contentsRect().center())

    def refreshView(self):
        self.repaint(True)

    def setGrid(self, grid1, grid2, weak=False):
        self.scene.proj.grid1 = grid1
        self.scene.proj.grid2 = grid2
        self.scene.proj.weakgrid = weak
        self.repaint(True)

    def setSnap(self, snap):
        self.scene.proj.snap = snap
        self.repaint()

    def gridDialog(self):
        ok, g = GridDialog.execute({}, self)
        if ok:
            self.setSnap(g['snap'])
            self.setGrid(g['grid1'], g['grid2'], g['weak'])

    def useRuler(self):
        self._rulerOrigin = self._snap_pos
        self.repaint()

    def setUnit(self, unit):
        self.scene.proj.units = unit
        self.repaint()
        self.moveEvent.emit(self._snap_pos-self.origin)

    def cycleUnit(self):
        if self.scene.proj.units == 'mils':
            self.setUnit('mm')
        elif self.scene.proj.units == 'mm':
            self.setUnit('in')
        elif self.scene.proj.units == 'in':
            self.setUnit('cm')
        else:
            self.setUnit('mils')









from dlg_grid_ui import *
import smartside.signal as smartsignal


class GridDialog(QtGui.QDialog, Ui_dlg_grid, smartsignal.SmartSignal):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.auto_connect()
        self.data = None

    def _on_edt_snap_comp__textChanged(self): self.sel_snap_comp.setCurrentIndex(0)
    def _on_edt_snap_all__textChanged(self): self.sel_snap_all.setCurrentIndex(0)
    def _on_edt_grid1__textChanged(self): self.sel_grid1.setCurrentIndex(0)
    def _on_edt_grid2__textChanged(self): self.sel_grid2.setCurrentIndex(0)
    def _on_sel_snap_comp__currentIndexChanged(self):
        if self.sender().currentIndex() == 1: self.edt_snap_comp.setFocus()
    def _on_sel_snap_all__currentIndexChanged(self):
        if self.sender().currentIndex() == 1: self.edt_snap_all.setFocus()
    def _on_sel_grid1__currentIndexChanged(self):
        if self.sender().currentIndex() == 1: self.edt_grid1.setFocus()
    def _on_sel_grid2__currentIndexChanged(self):
        if self.sender().currentIndex() == 1: self.edt_grid2.setFocus()

    def _on_btn_ok__accepted(self):
        self.data = {}

        self.data['snap'] = dimConvert(self.sel_snap_all.currentText())
        if self.data['snap'] == 0:
            self.data['snap'] = dimConvert(self.edt_snap_all.text())
            if self.data['snap'] == 0:
                return

        self.data['grid1'] = dimConvert(self.sel_grid1.currentText())
        if self.data['grid1'] == 0:
            self.data['grid1'] = dimConvert(self.edt_grid1.text())
            if self.data['grid1'] == 0:
                return

        self.data['grid2'] = dimConvert(self.sel_grid2.currentText())
        if self.data['grid2'] == 0:
            self.data['grid2'] = dimConvert(self.edt_grid2.text())
            if self.data['grid2'] == 0:
                return

        self.data['weak'] = self.chk_weak.isChecked()

        self.accept()

    @staticmethod
    def execute(data, parent=None):
        dialog = GridDialog(data, parent)
        result = dialog.exec_()
        return (result == QtGui.QDialog.Accepted), dialog.data













class BaseXedaScene(object):

    def __init__(self, config, project, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cfg = config
        self.proj = project

        self.items = []

        self._layerImage = {}

        self.size = QtCore.QSize(0, 0)

        self.blah = None

    def setSceneSize(self, size):
        self.size = size

    def renderLayer(self, transf, layer, sceneRect, rect, force):
        if sceneRect != self.blah or force:
            self.blah = QtCore.QRectF(sceneRect)
            self._toshow = self.getItems(sceneRect)
        toshow = self._toshow

        if layer not in self._layerImage or sceneRect != self._layerImage[layer][1] or force:
            print('processando layer', layer)
            img = QtGui.QPixmap(rect.width(), rect.height())
            img.fill(QtGui.QColor(0, 0, 0, 0))
            p = QtGui.QPainter(img)
            p.setRenderHint(QtGui.QPainter.Antialiasing)
            p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
            p.setTransform(transf)
            self._layerImage[layer] = (img, QtCore.QRectF(sceneRect))

            # toshow = self.getItems(sceneRect)

            for i in toshow:
                if i._x_layer in (-1, layer):
                    i.paint(p, layer)

            if layer == 10:
                p.setPen(QtGui.QPen(QtGui.QColor(128, 128, 255, 127),
                      10,
                      QtCore.Qt.SolidLine,
                      QtCore.Qt.RoundCap,
                      QtCore.Qt.RoundJoin))
                p.drawLine(1000, 1000, 2000, 3000)
            if layer == 42:
                p.setPen(QtGui.QPen(QtGui.QColor(255, 128, 128, 127),
                      20,
                      QtCore.Qt.SolidLine,
                      QtCore.Qt.RoundCap,
                      QtCore.Qt.RoundJoin))
                p.drawLine(0,0,1000,1000)
        return self._layerImage[layer][0]

    def invalidate(self, layer):
        # print('marcando layer como sujo: ', layer)
        if layer == -1:
            self._layerImage = {}
        if layer in self._layerImage:
            del self._layerImage[layer]

        #TODO forcar repaint do viewer

    def addItem(self, item):
        self.items.append(item)
        self.invalidate(item._x_layer)

    def getItems(self, rect=None):
        if rect == None:
            rect = QtCore.QRect(0, 0, *self.size)

        inside = []
        for i in self.items:
            if rect.contains(i.getBounding()):#, proper=True):
                inside.append(i)
        print('total items: ', len(inside))
        return inside

    def removeItem(self, item):
        print('removeItem')

    def rotateItem(self, item):
        print('rotateItem')

    def getBounding(self):
        b = QtCore.QRectF()
        for i in self.items:
            print(i.getBounding())
            b = b.united(i.getBounding())
        print('tamanho total: ', b)
        return b









class SCHScene(BaseXedaScene):
    pass

class PCBScene(BaseXedaScene):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def cmdPlace(self, **kwargs):
        print('place!!!')

    def addVia(self, data, mode=1):
        self.addItem(PCBViaItem(self, data))

    # def addString(self, data, mode=1):
    #     self.addItem(PCBStringItem(data))

    # def addText(self, i):
    #     print('addText')
    # def addVia(self, i):
    #     print('addVia')
    # def addPad(self, i):
    #     print('addPad')
    # def addLine(self, i):
    #     print('addLine')
    # def addArc(self, i):
    #     print('addArc')
    # def addArea(self, i):
    #     print('addArea')
    # def addPart(self, i):
    #     print('addPart')
    # def setLayer(self, i):
    #     print('setLayer')
    # def addTrace(self, i):
    #     print('addTrace')














class BaseXedaItem(object):

    def __init__(self, parent, data=None):
        super().__init__()

        self._x_selected = False
        self._x_x = 0
        self._x_y = 0

        self.parent = parent

        self.isGhost = False
        self.inEdit = False
        self.drawClearance = True

        if data:
            self.unpack(data)

    def getBounding(self):
        raise NotImplementedError()

    def paint(self, painter, layer):
        if self._x_selected:
            self.paintSelected(painter, layer)
        elif self.inEdit:
            self.paintEdit(painter, layer)
        elif self.isGhost:
            self.paintGhost(painter, layer)
        else:
            self.paintNormal(painter, layer)

    def paintNormal(self, painter, layer):
        raise NotImplementedError()

    def paintSelected(self, painter, layer): pass
    def paintEdit(self, painter, layer): pass
    def paintGhost(self, painter, layer): pass

    def inspect(self):
        ok, data = self.myInspector.inspect(self.pack())
        if ok:
            self.unpack(data)

    def invalidate(self):
        self.parent.invalidate(self._x_layer)

    def setPos(self, x, y):
        self._x_x = x
        self._x_y = y
        self.invalidate()

    def pack(self):
        d = {}
        for m in dir(self):
            if m.startswith('_x_'):
                d[m[3:]] = getattr(self, m)
        # d['x'] = self.x()
        # d['y'] = self.y()
        return d

    def unpack(self, data):
        # self.setPos(data['x'], data['y'])
        # del data['x']
        # del data['y']
        for k, v in data.items():
            setattr(self, '_x_'+k, v)
        self.invalidate()










class BaseXedaInspector(QtGui.QDialog):

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.populate(data)

    def getByName(self, name):
        o = getattr(self, name, None)
        if o:
            if isinstance(o, QtGui.QWidget):
                return o
        return None

    def populate(self, data):
        print(data)
        self._data = data
        for t, f, ui in self._UI_XO:
            print(ui, f, data[f])
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
        print(self._data)
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
    _x_layer = 6
    myInspector = PCBViaInspector

    def __init__(self, *args, **kwargs):

        self._x_od = 50
        self._x_id = 28
        self._x_plated = False
        self._x_net = '3V3'
        self._x_start = 1
        self._x_end = 32
        self._x_tent = False
        self._x_mask = None

        super().__init__(*args, **kwargs)

    def getBounding(self):
        if self.drawClearance:
            r = QtCore.QRectF(-self._x_od/2-10, -self._x_od/2-10, self._x_od+20, self._x_od+20)
        else:
            r = QtCore.QRectF(-self._x_od/2, -self._x_od/2, self._x_od, self._x_od)

        return r.translated(self._x_x, self._x_y)

    def _drawVia(self, p, color):
        p.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        p.setBrush(QtGui.QBrush(color))
        r = QtCore.QRectF(-self._x_od/2, -self._x_od/2, self._x_od, self._x_od).translated(self._x_x, self._x_y)
        p.drawEllipse(r)
        p.drawEllipse(QtCore.QRectF(-self._x_id/2, -self._x_id/2, self._x_id, self._x_id).translated(self._x_x, self._x_y))

        p.setPen(QtGui.QPen('red'))
        p.drawText(r, QtCore.Qt.AlignCenter, self._x_net)

        if self.drawClearance:
            p.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
            p.setPen(QtGui.QPen(color))
            p.drawEllipse(self.getBounding())

    def paintNormal(self, painter, layer):
        self._drawVia(painter, QtGui.QColor(200, 200, 200, 127))

    def paintSelected(self, painter, layer): pass
    def paintEdit(self, painter, layer): pass
    def paintGhost(self, painter, layer): pass


