###############################
#
#   Randomize selected keys in the Graph Editor
#
#   Author:  Brian Ward  bwardcg@gmail.com  www.brianward.work
#
#   Requires:  
#
###############################

import maya.cmds as mc
import random

def randomize_selected_keyframes_value(min_value, max_value):
    """
    Randomizes the values of selected keyframes within a given range.

    Args:
        min_value (float): The minimum value for randomization.
        max_value (float): The maximum value for randomization.
    """
    anim_curves = mc.keyframe(query=True, name=True, selected=True)
    if not anim_curves:
        mc.warning("No keyframes selected. Please select keyframes in the Graph Editor.")
        return

    anim_curves = list(set(anim_curves))

    for curve in anim_curves:
        key_indices = mc.keyframe(curve, query=True, selected=True, indexValue=True)
        if not key_indices:
            continue

        for key_index in key_indices:
            current_value = mc.keyframe(curve, query=True, index=(key_index, key_index), valueChange=True)[0]
            current_time = mc.keyframe(curve, query=True, index=(key_index, key_index), timeChange=True)[0]
            
            random_offset = random.uniform(min_value, max_value)
            new_value = current_value + random_offset

            mc.keyframe(curve, edit=True, time=(current_time, current_time), valueChange=new_value)

def randomize_selected_keyframes_time(min_value, max_value):
    """
    Randomizes the time of selected keyframes within a given range.

    Args:
        min_value (float): The minimum time offset.
        max_value (float): The maximum time offset.
    """
    anim_curves = mc.keyframe(query=True, name=True, selected=True)
    if not anim_curves:
        mc.warning("No keyframes selected. Please select keyframes in the Graph Editor.")
        return

    anim_curves = list(set(anim_curves))

    for curve in anim_curves:
        key_indices = mc.keyframe(curve, query=True, selected=True, indexValue=True)
        if not key_indices:
            continue

        # Sort the key indices to avoid issues with keys shifting position.
        key_indices.sort(reverse=True)
        
        for key_index in key_indices:
            current_time = mc.keyframe(curve, query=True, index=(key_index, key_index), timeChange=True)[0]
            
            random_offset = random.uniform(min_value, max_value)
            new_time = current_time + random_offset

            # This is the more reliable way to change a key's time.
            try:
                mc.keyframe(curve, edit=True, index=(key_index, key_index), timeChange=new_time)
            except RuntimeError as e:
                mc.warning(f'{e}Unable to change time on key#: {key_index} for {curve}')


def create_randomizer_ui():
    """
    Creates the user interface for the keyframe randomizer tool.
    """
    window_name = "KeyframeRandomizerUI"
    if mc.window(window_name, exists=True):
        mc.deleteUI(window_name, window=True)

    mc.window(window_name, title="Keyframe Randomizer", widthHeight=(250, 100))
    mc.columnLayout(adjustableColumn=True, rowSpacing=5, columnOffset=("both", 5))

    mc.text(label="Randomize keyframe Values:")
    mc.floatFieldGrp("value_min_field", label="Min Value", value1=-1.0, precision=2)
    mc.floatFieldGrp("value_max_field", label="Max Value", value1=1.0, precision=2)
    mc.button(label="Randomize Value", command=run_randomizer_value)

    mc.separator(height=10, style="in")

    mc.text(label="Randomize keyframe Timing:")
    mc.floatFieldGrp("time_min_field", label="Min Time", value1=-5.0, precision=2)
    mc.floatFieldGrp("time_max_field", label="Max Time", value1=5.0, precision=2)
    mc.button(label="Randomize Time", command=run_randomizer_time)
    
    mc.showWindow(window_name)

def run_randomizer_value(*args):
    """
    Retrieves values from the UI for value randomization.
    """
    min_val = mc.floatFieldGrp("value_min_field", query=True, value1=True)
    max_val = mc.floatFieldGrp("value_max_field", query=True, value1=True)

    if min_val > max_val:
        mc.warning("Minimum value cannot be greater than the maximum value.")
        return

    randomize_selected_keyframes_value(min_val, max_val)

def run_randomizer_time(*args):
    """
    Retrieves values from the UI for time randomization.
    """
    min_val = mc.floatFieldGrp("time_min_field", query=True, value1=True)
    max_val = mc.floatFieldGrp("time_max_field", query=True, value1=True)

    if min_val > max_val:
        mc.warning("Minimum value cannot be greater than the maximum value.")
        return
    
    randomize_selected_keyframes_time(min_val, max_val)

if __name__ == "__main__":
    create_randomizer_ui()
