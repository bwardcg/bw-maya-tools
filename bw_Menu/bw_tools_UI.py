###############################
#
#   Basic Mayu UI for inhereting into my Tools GUIs
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_ui_maya
#
###############################

from PySide6 import QtWidgets
from bw_tools.bw_ui_maya import MayaWindowBase

UI_TITLE = "bw_Rig"
BUTTONS = ['Snap B-A', 'Snap A-B', 'Prep Char', 'Skinning', 'Reset Ctrls']

class BwToolsUI(MayaWindowBase):
    def __init__(self):
        # Close other windows of this class
        '''   This SHOULD happen on launch()
        for w in QtWidgets.QApplication.topLevelWidgets():
            if isinstance(w, BwToolsUI):
                w.close()
        '''

        super().__init__(title=UI_TITLE, width=200, height=400)
        self.buttons = []
        self.create_buttons()        

    def create_buttons(self):
        for btn_name in BUTTONS:
            btn = QtWidgets.QPushButton(f"{btn_name}")
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

            # using lambda expression so vaiable gets reset on each loop (inside button press)
            btn.clicked.connect(lambda *_, n=btn_name: self.on_button_clicked(n))

            self.buttons.append(btn)
            self.layout.addWidget(btn)  # Add directly in order

    def on_button_clicked(self, name):
        print(f"Button {name} clicked!")
        # ------------------------------- call Button Function methods here...
        if name == 'Snap B-A':
            snap_B_2_A()
        elif name == 'Snap A-B':
            snap_A_2_B()
        elif name == 'Prep Char':
            prep_char()
        elif name == 'Skinning':
            skinning()
        elif name == 'Reset Ctrls':
            reset()


# ------------------------- Run from bw_Menu --------
def run():
    # use .launch() to close_UIs, show(), and raise
    BwToolsUI().launch()
    # BwToolsUI().show()


# ------------------------- Button Functions...

def snap_B_2_A():
    from bw_tools.bw_Menu.snap import snap_B_2_A
    snap_B_2_A.run()

def snap_A_2_B():
    from bw_tools.bw_Menu.snap import snap_A_2_B
    snap_A_2_B.run()

def prep_char():
    from bw_tools.bw_Menu.rig import prep_char
    prep_char.run()

def skinning():
    from bw_tools.rigging.bw_skinning_UI import SkinUI
    SkinUI().show()

def reset():
    from bw_tools.bw_Menu.anim import reset_to_defaults
    reset_to_defaults.run()
