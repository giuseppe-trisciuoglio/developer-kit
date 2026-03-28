---
name: claude-code-optimizer
description: Ottimizza il consumo di token e la knowledge di progetto per Claude Code. Da utilizzare quando si lavora su progetti con file CLAUDE.md troppo grandi, problemi di latenza o necessità di migliorare la rilevanza del contesto.
---

# Claude Code Optimizer

Questa skill fornisce strategie e strumenti per ridurre il consumo di token in Claude Code fino al 60%, migliorando contemporaneamente la velocità di risposta e la qualità della conoscenza del progetto.

## Obiettivi di Ottimizzazione

L'obiettivo principale è mantenere il contesto rilevante ed efficiente seguendo questi parametri:
- **CLAUDE.md**: Le prime 200 righe devono contenere meno di 1.000 token.
- **Latenza**: Ridurre il tempo della prima risposta a 3-5 secondi.
- **Rilevanza**: Aumentare la pertinenza del contesto all'85% o superiore.

## Strategie Chiave

### 1. Documentazione a Livelli (Tiered Documentation)

Non caricare tutta la documentazione in `CLAUDE.md`. Mantieni il file principale snello e usa collegamenti a documenti specifici.

| Livello | File | Scopo | Target Token |
|---------|------|-------|--------------|
| **Critico** | `CLAUDE.md` | Regole fondamentali, architettura macro, comandi essenziali. | < 800 |
| **Componente** | `docs/*.md` | Dettagli API, Schema Database, Testing, Deployment. | 500 - 1.500 |
| **Riferimento** | Link esterni | Documentazione esterna o file di configurazione grezzi. | 0 (solo link) |

### 2. Session-Start Hook

Implementa un hook di inizio sessione per fornire a Claude Code un contesto immediato e dinamico senza sprecare token in file statici.

1. Crea la directory: `mkdir -p .claude/hooks`
2. Crea il file: `.claude/hooks/session-start.sh` (usa il template in `templates/session-start.sh.template`)
3. Rendi eseguibile: `chmod +x .claude/hooks/session-start.sh`

L'hook dovrebbe mostrare:
- Stato dei servizi (es. Docker, Database).
- Contesto Git (branch attuale, ultimo commit).
- Suggerimenti di documentazione basati sui file modificati recentemente.

### 3. Hub di Navigazione e Quick Reference

Crea file dedicati per compiti comuni e risoluzione dei problemi per evitare che Claude debba "indovinare" o cercare in tutto il repository.

- **`docs/INDEX.md`**: Un punto di partenza organizzato per "Cosa voglio fare...".
- **`docs/QUICK_REF.md`**: Comandi rapidi, tabelle di troubleshooting e regole critiche ("Mai fare X").

## Flusso di Lavoro Consigliato

1. **Audit**: Usa lo script `scripts/estimate_tokens.sh` per valutare lo stato attuale di `CLAUDE.md`.
2. **Refactoring**: Sposta le sezioni dettagliate (es. lista completa endpoint API) da `CLAUDE.md` a file in `docs/`.
3. **Priorità**: Sposta le "Critical Rules" nelle prime 40 righe di `CLAUDE.md`.
4. **Automazione**: Configura il `session-start.sh` hook per automatizzare il controllo dello stato del progetto.

## Risorse Incluse

- `scripts/estimate_tokens.sh`: Script per stimare i token e verificare il target di ottimizzazione.
- `templates/session-start.sh.template`: Template per l'hook di sessione.
- `templates/docs_templates.md`: Strutture suggerite per `INDEX.md` e `QUICK_REF.md`.

## Errori da Evitare

- **Non duplicare le informazioni**: Se un'informazione di troubleshooting è in `docs/API.md`, non ripeterla in `CLAUDE.md`. Usa un link.
- **Non nascondere info critiche**: Le regole di sicurezza e commit devono essere all'inizio di `CLAUDE.md`.
- **Non caricare tutto subito**: Claude Code è più intelligente con meno contesto ma più mirato.
