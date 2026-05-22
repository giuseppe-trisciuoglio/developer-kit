# Project Ontology — Ubiquitous Language

**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD

---

## Domain Glossary

| Term | Definition | Bounded Context |
|------|-----------|-----------------|
| [Term 1] | [Clear, unambiguous definition of the term] | [Context where this term applies] |
| [Term 2] | [Definition] | [Context] |

*Guidelines for definitions:*
- *One sentence if possible*
- *Avoid circular definitions*
- *Include the bounded context where it applies*
- *Distinguish from related but different terms*

## Bounded Contexts

| Context | Description | Key Terms |
|---------|-------------|-----------|
| [Context 1] | [What this context is responsible for] | [Comma-separated key terms] |
| [Context 2] | [Description] | [Key terms] |

## Conceptual Mapping

```
┌────────────────────────────────────────────────────────────┐
│                    [Domain Name]                           │
├────────────────────────────────────────────────────────────┤
│  [Context A] ──────────▶ [Context B]                      │
│       │                      │                             │
│       │   [Relationship type:                         │   │
│       │    upstream/downstream,                       │   │
│       │    conformist, anti-corruption-layer,         │   │
│       │    open-host-service, etc.]                   │   │
│       │                                              │   │
│       └──────────────────▶ [Context C]                 │   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

*Describe relationships between bounded contexts. Focus on integration patterns and data flow.*

## Ubiquitous Language Rules

1. **Consistent terminology**: Same term = same concept throughout
2. **No synonyms for defined terms**: If "User" is defined, don't use "Account" interchangeably
3. **Context matters**: A term may have different meanings in different contexts
4. **Living document**: Add terms as they emerge during brainstorming and implementation

## Anti-Patterns to Avoid

| Anti-Pattern | Example | Correct |
|-------------|---------|---------|
| Synonyms | Calling same entity "User" in one place and "Account" in another | Pick one term, use everywhere |
| Ambiguous terms | "Order" could mean order request, order entity, or order record | Specify: "OrderRequest", "OrderEntity", "OrderRecord" |
| Technical jargon in domain | Using "primary key", "foreign key" in domain descriptions | Use domain terms, not DB terms |
| Time-dependent definitions | "Active" meaning current vs historical | Specify temporal context |

## Enrichment Process

The ontology is enriched during the SDD lifecycle:

| Phase | How Ontology is Enriched |
|-------|------------------------|
| `constitution create` | Initial terms from project setup |
| `brainstorm` Phase 6.8.6 | Terms extracted from idea description |
| `spec-to-tasks` Phase 1.5 | Terms from spec added |
| `task-implementation` | New domain concepts added as discovered |

*When adding terms: Update `Last Updated` date and maintain consistent formatting.*