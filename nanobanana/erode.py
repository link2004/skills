#!/usr/bin/env python3
"""
Transparent Image Edge Erosion Tool
Erodes edges of transparent images by specified pixels.
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


def erode_image(image_path: str, output_path: str = None, iterations: int = 1) -> bool:
    """Erode edges of transparent image"""
    from PIL import Image
    import numpy as np
    from scipy.ndimage import binary_erosion

    output = output_path or image_path
    print(f"Input: {image_path}")
    print(f"Erosion: {iterations}px")

    try:
        img = Image.open(image_path).convert("RGBA")
        data = np.array(img)

        alpha = data[:, :, 3]
        alpha_mask = alpha > 0
        eroded_mask = binary_erosion(alpha_mask, iterations=iterations)
        data[~eroded_mask] = [0, 0, 0, 0]

        result = Image.fromarray(data, 'RGBA')
        result.save(output, "PNG")
        print(f"Output: {output}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    ensure_venv()

    parser = argparse.ArgumentParser(description="Transparent Image Edge Erosion Tool")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", help="Output image path (overwrites input if omitted)")
    parser.add_argument("-i", "--iterations", type=int, default=1, help="Erosion amount in pixels (default: 1)")

    args = parser.parse_args()
    success = erode_image(args.input, args.output, args.iterations)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
