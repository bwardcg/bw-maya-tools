###############################
#
#   Zero Pivot values on selected transforms
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_utils
#
###############################

import maya.cmds as mc
from bw_tools.rigging import bw_rigUtils

def run():
    for s in mc.ls(sl=1, type='transform'):
        if bw_rigUtils.cleanPivot(s):
            print(f'cleaned pivots on :{s}')
