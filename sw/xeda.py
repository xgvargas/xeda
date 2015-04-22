#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Gustavo Vargas <xgvargas@gmail.com>'
__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)


import sys, os
from xeda_ui import *   #this also imports QtGui and QtCore
import smartside.signal as smartsignal
from smartside import setAsApplication
import xedaviewer as bbb
import xhelper
import config



class MyApplication(QtGui.QMainWindow, Ui_MainWindow, smartsignal.SmartSignal):
    def __init__(self, parent=None):
        super(MyApplication, self).__init__(parent)
        self.setupUi(self)

        # self.edt_console.setLocals({'app': self})

        self.scene = bbb.PCBScene(config.meta.pcb, myproj.pcb)
        self.view_pcb.setScene(self.scene)
        self.scene22 = bbb.SCHScene(config.meta.sch, myproj.sch)
        self.view_sch.setScene(self.scene22)

        for x in xrange(0, 15000, 250):
            for y in xrange(0, 17000, 250):
                a = bbb.PCBViaItem(dict(x=x, y=y))
                self.scene.addItem(a)
                # if x%1000 == 0 and y%1000 == 0:
                #     a = bbb.PCBStringItem(dict(string='({:d},{:d})'.format(x, y), x=x, y=y))
                #     self.scene.addItem(a)

        # self.scene.addLine(1000, 1000, 2000, 3000,
        #                    pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 100,
        #                                   QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # self.scene.addLine(4000, 5000, 2000, 3000,
        #                    pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 14,
        #                                   QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # self.scene.addLine(4000, 5000, 4250, 6000,
        #                    pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 14,
        #                                   QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # self.scene22.addLine(2000, 3000, 5000, 3000,
        #                    pen=QtGui.QPen(QtGui.QColor(128, 128, 255, 127), 100,
        #                                   QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # self.scene.addLine(4000, 1000, 4000, 3500,
        #                    pen=QtGui.QPen(QtGui.QColor(255, 128, 128, 127), 200,
        #                                   QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))

        self.auto_connect()


    def closeEvent(self, event):
        pass

    def _on_action_Console__triggered(self):
        self.dock_console.show()

    def _on_view_pcb__moveEvent(self, e):
        self.status.showMessage('1- x: {:.1f} y: {:.1f}'.format(e.x(), e.y()))

    def _on_view_sch__moveEvent(self, e):
        self.status.showMessage('2- x: {:.1f} y: {:.1f}'.format(e.x(), e.y()))


######################################################################

config.init()
myproj = xhelper.readYamlConfig('defproj.yaml')


app = QtGui.QApplication(sys.argv)
window = MyApplication()
setAsApplication('techin.xeda.'+__version__)
window.show()
# window.print_all_signals()
ret = app.exec_()
sys.exit(ret)
