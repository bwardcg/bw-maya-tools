###############################
#
#   BW_CTRL_SHAPES  uses saved file to import control shapes
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires: 
#
##############################

import maya.cmds as cmds
import os, sys

CONTAINER = 'Shapes_Container'

class ShapePickerTool:
    """
    A Maya tool to import a file containing a base object with multiple shapes,
    spawn a UI with a list of those shapes, and create a new control from the selected shape.
    """
    def __init__(self):
        self.window_name = "shapePicker_Window"
        self.asset_path = self.get_asset_path()
        self.shape_nodes = []
        self.imported_object = None

    def get_asset_path(self):
        """Constructs the absolute path to the control shapes file."""
        try:
            current_script_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            current_script_dir = os.path.dirname(os.path.abspath(sys.argv))

        asset_file = os.path.join(current_script_dir, "ctrl_shapes", "ctrl_shapes.mb")
        return asset_file

    def create_ui(self):
        """Creates the main UI window for the tool and automatically handles the asset."""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name, window=True)

        self.window = cmds.window(
            self.window_name,
            title="Shape Picker Tool",
            widthHeight=(300, 300),
            minimizeButton=False,
            maximizeButton=False,
        )

        main_layout = cmds.columnLayout(adjustableColumn=True, parent=self.window)
        #cmds.text(label="Asset location: ", align="left")
        #cmds.text(label=self.asset_path, align="left", wordWrap=True)

        cmds.separator(height=10, style="in", parent=main_layout)
        cmds.text(label="Select a shape:", align="left")

        self.shape_list_widget = cmds.textScrollList(
            "shapeList",
            allowMultiSelection=False,
            parent=main_layout,
        )

        cmds.separator(height=10, style="in", parent=main_layout)
        cmds.button(
            label="Create New Control", command=self.create_control, parent=main_layout
        )

        self.handle_asset()
        cmds.showWindow(self.window)
        
    def handle_asset(self):
        """Checks for an existing object in the scene, otherwise imports the asset."""
        self.container_node = CONTAINER
        if not cmds.objExists(self.container_node):
            self.container_node = cmds.file(self.asset_path, i=True, returnNewNodes=True)
        self.get_shapes_list(self.container_node)

    def get_shapes_list(self, node):
        """Finds all shape nodes under the designated object and populates the UI list."""
        self.shape_nodes = cmds.listRelatives(
            node, shapes=True, fullPath=True
        ) or []

        if not self.shape_nodes:
            cmds.warning(f"No shape nodes found under '{node}'.")
            return

        cmds.textScrollList(self.shape_list_widget, edit=True, removeAll=True)
        for shape in self.shape_nodes:
            clean_name = shape.split("|")[-1]
            cmds.textScrollList(self.shape_list_widget, edit=True, append=clean_name)

    def create_control(self, *args):
        """
        Creates a new transform and parents a copied shape node under it.
        """
        selected_items = cmds.textScrollList(self.shape_list_widget, query=True, selectItem=True)
        if not selected_items:
            cmds.warning("Please select a shape from the list.")
            return

        selected_shape = selected_items[0]
        print(f'creating from {selected_shape}')

        temp_xform = cmds.duplicate(
            self.container_node,
            name="TEMP",
            parentOnly=False,
            inputConnections=False,
        )[0]

        # create our new control and delete TEMP
        new_ctrl = cmds.createNode("transform", name=f"{selected_shape}_ctrl")
        target_shape = f'|{temp_xform}|{selected_shape}'
        target_shape = cmds.rename(target_shape, f'{new_ctrl}Shape')
        cmds.parent(target_shape, new_ctrl, shape=True, relative=True)
        cmds.delete(temp_xform)
        cmds.select(new_ctrl)


def run_tool():
    """Initializes and runs the Shape Picker Tool."""
    ShapePickerTool().create_ui()

# Example usage:
if __name__ == "__main__":
    run_tool()
