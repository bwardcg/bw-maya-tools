###############################
#
#   Reloads entire bw_tools library (that have been imported) and rebuilds bw_Menu
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_menu
#
###############################

import sys
from importlib import reload
from bw_tools import bw_menu

PACKAGE = 'bw_tools'

def reload_package(package_name = PACKAGE, buildMenu=True):
    print(f"\nbw_reload...\n** Reloading package: {package_name}")
    
    # Collect all currently loaded modules that belong to this package
    modules_to_reload = [
        name for name in sys.modules
        if name.startswith('bw_tools') and not name.endswith('reload_tools')
        ]

    # Sort by depth: reload deepest modules first to handle imports properly
    modules_to_reload.sort(key=lambda x: x.count('.'), reverse=True)

    for module_name in modules_to_reload:
        try:
            print(f" - Reloading: {module_name}")
            reload(sys.modules[module_name])
        except Exception as e:
            print(f"!!!!! - Failed to reload {module_name}: \n\t\t{e}")

    print(f"** Reload complete for package: {package_name}\n")

    if buildMenu:
        bw_menu.build()

def run():
    reload_package()

if __name__ == '__main__':
    run()
