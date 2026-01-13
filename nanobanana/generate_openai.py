#!/usr/bin/env python3
"""
OpenAI GPT Image Generation Script
Generates and edits images using OpenAI's gpt-image-1 / gpt-image-1.5 models.
"""

import argparse
import base64
import os
import sys
import subprocess
from pathlib import Path

VENV_DIR = Path(__file__).parent / ".venv"


def ensure_venv():
    """Create and activate virtual environment"""
    venv_python = VENV_DIR / "bin" / "python"

    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
        subprocess.check_call([str(venv_python), "-m", "pip", "install", "-q", "openai", "pillow"])
        print("Setup complete")
    else:
        # Check if openai is installed
        result = subprocess.run(
            [str(venv_python), "-c", "import openai"],
            capture_output=True
        )
        if result.returncode != 0:
            print("Installing openai package...")
            subprocess.check_call([str(venv_python), "-m", "pip", "install", "-q", "openai"])

    if sys.executable != str(venv_python):
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)


def load_image_as_base64(image_path: str) -> str:
    """Load image and return as base64 encoded string"""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)

    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_image(
    prompt: str,
    output_path: str = "generated_image.png",
    size: str = "1024x1024",
    model: str = "gpt-image-1",
    quality: str = "medium",
    background: str = "auto",
    output_format: str = "png",
    reference_image: str = None,
    n: int = 1
) -> str:
    """Generate image using OpenAI API"""
    from openai import OpenAI

    # Check API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: Environment variable OPENAI_API_KEY is not set")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print(f"Model: {model}")
    print(f"Prompt: {prompt[:100]}...")
    print(f"Size: {size}, Quality: {quality}, Background: {background}")
    if reference_image:
        print(f"Reference image: {reference_image}")
    print("Generating...")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if reference_image:
        # Image edit mode
        with open(reference_image, "rb") as f:
            response = client.images.edit(
                model=model,
                image=f,
                prompt=prompt,
                size=size,
            )
    else:
        # New generation mode
        response = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            background=background,
            output_format=output_format,
            n=n,
        )

    # Save images
    if response.data:
        for i, image_data in enumerate(response.data):
            if n > 1:
                # Add number suffix for multiple images
                stem = output_file.stem
                suffix = output_file.suffix
                save_path = output_file.parent / f"{stem}_{i+1:02d}{suffix}"
            else:
                save_path = output_file

            if hasattr(image_data, 'b64_json') and image_data.b64_json:
                image_bytes = base64.b64decode(image_data.b64_json)
                with open(save_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Saved: {save_path.absolute()}")
            elif hasattr(image_data, 'url') and image_data.url:
                # Download from URL
                import urllib.request
                urllib.request.urlretrieve(image_data.url, save_path)
                print(f"Saved: {save_path.absolute()}")

        return str(output_file.absolute())

    print("Warning: No image was generated")
    return ""


def main():
    ensure_venv()

    parser = argparse.ArgumentParser(
        description="OpenAI GPT Image Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_openai.py "cute cat illustration"
  python generate_openai.py "sunset landscape" -s 1536x1024 -o sunset.png
  python generate_openai.py "icon" --background transparent -o icon.png
  python generate_openai.py "edit this image" -r input.png -o edited.png

Models:
  gpt-image-1      Standard model
  gpt-image-1-mini Lightweight, fast
  gpt-image-1.5    Latest, highest quality (recommended)

Sizes:
  1024x1024  Square
  1536x1024  Landscape
  1024x1536  Portrait
  auto       Automatic

Quality:
  low     Low quality, fast
  medium  Standard (default)
  high    High quality
        """
    )
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", default="generated_image.png", help="Output file path")
    parser.add_argument("-s", "--size", default="1024x1024",
                        choices=["1024x1024", "1536x1024", "1024x1536", "auto"],
                        help="Image size")
    parser.add_argument("-m", "--model", default="gpt-image-1.5",
                        choices=["gpt-image-1", "gpt-image-1-mini", "gpt-image-1.5"],
                        help="Model")
    parser.add_argument("-q", "--quality", default="medium",
                        choices=["low", "medium", "high"],
                        help="Quality")
    parser.add_argument("-b", "--background", default="auto",
                        choices=["transparent", "opaque", "auto"],
                        help="Background (transparent=transparent)")
    parser.add_argument("-f", "--format", default="png",
                        choices=["png", "jpeg", "webp"],
                        help="Output format")
    parser.add_argument("-r", "--reference", default=None,
                        help="Reference/edit image path")
    parser.add_argument("-n", "--number", type=int, default=1,
                        choices=range(1, 11),
                        help="Number of images to generate (1-10)")

    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        output_path=args.output,
        size=args.size,
        model=args.model,
        quality=args.quality,
        background=args.background,
        output_format=args.format,
        reference_image=args.reference,
        n=args.number
    )


if __name__ == "__main__":
    main()
