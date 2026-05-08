# ADR-039: Gestione dei git worktree con integrazione auto-branch creation

| Campo | Valore |
|---|---|
| **Data** | 2026-05-02 |
| **Stato** | Proposto |
| **Autore** | Giuseppe Trisciuoglio |
| **Componenti coinvolti** | `cmd/specs-kit/task_run.go`, gestione repository git |

---

## 1. Sommario

Introduciamo la gestione dei git worktree per permettere agli utenti di lavorare su più specifiche in parallelo. Ogni specifica può essere sviluppata in un working tree isolato, integrando la logica di auto-creazione branch dell'ADR-038 in modo che il worktree venga creato con il branch corretto già checkoutato.

---

## 2. Contesto

### Comportamento attuale

L'ADR-038 introduce l'auto-creazione del branch durante `task run`, ma lavora sul working tree principale del repository. Questo significa che:
- L'utente può lavorare su una sola specifica alla volta nel medesimo working tree
- Per cambiare task è necessario `git stash`, commit temporanei o cambio manuale di branch
- Non è possibile eseguire test o build su più specifiche contemporaneamente

### Problema

In workflow dove lo sviluppo è organizzato per specifiche, gli utenti avanzati necessitano di:
1. Lavorare su più task in parallelo senza conflitti
2. Mantenere il contesto di lavoro di ogni specifica (file modificati, dipendenze, build)
3. Evitare operazioni di stash/switch ripetute che introducono frizione e rischio di errore

---

## 3. Decisione

**Comportamento:** Integrare `git worktree add` nel flusso di `task run` (o in un comando dedicato) per creare una directory di lavoro separata per ogni specifica, riutilizzando la logica di auto-creazione branch dell'ADR-038.

### Logica

```
SE:
  - Progetto usa git (verifica con git rev-parse --git-dir)
  - L'utente richiede esecuzione in modalità worktree (es. flag --worktree o config)
  - Branch "specs/XXX-nome-progetto" non esiste oppure esiste ma non è checkoutato in alcun worktree

ALLORA:
  - Crea worktree in <path-configurabile>/specs-XXX-nome-progetto
  - Se il branch non esiste, crealo da branch base (come ADR-038)
  - Checkout del branch nel nuovo worktree
  - Esegui il task nel contesto del nuovo worktree
```

### Configurazione

La directory base per i worktree può essere configurata in `specs-kit.yaml`:

```yaml
git:
  worktreeBasePath: ../worktrees  # default: ../<repo-name>-worktrees
```

---

## 4. Conseguenze

### Positive
- **Parallelismo**: possibilità di lavorare su più task contemporaneamente senza conflitti di working tree
- **Contesto isolato**: ogni specifica mantiene il proprio stato di file modificati, build artifact e dipendenze
- **Zero stash**: nessun bisogno di `git stash` o commit temporanei quando si cambia task
- **Integrazione ADR-038**: riutilizza la logica di auto-creazione branch esistente

### Negative
- **Spazio disco**: ogni worktree replica i file tracciati del repository (il `.git` è condiviso)
- **Complessità gestione**: necessità di gestire worktree orfani, lock, prune e rimozione
- **Limitazioni submodule**: git worktree ha supporto incompleto per i submodule
- **Tooling esterno**: IDE e strumenti devono essere configurati per riconoscere i path dei worktree

### Rischi
- Medio: se un worktree viene eliminato manualmente senza `git worktree remove`, rimangono riferimenti stale (risolvibili con `git worktree prune`)
- Medio: branch già checkoutati in altri worktree richiedono gestione `--force` o logica di riutilizzo

---

## 5. Alternative considerate

**Utilizzare solo branch switching sul working tree principale**: Scartata perché non risolve il problema del lavoro parallelo e introduce frizione con stash/switch continui.

**Creare clone completi del repository**: Scartata perché duplica anche la history e gli oggetti git, consumando molto più spazio rispetto ai worktree che condividono il `.git`.

---

## 6. Implementazione

1. Verificare se il progetto è un repo git (`git rev-parse --git-dir`)
2. Determinare il path del nuovo worktree (`worktreeBasePath` + nome specifica)
3. Verificare se il worktree esiste già (`git worktree list`)
4. Se non esiste:
   a. Verificare se il branch della specifica esiste (`git branch --list`)
   b. Se non esiste, crearlo dal branch base (logica ADR-038)
   c. Creare il worktree: `git worktree add <path> <branch>`
5. Eseguire il task nel contesto del worktree (cambio directory o env appropriato)
6. Fornire comando di cleanup: `specs-kit task cleanup-worktrees` o integrare in `git worktree prune`

---

## 7. Compatibilità

- Retrocompatibile: se git non supporta worktree o il progetto non è un repo git, il comando continua sul working tree principale
- L'uso dei worktree è opt-in (flag o configurazione) per non cambiare il comportamento di default dell'ADR-038
