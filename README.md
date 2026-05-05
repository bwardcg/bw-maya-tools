# bw_tools — Maya Python Toolkit

A collection of Python scripts and utilities for Autodesk Maya, covering animation, rigging, snapping, constraint workflows, and general scene management.

**Author:** Brian Ward — [bwardcg@gmail.com](mailto:bwardcg@gmail.com) — [brianward.work](https://www.brianward.work)

## Requirements

- **Maya 2025+** (PySide6 / Python 3)
- **ffmpeg** on PATH (only needed for `bw_playblast`)

## Installation

The entire toolkit is designed to be loaded as a single package called **`bw_tools`**.

### Quick Install

1. Clone (or download) this repo into your Maya scripts directory and rename the folder to `bw_tools`:

   ```bash
   cd "<MAYA_SCRIPTS_DIR>"
   git clone https://github.com/bwardcg/bw-maya-tools.git bw_tools
   ```

   > **Where is `<MAYA_SCRIPTS_DIR>`?**
   > - **Windows:** `C:\Users\<you>\Documents\maya\scripts\`
   > - **macOS:** `~/Library/Preferences/Autodesk/maya/scripts/`
   > - **Linux:** `~/maya/scripts/`

2. **(Optional) Install the shelf:** Copy `bw_tools/shelves/shelf_bw_Tools.mel` into your Maya shelves directory:

   ```
   <MAYA_PREFS>/shelves/
   ```

   Or drag-and-drop the `.mel` file onto the Maya shelf area.

3. **(Optional) Copy icons:** Copy the contents of `bw_tools/icons/` into your Maya icons directory:

   ```
   <MAYA_PREFS>/prefs/icons/
   ```

### Verify Installation

In the Maya Script Editor (Python tab):

```python
from bw_tools import bw_menu
bw_menu.build()
```

This will create a **bw_Menu** dropdown in Maya's main menu bar with all available tools.

## Project Structure

```
bw_tools/
│
├── bw_menu.py              # Builds the Maya menu bar dropdown
├── bw_utils.py             # Core utility functions (getters, setters, misc)
├── bw_snap.py              # Object snapping / matching (Snap class)
├── bw_nodes.py             # Lightweight Maya node wrapper class
├── bw_playblast.py         # Playblast-to-MP4 via ffmpeg
├── bw_keys_randomizer.py   # Randomize keyframe values/timing (with UI)
├── bw_get_nearest_vert.py  # OpenMaya closest-vertex lookup
├── bw_ui_maya.py           # PySide6 base window class for tool UIs
├── bw_ui_template.py       # Minimal UI starter template
│
├── bw_Menu/                # Categorized menu scripts (each has a run())
│   ├── bw_tools_UI.py      # Quick-access PySide6 toolbar
│   ├── _RELOAD.py          # Hot-reload the entire bw_tools package
│   ├── anim/               # Animation: copy anim, plot path, randomize keys, etc.
│   ├── color/              # Wireframe color overrides (auto, red, blue, yellow)
│   ├── constrain/          # Constraint helpers (null parents, locator groups)
│   ├── modify/             # Scene cleanup (unique names, pivots, unlock xforms)
│   ├── rig/                # Rigging shortcuts (buffer xform, ctrls, follicles)
│   └── snap/               # Snap / match / cycle between objects
│
├── rigging/                # Full rigging modules
│   ├── bw_rigUtils.py      # Rig helper functions (skinCluster, colors, space switch)
│   ├── bw_skinning.py      # Skinning operations
│   ├── bw_skinning_UI.py   # PySide6 skinning interface
│   ├── bw_skinning_IO.py   # Skin weight import/export
│   ├── bw_prep_char.py     # Character prep / skeleton builder
│   ├── bw_ctrl_shapes.py   # Control curve shape library
│   ├── bw_blendshapeTools.py  # Blendshape utilities
│   ├── bw_attachToSkin.py  # Attach objects to skin
│   ├── bw_build.py         # Rig build entry point
│   ├── bw_spaceswitch.py   # Space switching setup
│   ├── tidy.py             # Scene cleanup / rig tidy
│   └── ctrl_shapes/        # Maya binary files with control curve shapes
│
├── icons/                  # PNG icons for shelf buttons
├── shelves/                # Maya shelf definition (shelf_bw_Tools.mel)
│
├── __init__.py
├── .gitignore
├── LICENSE
└── README.md
```

## Usage

### Menu System

The `bw_menu.py` script dynamically scans the `bw_Menu/` directory and builds a categorized dropdown menu in Maya's menu bar. Each Python file in the subdirectories should define a `run()` function.

```python
from bw_tools import bw_menu
bw_menu.build()
```

### Snapping Tools

```python
from bw_tools.bw_snap import Snap

snap = Snap()
snap.snapObjs(source_obj, [target1, target2], key=True)   # snap + set keyframe
snap.snapObjs(source_obj, [target1], trans=True, rot=False) # translate only
```

### Playblast to MP4

```python
from bw_tools.bw_playblast import playblast_to_mp4

playblast_to_mp4()                          # uses scene defaults
playblast_to_mp4(fps=30, width=1280, height=720, clear_temp=False)
```

### Keyframe Randomizer

```python
from bw_tools.bw_keys_randomizer import create_randomizer_ui
create_randomizer_ui()
```

### Hot Reload (Development)

After editing any script, reload the entire package without restarting Maya:

```python
from bw_tools.bw_Menu._RELOAD import reload_package
reload_package()
```

## License

[MIT License](LICENSE) — free to use, modify, and distribute.
