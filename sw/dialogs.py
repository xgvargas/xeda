# -*- coding: utf-8 -*-


from dlg_about_ui import *   #this also imports QtGui and QtCore
import smartside.signal as smartsignal
import config



class AboutDialog(QtGui.QDialog, Ui_dlg_about, smartsignal.SmartSignal):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.auto_connect()

    @staticmethod
    def execute(parent=None):
        dialog = AboutDialog(parent)
        result = dialog.exec_()
        return (result == QtGui.QDialog.Accepted)
