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

def generateVia(data, x, y, o_d, i_d, degenerate=None):

    o_r = o_d/2
    i_r = i_d/2

    res = 24

    delta = 2*math.pi/res

    for r in range(res+1):
        ang = delta*r
        c = math.cos(ang)
        s = math.sin(ang)

        p1 = [x+c*o_r, y+s*o_r]
        p2 = [x+c*i_r, y+s*i_r]

        if degenerate:
            data.append(degenerate)
            data.append(p1)
            degenerate = None

        data.append(p1)
        data.append(p2)

    return p2


class XedaViewerBase(QtOpenGL.QGLWidget):

    ready = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)

        self.lastPos = QtCore.QPoint()

        # self.line_data = np.array([
        #                       [0, 0, -5.5*2.54e6, 0,   0., 0., 1., .6,   1*2.54e6],
        #                       [0, 0, 0, 5.5*2.54e6,   1., 0., 0., .6,   .5*2.54e6],
        #                       [0, 0, 0, -5.5*2.54e6,   1., 1., 0, .6,   .6*2.54e6],
        #                       [-5, 0, 0, -5.5*2.54e6,   1., 1., 0, .6,   .6*2.54e6],
        #                       [5.5*2.54e6, -5.5*2.54e6, -5.5*2.54e6, 0,   0., 0., 1., .6,   1*2.54e6],
        #                       ], dtype='f')

        v = []
        degenerate = None
        for x in range(-100, 100, 4):
            for y in range(-100, 100, 4):
                degenerate = generateVia(v, x*2.54e5, y*2.54e5, .045*2.54e6, .028*2.54e6, degenerate)
        self.via_data = np.array(v, dtype='f')
        print(self.via_data.shape)

        l = []
        for x in range(-100, 100, 4):
            for y in range(-100, 100, 4):
                l.append([x*2.54e5, y*2.54e5, x*2.54e5+.8*2.54e6, y*2.54e5+.8*2.54e6,    random.random(), random.random(), random.random(), .6,   .014*2.54e6])
        self.line_data = np.array(l, dtype='f')

        self.grid1_data = self._generateGrid((-10*2.54e6, 10*2.54e6), (-10*2.54e6, 10*2.54e6), .1*2.54e6, .1*2.54e6)
        self.grid2_data = self._generateGrid((-10*2.54e6, 10*2.54e6), (-10*2.54e6, 10*2.54e6), 1*2.54e6, 1*2.54e6)

        self.view = np.identity(4, dtype='f')
        transf.scale(self.view, 1e-7)
        self.projection = np.identity(4, dtype='f')

    def _generateGrid(self, w, h, dx, dy):
        g = []
        for x in range(int(w[0]), int(w[1]), int(dx)):
            g.append([x, h[0]])
            g.append([x, h[1]])
        for y in range(int(h[0]), int(h[1]), int(dy)):
            g.append([w[0], y])
            g.append([w[1], y])

        return np.array(g, dtype='f')

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

        self.grid_shader = shader.ShaderProgram(codefile='shader/grid.glsl', link=True)
        self.line_shader = shader.ShaderProgram(codefile='shader/line.glsl', link=True)
        self.via_shader = shader.ShaderProgram(codefile='shader/via.glsl', link=True)

        self.grid1_vbo = glvbo.VBO(self.grid1_data)
        self.grid2_vbo = glvbo.VBO(self.grid2_data)
        self.line_vbo = glvbo.VBO(self.line_data)
        self.via_vbo = glvbo.VBO(self.via_data)

        self.font = bff.BFF('arial14.bff')

        self.ready.emit()

        self._angle = [0]*10
        self.startTimer(1000/80)

    def timerEvent(self, event):
        self._angle[0] += .04
        self.line_data[0][2] = 5.5*2.54e6*math.cos(self._angle[0])
        self.line_data[0][3] = 5.5*2.54e6*math.sin(self._angle[0])
        self.line_data[4][2] = 5.5*2.54e6*math.cos(self._angle[0])
        self.line_data[4][3] = 5.5*2.54e6*math.sin(self._angle[0])
        self._angle[1] += .1
        self.line_data[1][2] = 5*2.54e6*math.cos(self._angle[1])
        self.line_data[1][3] = 5*2.54e6*math.sin(self._angle[1])
        self._angle[2] += -.09
        self.line_data[2][2] = 4*2.54e6*math.cos(self._angle[2])
        self.line_data[2][3] = 4*2.54e6*math.sin(self._angle[2])
        self.line_data[3][2] = 4*2.54e6*math.cos(self._angle[2])
        self.line_data[3][3] = 4*2.54e6*math.sin(self._angle[2])
        # self.line_vbo = glvbo.VBO(self.line_data)
        # self.line_vbo.copy_data()
        self.line_vbo.set_array(self.line_data)
        self.repaint()

    def paintGL(self):
        """Event to repaint the scene.
        """
        glClear(GL_COLOR_BUFFER_BIT)

        #grid
        self.grid_shader.install()
        glUniformMatrix4fv(self.grid_shader.uniform['view'], 1, GL_FALSE, self.view)
        glUniformMatrix4fv(self.grid_shader.uniform['projection'], 1, GL_FALSE, self.projection)

        self.grid1_vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self.grid1_vbo.data[0].nbytes, self.grid1_vbo)
        glUniform3f(self.grid_shader.uniform['color'], .2, .2, 0)
        glDrawArrays(GL_LINES, 0, len(self.grid1_vbo))
        self.grid1_vbo.unbind()

        self.grid2_vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self.grid2_vbo.data[0].nbytes, self.grid2_vbo)
        glUniform3f(self.grid_shader.uniform['color'], .5, .5, .5)
        glDrawArrays(GL_LINES, 0, len(self.grid2_vbo))
        self.grid2_vbo.unbind()

        # linhas
        self.line_shader.install()
        glUniformMatrix4fv(self.line_shader.uniform['view'], 1, GL_FALSE, self.view)
        glUniformMatrix4fv(self.line_shader.uniform['projection'], 1, GL_FALSE, self.projection)

        glBlendEquation(GL_MAX)

        self.line_vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, self.line_vbo.data[0].nbytes, self.line_vbo)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, self.line_vbo.data[0].nbytes, self.line_vbo+4*4)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, self.line_vbo.data[0].nbytes, self.line_vbo+(4+4)*4)
        glUniform1i(self.line_shader.uniform['resolution'], 12)
        glDrawArrays(GL_POINTS, 0, len(self.line_data))
        self.line_vbo.unbind()

        # vias
        self.via_shader.install()
        glUniformMatrix4fv(self.via_shader.uniform['view'], 1, GL_FALSE, self.view)
        glUniformMatrix4fv(self.via_shader.uniform['projection'], 1, GL_FALSE, self.projection)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBlendEquation(GL_FUNC_ADD)

        self.via_vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self.via_vbo.data[0].nbytes, self.via_vbo)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, len(self.via_data))
        self.via_vbo.unbind()

        self.via_shader.uninstall()

        # textos

    def resizeGL(self, width, height):
        """Event to adjust viewport and projection when widget is resized.

        Args:
            width (int): new widget width
            height (int): new widget height
        """
        glViewport(0, 0, width, height)
        scale = 1/6e6 #self.projection[0, 0]
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
