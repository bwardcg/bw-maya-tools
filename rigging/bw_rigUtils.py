"""
Brian Ward's helper functions
not studio supported!!
"""


import maya.cmds as cmds
import maya.mel as mel
from bw_tools import bw_utils
from bw_tools.bw_snap import Snap

VIS_CTRL = 'vis_ctrls_node'

END = 'prefix'
LEN = 2
MIDDLE = 'm_'
RIGHT = 'r_'
LEFT = 'l_'


def getSkinCluster(obj, v=False):
    """
    find a skin cluster on given obj
    """
    skins = []
    if cmds.nodeType(obj) == 'mesh':
        shapes = [obj]
    else:
        shapes = cmds.listRelatives(obj, shapes=True, path=True, noIntermediate=True) or []

    for shape in shapes:
        history = cmds.listHistory(shape, pruneDagObjects=True, interestLevel=2)
        if history:
            skins = [x for x in history if cmds.nodeType(x) == 'skinCluster']
        if skins:
            if v:
                print("found skin: {}".format(skins))
            return skins[0]
        elif v:
            cmds.warning("found no skins on: {}".format(obj))
    return None


def get_anim_curves(sdk=False, pairblend=False):
    anim_curve_types = ['animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU']
    all_anim_curves = []

    for curve_type in anim_curve_types:
        all_anim_curves += cmds.ls(type=curve_type)

    to_return = []

    for curve in all_anim_curves:
        # Skip if it's a driven key and we don't want them
        incoming = cmds.listConnections(curve + '.input', source=True, destination=False) or []
        if incoming and not sdk:
            continue

        # Skip if connected to a pairBlend node (in or out)
        if not pairblend:
            connected_nodes = cmds.listConnections(curve, source=True, destination=True) or []
            if any(cmds.nodeType(node) == 'pairBlend' for node in connected_nodes):
                continue

        to_return.append(curve)

    return to_return


def cleanPivot(x, world=True):
    """ zero out local pivots"""
    result = False

    for a in ['rotatePivot', 'scalePivot']:
        for d in ['X', 'Y', 'Z']:
            attr = f'{x}.{a}{d}'
            if cmds.getAttr(attr) != 0:
                cmds.warning(f'resetting pivot: {attr}')
                cmds.setAttr(attr, e=True, lock=False)
                cmds.setAttr(attr, 0)
                result = True
    return result


def create_space_switch(name='space_switch', attr='space_switch', spaces=['local','world'], suf='spsw'):
    # make transform for spaceswitch
    null = cmds.group(name=f'{name}_spaceswitch_{suf}', empty=True)
    
    # add space attr
    cmds.addAttr(null, ln=attr, at="enum", en=':'.join(spaces))
    cmds.setAttr(f'{null}.{attr}', e=True, keyable=True)
    
    # make locators for spaces
    locs = []
    for i, s in enumerate(spaces):
        # create locator with short name
        loc = cmds.spaceLocator(name=s)[0]
        
        # constrain transform to locator
        constraint = cmds.parentConstraint(loc, null, name=f'{"_".join(spaces)}_parConst')[0]
    
        # rename locator and add to list
        loc = cmds.rename(loc, f'{name}_{s}_spc_{suf}')
        locs.append(loc)
    
        # create condition node
        cond_node = cmds.createNode("condition", name=f"condition_{loc}")
        
        # connect space switch enum to condition
        cmds.connectAttr(f'{null}.{attr}', f'{cond_node}.firstTerm')
    
        # connect condition to constraint
        cmds.connectAttr(f'{cond_node}.outColorR', f'{constraint}.{s}W{i}', force=True)
        
        # set condition node logic
        cmds.setAttr(f'{cond_node}.operation', 0) # 0 is 'Equal'
        cmds.setAttr(f'{cond_node}.secondTerm', i)
        cmds.setAttr(f'{cond_node}.colorIfTrueR', 1)
        cmds.setAttr(f'{cond_node}.colorIfFalseR', 0)
    
    if cmds.objExists(name):
        cmds.parent(name, null)


def extras_vis(name=None, objs_list=None):
    """make visibility groups for given accessories"""

    if not objs_list:
        objs_list = cmds.ls(sl=1, type='transform')
    if not name:
        name = bw_utils.inputPrompt(title='give your extras group a name')

    ctrl_node = VIS_CTRL
    attr = '{}_vis'.format(name)
    quantity = len(objs_list)

    # check for ctrl_node node and attr
    if not cmds.objExists(ctrl_node):
        print("** creating ctrl_node grp: {}".format(ctrl_node))
        ctrl_node = cmds.group(empty=True, name=ctrl_node)
    if not cmds.attributeQuery(attr, node=ctrl_node, exists=True):
        print("** adding vis attr: {}".format(attr))
        cmds.addAttr(ctrl_node, ln=attr, at='long')
        cmds.setAttr('{}.{}'.format(ctrl_node, attr), e=True, keyable=True)

    # set min max
    cmds.addAttr('{}.{}'.format(ctrl_node, attr), edit=True, min=0, max=(quantity - 1))

    # make group for given name
    top_grp = cmds.group(empty=True, name='{}_GRP'.format(name))
    cmds.parent(top_grp, ctrl_node)

    for index in range(quantity):
        # make groups
        cond = cmds.shadingNode('condition', asUtility=True, name='{}_{}_condition'.format(name, index))
        grp = cmds.group(empty=True, name='{}_{}_grp'.format(name, index))
        cmds.parent(grp, top_grp)

        # make condition node
        cmds.connectAttr('{}.{}'.format(ctrl_node, attr), '{}.firstTerm'.format(cond), force=True)
        cmds.setAttr('{}.secondTerm'.format(cond), index)
        cmds.setAttr('{}.operation'.format(cond), 1)

        # connect to ctrl_node group
        cmds.connectAttr('{}.outColor.outColorR'.format(cond), '{}.visibility'.format(grp), force=True)

        # parent geo to group
        cmds.parent(objs_list[index], grp)


def bufferXform(obj):
    """
    add parent group to zero out selected transform
    """
    if obj:
        if cmds.objectType(obj, isAType='transform'):
            # name the new null
            if obj[-5:] == '_Ctrl' or obj[-5:] == '_ctrl':
                buffName = obj[:-5] + "_buffer"
            else:
                buffName = obj + "_buffer"
            if cmds.objExists(buffName):
                buffName = buffName + "#"

            # make null and parent to next to target
            null = cmds.group(em=True, name=buffName)
            p = cmds.listRelatives(obj, parent=True, fullPath=True)
            if p:
                cmds.parent(null, p)

            # snap null to target and parent target under null
            snap_obj.snapObjs(obj, null)
            cmds.parent(obj, null)

            # return name of buffer
            return null
        else:
            print('%s is not a transform, SKIPPING' % obj)
    else:
        print('no transform given for buffering')
        return None


def scaleCurves(scaleVal = None, objList = None):
    """
    scale selected curve ctrls by scaleVal
    default scale value is Half
    """
    selected = cmds.ls(sl=1)
    curves = []
    shape = None
    if not scaleVal:
        scaleVal = .5
    if not objList:
        objList = selected
        
    # list shape nodes by type
    for sel in objList:
        # get shape node
        if cmds.objectType(sel, isAType='transform'):
            shape = cmds.listRelatives(sel, children=True, shapes=True)[0]
        elif cmds.objectType(sel, isAType='shape'):
            shape = sel
        # check type
        if cmds.objectType(shape) == 'nurbsCurve':
            curves.append(shape)
        elif cmds.objectType(shape) == 'camera':
            cams.append(shape)

    # scale curves
    if curves:
        # todo:  better way to get all the CVs?
        cmds.select(curves)
        cmds.pickWalk(d='up')
        mel.eval("selectCurveCV all")

        cmds.scale(scaleVal, scaleVal, scaleVal, relative=True, objectCenterPivot=True)
        cmds.select(clear=True)

    # restore selection
    cmds.select(selected)


# -----------------------  Color utilities ---------------
def changeColor(objs=None, color=None):
    """
    sets color override to 'red', 'yellow' or 'blue'.
    defaults to yellow
    """

    # BREAKS ON NON-UNIQUE NAMES !!!

    if color == 'red':
        colorIndex = 13
    elif color == 'blue':
        colorIndex = 6
    elif color == 'yellow':
        colorIndex = 17
    else:
        print("%s is not a valid color choice." % color)
        print("please choose 'red', 'blue' or 'yellow'.")
        return False

    if not objs:
        objs = cmds.ls(sl=1)

    print("coloring {}: {}".format(color, objs))
    for obj in objs:
        for objShape in cmds.listRelatives(obj, shapes=True):
            cmds.setAttr(objShape + ".overrideEnabled", 1)
            cmds.setAttr(objShape + ".overrideColor", colorIndex)
    return True


def colorByName(objs=None):
    """
    sets color override to 'red', 'yellow' or 'blue'.
    based on name prefix: r_, m_, l_
    """

    if not objs:
        objs = cmds.ls(sl=1)

    rightSide = []
    middle = []
    leftSide = []

    for obj in objs:
        if END == 'prefix':
            if obj[:LEN] == RIGHT:
                rightSide.append(obj)
            if obj[:LEN] == MIDDLE:
                middle.append(obj)
            if obj[:LEN] == LEFT:
                leftSide.append(obj)

    if middle:
        print("coloring middle: {}".format(middle))
        changeColor(objs=middle, color='yellow')
    if rightSide:
        print("coloring right: {}".format(rightSide))
        changeColor(objs=rightSide, color='red')
    if leftSide:
        print("coloring left: {}".format(leftSide))
        changeColor(objs=leftSide, color='blue')
