# cc-image

Unified image toolkit: generate, analyze, OCR, resize, and convert images.

**Requirements:**
- `cc-image.exe` must be in PATH
- OpenAI API key: set `OPENAI_API_KEY` (for generation, description, OCR)

---

## Quick Reference

```bash
# Generate image with DALL-E
cc-image generate "a sunset over mountains" -o sunset.png

# Describe an image
cc-image describe photo.jpg

# Extract text (OCR)
cc-image ocr document.png

# Get image info
cc-image info photo.jpg

# Resize image
cc-image resize photo.jpg -o thumbnail.jpg --width 300

# Convert format
cc-image convert photo.png -o photo.jpg
```

---

## Commands

### Generate (DALL-E)

```bash
# Generate image from prompt
cc-image generate "a cat wearing sunglasses" -o cat.png

# Different sizes
cc-image generate "prompt" -o out.png --size 1024x1024    # Square
cc-image generate "prompt" -o out.png --size 1024x1792    # Portrait
cc-image generate "prompt" -o out.png --size 1792x1024    # Landscape

# HD quality
cc-image generate "prompt" -o out.png --quality hd
```

### Describe (GPT-4 Vision)

```bash
# Get AI description of image
cc-image describe photo.jpg

# Analyze screenshot
cc-image describe screenshot.png
```

### OCR (Text Extraction)

```bash
# Extract text from image
cc-image ocr document.png

# Extract from screenshot
cc-image ocr screenshot.png
```

### Info

```bash
# Show image metadata
cc-image info photo.jpg
```

Output:
```
+------------+---------------+
| Property   | Value         |
+------------+---------------+
| Dimensions | 1920 x 1080   |
| Format     | JPEG          |
| Mode       | RGB           |
| Size       | 245.3 KB      |
+------------+---------------+
```

### Resize

```bash
# Resize by width (maintains aspect ratio)
cc-image resize photo.jpg -o thumb.jpg --width 300

# Resize by height
cc-image resize photo.jpg -o thumb.jpg --height 200

# Custom quality (1-100)
cc-image resize photo.jpg -o thumb.jpg --width 300 --quality 85
```

### Convert

```bash
# Convert PNG to JPEG
cc-image convert photo.png -o photo.jpg

# Convert with quality
cc-image convert photo.png -o photo.jpg --quality 90
```

---

## Options

| Command | Option | Description |
|---------|--------|-------------|
| generate | `-o, --output` | Output path (required) |
| generate | `-s, --size` | Size: 1024x1024, 1024x1792, 1792x1024 |
| generate | `-q, --quality` | Quality: standard, hd |
| resize | `-o, --output` | Output path (required) |
| resize | `-w, --width` | Target width |
| resize | `-h, --height` | Target height |
| resize | `-q, --quality` | JPEG quality 1-100 |
| convert | `-o, --output` | Output path (required) |
| convert | `-q, --quality` | JPEG quality 1-100 |

---

## Supported Formats

| Operation | Input | Output |
|-----------|-------|--------|
| Generate | - | PNG |
| Describe | JPEG, PNG, GIF, WebP | - |
| OCR | JPEG, PNG, GIF, WebP | - |
| Resize | JPEG, PNG, GIF, WebP | JPEG, PNG |
| Convert | JPEG, PNG, GIF, WebP, BMP | JPEG, PNG, GIF, WebP |

---

## Examples

### Generate Image for Documentation

```bash
cc-image generate "a modern software architecture diagram with microservices" -o architecture.png --size 1792x1024
```

### Extract Text from Screenshot

```bash
cc-image ocr error_message.png
```

Output:
```
Error: Connection refused
Please check your network settings and try again.
```

### Analyze a Diagram

```bash
cc-image describe flowchart.png
```

Output:
```
This is a flowchart showing a user authentication process. It starts with
a login form, branches on credential validation, and ends with either a
success redirect or an error message display.
```

### Create Thumbnails

```bash
cc-image resize product.jpg -o product_thumb.jpg --width 150 --quality 85
```

### Batch Convert

```bash
for file in *.png; do
  cc-image convert "$file" -o "${file%.png}.jpg"
done
```

---

## LLM Use Cases

1. **Image generation** - "Create an image of a cozy cabin in the woods"
2. **Document OCR** - "Extract the text from this screenshot"
3. **Image analysis** - "What does this diagram show?"
4. **Thumbnail creation** - "Resize these images for web thumbnails"
5. **Format conversion** - "Convert these PNGs to JPEGs"
