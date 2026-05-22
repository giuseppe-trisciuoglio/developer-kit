# Context Rot Prevention

Detailed scenarios and recovery protocols for maintaining Constitution relevance.

---

## What is Context Rot?

**Context rot** is the degradation of long conversations where:
1. Early decisions get buried deep in conversation context
2. Agents forget architectural constraints over time
3. Specifications drift from original principles
4. Team knowledge becomes implicit, not documented
5. Different agents have inconsistent understanding

---

## Why File-Based Constitution?

| Approach | Context Rot | Reliability | Team Visibility |
|----------|-------------|-------------|-----------------|
| **File-based** (ours) | Immune | Always current | Shared across team |
| Context-based | Degrades over time | May be incomplete | Single-user |
| Session memory | Degrades | Depends on model | Not shared |

---

## Session Start Checklist

At the beginning of EVERY session:

```
[ ] Read `docs/specs/architecture.md`
[ ] Read `docs/specs/ontology.md`
[ ] Check if Constitution has been updated since last session
[ ] Validate current work against Constitution
[ ] Flag any deviations in decision-log
```

---

## Warning Signs of Context Rot

If you notice these, re-read the Constitution immediately:

- "I assumed we use X but I see Y in the code"
- "I thought we had A but it's not in the codebase"
- "The spec says B but it doesn't match reality"
- Decisions contradicting previous conversations
- "This was decided earlier but I can't find it in context"

---

## Recovery Protocol

When context rot is detected:

1. **Stop**: Don't continue implementation
2. **Read**: `cat docs/specs/architecture.md` and `docs/specs/ontology.md`
3. **Compare**: Match current state against Constitution
4. **Fix**: Update decision-log if deviations exist
5. **Resume**: Continue with correct context

---

## Detailed Scenarios

### Scenario 1: Long Implementation Session

```
Day 1: Constitution created
Day 5: Brainstorm generates spec
Day 10: Implementation starts
Day 15: Context is fading...

→ At Day 15, re-read Constitution before continuing
→ Validate current work against architecture
→ Fix any drift before it compounds
```

### Scenario 2: Returning After Break

```
Week 1: Feature development started
Week 3: Other work on different features

→ Return to original feature → Re-read Constitution first
→ Match current state vs Constitution
→ Resume with correct context, not memory
```

### Scenario 3: Handoff to Different Agent

```
Agent A: Created Constitution, started work
Agent B: Taking over the feature

→ Agent B reads Constitution files first
→ Understands architecture from files, not memory
→ Continues with consistent context
```

### Scenario 4: Multi-Agent Environment

```
[Agent 1] → Works on Feature A
[Agent 2] → Works on Feature B

→ Both agents read Constitution at session start
→ Both validate against same architecture
→ Consistent decisions across features
```

---

## File Freshness Evaluation

When running `constitution check`, evaluate target file age:

| Age of Target File | Risk | Action |
|--------------------|------|--------|
| < 7 days | LOW | Proceed normally |
| 7-30 days | MEDIUM | Warn user, check for updates |
| > 30 days | HIGH | Suggest review/update, context rot likely |

**Context Rot Warning Template**:

```markdown
> ⚠️ **Context Rot Warning**: This file has not been updated in 30+ days.
> Context rot may have occurred — architectural decisions may have drifted.
> Consider running `specs.sync` or updating the spec before continuing.
```

---

## Recovery Actions (High Context Rot Risk)

1. Read current Constitution files (`docs/specs/architecture.md`, `docs/specs/ontology.md`)
2. Compare spec vs Constitution
3. Identify drifts
4. Update spec or Constitution
5. Document deviations in decision-log

---

## Prevention Strategies

1. **Short sessions**: Keep sessions focused, not sprawling
2. **Reference files**: Always point to file locations, not conversation context
3. **Update constitution**: When architecture changes, update the files
4. **Archive specs**: Completed specs go to `archived/`, not kept active forever
5. **Decision log**: Track architectural decisions in ADR format