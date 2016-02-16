# -*- coding: utf-8 -*-

import struct
import array
from OpenGL.GL import *


class BFF(object):

    def __init__(self, filename):
        with open(filename, 'rb') as f:
            fmt = '<BBiiiibb'
            data = f.read(struct.calcsize(fmt))
            a1, a2, imgW, imgH, celW, celH, self.bpp, self.base = struct.unpack(fmt, data)
            if a1 != 0xbf or a2 != 0xf2:
                raise RuntimeError('Invalid BFF file:', filename)
            self.cs = array.array('B')
            self.cs.fromfile(f, 256)
            self.img = f.read()

        # self.rp = imgW / celW
        self.col_factor = celW / imgW
        self.row_factor = celH / imgH

# RowPitch = ImageWidth / CellWidth
# ColFactor = CellWidth  / ImageWidth
# RowFactor = CellHeight / ImageHeight
# Row = ( CharASCIIValue - BaseCharOffset ) / RowPitch
# Col = ( CharASCIIValue - BaseCharOffset ) - ( Row * RowPitch )
# U = Col * ColFactor
# V = Row * RowFactor
# U1 = U + ColFactor
# V1 = V + ColFactor

        self.tId = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tId)

        # Fonts should be rendered at native resolution so no need for texture filtering
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
        # Stop characters from bleeding over edges
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);

        if self.bpp == 8:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_LUMINANCE, imgW, imgH, 0, GL_LUMINANCE, GL_UNSIGNED_BYTE, self.img);

        elif self.bpp == 24:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, imgW, imgH, 0, GL_RGB, GL_UNSIGNED_BYTE, self.img);

        elif self.bpp == 32:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, imgW, imgH, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.img);

        else:
            raise RuntimeError('Invalid BPP in file:', filename)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.tId)
        if self.bpp == 8:
            glBlendFunc(GL_SRC_ALPHA, GL_SRC_ALPHA);
            glEnable(GL_BLEND);

        elif self.bpp == 24:
            glDisable(GL_BLEND);

        else:
            glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA);
            glEnable(GL_BLEND);

    def render(self, text, pos):
        pass

    def getWidth(self, text):
        w = 0
        for c in text:
            w += self.cs[min(127, ord(c))]
        return w
