# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.arrays.vbo as glvbo
from shader import Shader
import numpy as np
import transf


vertex_source = """
#version 330

layout (location = 0) in vec4 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec2 width;

out vec3 point_color;
out vec2 line_width;

void main()
{
    gl_Position = position;
    point_color = color;
    line_width = width;
}
"""

geometry_source = """
#version 330

layout (points) in;
layout (line_strip, max_vertices = 2) out;

uniform mat4 transform;

in vec3 point_color[];
in vec2 line_width[];

out vec3 line_color;

void main()
{
    line_color = point_color[0];

    gl_Position = transform * vec4(gl_in[0].gl_Position.xy, 0., 1.);
    EmitVertex();

    gl_Position = transform * vec4(gl_in[0].gl_Position.zw, 0., 1.);
    EmitVertex();

    EndPrimitive();
}
"""

fragment_source = """
#version 330

precision highp float;

in vec3 line_color;
out vec4 out_color;

void main()
{
    out_color = vec4(line_color, 1.);
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

        self.data = np.array([
                              [0, 0, .5, .1,   1., 0., 0.,   .05],
                              [0, .2, .8, 1,   .5, .8, 0.,   .1],
                              [0, 0, 3, 5,   .2, .2, .9,   .2],
                              ], dtype='f')

        self.vbo = glvbo.VBO(self.data)

        self.lineShader = Shader(vertex_source, fragment_source)
        self.lineShader.addGeometryShader(geometry_source)
        self.lineShader.link()

        self.projection = np.eye(4, dtype='f')

        self.ready.emit()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        self.vbo.bind()
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, self.vbo.data[0].nbytes, self.vbo)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, self.vbo.data[0].nbytes, self.vbo+4*4)
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 1, GL_FLOAT, GL_FALSE, self.vbo.data[0].nbytes, self.vbo+(4+3)*4)
        self.lineShader.install()
        mat = self.lineShader.getUniform('transform')
        glUniformMatrix4fv(mat, 1, GL_FALSE, self.projection)
        glDrawArrays(GL_POINTS, 0, len(self.data))
        self.lineShader.uninstall()
        self.vbo.unbind()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        self.projection = transf.ortho(0, width, height, 0, 1, -1)


class XedaPCBViewer(XedaViewerBase):
    pass
