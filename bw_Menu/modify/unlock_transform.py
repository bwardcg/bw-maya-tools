###############################
#
#   Unlock all channels on selected transforms
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_utils
#
###############################

# prep character for publish script
import maya.cmds as mc
from bw_tools import bw_utils

def run():
    sel = mc.ls(sl=1)
    bw_utils.unlockTRSV(sel)
