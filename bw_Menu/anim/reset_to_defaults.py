###
# Reset_To_Default_Value.py
# this tool will reset the selected control's attributes to their default values
# Written by Delano Athias / modified by Brian Ward
###

from maya import cmds


skipAttrList = [""]


def reset(objs):
    
    for node in cmds.ls(objs,  type='transform'):
        attrList = cmds.listAttr(
                    node, 
                    keyable=True, 
                    unlocked=True, 
                    multi=True
                    )
        # remove protected attributes that we want to skip ----
        for skipAttr in skipAttrList:
            if skipAttr in attrList:
                attrList.remove(skipAttr)
            
        for attr in attrList:
            attrType = cmds.attributeQuery(attr,node=node,attributeType=True)
            defaultValues = cmds.attributeQuery(attr, n=node, listDefault=True)
            if defaultValues:
                if attrType == "double3":
                    attr_full_name = f"{node}.{attr}"
                    can_be_set = True
                    compNum = 0
                    for comp in ['X', 'Y', 'Z']:
                        component_attr = f"{attr_full_name}{comp}"
                        is_locked = cmds.getAttr(component_attr, lock=True)
                        connections = cmds.listConnections(component_attr, source=True, destination=False)
                        if not is_locked and not connections:
                            cmds.setAttr(component_attr, defaultValues[compNum])
                        compNum = compNum + 1
                else:
                    for value in defaultValues:
                        try:
                            cmds.setAttr(node + '.' + attr, value)
                        except:
                            cmds.warning(f'Failed to set attr: {attr} on: {node}')


def run():
    sel = cmds.ls(sl=True)
    reset(sel)