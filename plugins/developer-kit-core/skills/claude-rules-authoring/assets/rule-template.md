---
# Frontmatter is OPTIONAL — keep it only for policy/safety rules that must
# always be loaded. Delete this whole block for ordinary convention/pattern rules.
description: One-line summary of the rule
globs: "**/*"        # path glob(s) the rule applies to
alwaysApply: true    # true = always loaded; omit/false = context-triggered
priority: 00         # optional explicit ordering hint
---

# <Title: state the rule, not a vague topic>

<!--
Pick ONE section set below for the rule's shape, then delete the others.
-->

<!-- ========== SHAPE A: Policy / safety rule ========== -->
## Rule

- <Imperative, unambiguous statement of what must / must not be done.>

## Rationale

<Why this matters — the constraint or risk it guards against.>

## Exceptions

- <The narrow cases where the rule does not apply, or "None.">

<!-- ========== SHAPE B: Convention rule ========== -->
## Configuration

- <Concrete settings, with the real config file referenced.>

## Conventions

- <Naming, typing, organization rules. Use ✅ / ❌ for do vs don't.>
- ❌ `<anti-pattern>` → ✅ `<preferred>`
- <Flag dead patterns: "`X` no longer exists — use `Y`.">

<!-- ========== SHAPE C: Pattern / guide rule ========== -->
## Overview

<What this pattern is and when it applies.>

```
src/lib/
  <directory tree showing the canonical structure>
```

## Procedure

1. <Step, referencing real symbols / import aliases.>
2. <Step.>

```ts
// Worked example using exact names from the codebase.
```

<!-- ========== Always close with ========== -->
> Related: see `NN-other-rule.md`.
