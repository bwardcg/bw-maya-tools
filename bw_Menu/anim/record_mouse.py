###############################
#
#   RECORD MOUSE
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  
#
###############################

import maya.cmds as mc

def rec_attrs(obj, attrs=None):
    if not attrs:
        attrs = ['translateX', 'translateY', 'translateZ']
    
    print(f"Recording {attrs} on {obj}")
    mc.select(obj)
    mc.recordAttr(at=attrs)
    
    def cleanup():
        """Function to execute when playback stops."""
        print(f"Removing Record Nodes from {obj}")
        for con in mc.listConnections(obj):
            if 'record' in con:
                print(f" - Deleting {con}")
                mc.delete(con)

    # will run cleanup once playingBack stops
    mc.scriptJob(conditionChange=["playingBack", cleanup], runOnce=True)
    mc.play(forward=True, state=True, record=True)

def run():
    sel = mc.ls(sl=True)
    if not sel:
        mc.warning("No object selected!")
        return
    obj = sel[0]
    rec_attrs(obj)
