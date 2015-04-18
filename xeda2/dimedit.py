# -*- coding: utf-8 -*-

from __future__ import print_function
from PySide import QtCore, QtGui
import re

class DimEdit(QtGui.QLineEdit):

    def __init__(self, *args, **kwargs):
        super(DimEdit, self).__init__(*args, **kwargs)

        self.step = .1

    def _getDefUnit(self):
        return 'mils'      #TODO ler to projeto

    def _explode(self, txt):
        g = re.match(r'^\s*([+-]?\d+[,.]?\d*|[+-]?[.,]\d+)\s*(?:([+*/-])\s*(\d+[,.]?\d*|[.,]\d+))?\s*(mm|in|mils?|cm)?\s*$', txt)
        if g:
            return float(g.group(1)), g.group(2), float(g.group(3) or '0'), g.group(4) or self._getDefUnit()
        return None

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
