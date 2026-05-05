
import maya.cmds as mc
from bw_tools import bw_utils


def const_null(obj, cType="parent"):
    """ creates an empty group constrained to given obj """
    if mc.objectType(obj, isAType='transform'):
        name = bw_utils.getName(obj) + '_grp'


        # create null and give unique name
        if mc.objExists(name):
            null = mc.group(em=True, name=f"{name}#")
        else:
            null = mc.group(em=True, name=name)

        # get and match Rotation Order
        rotOrder = mc.getAttr(f"{obj}.ro")
        mc.setAttr(f"{null}.ro", rotOrder)

        # constrain null to obj
        con = bw_utils.constrain(null, obj, cType)
        return null, con
    else:
        type = mc.objectType(obj)
        mc.warning(f"{obj} is a {type}, not a transform")


def run():
    for obj in mc.ls(sl=1):
        print(f'Parent Constaining Null to {obj}')
        const_null(obj, "parent")
