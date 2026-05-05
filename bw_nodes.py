###############################
#
#   BW_NODES
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  
#
##############################

import maya.cmds as mc

class Maya_Node:
    def __init__(self, name):
        if not mc.objExists(name):
            raise ValueError(f"Object '{name}' does not exist in the scene.")
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Node('{self.name}')"

    @property
    def long(self):
        return mc.ls(self.name, long=True)[0]

    @property
    def type(self):
        return mc.objectType(self.name)

    def rename(self, new_name):
        self.name = mc.rename(self.name, new_name)
        return self

    def parent(self, new_parent):
        self.name = mc.parent(self.name, new_parent)[0]
        return self

    def unparent(self):
        self.name = mc.parent(self.name, world=True)[0]
        return self

    def delete(self):
        if mc.objExists(self.name):
            print(f'{self.long} is deleting itself.')
            mc.delete(self.name)

    def exists(self):
        return mc.objExists(self.name)

    def get_parent(self):
        parent = mc.listRelatives(self.name, parent=True)
        return parent[0] if parent else None

    def shapes(self):
        return mc.listRelatives(self.long, children=True, shapes=True, fullPath=True) or []

    def is_name_unique(self):
        return len(mc.ls(self.name)) == 1

    def is_mesh(self):
        if self.type == 'mesh':
            return True
        for shape in self.shapes():
            if mc.objectType(shape) == 'mesh':
                return True
        return False

    def namespace(self):
        parts = self.long.split(':')
        if len(parts) > 1:
            return ':'.join(parts[:-1])
        else:
            return ""

    @classmethod
    def create_transform(cls, name):
        obj = mc.createNode("transform", name=name)
        return cls(obj)
