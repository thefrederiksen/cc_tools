# cc-powerpoint

Convert Markdown to PowerPoint presentations with built-in themes.

## Commands

```bash
# Convert to PPTX
cc-powerpoint slides.md -o presentation.pptx

# Use a theme
cc-powerpoint slides.md -o deck.pptx --theme boardroom

# Default output (same name, .pptx extension)
cc-powerpoint slides.md

# List themes
cc-powerpoint --themes
```

## Slide Syntax

- `---` separates slides
- First slide with `# Title` and optional `## Subtitle` becomes title slide
- Subsequent slides auto-detect layout from content (bullets, tables, code, images)
- Speaker notes use blockquotes (`> note text`) at end of slide

## Themes

boardroom, paper (default), terminal, spark, thesis, obsidian, blueprint

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output .pptx file path | input name + .pptx |
| `--theme` | Theme name | paper |
