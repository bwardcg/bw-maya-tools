###############################
#
#   MATCH ANIM B to A
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  bw_snap
#
##############################

import maya.cmds as mc
from bw_tools import bw_utils as util
from bw_tools.bw_snap import Snap

class Match(Snap):
    def __init__(self):
        super().__init__()

    def match_frame_range(
            self, source_obj=None, target_objs=[], 
            bracket=True, start=None, end=None,
            trans=None, rot=None
            ):

        """
        snap target objs to source obj over a frame range
        """ 

        if not source_obj or not self.getXforms([source_obj]):
            print("no source obj given, nothing was snapped")
            return False

        # refresh playback start, end, current and first,last keyframes
        startFrame, endFrame = util.getFrameRange()
        firstKey = mc.findKeyframe(timeSlider=True, which="first")
        lastKey = mc.findKeyframe(timeSlider=True, which="last")
    
        # overide start and end args
        if start:
            startFrame = start
        if end:
            endFrame = end

        # fr will represent our current frame, setting to first keyframe
        fr = firstKey
        curTime = mc.currentTime(q = True)
        
        print(f'Matching {target_objs} to {source_obj} from fr{startFrame} to fr{endFrame}')

        # if bracket is on, key first playback frame
        if bracket:
            mc.currentTime(startFrame)
            #snap targets to source
            self.snapObjs(source_obj, target_objs, key=True)

        # if timeslider has more than one tick, loop through ticks
        if firstKey != lastKey:
            print(f'looping through keys: fr{firstKey} to fr{lastKey}')
            while fr < lastKey:
                mc.currentTime(fr)
                #snap targets to source
                self.snapObjs(source_obj, target_objs, key=True)
                # go to next visible key tick
                fr = mc.findKeyframe(timeSlider=True, which="next")

        # snap last (or only) frame
        mc.currentTime(fr)
        self.snapObjs(source_obj, target_objs, key=True)

        # if bracket is on, key last playback frame
        if bracket:
            mc.currentTime(endFrame)
            #snap targets to source
            self.snapObjs(source_obj, target_objs, key=True)

        # restore pevious current frame and playback range
        mc.currentTime(curTime)
        mc.playbackOptions(min = startFrame, max = endFrame)    # is this needed?

def run():
    match_obj = Match()
    
    # get all transforms from selection
    xforms = match_obj.getXforms()
    
    # use first xform as source
    source  = xforms[0]
    targets = xforms[1:]

    match_obj.match_frame_range(source, targets)
