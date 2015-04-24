# -*- coding: utf-8 -*-


from form_pcb_ui import *   #this also imports QtGui and QtCore
import smartside.signal as smartsignal
import config
import dialogs



class Layouter(QtGui.QMainWindow, Ui_PCBForm, smartsignal.SmartSignal):
    def __init__(self, parent=None):
        super(Layouter, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('XEDA Layouter -')

        self.auto_connect()

    def closeEvent(self, event):
        pass

	def _on_action_Via__activated(self): pass
	def _on_action_Trace__activated(self): pass
	def _on_action_Pad__activated(self): pass
	def _on_action_Line__activated(self): pass
	def _on_action_Ruler__activated(self): pass
	def _on_action_Set_rules__activated(self): pass
	def _on_action_Check_rules__activated(self): pass
	def _on_action_Save__activated(self): pass
	def _on_action_Print__activated(self): pass
	def _on_action_Export__activated(self): pass
	def _on_action_Inport__activated(self): pass
	def _on_actionGerber__activated(self): pass
	def _on_actionClose__activated(self): pass
	def _on_actionBoard_information__activated(self): pass
	def _on_action_Grid_Snap__activated(self): pass
	def _on_action_Set_layers__activated(self): pass
	def _on_action_String__activated(self): pass
	def _on_action_Part__activated(self): pass
	def _on_action_Content__activated(self): pass
	def _on_action_About__activated(self):
        dialogs.AboutDialog.execute()
	def _on_action_Inspector__activated(self): pass
	def _on_action_Layers__activated(self): pass
	def _on_actionSet_Libraries__activated(self): pass
	def _on_action_Arc__activated(self): pass
	def _on_actionAr_ea__activated(self): pass
	def _on_actionZoom_Iin__activated(self): pass
	def _on_actionZoo_m_Out__activated(self): pass
	def _on_actionZoom_Fit__activated(self): pass
	def _on_actionSet_Origin__activated(self): pass
	def _on_action_Reset_Origin__activated(self): pass
