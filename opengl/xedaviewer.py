# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.arrays.vbo as glvbo
import numpy as np
import transf
import shader
import math
import random
import bff
import layer


def generateVia(tri, x, y, o_d, i_d):

    o_r = o_d/2
    i_r = i_d/2

    res = 30

    delta = 2*math.pi/res

    ang = 0
    for i in range(res):

        tri.append((x, y))

        p = (x+math.cos(ang)*o_r, y+math.sin(ang)*o_r)
        pi2 = (x+math.cos(ang)*i_r, y+math.sin(ang)*i_r)
        tri.append(p)

        ang += delta
        p = (x+math.cos(ang)*o_r, y+math.sin(ang)*o_r)
        pi3 = (x+math.cos(ang)*i_r, y+math.sin(ang)*i_r)

        tri.append(p)

        #-----

        tri.append((x, y))
        tri.append(pi2)
        tri.append(pi3)


class XedaViewerBase(QtOpenGL.QGLWidget):

    ready = QtCore.Signal()
    cursor_event = QtCore.Signal(QtCore.QPoint)

    def __init__(self, parent=None):
        super().__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)

        self.setCursor(QtCore.Qt.BlankCursor)
        # self.unsetCursor()  #para mostrar o cursor denovo...
        # self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setMouseTracking(True)

        self._pan_pos = None
        self._cursor_pos = QtCore.QPoint()

        v = []
        for x in range(-100, 100, 2):
            for y in range(-100, 100, 2):
                generateVia(v, x*25.4e5, y*25.4e5, .1*25.4e6, .05*25.4e6)
        self.via_data = np.array(v, dtype='f')

        self.view = np.identity(4, dtype='f')
        transf.scale(self.view, 1e-8)
        self.projection = np.identity(4, dtype='f')

    def _generateGrid(self, w, h, dx, dy, color):
        g = []
        for x in range(int(w[0]), int(w[1]+1), int(dx)):
            g.append( (x, h[0], color) )
            g.append( (x, h[1], color) )
        for y in range(int(h[0]), int(h[1]+1), int(dy)):
            g.append( (w[0], y, color) )
            g.append( (w[1], y, color) )

        return np.array(g, dtype='f4, f4, i4')

    def minimumSizeHint(self):
        """Hint of the minimum size this widget accepts.
        """
        return QtCore.QSize(50, 50)

    # def sizeHint(self):
    #     return QtCore.QSize(400, 400)

    def initializeGL(self):
        """Event to initialize OpenGL context.

        Create shaders, VBOs and VAOs. Also link the layers to each VBO.
        """
        glClearColor(*(.1, .1, .1, 1))

        glEnable(GL_BLEND)
        # # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glBlendEquation(GL_MAX)
        # glfwWindowHint(GLFW_SAMPLES, 4)
        # glEnable(GL_MULTISAMPLE)
        # glEnable(GL_LINE_SMOOTH)
        # glEnable(GL_POLYGON_SMOOTH)
        # glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        # glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        self.main_shader = shader.ShaderProgram(codefile='shaders/main.glsl', link=True)


        self.top_layer = layer.Line(self, 4)
        for i in range(20):
            a = math.radians(i*360/20)
            self.top_layer.add(0, 0, 20*25.4e6*math.cos(a), 20*25.4e6*math.sin(a), .1*25.4e6, 'bunda')

        self.bottom_layer = layer.Line(self, 5)
        for x in range(-100, 100, 10):
            for y in range(-100, 100, 5):
                self.bottom_layer.add(x*25.4e5, y*25.4e5, x*25.4e5+.25*25.4e6, y*25.4e5+.25*25.4e6, .014*25.4e6, 'meleca')

        print(self.top_layer._vbo.data)

        g1 = self._generateGrid((-10*25.4e6, 10*25.4e6), (-10*25.4e6, 10*25.4e6), .1*25.4e6, .1*25.4e6, 1)
        g2 = self._generateGrid((-10*25.4e6, 10*25.4e6), (-10*25.4e6, 10*25.4e6), 1*25.4e6, 1*25.4e6, 2)

        self.grid_vbo = glvbo.VBO(np.append(g1, g2))
        # self.grid_vbo = glvbo.VBO(g2)

        self.via_vbo = glvbo.VBO(self.via_data)

        self.font = bff.BFF('arial14.bff')

        self.ready.emit()

    def paintGL(self):
        """Event to repaint the scene.
        """
        glClear(GL_COLOR_BUFFER_BIT)

        pallete = np.array([(1,1,1,1), (.4,.4,.1,1), (.6,.6,.6,1), (1,1,1,1),
                            (1,0,0,1), (0,0,1,1), (1,0,1,1), (1,0,1,1)], dtype='f')

        with self.main_shader:
            glUniformMatrix4fv(self.main_shader.uniform['view'], 1, GL_FALSE, self.view)
            glUniformMatrix4fv(self.main_shader.uniform['projection'], 1, GL_FALSE, self.projection)
            glUniform4fv(self.main_shader.uniform['palette'], 8, pallete)

            #grid
            with self.grid_vbo:
                glEnableVertexAttribArray(0)
                glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 12, self.grid_vbo)
                glEnableVertexAttribArray(1)
                glVertexAttribIPointer(1, 1, GL_INT, 12, self.grid_vbo+8)
                glDrawArrays(GL_LINES, 0, len(self.grid_vbo))

            # linhas
            glBlendEquation(GL_MAX)

            self.top_layer.drawItems()
            self.bottom_layer.drawItems()

            # # vias
            # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            # glBlendEquation(GL_FUNC_ADD)

            # with self.via_vbo:
            #     glEnableVertexAttribArray(0)
            #     glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self.via_vbo.data[0].nbytes, self.via_vbo)
            #     # glUniform4f(self.main_shader.uniform['color'], .5, .5, .5, .6)
            #     glDrawArrays(GL_TRIANGLES, 0, len(self.via_data))

            # textos

            #cursor
            # TODO declarar essa coisa como stream!!
            c = np.array([(-1e9, self._cursor_pos.y(), 0), (1e9, self._cursor_pos.y(), 0),
                         (self._cursor_pos.x(), 1e9, 0), (self._cursor_pos.x(), -1e9, 0)], dtype='f4, f4, i4')
            vbo = glvbo.VBO(c)
            with vbo:
                glEnableVertexAttribArray(0)
                glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 12, vbo)
                glEnableVertexAttribArray(1)
                glVertexAttribIPointer(1, 1, GL_INT, 12, vbo+8)
                glDrawArrays(GL_LINES, 0, 4)

    def resizeGL(self, width, height):
        """Event to adjust viewport and projection when widget is resized.

        Args:
            width (int): new widget width
            height (int): new widget height
        """
        glViewport(0, 0, width, height)
        self.window = QtCore.QSize(width, height)
        # scale = 1/6e6 #self.projection[0, 0]
        self.projection = transf.ortho(-width/height, width/height, -1, 1, -1, 1)
        # print(self.projection[0,0])
        # transf.scale(self.projection, scale)
        # print(self.projection[0,0])

# glMatrixMode(GL_PROJECTION);
# glLoadIdentity();
# if (w <= h)
#     glOrtho(-4.0, 4.0, -3.0 * (GLfloat) h / (GLfloat) w, 5.0 * (GLfloat) h / (GLfloat) w, -10.0, 10.0);
# else
#     glOrtho(-4.0 * (GLfloat) w / (GLfloat) h, 4.0 * (GLfloat) w / (GLfloat) h, -3.0, 5.0, -10.0, 10.0);



    def mapToScene(self, point):
        """Map a screen coordinate to scene coordinate.

        Args:
            point (QPoint): screen point

        Returns:
            QPoint: scene point
        """
        pass

    def mapFromScene(self, point):
        """Map a scene coordinate to screen coordinate.

        Args:
            point (QPoint): scene coordinate

        Returns:
            QPoint: screen coordinate
        """
        pass

    def wheelEvent(self, event):
        """Event to handle zoom.
        """
        if event.orientation() == QtCore.Qt.Orientation.Vertical:
            if event.delta() > 0:
                self.zoomIn()
            else:
                self.zoomOut()
            print(self.projection[0,0], self.view[0,0])
            event.accept()
        else:
            event.ignore()

    def enterEvent(self, event):
        pass
        # self.setFocus()

    def leaveEvent(self, event):
        pass
        # super().leaveEvent(event)
        # self._snap_pos = None
        # self.repaint()
        # self.clearFocus()

    def mousePressEvent(self, event):
        # super().mousePressEvent(event)
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pass
            # i = self._discoverItem(None)
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

        x = 2*event.x()/self.window.width()-1
        y = -2*event.y()/self.window.height()+1

        x /= self.view[0, 0]*self.projection[0, 0]
        y /= self.view[0, 0]

        snap = .025*25.4e6

        self._cursor_pos = QtCore.QPoint((x//snap)*snap, (y//snap)*snap)

        self.cursor_event.emit(self._cursor_pos)

        self.repaint()


        # super().mouseMoveEvent(event)
        # self._mouse_pos = self.mapToScene(event.pos())
        # n = self.scene.proj.snap
        # self._snap_pos = QtCore.QPoint((self._mouse_pos.x()//n)*n, (self._mouse_pos.y()//n)*n)
        # # self.moveEvent.emit(self._mouse_pos)
        # self.moveEvent.emit(self._snap_pos-self.origin)
        # self.repaint()
        #self._discoverItem(None) #TODO quando tiver mas de um item isso sera assincrono.... fudeu
        if self._pan_pos:
            p = event.pos()-self._pan_pos
            self._pan_pos = event.pos()
            s = self.view[0,0]
            print(s, 1/s)
            transf.translate(self.view, p.x()*s, -p.y()*s, 0)
            self.repaint()
            # self.viewRect.setLeft(min(self.viewSize.width()-self.viewRect.width(),
            #                           max(0, self.viewRect.left()-p.x()/self.scale)))
            # self.viewRect.setTop(min(self.viewSize.height()-self.viewRect.height(),
            #                          max(0, self.viewRect.top()-p.y()/self.scale)))
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        # super().mouseReleaseEvent(event)
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

    def zoomIn(self, pos=None):
        """Zoom a single step in.

        Args:
            pos (QPoint, optional): center of the zoom in screen coordinate. If `None` (default), the zoom center
                will be at the widget center.
        """
        transf.scale(self.view, 1.25)
        self.repaint()
        pass
        # if self.scale < 1.6:
        #     self.scale *= 1.25
        #     cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        #     if not self.contentsRect().contains(cursor):
        #         cursor = self.contentsRect().center()
        #     self.matchPoints(self._mouse_pos, cursor)

    def zoomOut(self, pos=None):
        """Zoom a single step out.

        Args:
            pos (QPoint, optional): center of the zoom in screen coordinate. If `None` (default), the zoom
                center will be the widget center.
        """
        transf.scale(self.view, 1/1.25)
        self.repaint()
        pass
        # if self.scale > .04:
        #     self.scale /= 1.25
        #     cursor = self.mapFromGlobal(QtGui.QCursor.pos())
        #     if not self.contentsRect().contains(cursor):
        #         cursor = self.contentsRect().center()
        #     self.matchPoints(self._mouse_pos, cursor)

    def zoomFit(self):
        """Zoom to fit whole scene.
        """
        pass
        #TODO ajustar a escala....
        # self.matchPoints(self.scene.getBounding().center(), self.contentsRect().center())

    def refreshView(self):
        """Repaint whole scene.
        """
        pass

    def setGrid(self, grid1, grid2, weak=False):
        """Set the grid size.

        Args:
            grid1 (float): grid 1 size. > 1 to disable it.
            grid2 (float): grid 2 size. > 1 to disable it.
            weak (bool, optional): If True the grid will fade as it zoom out.
        """
        pass
        # self.scene.proj.grid1 = grid1
        # self.scene.proj.grid2 = grid2
        # self.scene.proj.weakgrid = weak
        # self.repaint(True)

    def setSnap(self, snap):
        pass
        # self.scene.proj.snap = snap
        # self.repaint()

    def useRuler(self, pos):
        """Display the meassuring ruler.

        Args:
            pos (QPoint): center of the ruler in screen coordinate.
        """
        pass
        # self._rulerOrigin = self._snap_pos
        # self.repaint()




class XedaPCBViewer(XedaViewerBase):
    pass
