###############################
#
#   CYCLE SNAP
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_snap
#
##############################

import maya.cmds as mc
from bw_tools.bw_snap import Snap

class Cycle(Snap):
    def __init__(self):
        super().__init__()

    def cycle_snap(self, objsInput = []):
        """
        snaps each selected obj to next selection and last obj to first
        """
        # get list of transforms from input or selection
        xforms = self.getXforms(objsInput)

        # create locator to record position of first target
        target = xforms[-1]
        loc = self.makeLocator(target)
        source = loc
        # print("snapping %s to %s" %(loc, target))
        self.snap(target, loc)

        # loop through rest of selection (except last obj) snapping each to next
        for obj in xforms[0:-1]:
            source = obj
            # print("snapping %s to %s" %(target, source))
            self.snap(source, target)
            target = obj

        # snap last source back to first target pos marked by locator
        self.snap(loc, source)

        # change selection to all modified objs and delete temp locator
        mc.select(xforms)
        mc.delete(loc)

def run():
    snap_obj = Cycle()
    snap_obj.cycle_snap()
