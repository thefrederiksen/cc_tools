# trisight

TriSight detection pipeline: 3-tier element detection for Windows desktop automation (UI Automation + OCR + Pixel Analysis).

**Requirements:**
- `trisight.exe` must be in PATH
- Windows only

---

## Quick Reference

```bash
# Full detection on a window
trisight detect --window "Notepad" --screenshot screen.png

# UI Automation only
trisight uia --window "Notepad"

# OCR text detection
trisight ocr --screenshot screen.png

# Annotate screenshot with element labels
trisight detect --window "Notepad" --screenshot screen.png --annotate --output annotated.png
```

---

## Detection Tiers

| Tier | Method | Detects |
|------|--------|---------|
| 1 | UI Automation | Native Windows controls, buttons, text boxes |
| 2 | OCR | Text in images, custom UI, non-standard controls |
| 3 | Pixel Analysis | Visual patterns, icons, images |

The `detect` command fuses results from all tiers for comprehensive coverage.

---

## Commands

### Full Detection (detect)

```bash
# Basic detection
trisight detect --window "Notepad" --screenshot screen.png

# Select specific tiers
trisight detect --window "Notepad" --screenshot screen.png --tiers uia,ocr

# With annotated output
trisight detect --window "Notepad" --screenshot screen.png --annotate --output annotated.png

# Custom tree depth
trisight detect --window "Notepad" --screenshot screen.png --depth 20
```

Output:
```json
{
  "success": true,
  "windowTitle": "Notepad",
  "elementCount": 45,
  "uiaCount": 30,
  "ocrCount": 10,
  "pixelCount": 5,
  "detectionTimeMs": 250,
  "annotatedScreenshot": "annotated.png",
  "elements": [
    {
      "id": "e1",
      "type": "Button",
      "name": "File",
      "bounds": {"x": 10, "y": 30, "width": 40, "height": 20},
      "center": {"x": 30, "y": 40},
      "automationId": "FileMenu",
      "isEnabled": true,
      "isInteractable": true,
      "sources": "Uia",
      "confidence": 1.0
    }
  ]
}
```

### UI Automation Only (uia)

```bash
# Get UI Automation element tree
trisight uia --window "Notepad"

# Custom depth
trisight uia --window "Notepad" --depth 10
```

### OCR Only (ocr)

```bash
# Detect text regions in screenshot
trisight ocr --screenshot screen.png
```

Output:
```json
{
  "success": true,
  "count": 15,
  "regions": [
    {
      "text": "File",
      "bounds": {"x": 10, "y": 30, "width": 30, "height": 15},
      "confidence": 0.95
    }
  ]
}
```

### Annotate Screenshot (annotate)

```bash
# Annotate with auto-detection
trisight annotate --screenshot screen.png --window "Notepad" --output annotated.png

# Annotate with pre-computed elements
trisight annotate --screenshot screen.png --elements elements.json --output annotated.png
```

---

## Options

| Command | Option | Description |
|---------|--------|-------------|
| detect | `--window, -w` | Window title (required) |
| detect | `--screenshot, -s` | Screenshot path |
| detect | `--tiers` | Tiers: uia,ocr,pixel |
| detect | `--annotate` | Generate annotated screenshot |
| detect | `--output, -o` | Annotated output path |
| detect | `--depth, -d` | UIA tree depth (default: 15) |
| uia | `--window, -w` | Window title (required) |
| uia | `--depth, -d` | Tree depth (default: 15) |
| ocr | `--screenshot, -s` | Screenshot path (required) |
| annotate | `--screenshot, -s` | Screenshot path (required) |
| annotate | `--window, -w` | Window for auto-detect |
| annotate | `--elements, -e` | Pre-computed elements JSON |
| annotate | `--output, -o` | Output path |

---

## Element Properties

Each detected element includes:

| Property | Description |
|----------|-------------|
| `id` | Unique element ID (e1, e2, ...) |
| `type` | Control type (Button, TextBox, etc.) |
| `name` | Display text or label |
| `bounds` | Rectangle {x, y, width, height} |
| `center` | Center point {x, y} |
| `automationId` | UI Automation ID |
| `isEnabled` | Whether enabled |
| `isInteractable` | Whether clickable |
| `sources` | Detection tier(s) |
| `confidence` | Detection confidence (0-1) |

---

## Examples

### Comprehensive Window Analysis

```bash
# 1. Take screenshot
# 2. Run full detection with annotation
trisight detect --window "Calculator" \
  --screenshot calc.png \
  --annotate \
  --output calc_annotated.png
```

Output includes:
- JSON with all detected elements
- Annotated screenshot with numbered labels

### Quick UI Tree Exploration

```bash
trisight uia --window "Notepad" --depth 5
```

### Extract Text from Screenshot

```bash
trisight ocr --screenshot screenshot.png
```

### Create Labeled Screenshot

```bash
trisight annotate \
  --screenshot app.png \
  --window "MyApp" \
  --output labeled.png
```

---

## Use with cc-click

```bash
# 1. Detect all elements
trisight detect --window "App" --screenshot app.png > elements.json

# 2. Find target element ID from JSON

# 3. Use cc-click to interact
cc-click click --window "App" --name "Submit"
```

---

## LLM Use Cases

1. **UI exploration** - "What elements are in this window?"
2. **Screenshot analysis** - "Label all the buttons in this screenshot"
3. **Accessibility testing** - "Check what controls are available"
4. **Automation planning** - "Find the element I need to click"
5. **OCR extraction** - "Extract all text from this screenshot"
