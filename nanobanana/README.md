# Nano Banana - Image Generation Skill

Generate and edit images using Google Gemini or OpenAI GPT Image models. This skill provides tools for image generation, background removal, and image splitting for stickers.

## Features

- **Image Generation**: Create images from text prompts using Gemini or OpenAI
- **Style Transfer**: Copy style from reference images (Gemini)
- **Background Removal**: Multiple methods including Vision API and magenta detection
- **Sticker Sheet Splitting**: Split transparent images into individual objects
- **Transparent PNG Support**: Native transparent background generation with OpenAI

## Requirements

- Python 3.8+
- For Gemini: `GEMINI_API_KEY` environment variable
- For OpenAI: `OPENAI_API_KEY` environment variable
- For Vision API: macOS 14.0 (Sonoma) or later

## Tools

| Tool | Description |
|------|-------------|
| `generate.py` | Gemini image generation |
| `generate_openai.py` | OpenAI image generation |
| `remove-bg-magenta.py` | Magenta background removal (includes 1px erosion) |
| `remove-bg-vision.py` | Vision API background removal (macOS) |
| `erode.py` | Transparent image edge erosion |
| `split_transparent.py` | Split transparent image into individual objects |

## Quick Start

### Generate with Gemini
```bash
python3 generate.py "cute cat illustration" -o cat.png
```

### Generate with OpenAI (Transparent Background)
```bash
python3 generate_openai.py "simple star icon" -b transparent -o star.png
```

### Generate Multiple Images
```bash
python3 generate_openai.py "cute animal icon" -n 5 -b transparent -o animals.png
```

### Style Transfer with Reference Image
```bash
python3 generate.py "Same style. Object: coffee cup" -r reference.png -o coffee.png
```

### Background Removal
```bash
# Using Vision API (best for photos)
python3 remove-bg-vision.py input.png -o output.png

# Using magenta detection (best for illustrations)
python3 remove-bg-magenta.py input.png -o output.png
```

### Split Sticker Sheet
```bash
python3 split_transparent.py sheet.png ./stickers/
```

## Model Comparison

### Gemini Models
| Model | ID | Features |
|-------|-----|----------|
| Flash | `gemini-2.5-flash-image` | Fast, cost-efficient |
| Pro | `gemini-3-pro-image-preview` | High quality, complex instructions |

### OpenAI Models
| Model | ID | Features |
|-------|-----|----------|
| GPT Image 1.5 | `gpt-image-1.5` | Latest & highest quality (recommended) |
| GPT Image 1 | `gpt-image-1` | Standard model |
| GPT Image Mini | `gpt-image-1-mini` | Lightweight, fast, low cost |

## Background Removal Methods

| Method | Best For |
|--------|----------|
| OpenAI Transparent | Direct generation with transparent background |
| Vision API | Photos, complex backgrounds, gradients |
| Magenta Removal | Illustrations, simple shapes, flat design |

## License

MIT
