
# set default value from current (doesn't handle non-floats)
import maya.cmds as cmds
from bw_tools import bw_utils

def run():
    sel = cmds.ls(sl=1)
    print(f"Setting current USER attr values as Default for {len(sel)} selected objs.")
    print("Attributes must be unlocked and keyable to be affected.")
    for s in sel:
    	bw_utils.set_user_attr_defaults(s, keyable=True)
