# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.arrays.vbo as glvbo
from shader import Shader
import numpy as np


vertex_source = """
#version 330

layout (location = 0) in vec2 position;

void main()
{
    gl_Position = vec4(position.x, .4 * sin(20 * position.x), 0., 1.);
}
"""

fragment_source = """
#version 330

out vec4 out_color;

void main()
{
    // cor amarela
    out_color = vec4(1., 1., 0., .2);
}
"""

geometry_source = """
#version 330

void main()
{

}
"""


class XedaViewerBase(QtOpenGL.QGLWidget):

    ready = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(None)

        self.lastPos = QtCore.QPoint()

    def minimumSizeHint(self):
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
        glClearColor(*(.8, .1, .4, 1))

        self.data = np.zeros((10000, 2), dtype=np.float32)
        self.data[:,0] = np.linspace(-1., 1., len(self.data))

        self.vbo = glvbo.VBO(self.data)

        self.lineShader = Shader(vertex_source, fragment_source)
        # self.lineShader.addVertexShader(vertex_source)
        # self.lineShader.addFragmentShader(fragment_source)
        # self.lineShader.addGeometryShader(geometry_source)
        self.lineShader.link()

        self.viaShader = Shader()
        self.viaShader.link()

        self.padShader = Shader()
        self.padShader.link()

        self.ready.emit()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        self.vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, None)
        self.lineShader.install()
        glDrawArrays(GL_LINE_STRIP, 0, len(self.data))
        self.lineShader.uninstall()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)


class XedaPCBViewer(XedaViewerBase):
    pass
