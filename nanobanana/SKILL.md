---
name: nanobanana
description: Generate and edit images using Google Gemini or OpenAI GPT Image models. Automatically used for requests like "generate an image", "create an illustration", "edit this image". Also supports sticker sheet generation and splitting for requests like "create some stickers" or "generate multiple icons and split them". Choose between Gemini (Nano Banana) and OpenAI (gpt-image-1.5) providers.
allowed-tools: Bash, Read, Write, AskUserQuestion
---

# Nano Banana Image Generation Skill

Generate and edit images using Google Gemini or OpenAI GPT Image.

---

## Referencing Pasted Images

When images are pasted into Claude Code, they are cached at `~/.claude/image-cache/`. Copy from this cache to tmp and use as reference image.

### How to Get Image Path (Recommended)

**Important**: When an image is pasted, always save it to tmp before using.

1. User pastes an image
2. Check the image-cache path from `Additional working directories` in environment info
   - Example: `/Users/username/.claude/image-cache/0353f5a1-9885-4743-a956-d2d195b445d4`
3. Copy the image file from that directory to tmp
4. Pass the tmp path to the `-r` option

### Command to Save Image to tmp

```bash
# 1. Check image-cache path (from Additional working directories in environment info)
# Example: /Users/username/.claude/image-cache/0353f5a1-9885-4743-a956-d2d195b445d4

# 2. Check images in cache
ls ~/.claude/image-cache/<session-id>/

# 3. Copy to tmp
cp ~/.claude/image-cache/<session-id>/*.png /tmp/reference_image.png

# 4. Use as reference image
python3 ~/.claude/skills/nanobanana/generate.py "Same style. Object: cat" \
  -r "/tmp/reference_image.png" -o cat.png
```

### Example: Generate Using Pasted Image as Reference

```bash
# 1. Copy latest image from image-cache to tmp
cp ~/.claude/image-cache/0353f5a1-9885-4743-a956-d2d195b445d4/3.png /tmp/reference_image.png

# 2. Gemini: Copy reference image style
python3 ~/.claude/skills/nanobanana/generate.py "Same style. Object: cat" \
  -r "/tmp/reference_image.png" -o cat.png

# 3. OpenAI: Edit reference image
python3 ~/.claude/skills/nanobanana/generate_openai.py "Change background to night sky" \
  -r "/tmp/reference_image.png" -o edited.png
```

### Legacy Method (When Path is in Metadata)

If image metadata contains `[Image: source: /path/to/image.png]`, use that path directly.

```bash
python3 ~/.claude/skills/nanobanana/generate.py "Same style. Object: cat" \
  -r "/Users/user/Desktop/reference.png" -o cat.png
```

**Note**: Always wrap paths containing spaces in double quotes.

---

## Pre-generation Confirmation Flow

**Important**: Before starting image generation, always confirm the following using the `AskUserQuestion` tool.

### Confirmation Items

**Common (Always Confirm):**
| Item | Options | Description |
|------|---------|-------------|
| **Provider** | `gemini` / `openai` | gemini=Nano Banana, openai=GPT Image |
| **Model** | Gemini: `pro`/`flash`, OpenAI: `1.5`/`1`/`mini` | See details below |
| **Reference Image** | Yes / No | Whether there's a source image to copy style from (pasted images can be used) |
| **Background Removal** | Vision API / Magenta removal / OpenAI transparent / Not needed | See methods below |

**Additional for Multiple Image Generation:**
| Item | Options | Description |
|------|---------|-------------|
| **Generation Method** | Sheet→split / Parallel generation | Sheet→split recommended (efficient) |

### Provider Characteristics

| Provider | Strengths | API Key Environment Variable |
|----------|-----------|------------------------------|
| **Gemini** | Japanese prompts, reference image style copying | `GEMINI_API_KEY` |
| **OpenAI** | High quality, native transparent background, multiple simultaneous generation | `OPENAI_API_KEY` |

### Model Comparison

**Gemini:**
| Model | ID | Features |
|-------|-----|----------|
| Flash | `gemini-2.5-flash-image` | Fast, cost-efficient |
| Pro | `gemini-3-pro-image-preview` | High quality, handles complex instructions |

**OpenAI:**
| Model | ID | Features |
|-------|-----|----------|
| GPT Image 1.5 | `gpt-image-1.5` | Latest & highest quality (recommended) |
| GPT Image 1 | `gpt-image-1` | Standard model |
| GPT Image Mini | `gpt-image-1-mini` | Lightweight, fast, low cost |

### Background Removal Method Selection

| Method | Best For | Provider |
|--------|----------|----------|
| **OpenAI Transparent** | Use `--background transparent` for direct transparent generation with OpenAI | OpenAI only |
| **Vision API** | Real photos, photo-style, complex backgrounds, gradient backgrounds | Gemini |
| **Magenta Removal** | Illustrations, simple shapes, line art, flat design | Gemini |

### Recommended Settings

| Case | Provider | Model | Background Removal |
|------|----------|-------|-------------------|
| Transparent icons/stickers | OpenAI | 1.5 | `--background transparent` |
| Reference image style copy | Gemini | pro | Vision API |
| Simple illustrations | Gemini | flash | Magenta removal |
| High quality illustrations | OpenAI | 1.5 | None or transparent |
| Prototype/testing | OpenAI | mini | None |

---

## Tool List

| Tool | Description |
|------|-------------|
| `generate.py` | Gemini image generation |
| `generate_openai.py` | OpenAI image generation |
| `remove-bg-magenta.py` | Magenta background removal (includes 1px erosion) |
| `remove-bg-vision.py` | Vision API background removal |
| `erode.py` | Transparent image edge erosion |
| `split_transparent.py` | Split transparent image into individual objects |

## Prerequisites

1. **For Gemini**: Set environment variable `GEMINI_API_KEY`
2. **For OpenAI**: Set environment variable `OPENAI_API_KEY`
3. **Vision API**: Requires macOS 14.0 (Sonoma) or later

---

## 1. generate.py - Gemini Image Generation

```bash
python3 ~/.claude/skills/nanobanana/generate.py "prompt" [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o`, `--output` | Output file path | `generated_image.png` |
| `-a`, `--aspect-ratio` | Aspect ratio (`1:1`, `16:9`, `9:16`, `4:3`, `3:4`) | `1:1` |
| `-m`, `--model` | Model (`flash`, `pro`) | `pro` |
| `--magenta-bg` | Generate with magenta background | None |
| `-r`, `--reference` | Reference image path | None |

### Examples

```bash
# Simple generation
python3 ~/.claude/skills/nanobanana/generate.py "cute cat illustration"

# Copy reference image style
python3 ~/.claude/skills/nanobanana/generate.py "Same exact style as this image. Object: coffee cup. NO text." -r reference.png -o coffee.png

# Generate with magenta background (for later transparency processing)
python3 ~/.claude/skills/nanobanana/generate.py "simple star icon" --magenta-bg -o star.png
```

---

## 2. generate_openai.py - OpenAI Image Generation

```bash
python3 ~/.claude/skills/nanobanana/generate_openai.py "prompt" [options]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o`, `--output` | Output file path | `generated_image.png` |
| `-s`, `--size` | Size (`1024x1024`, `1536x1024`, `1024x1536`, `auto`) | `1024x1024` |
| `-m`, `--model` | Model (`gpt-image-1`, `gpt-image-1-mini`, `gpt-image-1.5`) | `gpt-image-1.5` |
| `-q`, `--quality` | Quality (`low`, `medium`, `high`) | `medium` |
| `-b`, `--background` | Background (`transparent`, `opaque`, `auto`) | `auto` |
| `-f`, `--format` | Output format (`png`, `jpeg`, `webp`) | `png` |
| `-r`, `--reference` | Image path to edit | None |
| `-n`, `--number` | Number of images to generate (1-10) | `1` |

### Examples

```bash
# Simple generation
python3 ~/.claude/skills/nanobanana/generate_openai.py "cute cat illustration"

# Generate with transparent background (no background removal needed)
python3 ~/.claude/skills/nanobanana/generate_openai.py "simple star icon" -b transparent -o star.png

# High quality, landscape
python3 ~/.claude/skills/nanobanana/generate_openai.py "sunset landscape" -s 1536x1024 -q high -o sunset.png

# Generate multiple simultaneously
python3 ~/.claude/skills/nanobanana/generate_openai.py "cute animal icon, single animal" -n 5 -b transparent -o animals.png

# Image editing
python3 ~/.claude/skills/nanobanana/generate_openai.py "change background to night sky" -r input.png -o edited.png
```

---

## 3. remove-bg-magenta.py - Magenta Background Removal

Remove magenta/pink background using color-based detection.

```bash
python3 ~/.claude/skills/nanobanana/remove-bg-magenta.py input_image [-o output_image]
```

### How it Works
- Makes colors with R>180, G<100, B>100 transparent
- 1px erosion removes pink edge residue

---

## 4. remove-bg-vision.py - Vision API Background Removal

Automatically detect and remove background using macOS Vision API.

```bash
python3 ~/.claude/skills/nanobanana/remove-bg-vision.py input_image [-o output_image]
```

### Features
- Automatic foreground detection
- Best for images maintaining reference image style (including background)
- Requires macOS 14.0 or later

---

## 5. erode.py - Edge Erosion

Erode transparent image edges by specified pixels.

```bash
python3 ~/.claude/skills/nanobanana/erode.py input_image [-o output_image] [-i iterations]
```

| Option | Description | Default |
|--------|-------------|---------|
| `-o`, `--output` | Output image path | Overwrites input |
| `-i`, `--iterations` | Erosion amount (pixels) | `1` |

---

## 6. split_transparent.py - Transparent Image Splitting

Split transparent PNG into individual objects (for sticker sheets).

```bash
python3 ~/.claude/skills/nanobanana/split_transparent.py input_image [output_directory]
```

### How it Works
- Detects boundaries using alpha channel (transparent areas)
- Extracts each connected component
- Numbers from top-left to bottom-right

---

## Workflow Examples

### Generate Using Pasted Image as Reference (Recommended)

When user pastes an image, copy from image-cache to tmp and use as reference.

```bash
# 1. Check image-cache path from Additional working directories in environment info
# Example: /Users/username/.claude/image-cache/0353f5a1-9885-4743-a956-d2d195b445d4

# 2. Copy from image-cache to tmp
cp ~/.claude/image-cache/0353f5a1-9885-4743-a956-d2d195b445d4/*.png /tmp/reference_image.png

# 3. Gemini: Generate different object in same style
python3 ~/.claude/skills/nanobanana/generate.py "Same exact style as this image. Object: coffee cup. NO text." \
  -r "/tmp/reference_image.png" -o coffee.png

# 4. OpenAI: Edit image
python3 ~/.claude/skills/nanobanana/generate_openai.py "change background to outer space" \
  -r "/tmp/reference_image.png" -o space.png
```

### OpenAI: Transparent Icon Generation (Recommended - Simplest)

```bash
# Generate transparent PNG in one step
python3 ~/.claude/skills/nanobanana/generate_openai.py "simple star icon" -b transparent -o star.png
```

### OpenAI: Multiple Icon Simultaneous Generation

```bash
# Generate 5 transparent PNGs simultaneously
python3 ~/.claude/skills/nanobanana/generate_openai.py "cute animal icon, single animal" -n 5 -b transparent -o animal.png
# → animal_01.png, animal_02.png, ... will be generated
```

### Gemini: Transparent Sticker Generation (Simple Objects)

```bash
# 1. Generate with magenta background
python3 ~/.claude/skills/nanobanana/generate.py "simple star icon" --magenta-bg -o star.png

# 2. Remove magenta
python3 ~/.claude/skills/nanobanana/remove-bg-magenta.py star.png
```

### Gemini: Reference Image Style Copy + Transparency

```bash
# 1. Generate with reference image style (no magenta to maintain style)
python3 ~/.claude/skills/nanobanana/generate.py "Same exact style as this image. Object: coffee cup. NO text." -r reference.png -o coffee.png

# 2. Remove background with Vision API
python3 ~/.claude/skills/nanobanana/remove-bg-vision.py coffee.png
```

### Gemini: Sticker Sheet Generation → Split

```bash
# 1. Generate multiple stickers with magenta background
python3 ~/.claude/skills/nanobanana/generate.py \
  "Multiple separate kawaii stickers with LARGE gaps: coffee cup, donut, cat, star. Arranged in 2x2 grid, well separated." \
  --magenta-bg -o sheet.png

# 2. Make background transparent
python3 ~/.claude/skills/nanobanana/remove-bg-magenta.py sheet.png

# 3. Split into individual files
python3 ~/.claude/skills/nanobanana/split_transparent.py sheet.png ./stickers/
```

**Prompt Tips:**
- `LARGE gaps between them` - Wide spacing
- `well separated` - No overlapping
- `Arranged in XxY grid` - Specify grid layout

---

## File Structure

```
~/.claude/skills/nanobanana/
├── SKILL.md               # This document
├── generate.py            # Gemini image generation
├── generate_openai.py     # OpenAI image generation
├── remove-bg-magenta.py   # Magenta background removal (includes 1px erosion)
├── remove-bg-vision.py    # Vision API background removal
├── remove-bg.swift        # Vision API implementation (Swift)
├── erode.py               # Edge erosion (standalone)
└── split_transparent.py   # Transparent image splitting
```
