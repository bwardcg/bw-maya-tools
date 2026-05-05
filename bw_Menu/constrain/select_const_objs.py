
import maya.cmds as mc
from bw_tools import bw_utils


def run():
    '''
    changes selection to objects selected objs are constrained by
    '''
    select_list = []
    tgts_list = []
    print('-- checking sel objs for constraints')
    for obj in cmds.ls(sl=True, type='transform'):
        tgts_list = bw_utils.get_constraining_objs(obj)
        print(f'found constraints: {tgts_list}')
        select_list += tgts_list
    if select_list:
        print('-- selecting constraints')
        cmds.select(select_list, replace=True)
