import maya.cmds as cmds
import maya.api.OpenMaya as om

def get_mesh_fn(mesh_name):
    sel = om.MSelectionList()
    sel.add(mesh_name)
    dagPath = sel.getDagPath(0)
    return om.MFnMesh(dagPath), dagPath

def get_face_center(mesh_fn, face_id):
    face_verts = mesh_fn.getPolygonVertices(face_id)
    points = [om.MVector(mesh_fn.getPoint(v, om.MSpace.kWorld)) for v in face_verts]
    center = sum(points, om.MVector()) / len(points)
    return om.MPoint(center)

def get_closest_uv(mesh_fn, point):
    mpoint = om.MPoint(point)
    closest_point = mesh_fn.getClosestPoint(mpoint, om.MSpace.kWorld)[0]
    uv = mesh_fn.getUVAtPoint(closest_point, om.MSpace.kWorld)
    return uv

def create_follicle(mesh_shape, mesh_transform, u, v, index):
    follicle_shape = cmds.createNode('follicle', name=f"{mesh_transform}_follicle{index}_Shape")
    follicle_transform = cmds.listRelatives(follicle_shape, parent=True)[0]

    # Connect mesh to follicle
    cmds.connectAttr(f"{mesh_shape}.outMesh", f"{follicle_shape}.inputMesh", force=True)
    cmds.connectAttr(f"{mesh_shape}.worldMatrix[0]", f"{follicle_shape}.inputWorldMatrix", force=True)
    cmds.connectAttr(f"{follicle_shape}.outTranslate", f"{follicle_transform}.translate")
    cmds.connectAttr(f"{follicle_shape}.outRotate", f"{follicle_transform}.rotate")

    # Set UV values
    cmds.setAttr(f"{follicle_shape}.parameterU", u)
    cmds.setAttr(f"{follicle_shape}.parameterV", v)

    return follicle_transform

def attach_follicle_to_face(face):
    mesh_name = face.split('.f')[0]
    if not cmds.objExists(mesh_name):
        cmds.error(f"Mesh '{mesh_name}' does not exist.")
        
    mesh_fn, dag_path = get_mesh_fn(mesh_name)
    mesh_shape = cmds.listRelatives(mesh_name, shapes=True, fullPath=True)[0]
    
    face_num = int(face.split('.f')[-1][1:-1])
    center = get_face_center(mesh_fn, face_num)
    try:
        uv = get_closest_uv(mesh_fn, center)
        create_follicle(mesh_shape, mesh_name, uv[0], uv[1], face_num)
    except RuntimeError:
        cmds.warning(f"Could not place follicle on {face} (UV issue). Skipping.")

def run():
    for sel in cmds.ls(selection=True, flatten=True) or []:
        if len(sel.split('.vtx')) > 1:
            cmds.warning(f"Please select FACES on target object")
        else:
            print(f'attaching follicle to {sel}')
            attach_follicle_to_face(sel)
