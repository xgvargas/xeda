# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.arrays.vbo as glvbo
import numpy as np
import transf
import shader
import shader.line as shaderLine


class XedaViewerBase(QtOpenGL.QGLWidget):

    ready = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(None)

        self.lastPos = QtCore.QPoint()

    def minimumSizeHint(self):
        """Hint of the minimum size this widget accepts.
        """
        return QtCore.QSize(50, 50)

    # def sizeHint(self):
    #     return QtCore.QSize(400, 400)

    # def mousePressEvent(self, event):
    #     self.lastPos = QtCore.QPoint(event.pos())

    # def mouseMoveEvent(self, event):
    #     dx = event.x() - self.lastPos.x()
    #     dy = event.y() - self.lastPos.y()

    #     if event.buttons() & QtCore.Qt.LeftButton:
    #         self.setXRotation(self.xRot + 8 * dy)
    #         self.setYRotation(self.yRot + 8 * dx)
    #     elif event.buttons() & QtCore.Qt.RightButton:
    #         self.setXRotation(self.xRot + 8 * dy)
    #         self.setZRotation(self.zRot + 8 * dx)

    #     self.lastPos = QtCore.QPoint(event.pos())

    def initializeGL(self):
        """Event to initialize OpenGL context.

        Create shaders, VBOs and VAOs. Also link the layers to each VBO.
        """
        glClearColor(*(.8, .1, .4, 1))

        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

        self.data = np.array([
                              [0, 0, .5, .1,   1., 0., 0.,   .05],
                              [0, .2, .8, 1,   .5, .8, 0.,   .1],
                              [0, 0, 3, 5,   .2, .2, .9,   .2],
                              ], dtype='f')

        self.vbo = glvbo.VBO(self.data)

        self.lineShader = shader.ShaderProgram(shaderLine.vertex, shaderLine.fragment, shaderLine.geometry)
        self.lineShader.link()
        # self.viaShader = Shader(via_vertex, via_fragment, via_geometry)
        # self.viaShader.link()
        # self.textShader = Shader(text_vertex, text_fragment, text_geometry)
        # self.textShader.link()
        # self.padShader = Shader(pad_vertex, pad_fragment, pad_geometry)
        # self.padShader.link()

        # self.model = np.eye(4, dtype='f')
        self.view = np.eye(4, dtype='f')
        self.projection = np.eye(4, dtype='f')

        self.ready.emit()

    def paintGL(self):
        """Event to repaint the scene.
        """
        glClear(GL_COLOR_BUFFER_BIT)

        self.vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, self.vbo.data[0].nbytes, self.vbo)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.vbo.data[0].nbytes, self.vbo+4*4)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, self.vbo.data[0].nbytes, self.vbo+(4+3)*4)
        self.lineShader.install()
        viewLoc = self.lineShader.getUniform('view')
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, self.view)
        projectionLoc = self.lineShader.getUniform('projection')
        glUniformMatrix4fv(projectionLoc, 1, GL_FALSE, self.projection)
        glDrawArrays(GL_POINTS, 0, len(self.data))
        self.lineShader.uninstall()
        self.vbo.unbind()




    def resizeGL(self, width, height):
        """Event to adjust viewport and projection when widget is resized.

        Args:
            width (int): new widget width
            height (int): new widget height
        """
        glViewport(0, 0, width, height)
        # self.projection = transf.ortho(0, width, height, 0, 1, -1)
        self.projection = transf.ortho(-6, 6, -6, 6, 1, -1)

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
            # p = event.pos()-self._pan_pos
            # self._pan_pos = event.pos()
            # self.viewRect.setLeft(min(self.viewSize.width()-self.viewRect.width(),
            #                           max(0, self.viewRect.left()-p.x()/self.scale)))
            # self.viewRect.setTop(min(self.viewSize.height()-self.viewRect.height(),
            #                          max(0, self.viewRect.top()-p.y()/self.scale)))
            # self.repaint()
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
