[![License](https://img.shields.io/github/license/giuseppe-trisciuoglio/developer-kit.svg)](./LICENSE)
[![Security Scan](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/security-scan.yml)
[![Plugin Validation](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml/badge.svg)](https://github.com/giuseppe-trisciuoglio/developer-kit/actions/workflows/plugin-validation.yml)
[![Skills](https://img.shields.io/badge/habilidades-150%2B-blue.svg)](./plugins)
[![Agents](https://img.shields.io/badge/agentes-45%2B-purple.svg)](./plugins)

**🌐 Idiomas:** [English](README.md) | [Italiano](./README_IT.md) | [中文](./README_CN.md) | [Español](./README_ES.md)

![](https://repository-images.githubusercontent.com/1080332870/5124e0d2-98f8-4486-9659-dde59a5ad251)

**Un sistema de plugins AI modular que potencia tu flujo de trabajo de desarrollo en múltiples lenguajes y frameworks.**

[Instalación](#instalación) • [Inicio Rápido](#inicio-rápido) • [Plugins](#plugins-disponibles) • [Documentación](https://github.com/giuseppe-trisciuoglio/developer-kit/blob/main/README.md) • [Changelog](./CHANGELOG.md)

</div>

---

## ¿Por qué Developer Kit?

Developer Kit es un **mercado de plugins modular** para Claude Code que enseña a Claude cómo realizar tareas de desarrollo de manera repetible y de alta calidad. En lugar de respuestas AI genéricas, obtienes experiencia específica del dominio para tu stack tecnológico exacto.

- **🧩 Modular por Diseño** — Instala solo lo que necesitas. ¿Desarrollador Java? Toma `developer-kit-java`. ¿TypeScript full-stack? Agrega `developer-kit-typescript`.
- **🎯 Expertos de Dominio** — Más de 45 agentes especializados para revisión de código, refactoring, auditorías de seguridad, diseño de arquitectura y pruebas en más de 7 lenguajes.
- **📚 150+ Habilidades** — Capacidades reutilizables desde generación CRUD de Spring Boot hasta plantillas de CloudFormation, todas con mejores prácticas integradas.
- **🔄 Soporte Multi-CLI** — Funciona con Claude Code, GitHub Copilot CLI, OpenCode CLI y Codex CLI.
- **⚡ Activación Automática** — Las reglas con alcance de ruta se activan automáticamente cuando abres archivos relevantes. No se necesita configuración.

---

## Instalación

### Instalación Rápida (Recomendada)

#### Claude Code

```bash
# Instalar desde el marketplace
/plugin marketplace add giuseppe-trisciuoglio/developer-kit

# O instalar desde directorio local
/plugin install /path/to/developer-kit
```

#### Claude Desktop

[Habilitar Habilidades en Configuración](https://claude.ai/settings/capabilities) → Agregar `giuseppe-trisciuoglio/developer-kit`

#### Instalación Manual

```bash
# Clonar el repositorio
git clone https://github.com/giuseppe-trisciuoglio/developer-kit.git

# Instalar vía Makefile (detecta automáticamente tu CLI)
cd developer-kit
make install

# O instalar para CLI específica
make install-claude      # Claude Code
make install-opencode    # OpenCode CLI
make install-copilot     # GitHub Copilot CLI
make install-codex       # Codex CLI
```

---

## Inicio Rápido

```bash
# Después de la instalación, inicia tu CLI
claude

# Ver comandos disponibles
/help

# Usar un comando de Developer Kit
/devkit.refactor

# O iniciar un flujo de trabajo de especificaciones
/specs:brainstorm
```

### Ejemplos de Prompts

```
Genera un módulo CRUD completo para la entidad User con NestJS y Drizzle ORM
Revisa este servicio Spring Boot Java para problemas de seguridad
Crea una plantilla de CloudFormation para ECS con auto-scaling
Ayúdame a refactorizar esta clase monolítica a clean architecture
Genera pruebas unitarias para este servicio TypeScript con 100% de cobertura
```

---

## Uso

Developer Kit proporciona **cuatro capas** de capacidades:

### 1. Habilidades
Capacidades reutilizables cargadas bajo demanda. Ejemplo:

```
[Habilidad: spring-boot-crud-patterns activada]
```

Las habilidades proporcionan automáticamente patrones, plantillas y mejores prácticas para tareas específicas.

### 2. Agentes
Sub-agentes especializados para flujos de trabajo complejos:

```bash
# Invocar mediante lenguaje natural
"Revisa este código como un experto en Spring Boot"

# O usar comandos
/devkit.java.code-review
/devkit.typescript.code-review
```

### 3. Desarrollo Guiado por Especificaciones (SDD)
Transforma ideas en código listo para producción a través de un flujo de trabajo estructurado:

![Flujo de Trabajo SDD](./docs/specs-life-cycle.png)

#### Fase 1: Creación de Especificaciones

| Comando | Cuándo Usar | Salida |
|---------|-------------|--------|
| `/specs:brainstorm` | Nuevas funcionalidades, requisitos complejos | Especificación completa con 9 fases |
| `/specs:quick-spec` | Corrección de errores, mejoras pequeñas | Especificación ligera de 4 fases |

La especificación se guarda en `docs/specs/[id]/YYYY-MM-DD--feature-name.md`

#### Fase 2: Generación de Tareas

| Comando | Descripción |
|---------|-------------|
| `/specs:spec-to-tasks` | Convierte la especificación en archivos de tareas ejecutables |
| `/specs:task-manage` | Agregar, dividir, actualizar o reorganizar tareas |

Las tareas se generan en `docs/specs/[id]/tasks/` con archivos individuales.

#### Fase 3: Implementación

| Comando | Descripción |
|---------|-------------|
| `/specs:task-implementation` | Implementación guiada de una tarea específica |
| `/specs:task-tdd` | Enfoque de Desarrollo Guiado por Pruebas para la tarea |

Cada implementación de tarea actualiza el Grafo de Conocimiento para la preservación del contexto.

#### Fase 4: Garantía de Calidad

| Comando | Descripción |
|---------|-------------|
| `/specs:task-review` | Verifica que la tarea cumpla las especificaciones y estándares de calidad |
| `/specs:code-cleanup` | Limpieza profesional: eliminar logs de depuración, optimizar imports |
| `/specs:spec-sync-with-code` | Sincroniza la especificación con la implementación actual |

#### Comandos Adicionales del Flujo de Trabajo

| Comando | Descripción |
|---------|-------------|
| `/specs:spec-quality-check` | Evaluación interactiva de calidad de especificaciones |
| `/specs:spec-sync-context` | Sincroniza Grafo de Conocimiento, Tareas y estado del Código |
| `/specs:ralph-loop` | Bucle automatizado para desarrollo guiado por especificaciones |
| `/devkit.refactor` | Refactorizar código existente con análisis arquitectónico |
| `/devkit.github.create-pr` | Crear PR con descripción completa |

### 4. Reglas
Reglas de activación automática basadas en patrones de archivos:

```yaml
# Se activa automáticamente para archivos *.java
globs: ["**/*.java"]
---
Usa siempre inyección por constructor. Nunca uses inyección de campo con @Autowired.
```

> **📋 Nota sobre la instalación de Reglas**
>
> Los plugins no instalan automáticamente las reglas en el proyecto. Para utilizar las reglas, puedes copiarlas manualmente
> o usar el comando del Makefile:
>
> ```bash
> # Copia las reglas de un plugin específico
> make copy-rules PLUGIN=developer-kit-java
>
> # O copia manualmente los archivos .md de la carpeta rules/ del plugin
> mkdir -p .claude/rules
> cp plugins/developer-kit-[lenguaje]/rules/*.md .claude/rules/
> ```
>
> Las reglas se activarán automáticamente según los patrones `globs:` definidos en el header de cada archivo.

---

## Plugins Disponibles

| Plugin | Lenguaje/Dominio | Componentes | Descripción |
|--------|------------------|-------------|-------------|
| `developer-kit-core` | Core | 6 Agentes, 8 Comandos, 4 Habilidades | Plugin base requerido con capacidades de propósito general |
| `developer-kit-specs` | Flujo de trabajo | 9 Comandos, 2 Habilidades | Flujo de trabajo de desarrollo guiado por especificaciones (SDD) |
| `developer-kit-java` | Java | 9 Agentes, 11 Comandos, 51 Habilidades, 4 Reglas | Spring Boot, LangChain4J, AWS SDK, GraalVM |
| `developer-kit-typescript` | TypeScript | 13 Agentes, 3 Comandos, 25 Habilidades, 17 Reglas | NestJS, React, Next.js, Drizzle ORM, Monorepo |
| `developer-kit-python` | Python | 4 Agentes, 4 Reglas | Django, Flask, FastAPI, AWS Lambda |
| `developer-kit-php` | PHP | 5 Agentes, 3 Habilidades, 4 Reglas | WordPress, Sage, AWS Lambda |
| `developer-kit-aws` | AWS | 3 Agentes, 19 Habilidades | CloudFormation, SAM, CLI, Arquitectura |
| `developer-kit-ai` | AI/ML | 1 Agente, 3 Habilidades, 1 Comando | Prompt Engineering, RAG, Chunking |
| `developer-kit-devops` | DevOps | 2 Agentes | Docker, GitHub Actions |
| `developer-kit-tools` | Herramientas | 4 Habilidades | NotebookLM, Copilot CLI, Gemini, Codex |
| `github-spec-kit` | GitHub | 3 Comandos | Integración de especificaciones GitHub |

**Total: 150+ Habilidades | 45+ Agentes | 20+ Comandos | 45+ Reglas**

---

## Arquitectura de Plugins

```
developer-kit/
├── plugins/
│   ├── developer-kit-core/          # Base requerida
│   │   ├── agents/                  # Definiciones de agentes (.md)
│   │   ├── commands/                # Comandos de barra inclinada (.md)
│   │   ├── skills/                  # Habilidades reutilizables (SKILL.md)
│   │   ├── rules/                   # Reglas auto-activadas
│   │   └── .claude-plugin/
│   │       └── plugin.json          # Manifiesto del plugin
│   ├── developer-kit-java/          # Ecosistema Java
│   ├── developer-kit-typescript/    # Ecosistema TypeScript
│   └── ...
├── .skills-validator-check/         # Sistema de validación
└── Makefile                         # Comandos de instalación
```

Cada plugin es autocontenido con su propio manifiesto, componentes y dependencias.

---

## Configuración

### Selección de Plugins

Instala solo los plugins que necesitas:

```bash
# Core + Java + AWS
make install-claude
# Luego habilita: developer-kit-core, developer-kit-java, developer-kit-aws

# Full-stack TypeScript
# Habilita: developer-kit-core, developer-kit-typescript, developer-kit-aws
```

### Activación Automática de Reglas

Las reglas se activan automáticamente basándose en patrones de archivos:

```yaml
---
globs: ["**/*.java"]
---
# Esta regla se activa para todos los archivos Java
- Usa inyección por constructor
- Sigue las convenciones de nomenclatura
```

### Integración LSP

Los plugins de lenguaje incluyen configuraciones de servidor LSP (`.lsp.json`):

| Lenguaje | Servidor |
|----------|----------|
| Java | jdtls |
| TypeScript | typescript-language-server |
| Python | pyright-langserver |
| PHP | intelephense |

---

## Matriz de Soporte de Lenguajes

| Lenguaje | Habilidades | Agentes | Comandos | Reglas | LSP |
|----------|-------------|---------|----------|--------|-----|
| Java/Spring Boot | 51 | 9 | 11 | 4 | ✅ |
| TypeScript/Node.js | 25 | 13 | 3 | 17 | ✅ |
| Python | 2 | 4 | 0 | 4 | ✅ |
| PHP/WordPress | 3 | 5 | 0 | 4 | ✅ |
| AWS/CloudFormation | 19 | 3 | 0 | 0 | ❌ |
| AI/ML | 3 | 1 | 1 | 0 | ❌ |

---

## Validación y Calidad

Developer Kit incluye un sistema de validación completo:

```bash
# Validar todos los componentes
python .skills-validator-check/validators/cli.py --all

# Escaneo de seguridad (cumplimiento MCP)
make security-scan

# Hooks pre-commit
.skills-validator-check/install-hooks.sh
```

---

## Ecosistema

**Listado en:**
- [context7](https://context7.com/giuseppe-trisciuoglio/developer-kit?tab=skills) — Mercado de habilidades
- [skills.sh](https://skills.sh/giuseppe-trisciuoglio/developer-kit) — Directorio de habilidades AI

**Proyectos Relacionados:**
- [Claude Code](https://claude.ai/code) — Terminal impulsada por AI de Anthropic
- [OpenCode](https://github.com/opencode-ai/opencode) — Asistente de código AI open-source
- [GitHub Copilot CLI](https://github.com/github/copilot.vim) — Programación en pareja AI
- [Codex CLI](https://github.com/openai/codex) — Agente de codificación de OpenAI

---

## Contribuir

¡Damos la bienvenida a las contribuciones! Consulta [CONTRIBUTING.md](./CONTRIBUTING.md) para:
- Agregar nuevas habilidades, agentes y comandos
- Guías de desarrollo de plugins
- Requisitos de validación
- Estrategia de ramas y versionado

## Seguridad

Las habilidades pueden ejecutar código. Revisa todas las habilidades personalizadas antes de desplegar:

- ✅ Instala solo desde fuentes confiables
- ✅ Revisa SKILL.md antes de habilitar
- ✅ Prueba primero en ambientes no productivos
- ✅ Ejecuta `make security-scan` antes de releases

Los escaneos de seguridad se ejecutan automáticamente vía GitHub Actions en cada PR.

---

## Licencia

[Licencia MIT](./LICENSE) — Open source y libre de usar.

---

## Agradecimientos

- **Claude Code** de Anthropic — La base que extiende este sistema de plugins
- **Qwen Code** — Inspiración para el diseño del README
- **Contribuidores** — Gracias a todos los que han contribuido habilidades y plugins

---

<div align="center">

**Hecho con ❤️ para Desarrolladores que usan Claude Code**

También compatible con OpenCode, GitHub Copilot CLI y Codex

</div>
