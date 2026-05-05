# make fk ctrl
# optional: first make an empty group with ctrl name, parent it, select it
pre = 'chr'
suf = 'anim'

node = None
parent_node = None

lock = ['scaleX', 'scaleY', 'scaleZ']

# get node and name
sel = cmds.ls(sl=1)
if sel:
    node = sel[0]
    # parent_node = cmds.listRelatives(node, p=1)
    name = node
else:
    name = 'Control'
    
if not node:
    node = cmds.group(empty=True, name=name)
wld = cmds.rename(node, f'{pre}_{name}_{suf}_grp_world')
    
# make control
ctrl = cmds.circle(name=f'{pre}_{name}_{suf}', degree=1, sections=6)

# parent ctrl
lcl = cmds.group(name=f'{pre}_{name}_{suf}_grp_lcl')
cmds.parent(lcl, wld)
cmds.setAttr(f'{lcl}.translate', 0,0,0)
cmds.setAttr(f'{lcl}.rotate', 0,0,0)
for a in lock:
    cmds.setAttr(f'{ctrl}.{a}', lock=True, keyable=False, channelBox=False)

