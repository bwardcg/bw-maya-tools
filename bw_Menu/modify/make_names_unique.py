###############################
#
#   Rename all non-unique DAG nodes
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
    all_nodes = mc.ls(sl=1)
    renamed = bw_utils.make_names_unique(all_nodes)

    mc.inViewMessage(amg=f'Renamed {len(renamed)} duplicate node(s).', pos='topCenter', fade=True)
    return renamed
