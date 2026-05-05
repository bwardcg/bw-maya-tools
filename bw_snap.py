###############################
#
#   BW_SNAP
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_utils
#
##############################

# usage:
'''
from bw_tools.bw_snap import Snap
snap_obj = Snap()
snap_obj.snapObjs(source_obj, targets_list)
'''

import maya.cmds as mc
from bw_tools import bw_utils as util

attrsT = ['.tx', '.ty', '.tz']
attrsR = ['.rx', '.ry', '.rz']

class Snap():
    def __init__(self):
        """declare some variables"""
        self.rot = True
        self.trans = True
        self.attrsT = attrsT
        self.attrsR = attrsR

    # --------------------------- UTILITIES --------------------

    def makeLocator(self, obj=None):
        """
        creates locator and names it after input obj
        sets locator rotate order to match object
        """
        
        # get name for locator
        name = self.formatName(obj) + "_LOC"

        #make LOCATOR and give unique name
        if mc.objExists(name):
            name = name + "#"
        locs = mc.spaceLocator(name=name)
        loc = locs[0]

        #get and match Rotation Order
        if obj and mc.objExists(obj):
            rotOrder = mc.getAttr( obj +".ro" )                                  
            mc.setAttr( loc +".ro", rotOrder)
    
        return loc


    def set_key(self, obj):
        if self.trans:
            for a in self.attrsT:
                mc.setKeyframe(obj, at=a)
        if self.rot:
            for a in self.attrsR:
                mc.setKeyframe(obj, at=a)

    # --------------------------- STATIC METHODS --------------------
    @staticmethod
    def getXforms(objs=[]):
        """
        checks input, or selection, for transforms.
        """
        xforms = []
        if not objs:
            # print("no input given, operating on selection")
            objs = mc.ls(sl=True)
        for o in objs:
            if mc.objExists(o) and mc.objectType(o, isAType='transform'):
                xforms.append(o)
        if xforms == []:
            mc.error(f'No transforms found in {objs}')
            return None
        return xforms

    @staticmethod
    def formatName(obj):
        """
        get a name that includes the root namespace
        """
        if obj:
            util.getName(obj)
        else:
            name = "null"
        return name

    
    # --------------------------- SNAP METHODS --------------------
    def snap(self, source_obj, targetObj):
        """
        snap single target object to source using matchTranform (unless legacy)
        """
        try:
            # snapping using Maya matchTransform command
            mc.matchTransform(targetObj, source_obj, rot=self.rot, pos=self.trans)
        except:
            print("MatchTransform command failed. Maybe we're using an older version of Maya without matchTransform? Using old snap function.")
            self.snap_legacy(source_obj, targetObj)
        
    
    def snap_legacy(self, source_obj, targetObj):
        """
        snap single target object to source using constrained locators.
        DEPRICATED - Now that Maya 2016 sp2+ has matchTranform
        """

        # create locators
        sourceLoc = self.makeLocator(source_obj)
        targetLoc = self.makeLocator(targetObj)

        # constrain locators
        mc.parentConstraint(source_obj, sourceLoc, w=1, mo=False )
        mc.parentConstraint(targetObj, targetLoc, w=1, mo=False )

        # get source trans and rots
        sourceT = mc.getAttr(sourceLoc + ".t")[0]
        sourceR = mc.getAttr(sourceLoc + ".r")[0]
        # get target trans
        targetT = mc.getAttr(targetLoc + ".t")[0]

        # get trans difference
        tx = sourceT[0] - targetT[0]
        ty = sourceT[1] - targetT[1]
        tz = sourceT[2] - targetT[2]
        rx = sourceR[0]
        ry = sourceR[1]
        rz = sourceR[2]

        # apply transforms (trans relative, rot absolute)
        if self.trans:
            mc.xform(targetObj, r=True, ws=True, t=(tx, ty, tz) )
        if self.rot:
            mc.xform(targetObj, a=True, ws=True, ro=(rx, ry, rz) )

        # clean up locators
        mc.delete(sourceLoc,targetLoc)


    def snapObjs(self, source_obj=None, target_objs=[], trans=None, rot=None, key=False):
        """
        snap target objs to source obj
        """

        if not source_obj or not self.getXforms([source_obj]):
            print("no source obj given, nothing was snapped")
            return False

        if trans is not None:
            self.trans = trans
        if rot is not None:
            self.rot = rot

        # snap targets to source
        for obj in self.getXforms(target_objs):
            self.snap(source_obj, obj)
            if key:
                self.set_key(obj)

        # change selection to targets
        mc.select(target_objs, r=True)
