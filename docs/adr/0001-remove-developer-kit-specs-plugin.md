# ADR 0001: Remove developer-kit-specs plugin

## Status

Accepted — 2026-08-18

## Context

The `developer-kit-specs` plugin defined an internal Specification-Driven Development (SDD) workflow that turned ideas into functional specifications and executable tasks. It lived inside this repository as a first-class plugin, exposing 13 slash commands and 9 skills (brainstorm, spec-to-tasks, task-implementation, task-review, sync, ralph-loop, etc.).

The maintenance model has shifted. The workflow has been migrated to a dedicated external tool, [pi-specs-kit](https://github.com/giuseppe-trisciuoglio/pi-specs-kit), which is a pi coding agent extension running an autonomous spec implementation loop. Going forward, pi is the harness where time and development focus are invested.

## Decision

Remove the `developer-kit-specs` plugin from this repository in full, including:

- The plugin directory `plugins/developer-kit-specs/` (commands, skills, templates, scripts, hooks, docs).
- Historical spec artifacts produced by the plugin (`docs/specs/001-real-e2e-verification/`, `docs/specs/architecture.md`, `docs/specs/ontology.md`, `docs/specs-life-cycle.png`).
- The example template `examples/AGENTS.md` that documented the now-removed workflow.
- The system-wide Ralph-loop orchestrator `scripts/agents_loop.py` and the `install-agents-loop` Makefile target (it depended on the removed plugin's `ralph_loop.py`).
- Configuration and documentation entries across:
  - `.claude-plugin/marketplace.json`
  - `tile.json`
  - `Makefile` (target `install-specs-skills`, `SPECS_PLUGIN_DIR`, help text)
  - `README.md`, `README_IT.md`, `README_ES.md`, `README_CN.md` (entire SDD section, plugin table row, dangling command references)
  - `plugins/developer-kit-core/README.md` (Related Plugins section)
  - `plugins/developer-kit-core/docs/README.md` (cross-link)
  - `plugins/developer-kit-core/docs/installation.md` (plugin row)
  - `plugins/developer-kit-core/commands/devkit.feature-development.md` (3 dangling references, now generic)
- A new `Removed` entry under `CHANGELOG.md` → `[Unreleased]`.

The retained `specs-kit.yaml` at the repository root is the configuration file for the new external pi-specs-kit tool and stays untouched. The `github-spec-kit` plugin is unrelated and stays untouched.

## Consequences

Positive:
- The repository no longer carries a duplicated specs workflow.
- Maintenance burden shifts to a single source of truth (pi-specs-kit).
- The plugin set is reduced from 12 to 11; tile.json skill count drops from 111 to 110.
- Documentation, configuration, and example files no longer reference removed commands.

Negative / Migration notes:
- Users who relied on the `developer-kit-specs` commands (e.g. `/specs:brainstorm`, `/specs:task-implementation`) must install [pi-specs-kit](https://github.com/giuseppe-trisciuoglio/pi-specs-kit) instead.
- Historical changelog entries still mention `developer-kit-specs`; they are intentionally preserved for traceability.
- The `developers-kit-core/devkit.feature-development` command now uses generic specs references instead of pointing at the old plugin.

## Alternatives considered

- Keep the plugin and just deprecate it: rejected. The plugin is fully superseded by the external tool; keeping it would create two parallel sources of truth.
- Rename the plugin to match the new tool's branding: rejected. The new tool lives in a separate repository and has its own release cadence; rebranding here would not unify them.
- Move the plugin to a separate repository: rejected. The plugin is end-of-life and the new tool is the replacement.

## References

- New tool: https://github.com/giuseppe-trisciuoglio/pi-specs-kit
- Local config (kept): `specs-kit.yaml`
- Changelog entry: `CHANGELOG.md` → `[Unreleased]` → `Removed`
