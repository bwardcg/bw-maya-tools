import os
import glob
import subprocess
import shutil
import maya.cmds as cmds

def playblast_to_mp4(
        output_mp4=None,
        fps=24,
        width=1920,
        height=1080,
        quality=100,
        percent=100,
        offscreen=True,
        clear_temp=True,
        use_time_slider_or_sel=True,
        step=1,
        image_type="jpg"):
    """
    Playblast current time range (or selected range) to JPGs and encode to MP4 via ffmpeg.

    Args:
        output_mp4 (str): Full path to final mp4. If None, uses scene folder/sceneName_playblast.mp4.
        fps (int): Frame rate for ffmpeg.
        width (int): Playblast width.
        height (int): Playblast height.
        quality (int): Playblast quality (0–100).
        offscreen (bool): Use offscreen rendering.
        clear_temp (bool): Remove temp JPGs afterwards.
        use_time_slider_or_sel (bool): If True, use selected time range if any, otherwise time slider.
        step (int): Hold frames by this amount to effectively lower the fps.
        image_type (str): Type of image to playblast (e.g. 'jpg', 'png').
    """

    # Determine start/end frame
    if use_time_slider_or_sel and cmds.keyframe(query=True, selected=True):
        # Range of selected keys
        sel_min = cmds.playbackOptions(min=True, query=True)
        sel_max = cmds.playbackOptions(max=True, query=True)
        start = sel_min
        end = sel_max
    else:
        # Use time slider playback range
        start = cmds.playbackOptions(minTime=True, query=True)
        end = cmds.playbackOptions(maxTime=True, query=True)

    start = int(start)
    end = int(end)

    # Scene path and name
    scene_path = cmds.file(query=True, sceneName=True)
    if not scene_path:
        scene_dir = cmds.internalVar(userWorkspaceDir=True)
        scene_name = "untitled"
    else:
        scene_dir = os.path.dirname(scene_path)
        scene_name = os.path.splitext(os.path.basename(scene_path))[0]

    # Playblast folder
    pb_dir = os.path.join(scene_dir, "Playblasts")
    if not os.path.exists(pb_dir):
        os.makedirs(pb_dir)
    # Temp image folder        
    temp_dir = os.path.join(pb_dir, f"playblast_{scene_name}")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Image sequence filename pattern
    # Maya will produce something like: playblast.0001.jpg, playblast.0002.jpg, etc.
    img_name = f"pblast_{scene_name}"
    img_base = os.path.join(temp_dir, img_name)

    # Optionally clean temporary images
    if clear_temp:
        for f in glob.glob(os.path.join(temp_dir, f"{img_name}.*.{image_type}")):
            try:
                os.remove(f)
            except OSError:
                pass

    if image_type.lower() == "png":
        # Ensure Maya viewport background is transparent for RGBA PNGs
        try:
            cmds.setAttr("hardwareRenderingGlobals.transparentState", 1)
        except Exception:
            pass

    playblast_kwargs = {
        "filename": img_base,
        "forceOverwrite": True,
        "format": "image",
        "compression": image_type,
        "quality": quality,
        "viewer": False,
        "showOrnaments": False,
        "widthHeight": (width, height),
        "percent": percent,
        "offScreen": offscreen
    }

    if step > 1:
        # Calculate the actual frames we need to evaluate
        unique_frames = sorted(list(set([start + ((f - start) // step) * step for f in range(start, end + 1)])))
        playblast_kwargs["frame"] = unique_frames
        playblast_kwargs["rawFrameNumbers"] = True
    else:
        playblast_kwargs["startTime"] = start
        playblast_kwargs["endTime"] = end

    # Do the playblast to JPG sequence
    cmds.playblast(**playblast_kwargs)

    # Fill in the held frames by copying the stepped frames
    if step > 1:
        for f in range(start, end + 1):
            snapped = start + ((f - start) // step) * step
            if f != snapped:
                src = f"{img_base}.{snapped:04d}.{image_type}"
                dst = f"{img_base}.{f:04d}.{image_type}"
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copy2(src, dst)

    # ffmpeg output mp4 path
    if output_mp4 is None:
        output_mp4 = os.path.join(pb_dir, f"{scene_name}_playblast.mp4")

    # Build ffmpeg input pattern:
    # If Maya produced playblast.####.ext with 4‑digit padding, use %04d
    ffmpeg_input = os.path.join(temp_dir, f"{img_name}.%04d.{image_type}")

    # ffmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",                     # overwrite
        "-framerate", str(fps),
        "-start_number", str(start),
        "-i", ffmpeg_input,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_mp4
    ]

    print(f"Running: {ffmpeg_cmd}")
    try:
        subprocess.check_call(ffmpeg_cmd)
    except subprocess.CalledProcessError as e:
        cmds.warning("ffmpeg failed: {}".format(e))
        return

    # Optionally clean temporary directory
    if clear_temp:
        try:
            os.remove(temp_dir)
        except OSError:
            pass

    print("Playblast written to:", output_mp4)
    cmds.inViewMessage(amg="Playblast saved: <hl>{}</hl>".format(output_mp4),
                       pos="topCenter",
                       fade=True)

# Example: call this from a shelf button
# playblast_to_mp4()
# playblast_to_mp4(clear_temp=False)