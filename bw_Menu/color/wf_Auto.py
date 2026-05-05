###############################
#
#   Wireframe Color Over-ride
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_rigUtils
#
###############################

import maya.cmds as mc
from bw_tools.rigging import bw_rigUtils

def run():
    sl = mc.ls(sl=1)
    bw_rigUtils.colorByName(sl)
