###############################
#
#   Prep Char Geo for Rigging and/or Publishing
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_prep_char
#
###############################

# prep character for publish script
import maya.cmds as mc
from bw_tools import bw_utils
from bw_tools.rigging import bw_prep_char

# get naming from bw_prep_char
mdl = bw_prep_char.mdl
mdl_pre = bw_prep_char.mdl_pre
var_suf = bw_prep_char.var_suf

def run():
    # check for geo and variants in scene:
    if not mc.objExists(mdl):
        mc.warning(f'No {mdl} found !!!  You need a character in your scene')
        bw_utils.ensure_path(mdl)

    mdl_grps = mc.listRelatives(mdl, children=True) or []
    variants = bw_prep_char.get_variants(mdl_grps)

    if not variants:
        mc.warning(f'Nothing in "master|mdl" matches {mdl_pre}*{var_suf} !!!')
    bw_prep_char.cleanup_UI(variants)
