# cc-click

CLI UI automation tool for Windows desktop applications using UI Automation.

**Requirements:**
- `cc-click.exe` must be in PATH
- Windows only (uses UI Automation API)

---

## Quick Reference

```bash
# List visible windows
cc-click list-windows

# List UI elements in a window
cc-click list-elements --window "Notepad"

# Click an element
cc-click click --window "Notepad" --name "File"

# Type text into an element
cc-click type --window "Notepad" --text "Hello World"

# Take screenshot
cc-click screenshot --output screenshot.png

# Read element text
cc-click read-text --window "Notepad" --id "content"
```

---

## Commands

### List Windows

```bash
# List all visible top-level windows
cc-click list-windows

# Filter by title
cc-click list-windows --filter "Notepad"
```

Output:
```json
{
  "windows": [
    {"title": "Untitled - Notepad", "processId": 1234},
    {"title": "Document.txt - Notepad", "processId": 5678}
  ]
}
```

### List Elements

```bash
# List all elements in a window
cc-click list-elements --window "Notepad"

# Filter by control type
cc-click list-elements --window "Notepad" --type Button
cc-click list-elements --window "Notepad" --type TextBox
cc-click list-elements --window "Notepad" --type MenuItem

# Limit tree depth
cc-click list-elements --window "Notepad" --depth 10
```

Output:
```json
{
  "elements": [
    {
      "name": "File",
      "automationId": "FileMenu",
      "controlType": "MenuItem",
      "bounds": {"x": 10, "y": 30, "width": 40, "height": 20}
    }
  ]
}
```

### Click

```bash
# Click by element name (display text)
cc-click click --window "Notepad" --name "File"

# Click by AutomationId
cc-click click --window "Notepad" --id "FileMenu"

# Click at screen coordinates
cc-click click --xy "500,300"
```

### Type

```bash
# Type into focused element
cc-click type --window "Notepad" --text "Hello World"

# Type into specific element
cc-click type --window "Notepad" --id "content" --text "Hello"
cc-click type --window "Notepad" --name "Text Editor" --text "Hello"
```

### Screenshot

```bash
# Screenshot entire screen
cc-click screenshot --output screenshot.png

# Screenshot specific window
cc-click screenshot --window "Notepad" --output notepad.png
```

### Read Text

```bash
# Read text from an element
cc-click read-text --window "Notepad" --id "content"
cc-click read-text --window "Notepad" --name "Text Editor"
```

---

## Options

| Option | Description |
|--------|-------------|
| `--window, -w` | Window title (substring match) |
| `--name` | Element name / display text |
| `--id` | Element AutomationId |
| `--type, -t` | Filter by ControlType |
| `--depth, -d` | Max tree depth (default: 25) |
| `--filter, -f` | Filter windows by title |
| `--xy` | Absolute screen coordinates |
| `--output, -o` | Output file path |
| `--text` | Text to type |

---

## Control Types

Common control types for `--type` filter:
- `Button`
- `TextBox` / `Edit`
- `MenuItem`
- `ListItem`
- `TreeItem`
- `CheckBox`
- `RadioButton`
- `ComboBox`
- `Tab`
- `Window`
- `Pane`

---

## Examples

### Automate Notepad

```bash
# 1. List windows to find Notepad
cc-click list-windows --filter "Notepad"

# 2. Click File menu
cc-click click --window "Notepad" --name "File"

# 3. Click Save As
cc-click click --window "Notepad" --name "Save As"

# 4. Type filename
cc-click type --window "Save As" --id "FileNameControlHost" --text "document.txt"

# 5. Click Save button
cc-click click --window "Save As" --name "Save"
```

### Find All Buttons in an App

```bash
cc-click list-elements --window "Calculator" --type Button
```

### Take App Screenshot

```bash
cc-click screenshot --window "Calculator" --output calc.png
```

### Read Text Content

```bash
cc-click read-text --window "Notepad" --id "RichEditD2DPT"
```

---

## Tips

1. **Window matching** - Uses substring match, so "Note" matches "Notepad"
2. **Element finding** - Try `--name` first (display text), fall back to `--id` (AutomationId)
3. **Explore first** - Use `list-elements` to discover available elements before automating
4. **JSON output** - All output is JSON for easy parsing

---

## LLM Use Cases

1. **Desktop automation** - "Click the Save button in Notepad"
2. **Data entry** - "Type this text into the application"
3. **UI exploration** - "What buttons are in this window?"
4. **Screen capture** - "Take a screenshot of the Calculator app"
5. **Reading data** - "Read the text from this dialog box"
