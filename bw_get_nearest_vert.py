###############################
#
#   BW_GET_NEAREST_VERT
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  
#
##############################

# returns an integer for the vertex ID it found
# example usage:
# get_closest_vertex('source_obj','target_obj', 592)

import maya.api.OpenMaya as om

def get_closest_vertex(source_mesh, target_mesh, source_vertex_index):
    """Find the closest vertex on target_mesh to the given vertex on source_mesh (world space)."""
    source_pos = om.MVector(*get_world_position(source_mesh, int(source_vertex_index)))
    target_positions = get_all_world_positions(target_mesh)

    min_dist = float('inf')
    closest_index = -1

    for i, pos in enumerate(target_positions):
        pos_vec = om.MVector(*pos)
        dist = (pos_vec - source_pos).length()
        if dist < min_dist:
            min_dist = dist
            closest_index = i

    return closest_index

def get_world_position(mesh, index):
    """Returns world space position of a single vertex as a list [x, y, z]."""
    sel_list = om.MSelectionList()
    sel_list.add(mesh)
    dag_path = sel_list.getDagPath(0)
    mfn_mesh = om.MFnMesh(dag_path)
    point = mfn_mesh.getPoint(index, om.MSpace.kWorld)
    return [point.x, point.y, point.z]

def get_all_world_positions(mesh):
    """Returns world space positions for all vertices on a mesh as a list of [x, y, z] lists."""
    sel_list = om.MSelectionList()
    sel_list.add(mesh)
    dag_path = sel_list.getDagPath(0)
    mfn_mesh = om.MFnMesh(dag_path)
    points = mfn_mesh.getPoints(om.MSpace.kWorld)
    return [[p.x, p.y, p.z] for p in points]
