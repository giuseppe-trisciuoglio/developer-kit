# Copilot CLI Command Reference (Skill Support)

Minimal reference used by the `copilot-cli` skill.

## Core non-interactive patterns

```bash
# Programmatic prompt execution
copilot -p "<english prompt>"

# Programmatic prompt with explicit model
copilot -p "<english prompt>" --model <model-name>

# Output only assistant response
copilot -p "<english prompt>" --silent
```

## Permission flags

```bash
# Single tool (preferred when possible)
copilot -p "<prompt>" --allow-tool 'shell(git)'

# All tools
copilot -p "<prompt>" --allow-all-tools

# All paths
copilot -p "<prompt>" --allow-all-paths

# All URLs
copilot -p "<prompt>" --allow-all-urls

# Full permissions (highest risk)
copilot -p "<prompt>" --yolo
```

## Session controls

```bash
# Resume a session
copilot --resume <session-id>

# Share session to markdown
copilot -p "<prompt>" --share

# Share session to explicit path
copilot -p "<prompt>" --share ./copilot-session.md
```

## Operational guidance

- Keep prompts in English for consistency and model performance.
- Prefer explicit model selection when reproducibility is important.
- Use least-privilege permission flags; avoid `--yolo` unless explicitly requested.
- Always review output before applying code changes.
