# -*- coding: utf-8 -*-

from OpenGL.GL import *
import re

class ShaderProgram(object):

    def __init__(self, vertex=None, fragment=None, geometry=None, codefile=None, link=False):
        """Create a new shade program.

        Args:
            vertex (str, optional): vertex code
            fragment (str, optional): fragment code
            geometry (str, optional): geometry code
            codefile (str, optional): filename with GLSL code. Each shader inside the file **MUST** be started by
                a comment like: ``//====== BLOCK: VERTEX``. Use any number of equal signals and all uppercased.
            link (bool, optional): if True then the program will be linked with no chance for more shaders to be added.

        Raises:
            RuntimeError: An invalid GLSL code was supplied.
        """
        self.shaders = []
        self.program = 0
        self.uniform = {}

        if vertex: self.addVertexShader(vertex)
        if fragment: self.addFragmentShader(fragment)
        if geometry: self.addGeometryShader(geometry)

        if codefile:
            block, code = '', ''
            def aux():
                if block == 'VERTEX': self.addVertexShader(code)
                elif block == 'GEOMETRY': self.addGeometryShader(code)
                elif block == 'FRAGMENT': self.addFragmentShader(code)

            with open(codefile, 'r') as fh:
                for line in fh:
                    b = re.match(r'\s*//=+\s*BLOCK:\s+(\w+)', line)
                    if b:
                        if b.group(1) in ('VERTEX', 'GEOMETRY', 'FRAGMENT'):
                            aux()
                            block, code = b.group(1), ''
                        else:
                            raise RuntimeError('Invalid GLSL block name {}'.format(b.group(1)))
                    else:
                        if block:
                            code += line
                aux()

        if link:
            self.link()

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

    def _uniformFinder(self, code):
        for u in re.finditer(r'uniform\s+[^;]{2,}\s+(\w+)[\[;]', code):
            self.uniform[u.group(1)] = None

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
            self._uniformFinder(code)
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
            self._uniformFinder(code)
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
            self._uniformFinder(code)
            return shader

    def link(self):
        """Link all added shaders to program.

        Link will also look for all uniforms and the dict ``ShaderProgram.uniform`` will be populated
        with all their locations.

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

            for u in self.uniform.keys():
                l = glGetUniformLocation(self.program, u)
                self.uniform[u] = l

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
        return self.uniform.get(name, None)

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

    @staticmethod
    def uninstall():
        """Remove this program from OpenGL.
        """
        glUseProgram(0)

    __enter__ = install

    def __exit__(self, exc_type, exc_val, exc_tb):
        ShaderProgram.uninstall()
        return False
