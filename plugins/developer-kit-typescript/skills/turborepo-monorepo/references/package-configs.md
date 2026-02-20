# Package Configurations in Turborepo

Le Package Configurations permettono di definire comportamenti specifici per singoli package senza influenzare l'intero repository.

## Struttura

```
apps/
  web/
    package.json
    turbo.json  # Package configuration
libs/
  ui/
    package.json
    turbo.json  # Package configuration
turbo.json      # Root configuration
```

## Estendere dalla configurazione root

Ogni `turbo.json` in un package deve estendere dalla root:

```json
{
  "$schema": "https://turborepo.dev/schema.json",
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", ".next/**"]
    }
  }
}
```

## Esempi di Package Configurations

### Next.js con output specifici

`apps/web/turbo.json`:

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", ".next/**", "!.next/cache/**"]
    },
    "dev": {
      "dependsOn": ["^dev"]
    }
  }
}
```

### NestJS API

`apps/api/turbo.json`:

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", "dist/**"]
    },
    "start:dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### Libreria UI

`libs/ui/turbo.json`:

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", "dist/**"]
    },
    "lint": {
      "outputs": [],
      "inputs": ["$TURBO_DEFAULT$", "src/**/*.tsx", "src/**/*.ts"]
    },
    "storybook": {
      "cache": false,
      "persistent": true
    }
  }
}
```

## Escludere task dall'ereditarietà

Usa `extends: false` per escludere un task:

```json
{
  "extends": ["//"],
  "tasks": {
    "lint": {
      "extends": false
    }
  }
}
```

O definisci un nuovo task non ereditato:

```json
{
  "extends": ["//"],
  "tasks": {
    "lint": {
      "extends": false,
      "outputs": [],
      "inputs": ["src/**/*.ts"]
    }
  }
}
```

## Condividere configurazioni

Crea un package di configurazione condivisa:

```
packages/
  turbo-config/
    package.json
    turbo.json
apps/
  web/
    turbo.json
```

`packages/turbo-config/turbo.json`:

```json
{
  "tasks": {
    "build": {
      "outputs": ["dist/**"]
    },
    "lint": {
      "outputs": []
    }
  }
}
```

`apps/web/turbo.json`:

```json
{
  "extends": ["//", "turbo-config"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", ".next/**"]
    }
  }
}
```

## Variabili di Environment per Package

Definisci variabili specifiche per package:

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "env": ["$TURBO_EXTENDS$", "NEXT_PUBLIC_STRIPE_KEY"]
    }
  }
}
```

## Task specifici per package

Definisci task che esistono solo in certi package:

```json
{
  "extends": ["//"],
  "tasks": {
    "storybook": {
      "cache": false,
      "persistent": true,
      "description": "Run Storybook for UI components"
    },
    "chromatic": {
      "dependsOn": ["build"],
      "outputs": [],
      "description": "Publish to Chromatic"
    }
  }
}
```

## Dipendenze specifiche per package

Definisci dipendenze tra task di package specifici:

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "dependsOn": ["utils#build", "shared#build"]
    }
  }
}
```

## Sovrascrivere outputs

Sostituisci completamente gli outputs ereditati:

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": [".next/**"]  // Sostituisce, non aggiunge
    }
  }
}
```

Oppure aggiungi agli outputs esistenti:

```json
{
  "extends": ["//"],
  "tasks": {
    "build": {
      "outputs": ["$TURBO_EXTENDS$", ".next/**"]
    }
  }
}
```

## Best Practices

1. **Estendi sempre dalla root** con `["//"]`
2. **Usa `$TURBO_EXTENDS$`** per aggiungere ai valori ereditati
3. **Mantieni le configurazioni semplici** - metti solo le differenze
4. **Documenta i task custom** con `description`
5. **Evita duplicazioni** - usa package config condivisi per pattern comuni
6. **Testa localmente** prima di committare configurazioni complesse
