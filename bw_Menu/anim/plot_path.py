###############################
#
#   Tool for converting animations into paths
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_ui_maya
#
###############################

import maya.cmds as cmds
from bw_tools import bw_utils 

def plotCurve(obj, keysOn=5, shortShot=100, longShot=500):
    """
    make a curve from translate of a transforms pivot
    args:
        requires one Maya Transform to plot
    kwargs:
        keysOn:     INT - keys on every INT frames
        longShot:   INT - shots longer than INT frames double keysOn
                          double INT is *4 keysOn
    returns:
        name of created curve, or None
    """

    long_len = longShot
    short_len = shortShot

    if not obj:
        cmds.warning('bw_path.plotCurve requires 1 transform as arg')
        return None

    startOn,endOn = bw_utils.getFrameRange()
    frLength = endOn - startOn

    if shortShot:
        # cap key freq to 2s
        if frLength < short_len and keysOn > 2:
            keysOn = 2

    if longShot:
        # less keys for longer shots
        if frLength > long_len:
            keysOn = keysOn*2
        if frLength > long_len*2:
            keysOn = keysOn*2     # double again
        if frLength > long_len*4:
            keysOn = keysOn*2     # double again

    points = list()
    if cmds.objExists(obj) and cmds.objectType(obj, isAType='transform'):
        fr = startOn
        while fr < (endOn + keysOn):
            cmds.currentTime(fr)
            points.append(cmds.xform(obj, q=True, ws=True, t=True))
            fr += keysOn
        # print points
        baseCurve = cmds.curve(d=3, p= points)
        name = bw_utils.getName(obj)
        matchedCV = cmds.fitBspline(baseCurve, ch=1, tol=.01, name=f'{name}_plotCurve')
        cmds.delete(baseCurve)
        return matchedCV
    else:
        cmds.warning(f'{obj} is not a transform')
        return None


def run():
    for sel in cmds.ls(sl=1):
        plotCurve(sel)