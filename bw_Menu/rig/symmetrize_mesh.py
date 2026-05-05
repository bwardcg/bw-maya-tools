###############################
#
#   Attempts to produce a symmetrical version of a mesh, given 3 selected+connected verts
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_get_nearest_vert
#
###############################


import maya.cmds as mc
from bw_tools import bw_get_nearest_vert as nearest


def run(axis="X", clean=True):
    '''
    select 3 vertexes that are already symmetrical 
    and share edges 1st to 2nd, 2nd to 3rd
    
    script will make copies and blendshape them together
    blend set to .5 /should be/ in perfect symmetry

    TODO: determine a symetrical face on one side
          make my own selection of 3 connected verts
    '''
    
    sel = mc.ls(selection=True, flatten=True)
    if not test_selection(sel):
        return False
    
    orig_obj = sel[0].split('.')[0]
    indexes = []
    for s in sel:
        i = s.split('.')[1][4:-1]
        indexes.append(i)
    
    # duplicate the input mesh and don't touch it again
    copy_obj = mc.duplicate(orig_obj, name=orig_obj + "_copy")[0]
    
    # Duplicate and mirror the mesh
    mirror_obj = mc.duplicate(copy_obj, name=orig_obj + "_mirrored")[0]
    mirror_xform(mirror_obj)
    
    # Find the 3 closest verts to selection on mirrored obj
    src, trg = find_nearest_verts(copy_obj, mirror_obj, indexes)
    
    # Remap vertices from original to mirrored (preserve vertex order)
    mc.meshRemap( 
        src[0], src[1], src[2],
        trg[0], trg[1], trg[2]
        )
    
    # Create blendShape between original and mirrored mesh
    blend = mc.blendShape(mirror_obj, copy_obj, name="symBlendShape")[0]
    mc.setAttr(blend + "." + mirror_obj, 0.5)
    
    # Duplicate result of the blend to get a baked symmetrical mesh
    final_output = mc.duplicate(copy_obj, name=copy_obj + "_symFinal")[0]
    
    if clean:
        # Clean up intermediate meshes
        mc.delete(mirror_obj, copy_obj)
        mc.delete(blend)
    else:
        mc.setAttr(f'{copy_obj}.v', 0)
        mc.setAttr(f'{mirror_obj}.v', 0)
    
    print(f"Symmetry blend mesh created: {final_output}")


def test_selection(sel):
    verts = [v for v in sel if '.vtx[' in v]
    if len(verts) == 3:
        print("Exactly 3 vertices are selected.")
        return True
    else:
        print(f"Selection contains {len(verts)} vertices. Select exactly 3.")
        return False


def mirror_xform(obj, axis="X"):
    # scale one axis
    mc.setAttr(f"{obj}.scale{axis}", -1)
    # freeze xforms
    mc.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0)
    # reverse normals
    mc.polyNormal(obj, normalMode=0, userNormalMode=False, ch=False)


def find_nearest_verts(src, trg, indexes):
    '''
    builds lists of source and target vertices
    based on closest vert on target to source
    
    src:  source object with the verts we already have
    trg:  target object to find nearest vert on
    indexes:  list of integers for the verts we're using
    '''
    src_list = []
    trg_list = []    
    for i in indexes:
        s = f'{src}.vtx[{i}]'
        src_list.append(s)
        print(f' -- searching for nearest vert to {s} on {trg}')
        n = nearest.get_closest_vertex(src, trg, i)
        t = f'{trg}.vtx[{n}]'
        print(f' -- -- nearest point found: {t}')
        trg_list.append(t)
    
    return src_list, trg_list
