
import maya.cmds as mc
from bw_tools import bw_utils


def run():
    '''
    create locator as parent of all selected objects
    '''
    # TODO:  Add buffer if transform is locked or animated
    sels = cmds.ls(sl=True, type='transform')
    if not sels:
        mc.warning("grp_under_locator requires selected transforms")
        return

    # use first selected obj for name and parent
    name = bw_utils.getName()
    loc = cmds.spaceLocator(name=f"{name}_grp")
    p = cmds.listRelatives(sels[0], parent=True)
    if p:
        cmds.parent(loc, p)

    cmds.delete(cmds.parentConstraint(sels, loc, w=1))
    cmds.parent(sels, loc)
    cmds.select(loc)
    return loc
