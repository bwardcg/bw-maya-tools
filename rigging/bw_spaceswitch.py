# create spaceswitch
attr_name = 'local_world'
chr_part = 'l_arm'
chr_ctrl = f'chr_l_wrist_ik_anim.{attr_name}'

# select World_loc, Local_loc, spsw_grp
sel = cmds.ls(sl=1)
spsw_world = sel[0]
spsw_local = sel[1]
spsw_xform = sel[2]

# create constraint
spsw_constr = cmds.parentConstraint(spsw_world,spsw_local,spsw_xform, w=1, mo=False, n=f"spsw_{chr_part}_parConstr")[0]

# input names
spsw_input_world = f'{spsw_world}W0'
spsw_input_local = f'{spsw_local}W1'

# direct connect to world
cmds.connectAttr(chr_ctrl, f'{spsw_constr}.{spsw_input_world}', force=True)

# inverse connect to local
spsw_reverse = cmds.shadingNode('reverse', asUtility=True, name=f'spsw_{chr_part}_reverse')
cmds.connectAttr(chr_ctrl, f'{spsw_reverse}.inputX', f=True)
cmds.connectAttr(f'{spsw_reverse}.outputX', f'{spsw_constr}.{spsw_input_local}', f=True)