# cc-docgen

Generate C4 architecture diagrams (context and container) from YAML manifest files.

## Commands

```bash
# Generate diagrams from manifest
cc-docgen generate
cc-docgen generate --manifest ./docs/cencon/architecture_manifest.yaml
cc-docgen generate --output ./docs/cencon/ --format svg

# Validate manifest without generating
cc-docgen validate
cc-docgen validate --manifest ./custom/manifest.yaml

# Version
cc-docgen --version
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--manifest, -m` | Path to architecture_manifest.yaml | `./docs/cencon/architecture_manifest.yaml` |
| `--output, -o` | Output directory | Same as manifest directory |
| `--format, -f` | Output format: png or svg | png |
| `--verbose, -v` | Verbose output | false |

## Output

- `context.png` - System context diagram (C4 Level 1)
- `container.png` - Container diagram (C4 Level 2)

## Requirements

- Graphviz installed and on PATH (`dot -V` to verify)
- Python diagrams library

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Manifest file not found |
| 2 | Invalid YAML syntax |
| 3 | Missing required field |
| 4 | Graphviz not installed |
| 5 | Output directory not writable |
