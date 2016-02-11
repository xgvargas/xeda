# -*- coding: utf-8 -*-

from OpenGL.GL import *

class Shader(object):

    def __init__(self, vertex=None, fragment=None, geometry=None):
        self.shaders = []
        self.program = 0
        if vertex: self.addVertexShader(vertex)
        if fragment: self.addFragmentShader(fragment)
        if geometry: self.addGeometryShader(geometry)

    @staticmethod
    def compile(code, kind):
        shader = glCreateShader(kind)
        glShaderSource(shader, code)
        glCompileShader(shader)
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not(result):
            raise RuntimeError(glGetShaderInfoLog(shader))

        return shader

    def addVertexShader(self, code):
        shader = Shader.compile(code, GL_VERTEX_SHADER)
        self.shaders.append(shader)
        return shader

    def addFragmentShader(self, code):
        shader = Shader.compile(code, GL_FRAGMENT_SHADER)
        self.shaders.append(shader)
        return shader

    def addGeometryShader(self, code):
        shader = Shader.compile(code, GL_GEOMETRY_SHADER)
        self.shaders.append(shader)
        return shader

    def link(self):
        self.program = glCreateProgram()
        for shader in self.shaders:
            glAttachShader(self.program, shader)

        glLinkProgram(self.program)
        result = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not(result):
            raise RuntimeError(glGetProgramInfoLog(self.program))

        return self.program

    def getProgram(self):
        return self.program

    def install(self):
        glUseProgram(self.program)

    def uninstall(self):
        glUseProgram(0)
