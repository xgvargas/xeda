# -*- coding: utf-8 -*-

from OpenGL.GL import *

class ShaderProgram(object):

    def __init__(self, vertex=None, fragment=None, geometry=None):
        """Create a new shade program.

        Args:
            vertex (str, optional): vertex code
            fragment (str, optional): fragment code
            geometry (str, optional): geometry code
        """
        self.shaders = []
        self.program = 0
        if vertex: self.addVertexShader(vertex)
        if fragment: self.addFragmentShader(fragment)
        if geometry: self.addGeometryShader(geometry)

    @staticmethod
    def compile(code, kind):
        """Compiles a shader.

        Args:
            code (str): Source code in GLSL
            kind (str): Any of: GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, GL_GEOMETRY_SHADER

        Raises:
            RuntimeError: maybe a syntax error...

        Returns:
            int: the compiled ID.
        """
        shader = glCreateShader(kind)
        glShaderSource(shader, code)
        glCompileShader(shader)
        result = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not(result):
            raise RuntimeError(glGetShaderInfoLog(shader))

        return shader

    def addVertexShader(self, code):
        """Compiles a vertex shader code and add to program.

        Args:
            code (str): vertex shader source code.

        Returns:
            int: shader ID
        """
        if not self.program:
            shader = ShaderProgram.compile(code, GL_VERTEX_SHADER)
            self.shaders.append(shader)
            return shader

    def addFragmentShader(self, code):
        """Compiles a fragment shader code and add to program.

        Args:
            code (str): fragment shader source code.

        Returns:
            int: shader ID
        """
        if not self.program:
            shader = ShaderProgram.compile(code, GL_FRAGMENT_SHADER)
            self.shaders.append(shader)
            return shader

    def addGeometryShader(self, code):
        """Compiles a geometry shader code and add to program.

        Args:
            code (str): geometry shader source code.

        Returns:
            int: shader ID
        """
        if not self.program:
            shader = ShaderProgram.compile(code, GL_GEOMETRY_SHADER)
            self.shaders.append(shader)
            return shader

    def link(self):
        """Link all added shaders to program.

        Raises:
            RuntimeError: Maybe a linker error....

        Returns:
            int: The program ID
        """
        if not self.program:
            self.program = glCreateProgram()
            for shader in self.shaders:
                glAttachShader(self.program, shader)

            glLinkProgram(self.program)
            result = glGetProgramiv(self.program, GL_LINK_STATUS)
            if not(result):
                raise RuntimeError(glGetProgramInfoLog(self.program))

            # once linked we no longer need that
            for shader in self.shaders:
                glDeleteShader(shader)

            self.shaders = None

        return self.program

    def getProgram(self):
        """Returns the program ID.

        Returns:
            int: program ID
        """
        return self.program

    def getUniform(self, name):
        """Return the location of a named uniform input.

        Args:
            name (str): Uniform name.

        Returns:
            int: Location of this uniform.
        """
        return glGetUniformLocation(self.program, name)

    def getAttrib(self, name):
        """Return the location of a named attribute.

        Args:
            name (str): Attribute name.

        Returns:
            int: Location of this attribute.
        """
        return glGetAttribLocation(self.program, name)

    def install(self):
        """Set OpenGL to use this program.
        """
        glUseProgram(self.program)

    def uninstall(self):
        """Remove this program from OpenGL.
        """
        glUseProgram(0)

