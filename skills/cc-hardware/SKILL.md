# cc-hardware

Query system hardware information: RAM, CPU, GPU, disk, OS, network, battery.

## Commands

```bash
# Show all hardware info
cc-hardware

# Individual components
cc-hardware cpu
cc-hardware ram
cc-hardware gpu
cc-hardware disk
cc-hardware os
cc-hardware network
cc-hardware battery

# JSON output
cc-hardware --json
cc-hardware cpu --json

# Version
cc-hardware --version
```

## Options

| Option | Description |
|--------|-------------|
| `--json, -j` | Output as JSON instead of formatted text |
| `--version, -v` | Show version |

## Notes

- GPU info requires NVIDIA GPU with drivers installed
- Battery info only available on laptops
- No API keys or network access required
