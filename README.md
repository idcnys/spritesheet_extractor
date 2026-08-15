# Sprite Sheet Extractor

Interactive Python tool to split a sprite sheet into individual PNG frames.

## Features

- Interactive terminal prompts
- `fixed_grid` mode for evenly spaced sprite sheets
- `auto_detect` mode for transparent-background sprite sheets
- Output organized by row: `row_1`, `row_2`, etc.

## Requirements

- Python 3.9+ (recommended)
- Pillow (listed in `/home/runner/work/spritesheet_extractor/spritesheet_extractor/requirement.txt`)

## Installation

From `/home/runner/work/spritesheet_extractor/spritesheet_extractor`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
```

## Basic Usage

Run:

```bash
python main.py
```

The script will ask for:

1. Sprite sheet image path
2. Output directory
3. Extraction mode (`fixed_grid` or `auto_detect`)
4. Mode-specific settings

## Usage Examples

### Example 1: Fixed Grid (auto cell size)

Use this when all frames are aligned in equal rows/columns:

```text
Path to sprite sheet image [pet1.png]: assets/character.png
Output directory [extracted]: character_frames
Extraction mode: 'fixed_grid' or 'auto_detect' [fixed_grid]:
--- Fixed Grid Settings ---
Number of rows [5]: 4
Number of columns (frames per row) [5]: 6
Do you want to specify custom cell width/height? (otherwise auto-calculated) [y/N]: n
```

### Example 2: Fixed Grid (custom cell size)

Use this when the sheet size is not perfectly divisible by rows/columns:

```text
Path to sprite sheet image [pet1.png]: assets/monster.png
Output directory [extracted]: monster_frames
Extraction mode: 'fixed_grid' or 'auto_detect' [fixed_grid]:
--- Fixed Grid Settings ---
Number of rows [5]: 3
Number of columns (frames per row) [5]: 8
Do you want to specify custom cell width/height? (otherwise auto-calculated) [y/N]: y
Cell width (pixels): 64
Cell height (pixels): 64
```

### Example 3: Auto Detect

Use this when sprites are separated by transparent gaps:

```text
Path to sprite sheet image [pet1.png]: assets/effects.png
Output directory [extracted]: effects_frames
Extraction mode: 'fixed_grid' or 'auto_detect' [fixed_grid]: auto_detect
--- Auto-Detect Settings ---
Alpha threshold (pixels with alpha <= this are empty) [10]: 10
Minimum gap (empty pixels) between sprites/rows [2]: 2
```

### Example 4: Existing Output Directory

If output directory already exists:

```text
Directory 'character_frames' already exists. Overwrite? [y/N]: y
Existing files will be overwritten if names conflict.
```

If you answer `n`, the tool exits.

## Output Layout

The extractor saves PNG files like:

```text
character_frames/
  row_1/
    frame_1.png
    frame_2.png
    ...
  row_2/
    frame_1.png
    frame_2.png
    ...
```

## Notes

- `fixed_grid`: frames are cropped using row/column coordinates.
- `auto_detect`: only pixels with alpha above threshold are treated as content.
- For best `auto_detect` results, keep clear transparent spacing between sprites.
