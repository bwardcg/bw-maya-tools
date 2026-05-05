###############################
#
#   SNAP B to A
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_snap
#
###############################

from bw_tools.bw_snap import Snap

def run():
    snap_obj = Snap()
    
    # get all transforms from selection
    xforms = snap_obj.getXforms()
    
    # use LAST xform as source
    source  = xforms[-1]
    targets = xforms[:-1]

    print(f'Snapping selected to {source}')
    snap_obj.snapObjs(source, targets)
