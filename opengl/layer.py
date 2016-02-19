# -*- coding: utf-8 -*-

from OpenGL.GL import *
import numpy as np
import OpenGL.arrays.vbo as glvbo
import math


class LayerBase(object):

    def __init__(self, viewer, color):
        self.viewer = viewer
        self.color = color
        self.name = 'top'
        self.visible = True
        self.triangles = np.array([], dtype='f')
        self._vbo = glvbo.VBO(self.triangles)
        self.items = np.array([], dtype=Line.dtype)

    def __len__(self):
        return self.items.shape[0]

    def drawLayer(self):
        with self._vbo:
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, self._vbo.data[0].nbytes, self._vbo)
            # glDrawArrays(GL_TRIANGLES, 0, self.triangles.size//2)
            glDrawArrays(GL_TRIANGLES, 0, self._vbo.data[0].size//2)

        print(dir(self._vbo.data[0]))

        # print('-->', len(self.line_data), self.line_data.size)
        print('flags', self._vbo.data[0].flags)
        print('shape', self._vbo.data[0].shape)
        print('strides', self._vbo.data[0].strides)
        print('ndim', self._vbo.data[0].ndim)
        print('data', self._vbo.data[0].data)
        print('size', self._vbo.data[0].size)
        print('itemsize', self._vbo.data[0].itemsize)
        print('nbytes', self._vbo.data[0].nbytes)
        print('base', self._vbo.data[0].base)

class Line(LayerBase):

    dtype = [('x1', 'i4'), ('y1', 'i4'), ('x2', 'i4'), ('y2', 'i4'), ('width', 'i4'), ('net', 'S15')]

    resolution = 12

    def __init__(self, *args, **wargs):
        super().__init__(*args, **wargs)

    def openglfy(self, idx):

        tri = []

        l = self.items[idx]

        print(l)

        a = math.atan2(l['y2']-l['y1'], l['x2']-l['x1'])

        b = a+math.pi/2
        c = b-math.pi

        radius = l['width']/2

        print(radius)

        pa = math.cos(b)*radius, math.sin(b)*radius
        pb = math.cos(c)*radius, math.sin(c)*radius

        p1 = l['x1']+pa[0], l['y1']+pa[1]
        p2 = l['x1']+pb[0], l['y1']+pb[1]
        p3 = l['x2']+pa[0], l['y2']+pa[1]
        p4 = l['x2']+pb[0], l['y2']+pb[1]

        tri.append(p1)
        tri.append(p2)
        tri.append(p3)

        tri.append(p2)
        tri.append(p4)
        tri.append(p3)

        delta = math.pi/Line.resolution

        def cap(x, y, ang):
            for i in range(Line.resolution):
                tri.append((x, y))
                p = (x+math.cos(ang)*radius, y+math.sin(ang)*radius)
                tri.append(p)
                ang += delta
                p = (x+math.cos(ang)*radius, y+math.sin(ang)*radius)
                tri.append(p)

        # cap(l['x1'], l['y1'], b)
        # cap(l['x2'], l['y2'], c)

        return np.array(tri, dtype='f')

    def add(self, *obj):
        idx = len(self.items)
        self.items = np.append(self.items, np.array(obj, dtype=Line.dtype))
        tri = self.openglfy(idx)
        print(tri)
        self.triangles = np.append(self.triangles, tri)
        print(self.triangles, self.triangles.size)
        self._vbo.set_array(self.triangles)
        # self._vbo.create_buffers()
        # self._vbo.copy_data()
        return idx

    def delete(self, idx):
        pass

    def edit(self, idx, obj):
        pass
