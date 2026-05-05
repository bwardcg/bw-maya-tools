# prep character for publish script
import maya.cmds as cmds

mdl_grps = cmds.listRelatives('master|mdl', children=True)
all_ctrls_set = 'ALL_CONTROLS'
mdl_pre = 'geo_'
jnt_pre = 'jnts_'
ctrl_pre = 'ctrls_'
var_suf = '_grp'
temp_blinks = 'TEMP_BLINKS'


def run_UI():
    variants = get_variants()
    if not variants:
        cmds.warning(f'Nothing in "master|mdl" matches {mdl_pre}*{var_suf} !!!')

    cleanup_UI(variants)
    

def cleanup_UI(options, title="Rigging Cleanup", message="Select current variant:"):
    '''
    # get current variant from list and launch clean up script
    # cleanup_UI(variants)
    '''
    if cmds.window("chooseOptionWin", exists=True):
        cmds.deleteUI("chooseOptionWin", window=True)

    window = cmds.window("chooseOptionWin", title=title, widthHeight=(300, 100))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center")

    cmds.text(label=message)
    option_menu = cmds.optionMenu("optionMenu", width=280)
    for opt in options:
        cmds.menuItem(label=opt)
    
    cur_var = None
    
    def on_clean(*args):
        nonlocal cur_var  # bring variable into function scope
        cur_var = cmds.optionMenu(option_menu, query=True, value=True)
        print("User selected:", cur_var)
        cleanup(cur_var)
    
    def on_dup(*args):
        # select (or fix) duplicate names
        check_for_dup_names()
        
    def on_cancel(*args):
        print("User canceled the dialog.")
        cmds.deleteUI(window)
        
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 100, 80), 
                    columnAlign3=("center","center", "center"))
    cmds.button(label="Clean Up", command=on_clean)
    cmds.button(label="Fix Dup Names", command=on_dup)
    cmds.button(label="Cancel", command=on_cancel)
    cmds.setParent('..')

    cmds.showWindow(window)    


# ----------------- clean_up script
def cleanup(cur_var):
    
    # check all ctrls in ALL_CONTROLS
    print('checking:  All ctrl names in Sel Sets')
    ctrls_set = in_ctrls_sets()
    for ctrl in cmds.ls(f'chr_*_anim'):
        if not ctrl in ctrls_set:
            print(f'{ctrl} not found in {all_ctrls_set}, ADDING now')
            cmds.sets(ctrl, add=all_ctrls_set)

    # check inherit transforms
    
    # check and set defaults
    
    # lock channels on 
    #    connect, spaceswitch, etc, leave one unlocked
    #    un-needed attrs, everything in rig?
    
    # select items for deletion (not blink shapes)
    print('checking:  Selecting items not needed for variant install')
    del_list = items_to_delete(cur_var)
    for sublist in del_list:
        cmds.select(sublist, add=True)
    

def get_variants():
    ''' returns a list of variants '''
    variants = []
    for mod in mdl_grps:
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
    
    # Get skinning meshes (group or meshes)
    for mod in mdl_grps:
        if 'SKINNING' in mod:
            skinning.append(mod)
    
    # if temp blinks are hidden
    if temp_blinks in mdl_grps:
        if cmds.getAttr(f'{temp_blinks}.v') == False:
            blinks = temp_blinks
    
    # non-current variants
    for var in get_variants():
        if var != cur_var:
            # select all grps
            for pre in [jnt_pre, ctrl_pre, mdl_pre]:
                grp = f'{pre}{var}{var_suf}'
                if cmds.objExists(grp):
                    var_grps.append(grp)
                else:
                    cmds.warning(f'{grp} NOT FOUND!')
    
    return [skinning,blinks,var_grps]


def in_ctrls_sets():
    sel = cmds.ls(sl=1)
    cmds.select(all_ctrls_set)
    all_ctrls = cmds.ls(sl=1)
    cmds.select(sel)
    return all_ctrls    


def check_for_dup_names(ctrls_first=True, prompt=True):
    dup_names = cmds.ls([x for x in cmds.ls(dag=True) if '|' in x])
    
    if dup_names:
        cmds.warning(f'{len(dup_names)} non-unique names found!!')
        
        # check if any are in Sel Sets
        if ctrls_first:
            all_ctrls = in_ctrls_sets()
            
            # look for ctrls in dup names
            dup_ctrls = []
            for dup in dup_names:
                if dup.split('|')[-1] in all_ctrls:
                    dup_ctrls.append(dup)
            
            # sort anything in sel set to front of list
            for item in dup_ctrls:
                dup_names.remove(item)
                dup_names.insert(0, item)
                print(f'ctrl: {item} will not be renamed')
            
        if prompt:
            # Prompt user for confirmation
            result = cmds.confirmDialog(
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
                cmds.select(dup_names)
        else:
            # no prompt needed
            new_names = make_names_unique(dup_names)
    else:
        print(f'Congratulations!!  All names in this scene are unique')


def make_names_unique(nodes_list):
    all_nodes = cmds.ls(nodes_list, dag=True, long=False)
    name_map = {}
    renamed = []

    for full_path in all_nodes:
        short_name = full_path.split('|')[-1]

        if short_name in name_map:
            name_map[short_name] += 1
            new_short = f"{short_name}_{name_map[short_name]}"
            try:
                new_full = cmds.rename(full_path, new_short)
                renamed.append((full_path, new_full))
            except Exception as e:
                cmds.warning(f"Could not rename {full_path}: {e}")
        else:
            name_map[short_name] = 1

    cmds.inViewMessage(amg=f'Renamed {len(renamed)} duplicate node(s).', pos='topCenter', fade=True)

    return renamed
