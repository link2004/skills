#!/usr/bin/env python3
"""
Magenta/Pink Background Removal Tool
Removes magenta/pink background using color-based detection.
"""

import argparse
import sys
import subprocess
from pathlib import Path

VENV_DIR = Path(__file__).parent / ".venv"


def ensure_venv():
    venv_python = VENV_DIR / "bin" / "python"
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
        subprocess.check_call([str(venv_python), "-m", "pip", "install", "-q", "pillow", "numpy", "scipy"])
    if sys.executable != str(venv_python):
        import os
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)


def remove_background_magenta(image_path: str, output_path: str = None) -> bool:
    """Remove magenta/pink background using color detection (with edge defringing)"""
    from PIL import Image
    import numpy as np
    from scipy.ndimage import binary_erosion, binary_dilation

    output = output_path or image_path
    print(f"Input: {image_path}")
    print("Removing background (magenta/pink color removal + defringe)...")

    try:
        img = Image.open(image_path).convert("RGBA")
        data = np.array(img, dtype=np.float32)

        r, g, b, a = data[:, :, 0], data[:, :, 1], data[:, :, 2], data[:, :, 3]

        # Magenta detection (relaxed conditions to catch anti-aliased areas)
        # Pure magenta: R high, G low, B high
        magenta_strong = (r > 180) & (g < 100) & (b > 100)
        # Light magenta/pink: R high, G low-ish, B higher than G
        magenta_weak = (r > 150) & (g < 150) & (b > g + 30) & (r > b)
        magenta_mask = magenta_strong | magenta_weak

        # Make magenta areas transparent
        data[magenta_mask] = [0, 0, 0, 0]

        # Edge detection (boundaries of remaining opaque areas)
        alpha = data[:, :, 3]
        alpha_mask = alpha > 0
        dilated = binary_dilation(alpha_mask, iterations=2)
        eroded = binary_erosion(alpha_mask, iterations=2)
        edge_mask = dilated & ~eroded & alpha_mask

        # Defringe edge pixels
        # Remove magenta component (where both R-G and B-G are high)
        edge_indices = np.where(edge_mask)
        for y, x in zip(edge_indices[0], edge_indices[1]):
            pixel = data[y, x]
            r_val, g_val, b_val, a_val = pixel
            if a_val > 0:
                # Calculate magenta contamination
                magenta_contamination = min(r_val - g_val, b_val - g_val)
                if magenta_contamination > 20:
                    # Remove magenta component (reduce R and B)
                    reduction = magenta_contamination * 0.7
                    data[y, x, 0] = max(0, r_val - reduction)  # R
                    data[y, x, 2] = max(0, b_val - reduction)  # B
                    # Slightly reduce alpha for soft edges
                    if magenta_contamination > 50:
                        data[y, x, 3] = a_val * 0.7

        # Make outermost 1px transparent (for remaining fine fringe)
        alpha_final = data[:, :, 3] > 0
        eroded_final = binary_erosion(alpha_final, iterations=1)
        data[~eroded_final] = [0, 0, 0, 0]

        result = Image.fromarray(data.astype(np.uint8), 'RGBA')
        result.save(output, "PNG")
        print(f"Output: {output}")
        print("Background removal complete (defringe + 1px erosion applied)")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    ensure_venv()

    parser = argparse.ArgumentParser(description="Magenta Background Removal Tool")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", help="Output image path (overwrites input if omitted)")

    args = parser.parse_args()
    success = remove_background_magenta(args.input, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
