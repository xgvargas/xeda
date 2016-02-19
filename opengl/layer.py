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
        self._vbo = glvbo.VBO(np.array([], dtype='f4, f4, i4'))
        self.items = np.array([], dtype=Line.dtype)

    def __len__(self):
        return self.items.shape[0]

    def drawItems(self):
        with self._vbo:
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 12, self._vbo)
            glEnableVertexAttribArray(1)
            glVertexAttribIPointer(1, 1, GL_INT, 12, self._vbo+8)
            glDrawArrays(GL_TRIANGLES, 0, self._vbo.data.size)

    def drawLabel(self):
        pass


class Line(LayerBase):

    dtype = [('x1', 'i4'), ('y1', 'i4'), ('x2', 'i4'), ('y2', 'i4'), ('width', 'i4'), ('net', 'S15')]

    resolution = 12

    def __init__(self, *args, **wargs):
        super().__init__(*args, **wargs)

    def openglfy(self, idx):

        tri = []

        l = self.items[idx]

        a = math.atan2(l['y2']-l['y1'], l['x2']-l['x1'])

        b = a+math.pi/2
        c = b-math.pi

        radius = l['width']/2

        pa = math.cos(b)*radius, math.sin(b)*radius
        pb = math.cos(c)*radius, math.sin(c)*radius

        p1 = l['x1']+pa[0], l['y1']+pa[1], self.color
        p2 = l['x1']+pb[0], l['y1']+pb[1], self.color
        p3 = l['x2']+pa[0], l['y2']+pa[1], self.color
        p4 = l['x2']+pb[0], l['y2']+pb[1], self.color

        tri.append(p1)
        tri.append(p2)
        tri.append(p3)

        tri.append(p2)
        tri.append(p4)
        tri.append(p3)

        delta = math.pi/Line.resolution

        def cap(x, y, ang):
            for i in range(Line.resolution):
                tri.append( (x, y, self.color) )
                tri.append( (x+math.cos(ang)*radius, y+math.sin(ang)*radius, self.color) )
                ang += delta
                tri.append( (x+math.cos(ang)*radius, y+math.sin(ang)*radius, self.color) )

        cap(l['x1'], l['y1'], b)
        cap(l['x2'], l['y2'], c)

        return np.array(tri, dtype='f4, f4, i4')

    def add(self, *obj):
        idx = len(self.items)
        self.items = np.append(self.items, np.array(obj, dtype=Line.dtype))
        tri = self.openglfy(idx)
        self._vbo.set_array(np.append(self._vbo.data, tri))
        return idx

    def delete(self, idx):
        pass

    def edit(self, idx, obj):
        pass
