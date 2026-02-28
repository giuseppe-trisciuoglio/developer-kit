# NotebookLM CLI Command Reference

> Source: [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli)

## Command Structure

The CLI supports two styles — use whichever feels natural:

```bash
# Noun-first (resource-oriented)
nlm notebook create "Title"
nlm source add <notebook> --url <url>

# Verb-first (action-oriented)
nlm create notebook "Title"
nlm add url <notebook> <url>
```

## Notebooks

| Command | Description |
|---------|-------------|
| `nlm notebook list` | List all notebooks |
| `nlm notebook list --json` | JSON output |
| `nlm notebook create "Title"` | Create notebook |
| `nlm notebook get <id>` | Get details |
| `nlm notebook describe <id>` | AI summary |
| `nlm notebook rename <id> "New Title"` | Rename |
| `nlm notebook delete <id> --confirm` | Delete (IRREVERSIBLE) |
| `nlm notebook query <id> "question"` | Chat with sources |

## Sources

| Command | Description |
|---------|-------------|
| `nlm source list <notebook>` | List sources |
| `nlm source add <notebook> --url "<user-provided-url>"` | Add URL |
| `nlm source add <notebook> --url "<user-provided-url>" --wait` | Add URL and wait until ready |
| `nlm source add <notebook> --text "content" --title "Notes"` | Add text |
| `nlm source add <notebook> --file document.pdf --wait` | Upload file |
| `nlm source add <notebook> --youtube "<user-provided-url>"` | Add YouTube video |
| `nlm source add <notebook> --drive <doc-id>` | Add Google Drive doc |
| `nlm source get <source-id>` | Get content |
| `nlm source describe <source-id>` | AI summary |
| `nlm source stale <notebook>` | Check stale Drive sources |
| `nlm source sync <notebook> --confirm` | Sync stale sources |
| `nlm source delete <source-id> --confirm` | Delete (IRREVERSIBLE) |

## Studio Content Creation

### Audio (Podcasts)

```bash
nlm audio create <notebook> --confirm
nlm audio create <notebook> --format deep_dive --length long --confirm
```

- **Formats:** `deep_dive`, `brief`, `critique`, `debate`
- **Lengths:** `short`, `default`, `long`

### Video

```bash
nlm video create <notebook> --format explainer --style classic --confirm
```

- **Formats:** `explainer`, `brief`
- **Styles:** `auto_select`, `classic`, `whiteboard`, `kawaii`, `anime`, `watercolor`, `retro_print`, `heritage`, `paper_craft`

### Reports

```bash
nlm report create <notebook> --format "Briefing Doc" --confirm
```

- **Formats:** `"Briefing Doc"`, `"Study Guide"`, `"Blog Post"`, `"Create Your Own"`

### Other Content Types

| Command | Description |
|---------|-------------|
| `nlm quiz create <notebook> --count 10 --difficulty medium --confirm` | Generate quiz |
| `nlm flashcards create <notebook> --difficulty hard --confirm` | Generate flashcards |
| `nlm mindmap create <notebook> --confirm` | Generate mind map |
| `nlm slides create <notebook> --confirm` | Generate slide deck |
| `nlm infographic create <notebook> --orientation landscape --confirm` | Generate infographic |
| `nlm data-table create <notebook> --description "desc" --confirm` | Generate data table |

### Slide Revision

```bash
nlm slides revise <artifact-id> --slide '1 Make the title larger' --confirm
nlm slides revise <artifact-id> --slide '1 Fix title' --slide '3 Remove image' --confirm
```

## Downloads

| Command | Description |
|---------|-------------|
| `nlm download audio <notebook> <artifact-id> --output podcast.mp3` | Download audio |
| `nlm download video <notebook> <artifact-id> --output video.mp4` | Download video |
| `nlm download report <notebook> <artifact-id> --output report.md` | Download report |
| `nlm download mind-map <notebook> <artifact-id> --output mindmap.json` | Download mind map |
| `nlm download slide-deck <notebook> <artifact-id> --output slides.pdf` | Download slides |
| `nlm download infographic <notebook> <artifact-id> --output info.png` | Download infographic |
| `nlm download data-table <notebook> <artifact-id> --output data.csv` | Download data table |
| `nlm download quiz <notebook> <artifact-id> --format html --output quiz.html` | Download quiz |
| `nlm download flashcards <notebook> <artifact-id> --format markdown --output cards.md` | Download flashcards |

## Research

| Command | Description |
|---------|-------------|
| `nlm research start "query" --notebook-id <id> --mode fast` | Quick web search |
| `nlm research start "query" --notebook-id <id> --mode deep` | Extended research |
| `nlm research start "query" --notebook-id <id> --source drive` | Search Google Drive |
| `nlm research status <notebook> --max-wait 300` | Poll until done |
| `nlm research import <notebook> <task-id>` | Import research results |

## Aliases

| Command | Description |
|---------|-------------|
| `nlm alias set <name> <notebook-id>` | Create alias |
| `nlm alias list` | List all aliases |
| `nlm alias get <name>` | Resolve to UUID |
| `nlm alias delete <name>` | Remove alias |

## Authentication

| Command | Description |
|---------|-------------|
| `nlm login` | Login via Chrome cookie extraction |
| `nlm login --profile <name>` | Login with named profile |
| `nlm login --check` | Check authentication status |
| `nlm login switch <profile>` | Switch default profile |
| `nlm login profile list` | List all profiles |
| `nlm login profile delete <name>` | Delete a profile |
| `nlm login profile rename <old> <new>` | Rename a profile |

## Configuration

| Command | Description |
|---------|-------------|
| `nlm config list` | Show all settings |
| `nlm config set <key> <value>` | Change a setting |

### Available Settings

| Key | Default | Description |
|-----|---------|-------------|
| `output.format` | `table` | Default output format (table, json) |
| `output.color` | `true` | Enable colored output |
| `output.short_ids` | `true` | Show shortened IDs |
| `auth.browser` | `auto` | Browser for login (auto, chrome, chromium) |
| `auth.default_profile` | `default` | Profile to use when `--profile` not specified |

## Setup (MCP Server)

| Command | Description |
|---------|-------------|
| `nlm setup add claude-code` | Configure for Claude Code |
| `nlm setup add claude-desktop` | Configure for Claude Desktop |
| `nlm setup add gemini` | Configure for Gemini CLI |
| `nlm setup add cursor` | Configure for Cursor |
| `nlm setup add json` | Generate JSON config for any tool |
| `nlm setup remove <client>` | Remove configuration |
| `nlm setup list` | Show all clients and status |

## Output Formats

| Flag | Description |
|------|-------------|
| (none) | Rich table format |
| `--json` | JSON output |
| `--quiet` | IDs only |
| `--title` | "ID: Title" format |
| `--full` | All columns |

## Diagnostics

```bash
nlm doctor              # Run all diagnostic checks
nlm doctor --verbose    # Include additional details
```

## Authentication Lifecycle

| Component | Duration | Refresh |
|-----------|----------|---------|
| Cookies | ~2-4 weeks | Auto-refresh via headless Chrome |
| CSRF Token | ~minutes | Auto-refreshed on request failure |
| Session ID | Per session | Auto-extracted on start |
