import os
import sys
from PIL import Image

# -------- Terminal colors (ANSI codes) --------
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_RED = "\033[91m"

def color_text(text, color=COLOR_RESET, bold=False):
    """Wrap text with color and optional bold."""
    bold_code = COLOR_BOLD if bold else ""
    return f"{bold_code}{color}{text}{COLOR_RESET}"

def print_info(text):
    print(color_text(text, COLOR_CYAN))

def print_success(text):
    print(color_text(text, COLOR_GREEN, bold=True))

def print_error(text):
    print(color_text(text, COLOR_RED, bold=True))

def print_warning(text):
    print(color_text(text, COLOR_YELLOW))

def prompt(prompt_text, default=None, validator=None, is_yes_no=False):
    """
    Prompt user with optional default and validation.
    Returns the user's input (or default if empty).
    """
    if default is not None:
        if is_yes_no:
            default_display = "Y/n" if default.lower() in ('y', 'yes') else "y/N"
        else:
            default_display = str(default)
        full_prompt = f"{prompt_text} [{default_display}]: "
    else:
        full_prompt = f"{prompt_text}: "

    while True:
        user_input = input(color_text(full_prompt, COLOR_BLUE)).strip()
        if user_input == "" and default is not None:
            user_input = default
        if is_yes_no:
            if user_input.lower() in ('y', 'yes', 'n', 'no'):
                return user_input.lower() in ('y', 'yes')
            else:
                print_warning("Please answer y or n.")
                continue
        if validator is not None:
            try:
                validated = validator(user_input)
                return validated
            except ValueError as e:
                print_warning(f"Invalid input: {e}")
                continue
        return user_input

def path_validator(path_str):
    """Ensure a directory exists (for output) or file exists (for input)."""
    return path_str.strip()

def int_validator(min_val=None, max_val=None):
    def _validator(val):
        try:
            ival = int(val)
        except ValueError:
            raise ValueError("Must be an integer.")
        if min_val is not None and ival < min_val:
            raise ValueError(f"Must be >= {min_val}.")
        if max_val is not None and ival > max_val:
            raise ValueError(f"Must be <= {max_val}.")
        return ival
    return _validator

def float_validator(min_val=None, max_val=None):
    def _validator(val):
        try:
            fval = float(val)
        except ValueError:
            raise ValueError("Must be a number.")
        if min_val is not None and fval < min_val:
            raise ValueError(f"Must be >= {min_val}.")
        if max_val is not None and fval > max_val:
            raise ValueError(f"Must be <= {max_val}.")
        return fval
    return _validator

def positive_int_validator(val):
    return int_validator(min_val=1)(val)

# -------- Extraction functions (unchanged, except for output directory creation) --------
def extract_fixed_grid(sheet, output_dir, rows, cols, cell_width=None, cell_height=None):
    sheet_w, sheet_h = sheet.size

    cell_w = cell_width or sheet_w // cols
    cell_h = cell_height or sheet_h // rows

    print_info(f"Sheet size: {sheet_w}x{sheet_h}")
    print_info(f"Cell size: {cell_w}x{cell_h}  |  Rows: {rows}  Cols: {cols}")

    for row in range(rows):
        row_dir = os.path.join(output_dir, f"row_{row + 1}")
        os.makedirs(row_dir, exist_ok=True)

        for col in range(cols):
            left = col * cell_w
            upper = row * cell_h
            right = left + cell_w
            lower = upper + cell_h

            if right > sheet_w or lower > sheet_h:
                continue

            cell = sheet.crop((left, upper, right, lower))
            cell_path = os.path.join(row_dir, f"frame_{col + 1}.png")
            cell.save(cell_path)

        print_success(f"  Saved row_{row + 1} ({cols} frames) -> {row_dir}")

def find_content_bands(profile, min_gap):
    bands = []
    start = None
    gap = 0

    for i, has_content in enumerate(profile):
        if has_content:
            if start is None:
                start = i
            gap = 0
        else:
            if start is not None:
                gap += 1
                if gap > min_gap:
                    bands.append((start, i - gap))
                    start = None
                    gap = 0

    if start is not None:
        bands.append((start, len(profile) - 1))

    return bands

def extract_auto_detect(sheet, output_dir, alpha_threshold, min_gap):
    sheet = sheet.convert("RGBA")
    sheet_w, sheet_h = sheet.size
    pixels = sheet.load()

    # Row profile
    row_has_content = []
    for y in range(sheet_h):
        found = False
        for x in range(sheet_w):
            if pixels[x, y][3] > alpha_threshold:
                found = True
                break
        row_has_content.append(found)

    row_bands = find_content_bands(row_has_content, min_gap)
    print_info(f"Detected {len(row_bands)} row(s)")

    for row_idx, (y1, y2) in enumerate(row_bands):
        row_dir = os.path.join(output_dir, f"row_{row_idx + 1}")
        os.makedirs(row_dir, exist_ok=True)

        # Column profile within this row band
        col_has_content = []
        for x in range(sheet_w):
            found = False
            for y in range(y1, y2 + 1):
                if pixels[x, y][3] > alpha_threshold:
                    found = True
                    break
            col_has_content.append(found)

        col_bands = find_content_bands(col_has_content, min_gap)

        for frame_idx, (x1, x2) in enumerate(col_bands):
            cell = sheet.crop((x1, y1, x2 + 1, y2 + 1))
            cell_path = os.path.join(row_dir, f"frame_{frame_idx + 1}.png")
            cell.save(cell_path)

        print_success(f"  row_{row_idx + 1}: {len(col_bands)} frame(s) -> {row_dir}")

# -------- Interactive main --------
def main():
    print(color_text("=== Interactive Sprite Sheet Extractor ===", COLOR_MAGENTA, bold=True))
    print_info("This tool extracts individual frames from a sprite sheet.")
    print_info("You can choose between a fixed grid layout or automatic detection.")
    print()

    # 1. Input file
    while True:
        path = prompt("Path to sprite sheet image", default="pet1.png", validator=path_validator)
        if not os.path.exists(path):
            print_error(f"File '{path}' not found. Please try again.")
        else:
            break

    # 2. Output directory
    default_out = "extracted"
    out_dir = prompt("Output directory", default=default_out, validator=path_validator)

    # Check if output dir exists and ask for overwrite
    if os.path.exists(out_dir):
        if not prompt(f"Directory '{out_dir}' already exists. Overwrite?", default="n", is_yes_no=True):
            print_warning("Aborting.")
            sys.exit(0)
        # We'll keep existing files; extraction will overwrite individual frames if they exist.
        # But we can also delete everything? We'll just let it overwrite.
        print_warning("Existing files will be overwritten if names conflict.")

    # 3. Mode selection
    mode = prompt("Extraction mode: 'fixed_grid' or 'auto_detect'", default="fixed_grid")
    while mode not in ("fixed_grid", "auto_detect"):
        print_warning("Mode must be 'fixed_grid' or 'auto_detect'.")
        mode = prompt("Extraction mode", default="fixed_grid")

    # 4. Load image
    sheet = Image.open(path).convert("RGBA")

    # 5. Parameters depending on mode
    if mode == "fixed_grid":
        print_info("--- Fixed Grid Settings ---")
        rows = prompt("Number of rows", default="5", validator=positive_int_validator)
        cols = prompt("Number of columns (frames per row)", default="5", validator=positive_int_validator)

        # Optional cell width/height
        use_custom_cell = prompt("Do you want to specify custom cell width/height? (otherwise auto-calculated)", default="n", is_yes_no=True)
        cell_width = None
        cell_height = None
        if use_custom_cell:
            cell_width = prompt("Cell width (pixels)", validator=positive_int_validator)
            cell_height = prompt("Cell height (pixels)", validator=positive_int_validator)

        print_info("Extracting with fixed grid...")
        extract_fixed_grid(sheet, out_dir, rows, cols, cell_width, cell_height)

    else:  # auto_detect
        print_info("--- Auto-Detect Settings ---")
        alpha = prompt("Alpha threshold (pixels with alpha <= this are empty)", default="10", validator=int_validator(min_val=0, max_val=255))
        min_gap = prompt("Minimum gap (empty pixels) between sprites/rows", default="2", validator=positive_int_validator)

        print_info("Extracting with auto-detection...")
        extract_auto_detect(sheet, out_dir, alpha, min_gap)

    print_success("\nDone! Check the output directory: " + out_dir)

if __name__ == "__main__":
    main()