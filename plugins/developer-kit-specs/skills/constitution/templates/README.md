# Constitution Template Fallback

This directory contains a local copy of the canonical architecture template from `plugins/developer-kit-specs/templates/architecture.md`.

It is used as a fallback when the skill is installed in a coding agent that packages templates inside the skill folder instead of exposing `${CLAUDE_PLUGIN_ROOT}/templates/...`.

Lookup order used by `skills/constitution/SKILL.md`:
1. `${CLAUDE_PLUGIN_ROOT}/templates/architecture.md`
2. `templates/architecture.md` inside the installed standalone skill folder
