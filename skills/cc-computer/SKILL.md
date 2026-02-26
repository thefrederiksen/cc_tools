# cc-computer

AI desktop automation agent. Give natural language instructions and it controls Windows applications autonomously.

## Commands

```bash
# Single task (CLI)
cc-computer --cli "Open Notepad and type Hello World"

# Interactive REPL
cc-computer --cli

# GUI mode
cc-computer
```

## How It Works

Screenshot-in-the-loop: takes screenshot -> detects UI elements -> LLM decides action -> executes -> verifies result -> repeats until done.

## Configuration

Set `OPENAI_API_KEY` environment variable or configure in `appsettings.json`.

## Dependencies

- cc-click (UI automation actions)
- cc-trisight (element detection)
- OPENAI_API_KEY
- Windows, .NET 10.0
