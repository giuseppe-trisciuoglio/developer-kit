# Developer Kit Installation Makefile - Multi-Plugin Architecture
# Automates installation of agents, commands, and skills for multiple AI CLI tools
#
# Supported CLIs:
#   - Claude Code (local project installation with interactive selection)
#   - Copilot CLI (GitHub Copilot - agents + skills, NO commands)
#   - OpenCode CLI (agents + commands + skills)
#   - Codex CLI (skills only, NO agents)
#
# Usage:
#   make help                  Show all available targets
#   make list-plugins          List all discovered plugins
#   make install-claude        Interactive installer for Claude Code
#   make install-opencode      Install for OpenCode CLI
#   make install-copilot       Install for GitHub Copilot CLI
#   make install-codex         Install for Codex CLI
#   make install               Install for all detected CLIs
#   make status                Show installation status
#   make backup                Create backup of current configs
#   make uninstall             Remove all installations

SHELL := /bin/bash
.PHONY: all help check-deps list-plugins list-components list-agents list-commands list-skills \
        install install-claude install-opencode install-copilot install-codex \
        uninstall status backup clean security-scan security-scan-changed

# ═══════════════════════════════════════════════════════════════
# COLORS & OUTPUT FORMATTING
# ═══════════════════════════════════════════════════════════════

GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m # No Color

# ═══════════════════════════════════════════════════════════════
# DIRECTORY STRUCTURE
# ═══════════════════════════════════════════════════════════════

DEVKIT_DIR   := $(shell pwd)
PLUGINS_DIR  := $(DEVKIT_DIR)/plugins
BACKUP_DIR   := $(HOME)/.devkit-backups/$(shell date +%Y%m%d_%H%M%S)

# Target directories per CLI
CLAUDE_DIR        := .claude
OPENCODE_CONFIG   := $(HOME)/.config/opencode
OPENCODE_AGENTS   := $(OPENCODE_CONFIG)/agent
OPENCODE_COMMANDS := $(OPENCODE_CONFIG)/command
OPENCODE_SKILLS   := $(OPENCODE_CONFIG)/skills

COPILOT_CONFIG    := $(HOME)/.copilot
COPILOT_AGENTS    := $(COPILOT_CONFIG)/agents
COPILOT_SKILLS    := $(COPILOT_CONFIG)/skills

CODEX_CONFIG      := $(HOME)/.codex
CODEX_SKILLS      := $(CODEX_CONFIG)/skills
CODEX_AGENTS_MD   := $(CODEX_CONFIG)/AGENTS.md

# ═══════════════════════════════════════════════════════════════
# PLUGIN DISCOVERY
# ═══════════════════════════════════════════════════════════════

# Discover all plugin.json files
PLUGIN_JSON_FILES := $(shell find $(PLUGINS_DIR) -name "plugin.json" -path "*/.claude-plugin/*" 2>/dev/null)

# ═══════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

define check_jq
	@if ! command -v jq >/dev/null 2>&1; then \
		echo -e "$(RED)Error: jq is required but not installed$(NC)"; \
		echo "Install with: brew install jq (macOS) or apt-get install jq (Linux)"; \
		exit 1; \
	fi
endef

define info
	@echo -e "$(BLUE)ℹ $(1)$(NC)"
endef

define success
	@echo -e "$(GREEN)✓ $(1)$(NC)"
endef

define warning
	@echo -e "$(YELLOW)⚠ $(1)$(NC)"
endef

define error
	@echo -e "$(RED)✗ $(1)$(NC)"
endef

# Extract plugin name from plugin.json
define get_plugin_name
	$(shell jq -r '.name' $(1) 2>/dev/null)
endef

# Extract agents array from plugin.json
define get_plugin_agents
	$(shell jq -r '.agents[]?' $(1) 2>/dev/null)
endef

# Extract commands array from plugin.json
define get_plugin_commands
	$(shell jq -r '.commands[]?' $(1) 2>/dev/null)
endef

# Extract skills array from plugin.json
define get_plugin_skills
	$(shell jq -r '.skills[]?' $(1) 2>/dev/null)
endef

# Extract rules array from plugin.json
define get_plugin_rules
	$(shell jq -r '.rules[]?' $(1) 2>/dev/null)
endef

# Conflict resolution handler
define handle_conflict
	@echo -n "  ⚠ $(1) already exists. [O]verwrite, [S]kip, [R]ename? "
	@read -n 1 action; \
	echo ""; \
	case $$action in \
		O|o) rm -rf "$(2)"; cp -r "$(1)" "$(2)"; echo "  ✓ Overwritten" ;; \
		R|r) \
			read -p "  Enter new name: " new_name; \
			cp -r "$(1)" "$(TARGET_DIR)/$$new_name"; \
			echo "  ✓ Renamed to $$new_name" ;; \
		*) echo "  ○ Skipped" ;; \
	esac
endef

# ═══════════════════════════════════════════════════════════════
# DEFAULT TARGET
# ═══════════════════════════════════════════════════════════════

all: help

# ═══════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════

help:
	@echo ""
	@echo -e "$(BLUE)╔═══════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║     Developer Kit - Multi-Plugin Installation Tool           ║$(NC)"
	@echo -e "$(BLUE)╚═══════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(GREEN)Installation Targets:$(NC)"
	@echo "  make install-claude       Interactive installer for Claude Code (project-local)"
	@echo "  make install-opencode     Install for OpenCode CLI (global)"
	@echo "  make install-copilot      Install for GitHub Copilot CLI (global)"
	@echo "  make install-codex        Install for Codex CLI (global)"
	@echo "  make install              Install for all detected CLIs"
	@echo ""
	@echo -e "$(GREEN)Management:$(NC)"
	@echo "  make status               Show installation status for all CLIs"
	@echo "  make uninstall            Remove all Developer Kit installations"
	@echo "  make backup               Create backup of current configs"
	@echo "  make clean                Remove generated files"
	@echo ""
	@echo -e "$(GREEN)Information:$(NC)"
	@echo "  make check-deps           Check if required dependencies are installed"
	@echo "  make list-plugins         List all discovered plugins"
	@echo "  make list-components      List components of a specific plugin"
	@echo "  make list-agents          List all available agents"
	@echo "  make list-commands        List all available commands"
	@echo "  make list-skills          List all available skills"
	@echo ""
	@echo -e "$(GREEN)Quality:$(NC)"
	@echo "  make security-scan          Run MCP-Scan security check on all skills"
	@echo "  make security-scan-changed  Run MCP-Scan only on changed skills (vs main)"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# DEPENDENCY CHECK
# ═══════════════════════════════════════════════════════════════

check-deps:
	@$(call check_jq)

# ═══════════════════════════════════════════════════════════════
# LISTING TARGETS
# ═══════════════════════════════════════════════════════════════

list-plugins: check-deps
	@echo ""
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)                  Discovered Plugins                          $(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@if [ -z "$(PLUGIN_JSON_FILES)" ]; then \
		echo -e "$(YELLOW)⚠ No plugins found in $(PLUGINS_DIR)$(NC)"; \
	else \
		for plugin_json in $(PLUGIN_JSON_FILES); do \
			plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
			plugin_version=$$(jq -r '.version' "$$plugin_json" 2>/dev/null); \
			plugin_desc=$$(jq -r '.description' "$$plugin_json" 2>/dev/null); \
			num_agents=$$(jq -r '.agents | length' "$$plugin_json" 2>/dev/null); \
			num_commands=$$(jq -r '.commands | length' "$$plugin_json" 2>/dev/null); \
			num_skills=$$(jq -r '.skills | length' "$$plugin_json" 2>/dev/null); \
			num_rules=$$(jq -r 'if .rules then .rules | length else 0 end' "$$plugin_json" 2>/dev/null); \
			echo -e "$(GREEN)$$plugin_name$(NC) (v$$plugin_version)"; \
			echo "  $$plugin_desc"; \
			echo "  Components: $$num_agents agents, $$num_commands commands, $$num_skills skills, $$num_rules rules"; \
			echo ""; \
		done; \
	fi

list-components: check-deps
	@if [ -z "$(PLUGIN)" ]; then \
		echo -e "$(RED)✗ Usage: make list-components PLUGIN=developer-kit-core$(NC)"; \
		exit 1; \
	fi
	@echo ""
	@echo -e "$(BLUE)Components of plugin: $(GREEN)$(PLUGIN)$(NC)$(BLUE)$(NC)"
	@echo ""
	@plugin_json=$$(find "$(PLUGINS_DIR)" -name "plugin.json" -path "*/.claude-plugin/*" -exec jq -r 'select(.name == "$(PLUGIN)") | input_filename' {} \; 2>/dev/null | head -1); \
	if [ -z "$$plugin_json" ]; then \
		echo -e "$(RED)✗ Plugin '$(PLUGIN)' not found$(NC)"; \
		exit 1; \
	fi; \
	echo -e "$(CYAN)Agents:$(NC)"; \
	jq -r '.agents[]? // empty' "$$plugin_json" 2>/dev/null | while read agent; do \
		echo "  - $$agent"; \
	done; \
	echo ""; \
	echo -e "$(CYAN)Commands:$(NC)"; \
	jq -r '.commands[]? // empty' "$$plugin_json" 2>/dev/null | while read cmd; do \
		echo "  - $$cmd"; \
	done; \
	echo ""; \
	echo -e "$(CYAN)Skills:$(NC)"; \
	jq -r '.skills[]? // empty' "$$plugin_json" 2>/dev/null | while read skill; do \
		echo "  - $$skill"; \
	done; \
	echo ""; \
	echo -e "$(CYAN)Rules:$(NC)"; \
	jq -r '.rules[]? // empty' "$$plugin_json" 2>/dev/null | while read rule; do \
		echo "  - $$rule"; \
	done; \
	echo ""

list-agents: check-deps
	@echo ""
	@echo -e "$(BLUE)Available Agents:$(NC)"
	@echo ""
	@for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		agents=$$(jq -r '.agents[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$agents" ]; then \
			echo -e "$(YELLOW)$$plugin_name:$(NC)"; \
			for agent in $$agents; do \
				agent_path="$$base_dir/$$agent"; \
				if [ -f "$$agent_path" ]; then \
					agent_name=$$(basename "$$agent" .md); \
					desc=$$(head -10 "$$agent_path" | grep -E '^description:' | head -1 | sed 's/description: *//'); \
					if [ -z "$$desc" ]; then \
						desc="No description"; \
					fi; \
					printf "  $(GREEN)%-40s$(NC) %s\n" "$$agent_name" "$$desc"; \
				fi; \
			done; \
			echo ""; \
		fi; \
	done

list-commands: check-deps
	@echo ""
	@echo -e "$(BLUE)Available Commands:$(NC)"
	@echo ""
	@for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		commands=$$(jq -r '.commands[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$commands" ]; then \
			echo -e "$(YELLOW)$$plugin_name:$(NC)"; \
			for cmd in $$commands; do \
				cmd_path="$$base_dir/$$cmd"; \
				if [ -f "$$cmd_path" ]; then \
					cmd_name=$$(basename "$$cmd" .md); \
					desc=$$(grep -m1 "^description:" "$$cmd_path" 2>/dev/null | sed 's/^description: *//'); \
					if [ -z "$$desc" ]; then \
						desc=$$(head -1 "$$cmd_path" | sed 's/^# *//'); \
					fi; \
					printf "  $(GREEN)%-45s$(NC) %s\n" "$$cmd_name" "$$desc"; \
				fi; \
			done; \
			echo ""; \
		fi; \
	done

list-skills: check-deps
	@echo ""
	@echo -e "$(BLUE)Available Skills:$(NC)"
	@echo ""
	@for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		skills=$$(jq -r '.skills[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$skills" ]; then \
			echo -e "$(YELLOW)$$plugin_name:$(NC)"; \
			for skill_pattern in $$skills; do \
				for skill_dir in $$base_dir/$$skill_pattern; do \
					if [ -d "$$skill_dir" ]; then \
						skill_name=$$(basename "$$skill_dir"); \
						skill_md="$$skill_dir/SKILL.md"; \
						if [ -f "$$skill_md" ]; then \
							desc=$$(head -20 "$$skill_md" | grep -E '^description:' | head -1 | sed 's/description: *//'); \
							if [ -z "$$desc" ]; then \
								desc=$$(head -10 "$$skill_md" | grep -E '^#' | head -1 | sed 's/^# *//'); \
							fi; \
							printf "  $(GREEN)%-40s$(NC) %s\n" "$$skill_name" "$$desc"; \
						fi; \
					fi; \
				done; \
			done; \
			echo ""; \
		fi; \
	done; \
	echo ""

# ═══════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════

status:
	@echo ""
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)              Developer Kit Installation Status                $(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo -e "$(GREEN)Claude Code:$(NC)"
	@echo "  Project-local installation to .claude/ directory"
	@echo "  Use 'make install-claude' for interactive installation"
	@echo ""
	@echo -e "$(GREEN)GitHub Copilot CLI:$(NC)"
	@if [ -d "$(COPILOT_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(COPILOT_CONFIG)"; \
		if [ -d "$(COPILOT_AGENTS)" ] && ls "$(COPILOT_AGENTS)"/*.md >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Developer Kit agents installed$(NC)"; \
			echo "    Agents: $$(ls -1 "$(COPILOT_AGENTS)"/*.md 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Developer Kit agents not installed"; \
		fi; \
		if [ -d "$(COPILOT_SKILLS)" ] && ls "$(COPILOT_SKILLS)" >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Developer Kit skills installed$(NC)"; \
			echo "    Skills: $$(ls -1d "$(COPILOT_SKILLS)"/* 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Developer Kit skills not installed"; \
		fi; \
	else \
		echo -e "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""
	@echo -e "$(GREEN)OpenCode CLI:$(NC)"
	@if [ -d "$(OPENCODE_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(OPENCODE_CONFIG)"; \
		if [ -d "$(OPENCODE_AGENTS)" ] && ls "$(OPENCODE_AGENTS)"/*.md >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Developer Kit agents installed$(NC)"; \
			echo "    Agents: $$(ls -1 "$(OPENCODE_AGENTS)"/*.md 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Developer Kit agents not installed"; \
		fi; \
		if [ -d "$(OPENCODE_COMMANDS)" ] && ls "$(OPENCODE_COMMANDS)"/*.md >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Developer Kit commands installed$(NC)"; \
			echo "    Commands: $$(ls -1 "$(OPENCODE_COMMANDS)"/*.md 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Developer Kit commands not installed"; \
		fi; \
		if [ -d "$(OPENCODE_SKILLS)" ] && ls "$(OPENCODE_SKILLS)" >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Developer Kit skills installed$(NC)"; \
			echo "    Skills: $$(ls -1d "$(OPENCODE_SKILLS)"/* 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Developer Kit skills not installed"; \
		fi; \
	else \
		echo -e "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""
	@echo -e "$(GREEN)Codex CLI:$(NC)"
	@if [ -d "$(CODEX_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(CODEX_CONFIG)"; \
		if [ -f "$(CODEX_AGENTS_MD)" ] && grep -q "Developer Kit" "$(CODEX_AGENTS_MD)" 2>/dev/null; then \
			echo -e "  ✓ $(GREEN)Developer Kit installed$(NC)"; \
		else \
			echo "  ○ Developer Kit not installed"; \
		fi; \
		if [ -d "$(CODEX_SKILLS)" ] && ls "$(CODEX_SKILLS)" >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Developer Kit skills installed$(NC)"; \
			echo "    Skills: $$(ls -1d "$(CODEX_SKILLS)"/* 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Developer Kit skills not installed"; \
		fi; \
	else \
		echo -e "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""

# ═══════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════

backup:
	@echo -e "$(BLUE)Creating backup of existing configurations...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@if [ -d "$(COPILOT_AGENTS)" ] && ls "$(COPILOT_AGENTS)"/*.md >/dev/null 2>&1; then \
		cp -r "$(COPILOT_AGENTS)" "$(BACKUP_DIR)/copilot-agents" 2>/dev/null || true; \
		echo -e "$(GREEN)✓ Backed up Copilot agents$(NC)"; \
	fi
	@if [ -d "$(OPENCODE_AGENTS)" ]; then \
		cp -r "$(OPENCODE_AGENTS)" "$(BACKUP_DIR)/opencode-agents" 2>/dev/null || true; \
		echo -e "$(GREEN)✓ Backed up OpenCode agents$(NC)"; \
	fi
	@if [ -d "$(OPENCODE_COMMANDS)" ]; then \
		cp -r "$(OPENCODE_COMMANDS)" "$(BACKUP_DIR)/opencode-commands" 2>/dev/null || true; \
		echo -e "$(GREEN)✓ Backed up OpenCode commands$(NC)"; \
	fi
	@if [ -d "$(OPENCODE_SKILLS)" ]; then \
		cp -r "$(OPENCODE_SKILLS)" "$(BACKUP_DIR)/opencode-skills" 2>/dev/null || true; \
		echo -e "$(GREEN)✓ Backed up OpenCode skills$(NC)"; \
	fi
	@if [ -d "$(COPILOT_SKILLS)" ]; then \
		cp -r "$(COPILOT_SKILLS)" "$(BACKUP_DIR)/copilot-skills" 2>/dev/null || true; \
		echo -e "$(GREEN)✓ Backed up Copilot skills$(NC)"; \
	fi
	@if [ -f "$(CODEX_AGENTS_MD)" ]; then \
		cp "$(CODEX_AGENTS_MD)" "$(BACKUP_DIR)/codex-AGENTS.md" 2>/dev/null || true; \
		echo -e "$(GREEN)✓ Backed up Codex AGENTS.md$(NC)"; \
	fi
	@if [ -d "$(CODEX_SKILLS)" ]; then \
		cp -r "$(CODEX_SKILLS)" "$(BACKUP_DIR)/codex-skills" 2>/dev/null || true; \
		echo -e "$(GREEN)✓ Backed up Codex skills$(NC)"; \
	fi
	@echo ""
	@echo "  Backup location: $(BACKUP_DIR)"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# UNINSTALL
# ═══════════════════════════════════════════════════════════════

uninstall:
	@echo -e "$(BLUE)Removing Developer Kit installations...$(NC)"
	@echo ""
	@# Collect all installed files from all plugins
	@installed_agents=""; \
	installed_commands=""; \
	for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		agents=$$(jq -r '.agents[]? // empty' "$$plugin_json" 2>/dev/null); \
		for agent in $$agents; do \
			agent_name=$$(basename "$$agent"); \
			installed_agents="$$installed_agents $$agent_name"; \
		done; \
		commands=$$(jq -r '.commands[]? // empty' "$$plugin_json" 2>/dev/null); \
		for cmd in $$commands; do \
			cmd_name=$$(basename "$$cmd"); \
			installed_commands="$$installed_commands $$cmd_name"; \
		done; \
	done; \
	\
	if [ -d "$(COPILOT_AGENTS)" ]; then \
		for agent in $$installed_agents; do \
			if [ -f "$(COPILOT_AGENTS)/$$agent" ]; then \
				rm -f "$(COPILOT_AGENTS)/$$agent"; \
				echo -e "$(GREEN)✓ Removed Copilot agent: $$agent$(NC)"; \
			fi; \
		done; \
	fi; \
	\
	if [ -d "$(OPENCODE_AGENTS)" ]; then \
		for agent in $$installed_agents; do \
			if [ -f "$(OPENCODE_AGENTS)/$$agent" ]; then \
				rm -f "$(OPENCODE_AGENTS)/$$agent"; \
				echo -e "$(GREEN)✓ Removed OpenCode agent: $$agent$(NC)"; \
			fi; \
		done; \
	fi; \
	\
	if [ -d "$(OPENCODE_COMMANDS)" ]; then \
		for cmd in $$installed_commands; do \
			if [ -f "$(OPENCODE_COMMANDS)/$$cmd" ]; then \
				rm -f "$(OPENCODE_COMMANDS)/$$cmd"; \
				echo -e "$(GREEN)✓ Removed OpenCode command: $$cmd$(NC)"; \
			fi; \
		done; \
	fi; \
	\
	if [ -f "$(CODEX_AGENTS_MD)" ] && grep -q "Developer Kit" "$(CODEX_AGENTS_MD)" 2>/dev/null; then \
		rm -f "$(CODEX_AGENTS_MD)"; \
		echo -e "$(GREEN)✓ Removed Codex AGENTS.md$(NC)"; \
	fi
	@echo ""
	@echo -e "$(GREEN)✓ Uninstallation complete$(NC)"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# INSTALL ALL
# ═══════════════════════════════════════════════════════════════

install: backup
	@echo ""
	@$(call info "Installing Developer Kit for all detected CLIs...")
	@echo ""
	@$(MAKE) -s install-opencode-if-exists
	@$(MAKE) -s install-copilot-if-exists
	@$(MAKE) -s install-codex-if-exists
	@echo ""
	@$(call success "Installation complete!")
	@$(MAKE) -s status

install-opencode-if-exists:
	@if [ -d "$(OPENCODE_CONFIG)" ]; then \
		$(MAKE) -s install-opencode; \
	else \
		$(call warning "Skipping OpenCode CLI (not configured)"); \
	fi

install-copilot-if-exists:
	@if [ -d "$(COPILOT_CONFIG)" ]; then \
		$(MAKE) -s install-copilot; \
	else \
		$(call warning "Skipping Copilot CLI (not configured)"); \
	fi

install-codex-if-exists:
	@if [ -d "$(CODEX_CONFIG)" ]; then \
		$(MAKE) -s install-codex; \
	else \
		$(call warning "Skipping Codex CLI (not configured)"); \
	fi

# ═══════════════════════════════════════════════════════════════
# OPENCODE CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-opencode: check-deps
	@echo ""
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo -e "$(BLUE)Installing Developer Kit for OpenCode CLI$(NC)"
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo ""
	@mkdir -p $(OPENCODE_AGENTS)
	@mkdir -p $(OPENCODE_COMMANDS)
	@mkdir -p $(OPENCODE_SKILLS)
	@echo -e "$(CYAN)Installing agents...$(NC)"
	@agents_count=0; \
	for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		agents=$$(jq -r '.agents[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$agents" ]; then \
			for agent in $$agents; do \
				agent_path="$$base_dir/$$agent"; \
				if [ -f "$$agent_path" ]; then \
					agent_name=$$(basename "$$agent"); \
					cp "$$agent_path" "$(OPENCODE_AGENTS)/$$agent_name"; \
					echo "  ✓ $$plugin_name: $$agent_name"; \
					agents_count=$$((agents_count + 1)); \
				fi; \
			done; \
		fi; \
	done; \
	echo "  Total agents installed: $$agents_count"
	@echo ""
	@echo -e "$(CYAN)Installing commands...$(NC)"
	@commands_count=0; \
	for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		commands=$$(jq -r '.commands[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$commands" ]; then \
			for cmd in $$commands; do \
				cmd_path="$$base_dir/$$cmd"; \
				if [ -f "$$cmd_path" ]; then \
					cmd_name=$$(basename "$$cmd"); \
					cmd_subdir=$$(dirname "$$cmd"); \
					if [ "$$cmd_subdir" != "." ]; then \
						cmd_subdir_rel=$$(echo "$$cmd_subdir" | sed 's|^\./commands$$||' | sed 's|^\./commands/||'); \
						if [ -n "$$cmd_subdir_rel" ]; then \
							mkdir -p "$(OPENCODE_COMMANDS)/$$cmd_subdir_rel"; \
							cp "$$cmd_path" "$(OPENCODE_COMMANDS)/$$cmd_subdir_rel/$$cmd_name"; \
							echo "  ✓ $$plugin_name: $$cmd_subdir_rel/$$cmd_name"; \
						else \
							cp "$$cmd_path" "$(OPENCODE_COMMANDS)/$$cmd_name"; \
							echo "  ✓ $$plugin_name: $$cmd_name"; \
						fi; \
					else \
						cp "$$cmd_path" "$(OPENCODE_COMMANDS)/$$cmd_name"; \
						echo "  ✓ $$plugin_name: $$cmd_name"; \
					fi; \
					commands_count=$$((commands_count + 1)); \
				fi; \
			done; \
		fi; \
	done; \
	echo "  Total commands installed: $$commands_count"
	@echo ""
	@echo -e "$(CYAN)Installing skills...$(NC)"
	@skills_count=0; \
	for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		skills=$$(jq -r '.skills[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$skills" ]; then \
			for skill_pattern in $$skills; do \
				for skill_dir in $$base_dir/$$skill_pattern; do \
					if [ -d "$$skill_dir" ]; then \
						skill_name=$$(basename "$$skill_dir"); \
						cp -r "$$skill_dir" "$(OPENCODE_SKILLS)/$$skill_name"; \
						echo "  ✓ $$plugin_name: $$skill_name"; \
						skills_count=$$((skills_count + 1)); \
					fi; \
				done; \
			done; \
		fi; \
	done; \
	echo "  Total skills installed: $$skills_count"
	@echo ""
	@$(call success "OpenCode CLI installation complete")
	@echo "  Agents directory: $(OPENCODE_AGENTS)/"
	@echo "  Commands directory: $(OPENCODE_COMMANDS)/"
	@echo "  Skills directory: $(OPENCODE_SKILLS)/"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# COPILOT CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-copilot: check-deps
	@echo ""
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo -e "$(BLUE)Installing Developer Kit for GitHub Copilot CLI$(NC)"
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo ""
	@mkdir -p $(COPILOT_AGENTS)
	@mkdir -p $(COPILOT_SKILLS)
	@echo -e "$(CYAN)Installing agents...$(NC)"
	@agents_count=0; \
	for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		agents=$$(jq -r '.agents[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$agents" ]; then \
			for agent in $$agents; do \
				agent_path="$$base_dir/$$agent"; \
				if [ -f "$$agent_path" ]; then \
					agent_name=$$(basename "$$agent"); \
					cp "$$agent_path" "$(COPILOT_AGENTS)/$$agent_name"; \
					echo "  ✓ $$plugin_name: $$agent_name"; \
					agents_count=$$((agents_count + 1)); \
				fi; \
			done; \
		fi; \
	done; \
	echo "  Total agents installed: $$agents_count"
	@echo ""
	@echo -e "$(CYAN)Installing skills...$(NC)"
	@skills_count=0; \
	for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		skills=$$(jq -r '.skills[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$skills" ]; then \
			for skill_pattern in $$skills; do \
				for skill_dir in $$base_dir/$$skill_pattern; do \
					if [ -d "$$skill_dir" ]; then \
						skill_name=$$(basename "$$skill_dir"); \
						cp -r "$$skill_dir" "$(COPILOT_SKILLS)/$$skill_name"; \
						echo "  ✓ $$plugin_name: $$skill_name"; \
						skills_count=$$((skills_count + 1)); \
					fi; \
				done; \
			done; \
		fi; \
	done; \
	echo "  Total skills installed: $$skills_count"
	@echo ""
	@$(call success "Copilot CLI installation complete")
	@echo "  Agents directory: $(COPILOT_AGENTS)/"
	@echo "  Skills directory: $(COPILOT_SKILLS)/"
	@echo "  NOTE: Commands are NOT installed for Copilot CLI (not supported)"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# CODEX CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-codex: check-deps
	@echo ""
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo -e "$(BLUE)Installing Developer Kit for Codex CLI$(NC)"
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo ""
	@mkdir -p $(CODEX_CONFIG)
	@mkdir -p $(CODEX_SKILLS)
	@echo -e "$(CYAN)Installing skills...$(NC)"
	@skills_count=0; \
	for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		skills=$$(jq -r '.skills[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$skills" ]; then \
			for skill_pattern in $$skills; do \
				for skill_dir in $$base_dir/$$skill_pattern; do \
					if [ -d "$$skill_dir" ]; then \
						skill_name=$$(basename "$$skill_dir"); \
						cp -r "$$skill_dir" "$(CODEX_SKILLS)/$$skill_name"; \
						echo "  ✓ $$plugin_name: $$skill_name"; \
						skills_count=$$((skills_count + 1)); \
					fi; \
				done; \
			done; \
		fi; \
	done; \
	echo "  Total skills installed: $$skills_count"
	@echo ""
	@echo -e "$(CYAN)Creating AGENTS.md index...$(NC)"
	@echo "# Developer Kit for Codex CLI" > $(CODEX_AGENTS_MD)
	@echo "# Auto-generated by Developer Kit Makefile" >> $(CODEX_AGENTS_MD)
	@echo "" >> $(CODEX_AGENTS_MD)
	@echo "You have access to the Developer Kit, a curated collection of skills" >> $(CODEX_AGENTS_MD)
	@echo "for automating development tasks." >> $(CODEX_AGENTS_MD)
	@echo "" >> $(CODEX_AGENTS_MD)
	@echo "## Available Skills" >> $(CODEX_AGENTS_MD)
	@echo "" >> $(CODEX_AGENTS_MD)
	@for plugin_json in $(PLUGIN_JSON_FILES); do \
		plugin_dir=$$(dirname "$$plugin_json"); \
		base_dir=$$(dirname "$$plugin_dir"); \
		plugin_name=$$(jq -r '.name' "$$plugin_json" 2>/dev/null); \
		skills=$$(jq -r '.skills[]? // empty' "$$plugin_json" 2>/dev/null); \
		if [ -n "$$skills" ]; then \
			for skill_pattern in $$skills; do \
				for skill_dir in $$base_dir/$$skill_pattern; do \
					if [ -d "$$skill_dir" ]; then \
						skill_name=$$(basename "$$skill_dir"); \
						skill_md="$$skill_dir/SKILL.md"; \
						desc=""; \
						if [ -f "$$skill_md" ]; then \
							desc=$$(head -20 "$$skill_md" | grep -E '^description:' | head -1 | sed 's/description: *//'); \
						fi; \
						if [ -n "$$desc" ]; then \
							echo "- **$$skill_name**: $$desc" >> $(CODEX_AGENTS_MD); \
						else \
							echo "- $$skill_name" >> $(CODEX_AGENTS_MD); \
						fi; \
					fi; \
				done; \
			done; \
		fi; \
	done
	@echo "" >> $(CODEX_AGENTS_MD)
	@$(call success "Codex CLI installation complete")
	@echo "  AGENTS.md file: $(CODEX_AGENTS_MD)"
	@echo "  Skills directory: $(CODEX_SKILLS)/"
	@echo "  NOTE: Agents and commands are NOT installed for Codex CLI (not supported)"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# CLAUDE CODE INTERACTIVE INSTALLATION
# ═══════════════════════════════════════════════════════════════
# TO BE IMPLEMENTED - This will be a comprehensive interactive installer
# ═══════════════════════════════════════════════════════════════

install-claude: check-deps
	@echo ""
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo -e "$(BLUE)      Claude Code Interactive Developer Kit Installer          $(NC)"
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo ""
	@echo -e "$(YELLOW)⚠ This installer is designed for Claude Code only.$(NC)"
	@echo ""
	@bash $(DEVKIT_DIR)/scripts/install-claude.sh "$(PLUGIN_JSON_FILES)"

# ═══════════════════════════════════════════════════════════════
# CLEAN
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
# SECURITY SCANNING
# ═══════════════════════════════════════════════════════════════

security-scan:
	@python3 .skills-validator-check/validators/mcp_scan_checker.py --all -v

security-scan-changed:
	@python3 .skills-validator-check/validators/mcp_scan_checker.py --changed -v

# ═══════════════════════════════════════════════════════════════
# CLEAN
# ═══════════════════════════════════════════════════════════════

clean:
	@echo -e "$(BLUE)Cleaning generated files...$(NC)"
	@rm -f $(DEVKIT_DIR)/*.tmp
	@$(call success "Clean complete")
	@echo ""
