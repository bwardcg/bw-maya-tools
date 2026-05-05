###############################
#
#   Basic Maya Tools GUI
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_ui_maya
#
###############################

from PySide6 import QtWidgets
from bw_tools.bw_ui_maya import MayaWindowBase

UI_TITLE = "Brian's Maya UI Template"

class ToolUI(MayaWindowBase):
    def __init__(self):
        super().__init__(title=UI_TITLE, width=400, height=300)

        # placeholder for tool ui functions
        placeholder = QtWidgets.QLabel("Maya Tool UI Ready")
        self.layout.addWidget(placeholder)


# ------------------------------- run with bw_Menu
def run():
    ToolUI.launch()
