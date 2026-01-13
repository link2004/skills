#!/usr/bin/env python3
"""
Vision API Background Removal Tool (macOS)
Removes background using macOS Vision API.
Requires macOS 14.0 or later.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def remove_background_vision(image_path: str, output_path: str = None) -> bool:
    """Remove background using Vision API"""
    script_dir = Path(__file__).parent
    swift_script = script_dir / "remove-bg.swift"
    output = output_path or image_path

    print(f"Input: {image_path}")
    print("Removing background (Vision API)...")

    if not swift_script.exists():
        print(f"Error: {swift_script} not found")
        return False

    try:
        result = subprocess.run(
            ["swift", str(swift_script), image_path, output],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Output: {output}")
            print("Background removal complete (Vision API)")
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Vision API Background Removal Tool (macOS 14.0+)")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("-o", "--output", help="Output image path (overwrites input if omitted)")

    args = parser.parse_args()
    success = remove_background_vision(args.input, args.output)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
