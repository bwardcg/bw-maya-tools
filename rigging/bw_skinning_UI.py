"""
Some Skin Weighting IO tools.
Written by Brian Ward

usage:
from bw_tools.rigging import bw_skinning_UI
skin_ui = bw_skinning_UI.SkinUI()
skin_ui.show()

"""


try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
from bw_tools.rigging import bw_skinning as skin
from importlib import reload


def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


TITLE = 'BW Skinning'


#TODO  re-get path when char name entered


# --------------------------- UI code ------------------------

class CollapsibleSection(QtWidgets.QWidget):
    def __init__(self, title, parent=None):
        super(CollapsibleSection, self).__init__(parent)
        
        self.toggle_button = QtWidgets.QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { font-weight: bold; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.clicked.connect(self.on_toggle)

        self.content_area = QtWidgets.QWidget()
        self.content_area.setMaximumHeight(0)
        self.content_area.setMinimumHeight(0)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)
        self.init_animation()

    def init_animation(self):
        self.toggle_animation.addAnimation(QtCore.QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QtCore.QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QtCore.QPropertyAnimation(self.content_area, b"maximumHeight"))

    def on_toggle(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)

        content_height = self.content_area.sizeHint().height()

        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(200)
            animation.setStartValue(self.sizeHint().height())
            if checked:
                animation.setEndValue(self.sizeHint().height() + content_height)
            else:
                animation.setEndValue(self.sizeHint().height() - content_height)

        self.toggle_animation.start()


class SkinUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super(SkinUI, self).__init__(parent)
        self.setWindowTitle(TITLE)
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.main_layout = QtWidgets.QVBoxLayout(self)

        # Sections
        self.sections = {}
        for section_name in ["Bind", "Export/Import"]:
            section = CollapsibleSection(section_name)
            self.sections[section_name.lower().replace("/", "")] = section
            self.main_layout.addWidget(section)

        # Bind Section Content
        self.setup_bind_section()

        # Export/Import Section Content
        self.char = skin.get_char()
        self.dir = skin.get_dir(self.char, latest=True)
        self.setup_export_import_section()

        self.main_layout.addStretch()

    def browse_path(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory")
        if folder_path:
            self.path_input.setText(folder_path)  # Correct reference to path_input

    def setup_bind_section(self):
        # Bind Section Content (same as before)
        bind_section_layout = QtWidgets.QVBoxLayout()
        bind_label = QtWidgets.QLabel("Operates on Selected Geometry")
        bind_section_layout.addWidget(bind_label)

        max_influences_layout = QtWidgets.QHBoxLayout()

        self.max_influences_label = QtWidgets.QLabel("Max Influences:")
        self.max_influences_textbox = QtWidgets.QLineEdit()
        self.max_influences_textbox.setFixedWidth(60)
        self.max_influences_textbox.setValidator(QtGui.QIntValidator())
        self.max_influences_textbox.setPlaceholderText("0")
        max_influences_layout.addWidget(self.max_influences_label)
        max_influences_layout.addWidget(self.max_influences_textbox)

        self.maintain_max_influence_checkbox = QtWidgets.QCheckBox("Maintain Influence Max")
        max_influences_layout.addWidget(self.maintain_max_influence_checkbox)

        bind_section_layout.addLayout(max_influences_layout)

        self.bind_selected_button = QtWidgets.QPushButton("Bind to Selected Joints")
        self.bind_all_button = QtWidgets.QPushButton("Bind to ALL Joints")
        self.normalize_weights_button = QtWidgets.QPushButton("Normalize Weights")
        self.dup_skin_button = QtWidgets.QPushButton("Dup Skin Clstrs (source last)")
        
        bind_section_layout.addWidget(self.bind_selected_button)
        bind_section_layout.addWidget(self.bind_all_button)
        bind_section_layout.addWidget(self.normalize_weights_button)
        bind_section_layout.addWidget(self.dup_skin_button)

        self.sections["bind"].content_area.setLayout(bind_section_layout)

        # Connect buttons to their respective functions with proper arguments
        self.bind_selected_button.clicked.connect(self.on_bind_selected)
        self.bind_all_button.clicked.connect(self.on_bind_all)
        self.normalize_weights_button.clicked.connect(normalize_weights)
        self.dup_skin_button.clicked.connect(dup_skin)

    def setup_export_import_section(self):
        # Export/Import Section Content
        export_import_section_layout = QtWidgets.QVBoxLayout()

        # Char Input (preloaded string variable)
        self.char_label = QtWidgets.QLabel("Character:")
        self.char_input = QtWidgets.QLineEdit(self.char)  # Preloaded string variable
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_fields)

        export_import_section_layout.addWidget(self.char_label)

        # Add Char Name and Refresh Button in the same row
        char_layout = QtWidgets.QHBoxLayout()
        char_layout.addWidget(self.char_input)
        char_layout.addWidget(self.refresh_button)
        export_import_section_layout.addLayout(char_layout)

        # Path Input with Browse button for Export
        self.path_label = QtWidgets.QLabel("Path:")
        self.path_input = QtWidgets.QLineEdit(self.dir)  # Preloaded string variable
        self.browse_button = QtWidgets.QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_path)  # Correct method call

        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)

        export_import_section_layout.addWidget(self.path_label)
        export_import_section_layout.addLayout(path_layout)

        # Export Buttons (Same row)
        export_button_layout = QtWidgets.QHBoxLayout()
        self.export_selected_button = QtWidgets.QPushButton("Export Selected")
        self.export_all_button = QtWidgets.QPushButton("Export ALL")
        
        export_button_layout.addWidget(self.export_selected_button)
        export_button_layout.addWidget(self.export_all_button)

        export_import_section_layout.addLayout(export_button_layout)

        # Import Buttons (Next row)
        import_button_layout = QtWidgets.QHBoxLayout()
        self.import_selected_button = QtWidgets.QPushButton("Import Selected")
        self.import_all_button = QtWidgets.QPushButton("Import ALL")
        
        import_button_layout.addWidget(self.import_selected_button)
        import_button_layout.addWidget(self.import_all_button)

        export_import_section_layout.addLayout(import_button_layout)

        # Unbind Buttons (Next row)
        unbind_button_layout = QtWidgets.QHBoxLayout()
        self.unbind_selected_button = QtWidgets.QPushButton("Unbind Selected")
        self.unbind_all_button = QtWidgets.QPushButton("Unbind ALL")
        
        unbind_button_layout.addWidget(self.unbind_selected_button)
        unbind_button_layout.addWidget(self.unbind_all_button)

        export_import_section_layout.addLayout(unbind_button_layout)

        # Rebind Buttons (Next row)
        rebind_button_layout = QtWidgets.QHBoxLayout()
        self.rebind_selected_button = QtWidgets.QPushButton("Rebind Selected")
        self.rebind_all_button = QtWidgets.QPushButton("Rebind ALL")
        
        rebind_button_layout.addWidget(self.rebind_selected_button)
        rebind_button_layout.addWidget(self.rebind_all_button)

        export_import_section_layout.addLayout(rebind_button_layout)

        self.sections["exportimport"].content_area.setLayout(export_import_section_layout)

        # Connect buttons to their respective methods
        self.export_selected_button.clicked.connect(self.on_export_selected)
        self.export_all_button.clicked.connect(self.on_export_all)
        self.import_selected_button.clicked.connect(self.on_import_selected)
        self.import_all_button.clicked.connect(self.on_import_all)
        self.unbind_selected_button.clicked.connect(self.on_unbind_selected)
        self.unbind_all_button.clicked.connect(self.on_unbind_all)
        self.rebind_selected_button.clicked.connect(self.on_rebind_selected)
        self.rebind_all_button.clicked.connect(self.on_rebind_all)

    def on_bind_selected(self):
        max_influences = self.max_influences_textbox.text()
        maintain_max = self.maintain_max_influence_checkbox.isChecked()
        if max_influences:
            max_influences = int(max_influences)
        else:
            max_influences = 0  # Default to 0 if no value is provided
        bind_to_selected_joints(max_influences, maintain_max)

    def on_bind_all(self):
        max_influences = self.max_influences_textbox.text()
        maintain_max = self.maintain_max_influence_checkbox.isChecked()
        if max_influences:
            max_influences = int(max_influences)
        else:
            max_influences = 0  # Default to 0 if no value is provided
        bind_to_all_joints(max_influences, maintain_max)

    def on_export_selected(self):
        char_name = self.char_input.text()
        export_path = self.path_input.text()
        export_selected(char_name, export_path)

    def on_export_all(self):
        char_name = self.char_input.text()
        export_path = self.path_input.text()
        export_all(char_name, export_path)

    def on_import_selected(self):
        char_name = self.char_input.text()
        import_path = self.path_input.text()
        import_selected(char_name, import_path)

    def on_import_all(self):
        char_name = self.char_input.text()
        import_path = self.path_input.text()
        import_all(char_name, import_path)

    def on_unbind_selected(self):
        char_name = self.char_input.text()
        import_path = self.path_input.text()
        unbind_selected(char_name, import_path)

    def on_unbind_all(self):
        char_name = self.char_input.text()
        import_path = self.path_input.text()
        unbind_all(char_name, import_path)

    def on_rebind_selected(self):
        char_name = self.char_input.text()
        import_path = self.path_input.text()
        rebind_selected(char_name, import_path)

    def on_rebind_all(self):
        char_name = self.char_input.text()
        import_path = self.path_input.text()
        rebind_all(char_name, import_path)

    def refresh_fields(self):
        print("Refreshing Char Name and Path fields")
        # Logic to refresh Char Name and Path (preload new values here)
        # skin tool variables
        self.char = skin.get_char()
        self.dir = skin.get_dir(self.char, latest=True)

        self.char_input.setText(self.char)
        self.path_input.setText(self.dir)

# ----------------- call the UI

if __name__ == "__main__":
    try:
        bw_skin_ui.close() 
    except:
        pass
    bw_skin_ui = SkinUI()
    bw_skin_ui.show()


# ------------------------ Methods moved outside of the class-----------------------------

def bind_to_selected_joints(max_inf, maintain):
    print(f"Binding to Selected Joints with Max Influences: {max_inf}, Maintain Max: {maintain}")
    skin.bind_selected_geo(max_inf, maintain)

def bind_to_all_joints(max_influences, maintain_max):
    print(f"Binding to All Joints with Max Influences: {max_inf}, Maintain Max: {maintain}")
    skin.bind_selected_geo(max_inf, maintain, all_joints=True)

def normalize_weights():
    print("Normalizing Weights")
    sel = cmds.ls(sl=1)
    if sel:
        for s in sel:
            skin.normalizeWeights(s)
    elif cmds.objExists('|master|mdl'):
        # normalize all weights
        for obj in cmds.listRelatives('|master|mdl', ad=True, fullPath=True):
            # prune weights + remove unused infl?
            skin.normalizeWeights(obj)
    else:
        cmds.warning("either select geo with skinweights or have an unreferrenced char in scene")

def export_selected(char_name, export_path):
    reload(skin)
    export_path = skin.version_up(export_path)
    print(f"Exporting Selected with Character: {char_name} to {export_path}")
    skin.export_skin_weights(char_name, path=export_path, meshes=cmds.ls(sl=1))

def export_all(char_name, export_path):
    reload(skin)
    export_path = skin.version_up(export_path)
    print(f"Exporting All with Character: {char_name} to {export_path}")
    skin.export_skin_weights(char_name, path=export_path)

def import_selected(char_name, import_path):
    reload(skin)
    print(f"Importing Selected with Character: {char_name} from {import_path}")
    skin.import_skin_weights(char_name, path=import_path, meshes=cmds.ls(sl=1))

def import_all(char_name, import_path):
    reload(skin)
    print(f"Importing All with Character: {char_name} from {import_path}")
    skin.import_skin_weights(char_name, path=import_path)

def unbind_selected(char_name, import_path):
    reload(skin)
    print("Unbinding Selected Geometry")
    #  - still exports ALL weights
    skin.unbind(char_name, path=import_path, geo=cmds.ls(sl=1))  

def unbind_all(char_name, import_path):
    reload(skin)
    print("Unbinding All Geometry")
    skin.unbind(char_name, path=import_path)

def rebind_selected(char_name, import_path):
    reload(skin)
    print("Rebinding Selected Geometry")
    skin.rebind(char_name, path=import_path, selected=True)   
    # skip meshes unless selected

def rebind_all(char_name, import_path):
    reload(skin)
    print("Rebinding All Geometry")
    skin.rebind(char_name, path=import_path)                
    # binds unbound geo found in export

def dup_skin():
    reload(skin)
    # select meshes to bind, source mesh LAST
    sel = cmds.ls(sl=1)
    if len(sel) > 1:
        source = sel[-1]
        target_meshes = sel[:-1]

        for t in target_meshes:
            #print(source+' to '+t)
            sc = skin.duplicate_skin_cluster(source,t)
            cmds.rename(sc, f'sc_{t}')
    else:
        cmds.warning('Please select mesh(es) to bind, select source mesh LAST')
