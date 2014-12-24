#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Gustavo Vargas <xgvargas@gmail.com>'
__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)


import sys, os
from xeda_ui import *   #this also imports QtGui and QtCore
import smartside.signal as smartsignal
from smartside import setAsApplication
import pcbgraphicsview as bbb

class MyApplication(QtGui.QMainWindow, Ui_MainWindow, smartsignal.SmartSignal):
    def __init__(self, parent=None):
        super(MyApplication, self).__init__(parent)
        self.setupUi(self)

        self.edt_console.setLocals({'app': self})

        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(0, 0, 20000, 20000)
        self.gpv_pcb.setScene(self.scene)
        self.gpv_sch.setScene(self.scene)

        for x in xrange(0, 15000, 250):
            for y in xrange(0, 17000, 250):
                a = bbb.PCBViaItem()
                a.setPos(x, y)
                self.scene.addItem(a)
                if x%1000 == 0 and y%1000 == 0:
                    a = self.scene.addSimpleText('({:d},{:d})'.format(x, y))
                    a.setPos(x, y)
                    a.scale(1, -1)
                    a.setFont(QtGui.QFont("Times", 50, QtGui.QFont.Bold))
                    a.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 0)))

        self.scene.addLine(1000, 1000, 2000, 3000,
                           pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 100,
                                          QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.scene.addLine(2000, 3000, 5000, 3000,
                           pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 100,
                                          QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.scene.addLine(4000, 1000, 4000, 3500,
                           pen=QtGui.QPen(QtGui.QColor(255, 128, 128, 127), 200,
                                          QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

    def closeEvent(self, event):
        pass


######################################################################


app = QtGui.QApplication(sys.argv)
window = MyApplication()
setAsApplication('techin.xeda.'+__version__)
window.show()
# window.print_all_signals()
ret = app.exec_()
sys.exit(ret)
