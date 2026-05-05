"""
Brian Ward's helper functions
not studio supported!!
"""

import os, json, pprint, re
import maya.cmds as cmds
from random import random as rand
from bw_tools.rigging import bw_rigUtils
from bw_tools import bw_utils


BASE = "D:/Maya/skin_weights/"
JSON_FILE = 'BindingData.json'
ASSET_TAG = "master.pTag_AssetName"
FORMAT = 'xml'
JOINTS_PATTERN = "chr_*_skin"


def bind_geo(mesh, joints=[], mi=5, mmi=False):
    '''
    smooth binds a mesh
    mesh:    geometry to smooth bind (required)
    joints:  takes list of joints to bind to.
             defaults to sw_skinning.JOINTS_PATTERN ("chr_*_skin")
    '''
    if not joints:
        # default to all '_skin' joints
        joints = cmds.ls(JOINTS_PATTERN, type='joint')
    if bw_utils.is_mesh(mesh):
        # look for skin
        sc_old = bw_rigUtils.getSkinCluster(mesh)
        if not sc_old:
            sc = cmds.skinCluster(joints, mesh, toSelectedBones=True, 
                        bindMethod=0, normalizeWeights=1, dr=4,
                        maximumInfluences=mi, omi=mmi,
                        weightDistribution=0, rui=False)
            if sc:
                # name skin cluster
                sc = cmds.rename(sc, f'sc_{mesh}')
                
                # return skin cluster
                return sc
            else:
                cmds.warning(f'Failed to create skin cluster for {mesh}')
                return None
        else:
            cmds.warning(f'{mesh} already has skin cluster: {sc_old}')
            return sc_old
    else:
        print(f'{mesh} does not appear to be geometry, SKIPPING')
        return None


def bind_selected_geo(max_inf=5, maintain=False, joints=None, all_joints=False):
    '''
    smooth binds all selected meshes
    
    joints:  takes list of joints to bind to.
             all_joints will use all joints named "chr_*_skin"
             defaults to selected joints
    '''
    if not joints:
        if not all_joints:
            # bind to all selected joints
            joints = cmds.ls(sl=1, type='joint')
        else:
            # bind to all 'skin' joints
            joints = cmds.ls(JOINTS_PATTERN, type='joint')

    print(f'Binding to {len(joints)} joints')

    for mesh in cmds.ls(sl=1):
        if bw_utils.is_mesh(mesh):
            print(f'Binding {mesh}')
            sc = bind_geo(mesh, joints, mi=max_inf, mmi=maintain)
            if sc:
                print(f'{mesh} bound with new skincluster: {sc}')
            else:
                # print(f'!!!{mesh}: BIND FAILED')
                sc = bw_rigUtils.getSkinCluster(mesh)
                if sc:
                    print(f'!!!{mesh} is already skinned: {sc}')


def duplicate_skin_cluster(source_mesh=None, target_mesh=None):
    """
    duplicates skin cluster from first selected mesh to second selected mesh
    """
    
    if not source_mesh and not target_mesh:
        # use selected objects
        selection = cmds.ls(selection=True)
        if len(selection) != 2:
            cmds.error("Please select the source mesh first, then the target mesh.")
            return
        source_mesh, target_mesh = selection

    # Find the skinCluster of the source mesh
    source_skin_cluster = bw_rigUtils.getSkinCluster(source_mesh)

    # Get influences (joints) of the source skinCluster
    influences = cmds.skinCluster(source_skin_cluster, query=True, influence=True)

    # Bind the target mesh to the same influences
    target_skin_cluster = bind_geo(target_mesh, influences)

    # Copy skin weights from source to target
    cmds.copySkinWeights(ss=source_skin_cluster, ds=target_skin_cluster, noMirror=True, 
                         surfaceAssociation="closestPoint", influenceAssociation="closestJoint")
    
    print(f"SkinCluster duplicated from {source_mesh} to {target_mesh} successfully.")
    return target_skin_cluster


def unbind(char=None, path=None, geo=[]):  
    '''
    exports deformer weights and dictionary of influences for rebinding
    '''
    inf_dic = bind_data()

    if not geo:  # use all the geo in the data file
        geo = list(inf_dic.keys())

    # export ALL weights 
    
    path = export_skin_weights(char, path=path)
        
    # unbind geo
    for g in geo:
        sc = bw_rigUtils.getSkinCluster(g)
        if sc:
            # un-deform mesh before deleting
            cmds.setAttr(f'{sc}.envelope', 0)
            cmds.delete(sc)
    
    # delete Bind Poses
    cmds.delete(cmds.ls(type='dagPose'))
    
    # return stored influences
    return path


def rebind(char=None, path=None, inf_dic=None, selected=False):

    if not char:
        char = get_char()
    
    if not inf_dic:
        # attempt to read exported json
        if not path:
            path = get_dir(char, latest=True)
        jsonfile = os.path.join(path,JSON_FILE)
        print(f'reading Bind Data from disk: {jsonfile}')
        data = read_json(jsonfile)
    else:
        data = inf_dic
    
    if selected:
        sel = cmds.ls(sl=1)

    if data:
        # bind geo from dictionary
        for mesh in data:
            if selected:
                if not mesh in sel:
                    continue
            if cmds.objExists(mesh):
                if bw_rigUtils.getSkinCluster(mesh):
                    print(f'skin cluster already bound: {mesh}')
                else:
                    joints_data = data.get(mesh)
                    # check that all joints exist
                    joints = []
                    for jnt in joints_data:
                        all_matches = cmds.ls(jnt)
                        if len(all_matches) == 0:
                            print(f'object not found: {jnt}, skipping.')
                        elif len(all_matches) > 1:
                            print(f'more than one object found named {jnt}, skipping.')
                        else:
                            joints.append(jnt)
                    
                    print(f'rebinding: {mesh} to {joints}')
                    bind_geo(mesh, joints)
        
        # import weights
        geo = list(data.keys())
        if selected:
            geo = sel
        print(f'importing weights for: {geo}')
        import_skin_weights(char, meshes=geo)
    else:
        cmds.warning('!!! requires a dict of binding data')
        return None
    return True


class SkinByMaterial():
    def make_jnt_mtls():
        # create material per joint
        for jnt in cmds.ls(sl=1, type='joint'):
            # make new lambert
            shd = cmds.shadingNode('lambert', name='MTL_{}'.format(jnt), asShader=True)
            shdSG = cmds.sets(name='{}SG'.format(shd), empty=True, renderable=True, noSurfaceShader=True)
            cmds.connectAttr('{}.outColor'.format(shd), '{}.surfaceShader'.format(shdSG))
            # apply random color
            cmds.setAttr( "{}.color".format(shd), rand(), rand(), rand(), type='double3')
            # todo not assigning to anything yet
            #cmds.sets(node, e=True, forceElement=shdSG)

    def assign_mtl_weights(print_output=False):
        # assign weights to selected verts by material

        comp_sel = cmds.ls(sl=1, flatten=True)
        obj = comp_sel[0].split(':')[-1].split('.')[0]
        skin, shape = bw_util.get_skin(obj)
        shadGrps = cmds.listConnections(shape, type='shadingEngine')
        no_materials = []

        for vrt in comp_sel:
            # get shading groups surrounding vrt
            materials = set()
            faces = cmds.polyListComponentConversion(vrt, toFace=True)
            for face in cmds.ls(faces, flatten=True):
                for SG in shadGrps:
                    if cmds.sets(face, isMember=SG):
                        materials.add(SG)
            if materials:
                # build list of joint weights
                list = []
                count = len(materials)
                if print_output:
                    print("found materials: {}".format(materials))
                if count:
                    pcnt = 1.0/count
                    for mtl in materials:
                        jnt = mtl[4:-2]
                        if jnt in cmds.skinCluster(skin, query=True, inf=True):
                            item = (jnt, pcnt)
                            list.append(item)
                # set weights
                if list:
                    cmds.skinPercent(skin, vrt, transformValue=list, zeroRemainingInfluences=True)
                else:
                    print("could not find material weights for {}".format(vrt))

            else:
                no_materials.append(vrt)
        cmds.select(no_materials)
        if print_output:
            print_vtx_weights(skin, comp_sel)

    def print_vtx_weights(skin, verts):
        print('weights for verts: {}'.format(verts))
        print('ass assigned to: {}'.format(skin))
        for vrt in verts:
            print(cmds.skinPercent(skin, vrt, query=True, value=True, ignoreBelow=0.05 ))
            print(cmds.skinPercent(skin, vrt, transform=None, query=True, ignoreBelow=0.05 ))


def normalizeWeights(obj):
    if bw_utils.is_mesh(obj):
        sc = bw_rigUtils.getSkinCluster(obj)
        if sc:
            print(f'normalizing weights on: {obj}')
            cmds.skinPercent(sc, obj, normalize=True)


#----------------------------- Skinweights IO

def bind_data(skn_clstrs=[]):
    if not skn_clstrs:
        # record influences list for all skin clusters in dictionary
        skn_clstrs = cmds.ls(type="skinCluster")
    inf_dic = {}
    for sc in skn_clstrs:
        influences = cmds.skinCluster(sc, query=True, influence=True)
        mesh = cmds.skinCluster(sc, query=True, geometry=True)[0]
        if bw_utils.is_mesh(mesh):
            xfrm = cmds.listRelatives(mesh, parent=True)[0]
            inf_dic[xfrm] = influences
    return inf_dic


def export_skin_weights(char=None, meshes=None, path=None, v=True):
    '''
    meshes: List of geometry that have a skinCluster as a deformer
    v: (verbosity) Extra output on what's going on
    ----------------
    exports .xml for given list of skin clusters
    if no list is given will write for ALL skin_clusters in scene
    '''
        
    if meshes:
        skin_clusters = []
        for m in meshes:
            s = bw_rigUtils.getSkinCluster(m)
            skin_clusters.append(s)
    else:
        # List all skinCluster nodes in the scene
        all_skin_clusters = cmds.ls(type="skinCluster")

        # remove skn_clstrs in a namespace
        skin_clusters = [s for s in all_skin_clusters if ":" not in s]

    
    print(f'\nEXPORTING {len(skin_clusters)} SkinClusters')
    
    if not char:
        char = get_char()
    
    if not path:
        path = get_dir(char, ver_up=True)
    elif not os.path.exists(path):
        os.makedirs(path)
    
    # write out influence lists to disk
    data = bind_data(skin_clusters)
    if data:
        filename = dump_json(data, path)
        print(f'*** Bind Data exported to {filename}')
    else:
        cmds.warning('!!! Bind Data NOT FOUND!')
    
    for skn_clstr in skin_clusters:
        if cmds.objExists(skn_clstr):
            # Get the geometry influenced by the skinCluster
            geometry = cmds.listConnections(skn_clstr, type="mesh")
            
            if geometry:
                mesh = geometry[0]
                
                # use short name
                if '|' in mesh:
                    name = mesh.split('|')[-1]
                else:
                    name = mesh
                
                # add prefix
                name = f'sw_{char}_{mesh}.xml'
                                
                if v:
                    print(f'***Exporting: {skn_clstr}')
                    #print(f'   {name}')
                cmds.deformerWeights(name, export=True, deformer=skn_clstr, format=FORMAT.upper(), path=path)
        else:
            cmds.warning(f'Skin Cluster NOT FOUND: {skn_clstr}')
    # return path to exported files
    return path


def import_skin_weights(char=None, meshes=None, path=None, v=True, normalize=True):
    '''
    skin_clusters: List of skin cluster deformer names
    v: (verbosity) Extra output on what's going on
    ----------------
    imports .xml for given list of skin clusters
    if no list is given will write for ALL skin_clusters in scene
    '''

    if not char:
        char = get_char()
    if not path:
        path = get_dir(char, latest=True)
    print(f'found skinweights dir: {path}')

    files = os.listdir(path)
    prefix = f'sw_{char}_'
    ext = f'.{FORMAT}'
    
    for f in files:
        if ext in f:
            # strip extention and prefix from filename
            mesh = f.replace(ext, '')
            if prefix in mesh:
                mesh = mesh.replace(prefix, '')
                
                if meshes:
                    if not mesh in meshes:
                        continue
                
                if cmds.objExists(mesh):
                    if v: print(f'found mesh: {mesh}')
                    sc = bw_rigUtils.getSkinCluster(mesh)
                    if sc:
                        if v: print(f'found skincluster: {sc}')
                        # perform import
                        # shape = cmds.listRelatives(mesh, shapes=True, path=True, noIntermediate=True)[0]
                        result = cmds.deformerWeights(f, im=True, method='index', deformer=sc, path=path) 
                        if v: print(f'Imported Weights: {result}')

                        if normalize:
                            normalizeWeights(mesh)
                elif v:
                    print(f'mesh not found: {mesh}')


def dump_json(data, path):
    filename = os.path.join(path, JSON_FILE)
    # write a dictionary to a json file
    data_str = pprint.pformat(data, compact=False).replace("'",'"')
    with open(filename, 'w') as f: 
         f.write(data_str)
    return filename


def read_json(dumpfile):
    if os.path.exists(dumpfile):
        print("importing bind data")
        # Read JSON file
        with open(dumpfile, 'r') as f:
            data_from_disk = json.load(f)
        return data_from_disk
    else:
        cmds.warning(f'FAILED to read data: {dumpfile}')
        return None


def get_char():
    # get character name (hopefully)
    try:
        char = cmds.getAttr(ASSET_TAG)
        print(f'Found Char Name: {char}')
    except:
        char = 'UNKNOWN'
        print(f'{ASSET_TAG} not found')
    return char


def get_dir(char, latest=False, ver_up=False):
    """
    finds directory to read/write skinweights from/to
    latest: Flag to find latest version
    ver_up:  Flag to create new version
    if neither flag is given, defaults to character dir where version dirs would be
    """
    path = None
    dir_base = BASE
    if not char:
        char = get_char()
    dir_char = os.path.join(dir_base, char)
    
    if not os.path.exists(dir_char):
        os.makedirs(dir_char)
    
    if ver_up:
        # create versioned directory
        dir_ver = version_up(dir_char)
        return dir_ver
    
    if latest:
        # find highest version dir  (TODO: check for empty dir?)
        versions = os.listdir(dir_char)
        if versions:
            dir_ver = os.path.join(dir_char, max(versions))
        else:
            # create versioned directory
            dir_ver = version_up(dir_char)
            dir_ver = dir_char
        return dir_ver
    
    return dir_char
        

def version_up(dir_base):
    """Check for existing version directories (e.g., dir_v001, dir_v002, ...)"""
    version = 1

    # are we already in a ver dir??
    cur_dir = dir_base.split('/')[-1]
    if  bool(re.fullmatch(r'v\d{3}', cur_dir)):
        print(f'Currently in a version directory: {cur_dir}')
        version = int(cur_dir[1:])
        print(f'versioning up from {version}')
        # remove current (ver) directory from base path and replace first /
        dir_base = f'/{os.path.dirname(dir_base).lstrip("/")}'

    # create next version dir
    while version < 999:
        # Pad
        padded = f"{version:03}"
        
        # Create the versioned directory name
        versioned_dir = f"{dir_base}/v{padded}"
        
        # Check if the directory already exists
        if not os.path.exists(versioned_dir):
            os.makedirs(versioned_dir)
            print(f"Created directory: {versioned_dir}")
            break
        else:
            version += 1  # Increment version number and try again
    return versioned_dir
