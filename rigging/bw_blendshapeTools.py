import maya.cmds as cmds


def copyShapeFromAttrs(mesh=None, ctrl=None, attrs=None, prefix='bs', offset=25):
    # make shapes geo from F ctrl
    move = offset

    #get F ctrl and mesh
    sel = cmds.ls(sl=True)
    if not mesh:
        if len(sel) == 2:
            mesh = sel[0]
        else:
            mesh = 'm_head_wrap'
    if not ctrl:
        if len(sel) == 2:
            ctrl = sel[1]
        else:
            ctrl = 'm_face_CTRL'
    if not attrs:
        attrs = cmds.listAttr(ctrl, userDefined=True, keyable=True)

    for shape in attrs:
        attr = '{}.{}'.format(ctrl, shape)
        cmds.setAttr(attr, 10)
        newMesh = cmds.duplicate(mesh, name='{}_{}'.format(prefix, shape))
        cmds.setAttr(attr, 0)
        cmds.setAttr('{}.translateX'.format(newMesh[0]), move)
        cmds.setAttr('{}.visibility'.format(newMesh[0]), 1)
        move += offset
        cmds.setAttr(attr, 0)

def connectBStoCtrl(bs_node=None, F_ctrl=None):
    # connect a blendshape to F ctrl
    F_attrs = cmds.listAttr(F_ctrl, userDefined=True)

    for bs_attr in cmds.listAttr('{}.w'.format(bs_node), multi=True):
        # find matching F_ctrl attr to current blendshape attr
        F_attr = None
        for attr in F_attrs:
            # look for name of F_attr in bs_attr
            if bs_attr.find(attr) != -1:
                F_attr = attr
        if F_attr:
            if cmds.attributeQuery(F_attr, node=F_ctrl, exists=True):
                # make divide by 10 node
                dbt_node = cmds.shadingNode('multDoubleLinear', asUtility=True, name='DivByTen_{}'.format(F_attr))
                cmds.setAttr("{}.input2".format(dbt_node), 0.1)
                # connect F_ctrl to Blendshape
                cmds.connectAttr('{}.{}'.format(F_ctrl, F_attr), '{}.input1'.format(dbt_node), force=True)
                cmds.connectAttr('{}.output'.format(dbt_node), '{}.{}'.format(bs_node, bs_attr), force=True)
                print('\t connected {} to {}.{}'.format(bs_attr, F_ctrl, F_attr))
            else:
                print('attr not found: {}.{}'.format(F_ctrl, F_attr))
        else:
            print('attr: {} not found on {}'.format(bs_attr, F_ctrl))


def connectBlendshapes():
    # searches selection for blendshape nodes and a face ctrl
    blendshapes = []
    F_ctrl = None

    for sel in cmds.ls(sl=1):
        for shape in cmds.listRelatives(sel, children=True, shapes=True) or []:
            if cmds.objectType(shape) == 'nurbsCurve':
                if sel.find("face") != -1:
                    F_ctrl = sel

            elif cmds.objectType(shape) == 'mesh':
                for c in cmds.listConnections(shape, destination=False, type='blendShape') or []:
                    blendshapes.append(c)

            else:
                cmds.warning("{} is not a curve or a mesh, SKIPPING".format(sel))
    if blendshapes and F_ctrl:
        for bs in blendshapes:
            print('connecting BS[{}] to F_ctrl[{}]'.format(bs, F_ctrl))
            connectBStoCtrl(bs, F_ctrl)

