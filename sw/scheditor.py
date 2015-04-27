# -*- coding: utf-8 -*-


from form_sch_ui import *   #this also imports QtGui and QtCore
import smartside.signal as smartsignal
import config
import dialogs
import xedaviewer


class SCHEditor(QtGui.QMainWindow, Ui_SCHForm, smartsignal.SmartSignal):
    def __init__(self, project, parent=None):
        super(SCHEditor, self).__init__(parent)
        self.setupUi(self)

        self.setWindowTitle('XEDA SCHEditor -')

        self.scene = xedaviewer.SCHScene(config.meta.sch, project.sch)
        self.view_sch.setScene(self.scene)

        self.auto_connect()

    def closeEvent(self, event):
        pass

    def _on_action_Trace__activated(self): pass
    def _on_action_Line__activated(self): pass
    def _on_action_Save__activated(self): pass
    def _on_action_Print__activated(self): pass
    def _on_action_Export__activated(self): pass
    def _on_action_Inport__activated(self): pass
    def _on_actionClose__activated(self): pass
    def _on_action_Grid_Snap__activated(self): pass
    def _on_action_String__activated(self): pass
    def _on_action_Part__activated(self): pass
    def _on_action_Content__activated(self): pass
    def _on_action_About__activated(self):
        dialogs.AboutDialog.execute()
    def _on_action_Inspector__activated(self): pass
    def _on_actionP_ower__activated(self): pass
    def _on_action_Net_name__activated(self): pass
    def _on_actionGlobal_Port__activated(self): pass
    def _on_action_Bus__activated(self): pass
    def _on_actionSet_Libraries__activated(self): pass
    def _on_action_Append_Sheet__activated(self): pass
    def _on_action_Manage_sheets__activated(self): pass
    def _on_actionS_heet_symbol__activated(self): pass
    def _on_action_Junction__activated(self): pass
    def _on_action_Arc__activated(self): pass
    def _on_action_Text__activated(self): pass
    def _on_actionZoom_Iin__activated(self):
        self.view_pcb.zoomIn()
    def _on_actionZoo_m_Out__activated(self):
        self.view_pcb.zoomOut()
    def _on_actionZoom_Fit__activated(self):
        self.view_pcb.zoomFit()
    def _on_actionSet_Origin__activated(self):
        self.view_pcb.setOrigin()
    def _on_action_Reset_Origin__activated(self):
        self.view_pcb.resetOrigin()
