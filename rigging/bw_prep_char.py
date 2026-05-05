###############################
#
#   Prep Tools for Rigging and/or Publishing
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_utils, bw_rigUtils, reset_to_defaults
#
###############################

import maya.cmds as mc
from bw_tools.bw_Menu.anim import reset_to_defaults
from bw_tools.rigging import bw_rigUtils
from bw_tools import bw_utils

mdl = 'master|mdl'
all_ctrls_set = 'ALL_CONTROLS'
mdl_pre = 'geo_'
jnt_pre = 'jnts_'
ctrl_pre = 'ctrls_'
var_suf = '_grp'

def cleanup_UI(options, title="Rigging Cleanup", message="Select current variant:"):
    '''
    # get current variant from list and launch clean up script
    # cleanup_UI(variants)
    '''
    if mc.window("chooseOptionWin", exists=True):
        mc.deleteUI("chooseOptionWin", window=True)

    window = mc.window("chooseOptionWin", title=title, widthHeight=(280, 100))
    mc.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center")

    mc.text(label=message)
    option_menu = mc.optionMenu("optionMenu", width=150)
    for opt in options:
        mc.menuItem(label=opt)
    
    cur_var = None
    
    def on_clean(*args):
        nonlocal cur_var  # bring variable into function scope
        cur_var = mc.optionMenu(option_menu, query=True, value=True)
        print("---------------------------")
        print("Current Variant:", cur_var)
        cleanup(cur_var, mdl)
    
    def on_dup(*args):
        # select (or fix) duplicate names
        check_for_dup_names()
        
    def on_cancel(*args):
        print("User canceled the dialog.")
        mc.deleteUI(window)
        
    mc.rowLayout(numberOfColumns=3, columnWidth3=(80, 120, 80), 
                    columnAlign3=("center","center", "center"))
    mc.button(label="Clean Up", command=on_clean)
    mc.button(label="Fix Dup Names", command=on_dup)
    mc.button(label="Cancel", command=on_cancel)
    mc.setParent('..')

    mc.showWindow(window)    


# ----------------- clean_up script
def cleanup(cur_var, mdl):

    setup_autofocus()

    # check all ctrls in ALL_CONTROLS
    print('\nchecking:  Selection Sets')
    ctrls_set = in_ctrls_sets()
    for ctrl in mc.ls(f'chr_*_anim'):
        if not ctrl in ctrls_set:
            print(f'{ctrl} not found in {all_ctrls_set}, ADDING now')
            mc.sets(ctrl, add=all_ctrls_set)
    print('---- All ctrl names in Sel Sets')

    # check inherit transforms
    print('\nchecking:  Inherit transforms')
    if mc.objExists(mdl):
        mc.setAttr(f'{mdl}.inheritsTransform', 0)
        print(f'---- {mdl}.inheritsTransform turned OFF')
    else:
        mc.warning(f'!!!! {mdl} NOT FOUND !!!!')
    
    # delete all animation
    pairblends = []
    print('\nfinding all animation in file')
    for anim in bw_rigUtils.get_anim_curves(sdk=False, pairblend=True):
        connected_nodes = mc.listConnections(anim, source=True, destination=True) or []
        if any(mc.nodeType(node) == 'pairBlend' for node in connected_nodes):
            pairblends.append(anim)
        else:
            # delete the animation curve
            try:
                print(f'Deleting Anim Curve: {anim}')
                mc.delete(anim)
            except:
                mc.warning(f'could not delete {anim} Perhaps a locked node?')
    print(f'Suspected Pairblended anim skipped: {pairblends}')

    # check and set defaults
    sel = mc.ls(sl=True)
    print('\nchecking: ctrls to default')
    all_ctrls = in_ctrls_sets()
    mc.select(all_ctrls)
    reset_to_defaults.run()
    # restore selection
    if sel:
        mc.select(sel)
    else:
        mc.select(clear=True)

    # specific settings...
    try:
        mc.setAttr('master.skeleton', 0)
        mc.setAttr('master.editGeometry', 0)
    except:
        mc.warning('master obj missing attributes')

    if mc.objExists('chr_head_anim'):
        mc.setAttr('chr_head_anim.visAuxCtl', 0)

    print('---- All ctrls set to Defaults')

    # check mesh Arnold Attrs
    print('\nchecking:  Arnold attributes')
    turned_off = []
    for mesh in mc.ls(type='mesh'):

        if not mc.getAttr(f'{mesh}.castsShadows'):
            if not mc.getAttr(f'{mesh}.castsShadows', lock=True):
                print(f' --- Turning RENDER SHADOWS ON for: {mesh}')
                mc.getAttr(f'{mesh}.castsShadows')
            else:
                mc.warning(f'\n!!! RENDER SHADOWS is OFF and LOCKED on: {mesh} ')

        if not mc.getAttr(f'{mesh}.primaryVisibility'):
            if not mc.getAttr(f'{mesh}.primaryVisibility', lock=True):
                print(f' --- Turning RENDER VISIBILITY ON for: {mesh}')
                mc.getAttr(f'{mesh}.primaryVisibility')
            else:
                mc.warning(f'\n!!! RENDER VISIBILITY is OFF and LOCKED on: {mesh} ')
    
    # lock channels on 
    #    connect, spaceswitch, etc, leave one unlocked
    #    un-needed attrs, anything in rig that's not a ctrl?
    
    # select items for deletion (not blink shapes, they need to be geo)
    print('checking:  Items for Deletion')
    del_list = items_to_delete(cur_var)
    for sublist in del_list:
        mc.select(sublist, add=True)
    print('---- Selected items not needed for variant install')

def setup_autofocus():
    # left eye GEO needs a child named ccwFocusObj
    pass

def get_variants(grps):
    ''' returns a list of variants '''
    variants = []
    for mod in grps:
        if mod[:4]==mdl_pre and mod[-4:]==var_suf:
            var = mod.replace(mdl_pre,'').replace(var_suf,'')
            variants.append(var)
    return variants

def items_to_delete(cur_var):
    '''
    returns a list of lists of potentialy deletable items
    '''
    skinning = []
    blinks = None
    var_grps = []
    
    mdl_grps = mc.listRelatives(mdl, children=True) or []

    # Get skinning meshes (group or meshes)
    for mod in mdl_grps:
        if 'SKINNING' in mod:
            skinning.append(mod)
    
    # everything outside 'master'
    root = []
    keep = ['master', 'front', 'left', 'persp', 'side', 'top']
    for item in mc.ls('|*'): 
        if item not in keep:
            root.append(item)
    
    # non-current variants
    for var in get_variants(mdl_grps):
        if var != cur_var:
            # select all grps
            for pre in [jnt_pre, ctrl_pre, mdl_pre]:
                grp = f'{pre}{var}{var_suf}'
                if mc.objExists(grp):
                    var_grps.append(grp)
                else:
                    mc.warning(f'{grp} NOT FOUND!')
    
    return [skinning, root, var_grps]

def in_ctrls_sets():
    if mc.objExists(all_ctrls_set):
        sel = mc.ls(sl=1)
        mc.select(all_ctrls_set)
        all_ctrls = mc.ls(sl=1)
        mc.select(sel)
        return all_ctrls
    else:
        mc.warning(f'!!!! {all_ctrls_set} NOT FOUND !!!!')

def check_for_dup_names(prompt=True):
    dup_names = mc.ls([x for x in mc.ls(dag=True) if '|' in x])
    
    if dup_names:            
        if prompt:
            # Prompt user for confirmation
            result = mc.confirmDialog(
            title='Rename Nodes',
            message=f'Do you want to rename {len(dup_names)} duplicate node names to make them unique?',
            button=['Yes', 'No'],
            defaultButton='Yes',
            cancelButton='No',
            dismissString='No'
            )
            
            if result == 'Yes':
                print('great! here we go')
                new_names = make_names_unique(dup_names)    
            else:
                mc.select(dup_names)
        else:
            # no prompt needed
            new_names = make_names_unique(dup_names)
    else:
        mc.inViewMessage(f'Congratulations!!  All names in this scene are unique')
