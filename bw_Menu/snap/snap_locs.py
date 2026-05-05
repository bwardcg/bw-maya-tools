###############################
#
#   SNAP LOCATORS
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_snap
#
##############################

from bw_tools.bw_snap import Snap

class Locators(Snap):
    def __init__(self):
        super().__init__()

    def snap_locs(self, objsInput = []):
        """
        matches locators to all input objs
        """
        
        locs = []    

        # loop through selection, make locator and snap it to obj
        for obj in self.getXforms(objsInput):
            loc = self.makeLocator(obj)
            locs.append(loc)
            self.snap(obj, loc)        
        
        return locs

def run():
    snap_obj = Locators()
    snap_obj.snap_locs()
