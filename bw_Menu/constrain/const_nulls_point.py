
import maya.cmds as mc
import bw_tools.bw_Menu.rig.const_nulls_parent as const


def run():
    for obj in mc.ls(sl=1):
        print(f'Point Constaining Null to {obj}')
        const.const_null(obj, "point")
