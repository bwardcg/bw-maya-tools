###############################
#
#   Builds a menu on top menu bar, runs scripts with .run()
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
###############################


import os, sys, importlib
import subprocess
import maya.cmds as cmds
import maya.mel as mel


ROOT_DIR = os.path.join(os.path.dirname(__file__), 'bw_Menu')


def build(root_dir = None):

    if not root_dir:
        root_dir = ROOT_DIR

    if not os.path.exists(root_dir):
        cmds.warning(f"Directory does not exist: {root_dir}")
        return False

    menu_name = os.path.basename(root_dir)

    if cmds.menu(menu_name, exists=True):
        cmds.deleteUI(menu_name, menu=True)

    main_window = mel.eval('$tmpVar=$gMainWindow')
    menu = cmds.menu(menu_name, parent=main_window, tearOff=True)

    base_dir = os.path.dirname(os.path.dirname(root_dir))
    print(f'bw_Menu...\nBase dir found: {base_dir}\n -- adding Items...')
    add_items(menu, root_dir, base_dir)

    return True


#----- Util Functions ------

def file_to_module_path(full_path, base_dir):
    print(f'creating module path from: {full_path}')
    rel_path = os.path.relpath(full_path, base_dir)
    # get parent of python file as a module (scripts.blah.mod)
    module_path = rel_path.replace(os.sep, ".").replace('.py','')
    print(f' -- module path is: {module_path}')
    return module_path


def make_menu_command(module_path, file_path):
    def run_tool(*args):
        print(f"Running: {module_path} from {file_path}")
        try:
            module = importlib.import_module(module_path)
            importlib.reload(module)

            if hasattr(module, "run"):
                module.run()
            else:
                cmds.warning(f'{module} had no run() function defined')
        except Exception as e:
            cmds.warning(f"Error running {module_path}: {e}")
    return run_tool


def add_items(parent_menu, current_dir, base_dir):
    py_files = []
    subdirs = []

    for item in sorted(os.listdir(current_dir)):
        if item.startswith(".") or item.startswith("__"):
            continue

        full_path = os.path.join(current_dir, item)

        if os.path.isfile(full_path) and item.endswith(".py"):
            py_files.append(full_path)

        elif os.path.isdir(full_path):
            # Check if dir contains .py files recursively
            contains_py = False
            for root, dirs, files in os.walk(full_path):
                if any(f.endswith(".py") and not f.startswith(".") and not f.startswith("__") for f in files):
                    contains_py = True
                    break
            if contains_py:
                subdirs.append(full_path)

    for py_file in py_files:
        py_file = py_file.replace('\\','/')
        module_path = file_to_module_path(py_file, base_dir)
        label = os.path.splitext(os.path.basename(py_file))[0]
        menu_command = make_menu_command(module_path, py_file)

        cmds.menuItem(
            label=label,
            parent=parent_menu,
            command=menu_command
        )

    for subdir in subdirs:
        submenu = cmds.menuItem(
            label=os.path.basename(subdir),
            parent=parent_menu,
            subMenu=True,
            tearOff=True
        )
        add_items(submenu, subdir, base_dir)
