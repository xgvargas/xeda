#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""

# Lembrar de abrir issue na lib euclid3 com as mundacas feitas na linhs 578

import sys, os
from pcb_ui import *
import smartside.signal as smartsignal
import math


__author__ = 'Gustavo Vargas <xgvargas@gmail.com>'
__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)



class PCB(QtGui.QWidget, Ui_Form, smartsignal.SmartSignal):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.auto_connect()

        self.setWindowTitle('PCB v_'+__version__)


if __name__ == "__main__":

    # if hasattr(sys, "frozen") and cfg.getboolean('autoupdate', False):
    #     import esky
    #     updater = esky.Esky(sys.executable, "http://what.will.com/be/my/link")
    #     updater.auto_update()

    app = QtGui.QApplication(sys.argv)
    # translator = QtCore.QTranslator()
    # translator.load('i18n/'+cfg['language']+'.qm')
    # app.installTranslator(translator)
    window = PCB()
    window.show()
    # window.print_all_signals()
    sys.exit(app.exec_())