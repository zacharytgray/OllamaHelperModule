# Ollama Helper Module

Minimal agent wrapper around a local Ollama model with optional tool support.

## Features
- Conversation memory
- Optional tool binding (enable/disable via `use_tools` flag)
- Example calculator tool

## Usage
```python
from ollamaAgentModule import Agent

agent = Agent(modelName="gpt-oss:20b", instructionsFilepath="systemInstructions.txt", use_tools=False)
# When use_tools=False the model will not be bound to any tools even if they exist.
```

In the interactive chat (`chat.py`), update initialization if you want to enable tools:
```python
agent = Agent(modelName=model_name, instructionsFilepath=instructions_filepath, use_tools=True)
```

## Adding Custom Tools
Add tool functions decorated with `@tool` to `ollamaTools.py` and enable with `use_tools=True`.

## Calculator Tool
Provided example tool: `calculator(expression: str)` handles only very simple expressions in the form:

```
<number> <op> <number>
```

Supported operators: `+ - * /`

Examples: `2 + 2`, `7 * 3`, `10 / 4`.

If the format is different (parentheses, multiple operators, powers) it will return an error. This is intentional to keep the demo minimal.
