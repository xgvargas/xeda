#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ver isso para colocar o icone correto na taskbar do windows
http://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7
"""

from PySide.QtGui import *
from PySide.QtCore import *
import sys
from xeda_ui import *
from smartside import *


__author__ = 'Gustavo Vargas <xgvargas@gmail.com>'
__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)


class MyApplication(QtGui.QMainWindow, Ui_MainWindow, SmartSide):
    def __init__(self, parent=None):
        super(MyApplication, self).__init__(parent)
        self.setupUi(self)
        self.auto_connect()
        self.cfg = QSettings('oi', 'xeda')
        self.restoreGeometry(self.cfg.value('geometry'))
        self.restoreState(self.cfg.value('state'))
        #print 'lendo bunda:',self.cfg.value('bunda', type=int)

        # m = QMenu(self)
        # m.addAction('oi', self.temp)
        # self.tbtn_teste.setMenu(m)

    def temp(self):
        print 'vim do menu!'

    def closeEvent(self, event):
        self.cfg.setValue('geometry', self.saveGeometry())
        self.cfg.setValue('state', self.saveState())
        self.cfg.setValue('bunda', 12)
        event.accept()

    def keyPressEvent(self, event): #this event don't need to be acepted
        print event.key(), event.nativeModifiers(), event.nativeScanCode(), event.nativeVirtualKey()
        if event.key() == QtCore.Qt.Key_Escape:
            print 'foi ESC!'
            print dir(event)

    def _on_actionTeste__triggered(self):
        print 'foi'

if __name__ == "__main__":
    setAsApplication('xgvargas.xeda.1.1.1')
    app = QtGui.QApplication(sys.argv)
    window = MyApplication()
    window.show()
    #window.print_all_signals()
    sys.exit(app.exec_())
