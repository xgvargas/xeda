# -*- coding: utf-8 -*-

from __future__ import print_function
from PySide import QtCore, QtGui
import re

class DimEdit(QtGui.QLineEdit):

    def __init__(self, *args, **kwargs):
        super(DimEdit, self).__init__(*args, **kwargs)

        self.step = .1
        self.defunit = None

    def _explode(self, txt):
        g = re.match(r'^\s*([+-]?\d+[,.]?\d*|[+-]?[.,]\d+)\s*(?:([+*/-])\s*(\d+[,.]?\d*|[.,]\d+))?\s*(mm|in|mils?|cm)?\s*$', txt)
        if g:
            return float(g.group(1)), g.group(2), float(g.group(3) or '0'), g.group(4) or self.defunit
        return None, None, None, None

    def _resolve(self, n1, op, n2):
        if op == '+': return n1+n2
        if op == '-': return n1-n2
        if op == '*': return n1*n2
        if op == '/': return n1/n2
        return n1 or 0.0

    def focusOutEvent(self, e):
        n = self._explode(self.text())
        if n:
            self.setText('{:.3f} {}'.format(self._resolve(n[0], n[1], n[2]), n[3]))

        super(DimEdit, self).focusOutEvent(e)

    def wheelEvent(self, e):
        n = self._explode(self.text())
        if n:
            mul = 10 if e.modifiers() == QtCore.Qt.ControlModifier else 1

            v = self._resolve(n[0], n[1], n[2])+self.step*mul*cmp(e.delta(), 0)

            self.setText('{:.3f} {}'.format(v, n[3]))

        e.accept()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            n = self._explode(self.text())
            u = n[3]
            if u == 'mil' or u == 'mils': self.setDim(self.text(), 'mm')
            elif u == 'mm': self.setDim(self.text(), 'in')
            elif u == 'in': self.setDim(self.text(), 'cm')
            # elif u == 'cm': self.setDim(self.text(), 'mils')
            else: self.setDim(self.text(), 'mils')
            event.accept()
        else:
            super(DimEdit, self).mousePressEvent(event)
            # event.ignore()

    def _toMils(self, num, unit):
        if unit == 'mil' or unit == 'mils': return num
        if unit == 'in': return num*1000
        if unit == 'mm': return num*39.37
        if unit == 'cm': return num*393.7
        return 0

    def setDim(self, dim, unit):
        if not self.defunit:
            self.defunit = unit
        n = self._explode(dim)
        if n:
            mils = self._toMils(n[0], n[3])
            if unit == 'mils' or unit == 'mil': self.setText('{:.0f} mils'.format(mils))
            elif unit == 'in': self.setText('{:.3f} in'.format(mils/1000))
            elif unit == 'mm': self.setText('{:.3f} mm'.format(mils/39.37))
            elif unit == 'cm': self.setText('{:.3f} cm'.format(mils/393.7))
            else: self.setText('')
        else:
            self.setText('')

    def getDim(self):
        n = self._explode(self.text())
        if n:
            return self._toMils(n[0], n[3])
        return 0
