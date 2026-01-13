#!/usr/bin/env python3
"""
Nano Banana Image Generation Script
Generates images using Google Gemini's image generation models.
"""

import argparse
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
        subprocess.check_call([str(venv_python), "-m", "pip", "install", "-q", "google-genai", "pillow"])
        print("Setup complete")

    if sys.executable != str(venv_python):
        os.execv(str(venv_python), [str(venv_python)] + sys.argv)


def load_reference_image(image_path: str):
    """Load reference image"""
    from PIL import Image

    path = Path(image_path)
    if not path.exists():
        print(f"Error: Reference image not found: {image_path}")
        sys.exit(1)

    print(f"Reference image: {path.absolute()}")
    return Image.open(path)


def generate_image(
    prompt: str,
    output_path: str = "generated_image.png",
    aspect_ratio: str = "1:1",
    model_type: str = "pro",
    magenta_bg: bool = False,
    reference_image: str = None
) -> str:
    """Generate image using Gemini API"""
    from google import genai

    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Environment variable GEMINI_API_KEY is not set")
        sys.exit(1)

    # Optimize prompt for magenta background
    if magenta_bg:
        bg_instruction = (
            "BACKGROUND: solid flat uniform magenta pink (#FF00FF) color only. "
            "NO borders, NO outlines, NO frames, NO shadows, NO gradients. "
            "Subject has natural colors, floating directly on pure magenta background."
        )
        final_prompt = f"{prompt}. {bg_instruction}"
    else:
        final_prompt = prompt

    # Initialize client
    client = genai.Client(api_key=api_key)

    # Model selection
    model_ids = {
        "flash": "gemini-2.5-flash-image",
        "pro": "gemini-3-pro-image-preview"
    }
    model_id = model_ids.get(model_type, model_ids["pro"])

    print(f"Model: {model_id}")
    print(f"Prompt: {final_prompt[:100]}...")
    if magenta_bg:
        print("Option: Magenta background")
    if reference_image:
        print("Option: Reference image provided")
    print("Generating...")

    # Build content
    if reference_image:
        ref_img = load_reference_image(reference_image)
        contents = [final_prompt, ref_img]
    else:
        contents = final_prompt

    # Generate image
    response = client.models.generate_content(
        model=model_id,
        contents=contents,
    )

    # Save image
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    for part in response.parts:
        if part.inline_data is not None:
            image = part.as_image()
            image.save(output_file)
            print(f"Saved: {output_file.absolute()}")
            return str(output_file.absolute())

    if hasattr(response, 'text') and response.text:
        print(f"Response: {response.text}")

    print("Warning: No image was generated")
    return ""


def main():
    ensure_venv()

    parser = argparse.ArgumentParser(
        description="Nano Banana Image Generation (Google Gemini)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate.py "cute cat illustration"
  python generate.py "sunset landscape" -a 16:9 -o sunset.png
  python generate.py "icon" --magenta-bg -o icon.png
  python generate.py "draw a dog in same style" -r reference.png
        """
    )
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", default="generated_image.png", help="Output file path")
    parser.add_argument("-a", "--aspect-ratio", default="1:1", choices=["1:1", "16:9", "9:16", "4:3", "3:4"], help="Aspect ratio")
    parser.add_argument("-m", "--model", default="pro", choices=["flash", "pro"], help="Model: flash=fast, pro=high quality")
    parser.add_argument("--magenta-bg", action="store_true", help="Generate with magenta background (can be made transparent with remove-bg-magenta.py)")
    parser.add_argument("-r", "--reference", default=None, help="Reference image path")

    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        output_path=args.output,
        aspect_ratio=args.aspect_ratio,
        model_type=args.model,
        magenta_bg=args.magenta_bg,
        reference_image=args.reference
    )


if __name__ == "__main__":
    main()
