################################################
#                                              #
#   UI for bw_tools (Brian Ward's Maya Tools)  #
#                                              #
################################################


import maya.OpenMayaUI as omui
import maya.cmds as cmds
from importlib import reload

try:
    from PySide2 import QtWidgets, QtCore
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtWidgets, QtCore
    from shiboken6 import wrapInstance


DOCK_NAME = "bw_Dock"
UI_TITLE = "bw_Rig"

BUTTONS = ['Prep', 'Snap Rig', 'Skinning', 'Reset', 'Space Switch']


# ------------------------- Dockable UI
def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

class BwToolsUI(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(BwToolsUI, self).__init__(parent)
        self.setWindowTitle(UI_TITLE)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(15)
        self.buttons = []
        self.create_buttons()
        self.layout().addStretch()

    def create_buttons(self):
        for btn_name in BUTTONS:
            btn = QtWidgets.QPushButton(f"{btn_name}")
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            # using lambda expression so vaiable gets reset on each loop (inside button press)
            btn.clicked.connect(lambda *_, n=btn_name: self.on_button_clicked(n))
            self.buttons.append(btn)
            self.layout().addWidget(btn)  # Add directly in order

    # resize not great when docked
    '''
    def resizeEvent(self, event):
        # keeps buttons square
        super(BwToolsUI, self).resizeEvent(event)
        width = self.width() - self.layout().contentsMargins().left() - self.layout().contentsMargins().right()
        for btn in self.buttons:
            btn.setFixedHeight(width)
    '''

    def on_button_clicked(self, name):
        print(f"Button {name} clicked!")
        # ------------------------------- call Button Function methods here...
        if name == 'Snap Rig':
            snap_rig()
        elif name == 'Skinning':
            skinning()
        elif name == 'Prep':
            prep()
        elif name == 'Reset':
            reset()
        elif name == 'Space Switch':
            space_switch()
        elif name == BUTTONS[5]:
            print("ADD MORE FUNTIONS HERE")
        


def delete_old_ui():
    if cmds.workspaceControl(DOCK_NAME, q=True, exists=True):
        cmds.deleteUI(DOCK_NAME, control=True)

    if cmds.workspaceControlState(DOCK_NAME, exists=True):
        cmds.workspaceControlState(DOCK_NAME, remove=True)    


def get_workspace_control_widget(name):
    ptr = omui.MQtUtil.getCurrentParent()
    if ptr is None:
        ptr = omui.MQtUtil.findControl(name)
    return wrapInstance(int(ptr), QtWidgets.QWidget)


def show(width=100, dock=False, side='left'):

    delete_old_ui()

    # Create floating workspace control
    cmds.workspaceControl(
        DOCK_NAME,
        label=UI_TITLE,
        initialWidth=width,
        retain=False,
        floating=True
    )

    # --- Create layout and child UI immediately ---
    ctrl_widget = get_workspace_control_widget(DOCK_NAME)
    custom_ui = BwToolsUI()

    layout = ctrl_widget.layout()

    # Clear any old widgets
    for i in reversed(range(layout.count())):
        child = layout.itemAt(i).widget()
        if child:
            child.setParent(None)

    layout.addWidget(custom_ui)

    # --- Now dock if needed ---
    if dock and side:
        try:
            cmds.workspaceControl(DOCK_NAME, e=True, dockToMainWindow=(side, 1))
        except RuntimeError:
            # fallback: leave floating if docking fails
            pass


if __name__ == "__main__":
    # Run the UI
    print('running snaprig UI as Main')
    window = BwToolsUI()
    window.show()


# ------------------------- Run from bw_Menu --------
def run():
    show()


# ------------------------- Button Functions...

def snap_rig():
    from PA_tools import snaprig_UI as snaprig
    reload(snaprig)
    snaprig.show_snap_ui()

def skinning():
    from bw_tools.rigging import bw_skinning_UI as bw_skin
    reload(bw_skin)
    try:
        bw_skin_ui.close() 
    except:
        pass
    bw_skin_ui = bw_skin.SkinUI()
    bw_skin_ui.show()

def prep():
    from PA_tools import prep_char
    reload(prep_char)
    prep_char.run_UI()

def reset():
    from PA_tools import Reset_To_Default_Value as reset
    reload(reset)
    reset.initialize()

def space_switch():
    print("ADD SPACE SWITCH UI HERE")


