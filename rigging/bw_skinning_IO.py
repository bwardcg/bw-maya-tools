import maya.cmds as cmds

def export_callback(*args):
    character = cmds.textField("characterField", query=True, text=True)
    path = cmds.textField("pathField", query=True, text=True)
    selected_radio = cmds.radioButtonGrp("characterRadio", query=True, select=True)
    option = "Option A" if selected_radio == 1 else "Option B"

    print(f"Exporting {character} ({option}) to {path}")

def import_callback(*args):
    character = cmds.textField("characterField", query=True, text=True)
    path = cmds.textField("pathField", query=True, text=True)
    selected_radio = cmds.radioButtonGrp("characterRadio", query=True, select=True)
    option = "Option A" if selected_radio == 1 else "Option B"

    print(f"Importing {character} ({option}) from {path}")

def cancel_callback(*args):
    if cmds.window("myToolWindow", exists=True):
        cmds.deleteUI("myToolWindow", window=True)

def update_path(*args):
    """ Update Path Field Automatically """
    character = cmds.textField("characterField", query=True, text=True)
    path = f"/path/to/weights/{character}/"
    cmds.textField("pathField", edit=True, text=path)

def create_ui():
    if cmds.window("myToolWindow", exists=True):
        cmds.deleteUI("myToolWindow", window=True)

    window = cmds.window("myToolWindow", title="Skin Weight Tool", widthHeight=(420, 250))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    # Instructions
    cmds.text(label="Use this tool to Export or Import Skin Weights.", align="center")
    cmds.text(label="1. Enter the Character Name and select an option.", align="center")
    cmds.text(label="2. Path will auto-fill with the character name.", align="center")
    cmds.text(label="3. Click Export or Import.", align="center")
    cmds.separator(height=10, style="in")

    # Character Field with Radio Buttons
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(80, 200, 120), adjustableColumn=2)
    cmds.text(label="Character:")
    cmds.textField("characterField", changeCommand=update_path)
    cmds.radioButtonGrp("characterRadio", label="", labelArray2=["Option A", "Option B"], numberOfRadioButtons=2, select=1)
    cmds.setParent("..")

    # Path Field (Auto Updated)
    cmds.text(label="Path:")
    cmds.textField("pathField", editable=False)  # Read-only

    # Buttons
    cmds.separator(height=10, style="none")
    cmds.rowLayout(numberOfColumns=4, columnWidth4=(100, 100, 150, 150), adjustableColumn=2)
    cmds.button(label="Cancel", command=cancel_callback, backgroundColor=(0.6, 0.3, 0.3))
    cmds.text(label="")
    cmds.button(label="Export", command=export_callback, backgroundColor=(0.3, 0.6, 0.3))
    cmds.button(label="Import", command=import_callback, backgroundColor=(0.3, 0.3, 0.6))

create_ui()
