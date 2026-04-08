<div align="center">
[![License](https://img.shields.io/github/license/giuseppe-trisciuoglio/developer-kit.svg)](./LICENSE)
[![Security Scan](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml)
[![Plugin Validation](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml)
[![Skills](https://img.shields.io/badge/skill-150%2B-blue.svg)](./plugins)
[![Agents](https://img.shields.io/badge/agent-45%2B-purple.svg)](./plugins)

**🌐 Lingue:** [English](README.md) | [Italiano](./README_IT.md) | [中文](./README_CN.md) | [Español](./README_ES.md)

![](https://repository-images.githubusercontent.com/1080332870/5124e0d2-98f8-4486-9659-dde59a5ad251)

**Un sistema modulare di plugin AI che potenzia il tuo flusso di lavoro di sviluppo su più linguaggi e framework.**

[Installazione](#installazione) • [Avvio Rapido](#avvio-rapido) • [Plugin](#plugin-disponibili) • [Documentazione](https://github.com/giuseppe-trisciuoglio/developer-kit/blob/main/README.md) • [Changelog](./CHANGELOG.md)

</div>

---

## Perché Developer Kit?

Developer Kit è un **marketplace modulare di plugin** per Claude Code che insegna a Claude come eseguire task di sviluppo in modo ripetibile e di alta qualità. Invece di risposte AI generiche, ottieni competenze specifiche per il tuo stack tecnologico.

- **🧩 Modulare per Progettazione** — Installa solo ciò che ti serve. Sei uno sviluppatore Java? Prendi `developer-kit-java`. Full-stack TypeScript? Aggiungi `developer-kit-typescript`.
- **🎯 Esperti di Dominio** — Oltre 45 agenti specializzati per code review, refactoring, audit di sicurezza, design architetturale e testing su 7+ linguaggi.
- **📚 150+ Skill** — Capacità riutilizzabili dalla generazione CRUD Spring Boot ai template CloudFormation, tutti con le best practice integrate.
- **🔄 Multi-CLI** — Funziona con Claude Code, GitHub Copilot CLI, OpenCode CLI e Codex CLI.
- **⚡ Attivazione Automatica** — Le regole con scope sui percorsi si attivano automaticamente quando apri file pertinenti. Nessuna configurazione necessaria.

---

## Installazione

### Installazione Rapida (Consigliata)

#### Claude Code

```bash
# Installa dal marketplace
/plugin marketplace add giuseppe-trisciuoglio/developer-kit

# Oppure installa da directory locale
/plugin install /path/to/developer-kit
```

#### Claude Desktop

[Abilita Skill nelle Impostazioni](https://claude.ai/settings/capabilities) → Aggiungi `giuseppe-trisciuoglio/developer-kit`

#### Installazione Manuale

```bash
# Clona il repository
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git

# Installa via Makefile (rileva automaticamente la tua CLI)
cd developer-kit
make install

# Oppure installa per CLI specifica
make install-claude      # Claude Code
make install-opencode    # OpenCode CLI
make install-copilot     # GitHub Copilot CLI
make install-codex       # Codex CLI
```

---

## Avvio Rapido

```bash
# Dopo l'installazione, avvia la tua CLI
claude

# Controlla i comandi disponibili
/help

# Usa un comando Developer Kit
/devkit.refactor

# Oppure avvia un workflow di specifiche
/specs:brainstorm
```

### Esempi di Prompt

```
Genera un modulo CRUD completo per l'entità User con NestJS e Drizzle ORM
Revisiona questo servizio Spring Boot per problemi di sicurezza
Crea un template CloudFormation per ECS con auto-scaling
Aiutami a refactoring questa classe monolitica in clean architecture
Genera unit test per questo servizio TypeScript con copertura 100%
```

---

## Utilizzo

Developer Kit fornisce **quattro livelli** di capacità:

### 1. Skill
Capacità riutilizzabili caricate on-demand. Esempio:

```
[Skill: spring-boot-crud-patterns attivata]
```

Le skill forniscono automaticamente pattern, template e best practice per task specifici.

### 2. Agent
Sub-agent specializzati per workflow complessi:

```bash
# Invoca tramite linguaggio naturale
"Revisiona questo codice come un esperto Spring Boot"

# Oppure usa i comandi
/devkit.java.code-review
/devkit.typescript.code-review
```

### 3. Sviluppo Guidato dalle Specifiche (SDD)
Trasforma le idee in codice production-ready attraverso un workflow strutturato:

![Workflow SDD](./docs/specs-life-cycle.png)

#### Fase 1: Creazione della Specifica

| Comando | Quando Usare | Output |
|---------|--------------|--------|
| `/specs:brainstorm` | Nuove funzionalità, requisiti complessi | Specifica completa con 9 fasi |
| `/specs:quick-spec` | Bug fix, miglioramenti minori | Specifica leggera 4 fasi |

La specifica risiede in `docs/specs/[id]/YYYY-MM-DD--feature-name.md`

#### Fase 2: Generazione dei Task

| Comando | Descrizione |
|---------|-------------|
| `/specs:spec-to-tasks` | Converte la specifica in file di task eseguibili |
| `/specs:task-manage` | Aggiungi, dividi, aggiorna o riorganizza i task |

I task vengono generati in `docs/specs/[id]/tasks/` con file individuali.

#### Fase 3: Implementazione

| Comando | Descrizione |
|---------|-------------|
| `/specs:task-implementation` | Implementazione guidata di un task specifico |
| `/specs:task-tdd` | Approccio Test-Driven Development per il task |

Ogni implementazione aggiorna il Knowledge Graph per la conservazione del contesto.

#### Fase 4: Quality Assurance

| Comando | Descrizione |
|---------|-------------|
| `/specs:task-review` | Verifica che il task rispetti le specifiche e gli standard di qualità |
| `/specs:code-cleanup` | Pulizia professionale: rimuovi log di debug, ottimizza import |
| `/specs:spec-sync-with-code` | Sincronizza la specifica con l'implementazione effettiva |

#### Comandi Workflow Aggiuntivi

| Comando | Descrizione |
|---------|-------------|
| `/specs:spec-quality-check` | Valutazione interattiva della qualità delle specifiche |
| `/specs:spec-sync-context` | Sincronizza Knowledge Graph, Task e stato del Codebase |
| `/specs:ralph-loop` | Loop automatizzato per sviluppo guidato da specifiche |
| `/devkit.refactor` | Refactor del codice esistente con analisi architetturale |
| `/devkit.github.create-pr` | Crea PR con descrizione completa |

### 4. Regole
Regole con attivazione automatica basate su pattern di file:

```yaml
# Si attiva automaticamente per i file *.java
globs: ["**/*.java"]
---
Usa sempre l'iniezione tramite costruttore. Non usare mai l'iniezione su campo con @Autowired.
```

> **📋 Nota sull'installazione delle Regole**
>
> I plugin non installano automaticamente le regole nel progetto. Per utilizzare le regole, puoi copiarle manualmente
> oppure usare il comando del Makefile:
>
> ```bash
> # Copia le regole di un plugin specifico
> make copy-rules PLUGIN=developer-kit-java
>
> # Oppure copia manualmente i file .md dalla cartella rules/ del plugin
> mkdir -p .claude/rules
> cp plugins/developer-kit-[linguaggio]/rules/*.md .claude/rules/
> ```
>
> Le regole verranno automaticamente attivate in base ai pattern `globs:` definite nell'header di ogni file.

---

## Plugin Disponibili

| Plugin | Linguaggio/Dominio | Componenti | Descrizione |
|--------|-------------------|------------|-------------|
| `developer-kit-core` | Core | 6 Agent, 8 Comandi, 4 Skill | Plugin base richiesto con capacità generali |
| `developer-kit-specs` | Workflow | 9 Comandi, 2 Skill | Workflow di sviluppo guidato dalle specifiche (SDD) |
| `developer-kit-java` | Java | 9 Agent, 11 Comandi, 51 Skill, 4 Regole | Spring Boot, LangChain4J, AWS SDK, GraalVM |
| `developer-kit-typescript` | TypeScript | 13 Agent, 3 Comandi, 25 Skill, 17 Regole | NestJS, React, Next.js, Drizzle ORM, Monorepo |
| `developer-kit-python` | Python | 4 Agent, 4 Regole | Django, Flask, FastAPI, AWS Lambda |
| `developer-kit-php` | PHP | 5 Agent, 3 Skill, 4 Regole | WordPress, Sage, AWS Lambda |
| `developer-kit-aws` | AWS | 3 Agent, 19 Skill | CloudFormation, SAM, CLI, Architettura |
| `developer-kit-ai` | AI/ML | 1 Agent, 3 Skill, 1 Comando | Prompt Engineering, RAG, Chunking |
| `developer-kit-devops` | DevOps | 2 Agent | Docker, GitHub Actions |
| `developer-kit-tools` | Strumenti | 4 Skill | NotebookLM, Copilot CLI, Gemini, Codex |
| `github-spec-kit` | GitHub | 3 Comandi | Integrazione specifiche GitHub |

**Totale: 150+ Skill | 45+ Agent | 20+ Comandi | 45+ Regole**

---

## Architettura dei Plugin

```
developer-kit/
├── plugins/
│   ├── developer-kit-core/          # Base richiesto
│   │   ├── agents/                  # Definizioni agent (.md)
│   │   ├── commands/                # Comandi slash (.md)
│   │   ├── skills/                  # Skill riutilizzabili (SKILL.md)
│   │   ├── rules/                   # Regole auto-attivate
│   │   └── .claude-plugin/
│   │       └── plugin.json          # Manifesto plugin
│   ├── developer-kit-java/          # Ecosistema Java
│   ├── developer-kit-typescript/    # Ecosistema TypeScript
│   └── ...
├── .skills-validator-check/         # Sistema di validazione
└── Makefile                         # Comandi di installazione
```

Ogni plugin è autocontenuto con il proprio manifesto, componenti e dipendenze.

---

## Configurazione

### Selezione Plugin

Installa solo i plugin di cui hai bisogno:

```bash
# Core + Java + AWS
make install-claude
# Poi abilita: developer-kit-core, developer-kit-java, developer-kit-aws

# Full-stack TypeScript
# Abilita: developer-kit-core, developer-kit-typescript, developer-kit-aws
```

### Attivazione Automatica Regole

Le regole si attivano automaticamente basandosi su pattern di file:

```yaml
---
globs: ["**/*.java"]
---
# Questa regola si attiva per tutti i file Java
- Usa l'iniezione tramite costruttore
- Segui le convenzioni di naming
```

### Integrazione LSP

I plugin linguaggio includono configurazioni server LSP (`.lsp.json`):

| Linguaggio | Server |
|------------|--------|
| Java | jdtls |
| TypeScript | typescript-language-server |
| Python | pyright-langserver |
| PHP | intelephense |

---

## Matrice di Supporto Linguaggi

| Linguaggio | Skill | Agent | Comandi | Regole | LSP |
|------------|-------|-------|---------|--------|-----|
| Java/Spring Boot | 51 | 9 | 11 | 4 | ✅ |
| TypeScript/Node.js | 25 | 13 | 3 | 17 | ✅ |
| Python | 2 | 4 | 0 | 4 | ✅ |
| PHP/WordPress | 3 | 5 | 0 | 4 | ✅ |
| AWS/CloudFormation | 19 | 3 | 0 | 0 | ❌ |
| AI/ML | 3 | 1 | 1 | 0 | ❌ |

---

## Validazione e Qualità

Developer Kit include un sistema completo di validazione:

```bash
# Valida tutti i componenti
python .skills-validator-check/validators/cli.py --all

# Scansione sicurezza (conformità MCP)
make security-scan

# Hook pre-commit
.skills-validator-check/install-hooks.sh
```

---

## Ecosistema

**Disponibile su:**
- [context7](https://context7.com/giuseppe-trisciuoglio/developer-kit?tab=skills) — Marketplace di skill
- [skills.sh](https://skills.sh/giuseppe-trisciuoglio/developer-kit) — Directory di skill AI

**Progetti Correlati:**
- [Claude Code](https://claude.ai/code) — Terminale AI-powered di Anthropic
- [OpenCode](https://github.com/opencode-ai/opencode) — Assistente AI open-source
- [GitHub Copilot CLI](https://github.com/github/copilot.vim) — Pair programming AI
- [Codex CLI](https://github.com/openai/codex) — Coding agent di OpenAI

---

## Contribuire

Accogliamo con piacere i contributi! Vedi [CONTRIBUTING.md](./CONTRIBUTING.md) per:
- Aggiungere nuove skill, agent e comandi
- Linee guida per lo sviluppo di plugin
- Requisiti di validazione
- Strategia di branch e versioning

## Sicurezza

Le skill possono eseguire codice. Rivedi tutte le skill personalizzate prima del deploy:

- ✅ Installa solo da fonti affidabili
- ✅ Rivedi SKILL.md prima di abilitare
- ✅ Testa prima in ambienti non di produzione
- ✅ Esegui `make security-scan` prima delle release

Le scansioni di sicurezza vengono eseguite automaticamente via GitHub Actions su ogni PR.

---

## Licenza

[Licenza MIT](./LICENSE) — Open source e libero da usare.

---

## Riconoscimenti

- **Claude Code** di Anthropic — La fondazione che questo sistema di plugin estende
- **Qwen Code** — Ispirazione per il design del README
- **Contributori** — Grazie a tutti coloro che hanno contribuito con skill e plugin

---

<div align="center">

**Fatto con ❤️ per gli Sviluppatori che usano Claude Code**

Compatibile anche con OpenCode, GitHub Copilot CLI e Codex

</div>
