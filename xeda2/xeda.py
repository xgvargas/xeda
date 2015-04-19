#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Gustavo Vargas <xgvargas@gmail.com>'
__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)


import sys, os
from xeda_ui import *   #this also imports QtGui and QtCore
import smartside.signal as smartsignal
from smartside import setAsApplication
import xedagraphicsview as bbb
import xhelper
import config



class MyApplication(QtGui.QMainWindow, Ui_MainWindow, smartsignal.SmartSignal):
    def __init__(self, parent=None):
        super(MyApplication, self).__init__(parent)
        self.setupUi(self)

        # self.edt_console.setLocals({'app': self})

        self.scene = bbb.PCBScene(config.meta.pcb, myproj.pcb)
        self.gpv_pcb.setScene(self.scene)
        self.scene22 = bbb.SCHScene(config.meta.sch, myproj.sch)
        self.gpv_sch.setScene(self.scene22)

        for x in xrange(0, 15000, 250):
            for y in xrange(0, 17000, 250):
                a = bbb.PCBViaItem()
                a.setPos(x, y)
                self.scene.addItem(a)
                if x%1000 == 0 and y%1000 == 0:
                    a = bbb.PCBStringItem()
                    a.setPos(x, y)
                    self.scene.addItem(a)
                    # a = self.scene.addSimpleText('({:d},{:d})'.format(x, y))
                    # a.setPos(x, y)
                    # a.scale(1, -1)
                    # a.setFont(QtGui.QFont("Times", 50, QtGui.QFont.Bold))
                    # a.setBrush(QtGui.QBrush(QtGui.QColor(0, 255, 0)))

        self.scene.addLine(1000, 1000, 2000, 3000,
                           pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 100,
                                          QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.scene22.addLine(2000, 3000, 5000, 3000,
                           pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 100,
                                          QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        self.scene.addLine(4000, 1000, 4000, 3500,
                           pen=QtGui.QPen(QtGui.QColor(255, 128, 128, 127), 200,
                                          QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

        self.auto_connect()


    def closeEvent(self, event):
        pass

    def _on_action_Console__triggered(self):
        self.dock_console.show()


######################################################################

config.init()

print dir(config.meta)
print dir (config.meta.pcb.colors.layer)
# sys.exit(0)

myproj = xhelper.readYamlConfig('defproj.yaml')


app = QtGui.QApplication(sys.argv)
window = MyApplication()
setAsApplication('techin.xeda.'+__version__)
window.show()
# window.print_all_signals()
ret = app.exec_()
sys.exit(ret)
