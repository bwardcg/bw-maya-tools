###############################
#
#   BW_UTILS  my general Maya helper functions
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires: 
#
##############################

import maya.cmds as mc
import maya.mel as mm

# ---------------------------- GETTERS -----------------
def getFrameRange():
    """
    returns start and end frames from timeline
    if selection on timeline is highlighted that range will be returned instead
    """
    # check for selection on timeline:
    aPlayBackSliderPython = mm.eval('$tmpVar=$gPlayBackSlider')
    if mc.timeControl(aPlayBackSliderPython, q=True, rangeVisible=True):
        selectedTime = mc.timeControl(aPlayBackSliderPython, q=True, rangeArray=True)
        start = int(selectedTime[0])
        end = int(selectedTime[1])
    else:
        start = int(mc.playbackOptions(minTime=True, q=True))
        end = int(mc.playbackOptions(maxTime=True, q=True))
    return start, end

def getNamespace(obj):
    """
    get ROOT (first) namespace of a node
    :param obj: node to operate on
    :return: ROOT (first) namespace, if found
    """
    if obj:
        parts = obj.split(":")
        if len(parts) > 1:
            return parts[0]
        else:
            print('%s is in the root namespace' %obj)
            return ""
    else:
        print('no input given to determine namespace')
        return None

def getName(obj):
    # determine name and namespace
    name = str(obj.split(":")[-1])
    ns = getNamespace(obj)
    if ns:
        name = f'{ns}_{name}'
    return name

def getAnimCurves(ignoreReferenced=True):
    """
    find all anim curves in the scene
    if ignoreReferenced = 1 returns non-referenced curves only (default)
    if ignoreReferenced = 0 returns all anim curves
    """
    localCurves = []
    referencedCurves = []
    curves = mc.ls(type='animCurve')
    if not ignoreReferenced:
        return curves
    else:
        for crv in curves:
            # check if referenced
            if mc.referenceQuery(crv, isNodeReferenced=True):
                referencedCurves.append(crv)
            else:
                localCurves.append(crv)
        return localCurves

def get_blendshapes(mesh):
    # get blendshapes list
    history = mc.listHistory(mesh)
    blndshp_list = mc.ls(history, type="blendShape")
    return blndshp_list

def get_deformers(obj, types=False):
    """
    attempt to find deformers on an object
    :param obj: to check for deformers
    :param types: if True - return list of deformer types
    :return: list of deformer nodes found (unless types is True)
    """
    deformers = []
    deformerTypes = []
    # check for deformers by looking for geometryFilter as an inherited type
    for shape in mc.listRelatives(obj, children=True, shapes=True):
        for item in mc.listHistory(shape):
            if 'geometryFilter' in mc.nodeType(item, inherited=True):
                deformers.append(item)
                deformerTypes.append(mc.nodeType(item))
    if types:
        return sorted(set(deformerTypes))
    else:
        return deformers

def getNonProxyAttrs(obj, v = None):
    """
    returns attributes that are used as a proxy
    """
    faceAttrs = mc.listAttr(obj, keyable = True)
    nonProxyAttrs = []
    if v: print("\nchecking {} for Proxy Attrs".format(obj))
    for attr in faceAttrs:
        if mc.addAttr(obj+'.'+attr, query = True, uap = True):
            if v: print(' -- {} is a proxy attr'.format(attr))
        else:
            nonProxyAttrs.append(attr)
    return nonProxyAttrs

def get_skin(obj):
    # get shape and skincluster
    for shapenode in mc.listRelatives(obj, children=True, type='mesh'):
        hist = mc.listHistory(shapenode)
        skinnode = mc.ls(hist, type='skinCluster')
        if skinnode:
            return skinnode[0], shapenode

def get_constraining_objs(obj):
    '''
    Returns an Obj's Constraint Target(s) for all constraints
    '''
    if not obj:
        obj = mc.ls(sl=True, type='transform')[0]
    cns = mc.listRelatives(obj, type='constraint')
    tgt_list = []
    for cn in cns:
        tgts = mc.listConnections(cn + '.target')
        tgt = set([c for c in tgts if not cn in c])
        for t in tgt:
            tgt_list.append(t)
    return tgt_list


# ---------------------------- SETTERS -----------------
def set_user_attr_defaults(obj, keyable=True):
    '''
    sets an objects User Attrs default value to current value
    currently only specifies Float and Int values, everything else is luck
    '''
    outcome = False
    for attr in mc.listAttr(obj, k=True, userDefined=True, unlocked=True, m=True) or []:
        val = mc.getAttr(f'{obj}.{attr}')
        if isinstance(val, float):
            defval = mc.attributeQuery(attr, n=obj, ld=True)[0]
            if val != defval:
                val = float(val)
                print(f'setting {obj}.{attr} default value to {val}')
                mc.addAttr(f'{obj}.{attr}', edit=True, defaultValue=val)
                outcome = True
        elif isinstance(val, int):
            defval = mc.attributeQuery(attr, n=obj, ld=True)[0]
            if val != defval:
                val = int(val)
                print(f'setting {obj}.{attr} default value to {val}')
                mc.addAttr(f'{obj}.{attr}', edit=True, defaultValue=val)
                outcome = True
        else:
            defval = mc.attributeQuery(attr, n=obj, ld=True)[0]
            if val != defval:
                try:
                    print(f'setting {obj}.{attr} default value to {val}')
                    mc.addAttr(f'{obj}.{attr}', edit=True, defaultValue=val)
                    outcome = True
                except:
                    mc.warning(f'failed to set default value for: {obj}.{attr}')
    return outcome

def unlockTRSV(objs):
    # unlock basic attrs and make visible and keyable
    atts = "v tx ty tz rx ry rz sx sy sz translate rotate scale"
    for obj in objs:
        for att in atts.split(" "):
            mc.setAttr('{}.{}'.format(obj, att), k=True, lock=False)

def makeSelectable(obj):
    """
    makes node selectable (unless in layer)
    :param obj: node to operate on
    :return: name of node if it is changed
    """
    if mc.objExists(obj):
        # get shapes and add transform to list
        shapes = mc.listRelatives(obj, children=True) or []
        shapes.append(obj)
        for s in shapes:
            if mc.toggle(s, q=True, template=True):
                print("untemplating: {}".format(s))
                mc.toggle(s, template=True)
            if mc.attributeQuery('overrideDisplayType', node=obj, exists=True):
                if mc.getAttr('{}.overrideDisplayType'.format(s)):
                    print("setting display type override to normal: {}".format(s))
                    mc.setAttr('{}.overrideDisplayType'.format(s), 0)

def make_names_unique(nodes_list):
    # get dup names and sort by length
    dups = check_for_dup_names(nodes_list)
    dups.sort(key=len)
    dups.reverse()
    # use a dict to count name occurances
    name_count = {}
    # list to track pairs of names
    renamed = []

    for dup in dups:
        #print(dup)
        short_name = dup.split('|')[-1]
        if not short_name in name_count:
            # add it's name to name counter
            name_count[short_name] = 1
        else:
            # increase it's count by one
            name_count[short_name] += 1
        # rename to name_#
        # print(f'renaming {dup}')
        new_short = f"{short_name}_{name_count[short_name]}"
        try:
            new = mc.rename(dup, new_short)
            renamed.append((dup, new))
        except Exception as e:
            mc.warning(f"!!! Could not rename {dup}: {e}")
    return renamed

# ---------------------------- CREATE -----------------
def constrain(target, source, type="parent"):
    # constrain target to source
    print(f"{type} constraining {target} to {source}")
    if type == "parent":
        con = mc.parentConstraint(source, target, w=1, mo=False, n=f"cstr_par_{source}")
    elif type == "point":
        con = mc.pointConstraint(source, target, w=1, mo=False, n=f"cstr_pnt_{source}")
    else:
        mc.warning(f"Constraint of {type} not recognized, please use parent or point")
    return con

def ensure_path(path, node_type="transform"):
    """
    Ensures that a given DAG path exists in the Maya scene.
    Creates any missing transforms (or other specified node_type).
    Args:
        path (str): DAG path, e.g. 'first|next|another|last'
        node_type (str): Type of node to create for missing entries (default = "transform").
    Returns:
        str: The full path to the last node.
    """
    parts = path.split('|')
    current = ""
    for part in parts:
        next_path = part if not current else current + "|" + part
        if not mc.objExists(next_path):
            mc.createNode(node_type, name=part, parent=current if current else None)
        current = next_path
    return current


# -----------------------  MISC utilities ---------------
def is_mesh(dagPath):
    # is given object geometry?
    if mc.objectType(dagPath) == 'mesh':
        return True
    # have we got the transform of a mesh?
    for shape in mc.listRelatives(dagPath, children=True, shapes=True, fullPath=True) or []:
        if mc.objectType(shape) == 'mesh':
            return True
    # guess not
    return False

def is_name_unique(obj_name):
    """
    Checks if the object name in Maya is unique.
    :param obj_name: name to check
    :return: True if unique, False otherwise
    """
    all_matches = mc.ls(obj_name)
    return len(all_matches) == 1

def check_for_dup_names(objs=None):
    # returns nodes that ls with a long name
    if not objs:
        objs = mc.ls(dag=True, long=False)
    return [x for x in objs if '|' in x]

def inputPrompt(title='Johny 5 needs input'):
    """
    spawn a window to get some text input from the user
    :param title: give a title for the window
    :return: user input text
    """
    result = mc.promptDialog(
        title=title,
        message='Enter Input:',
        button=['OK', 'Cancel'],
        defaultButton='OK',
        cancelButton='Cancel',
        dismissString='Cancel')
    if result == 'OK':
        text = mc.promptDialog(query=True, text=True)
        return text

def deleteConnection(plug):
    if mc.connectionInfo(plug, isDestination=True):
        plug = mc.connectionInfo(plug, getExactDestination=True)
        readOnly = mc.ls(plug, ro=True)
        #delete -icn doesn't work if destination attr is readOnly 
        if readOnly:
            source = mc.connectionInfo(plug, sourceFromDestination=True)
            mc.disconnectAttr(source, plug)
        else:
            mc.delete(plug, icn=True)
