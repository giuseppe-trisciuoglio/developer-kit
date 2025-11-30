# Developer Kit Installation Makefile
# Automates installation of agents and commands for multiple AI CLI tools
#
# Supported CLIs:
#   - Copilot CLI (GitHub Copilot)
#   - OpenCode CLI
#   - Codex CLI (OpenAI)
#
# Usage:
#   make install              # Install for all detected CLIs
#   make install-copilot      # Install only for Copilot CLI
#   make install-opencode     # Install only for OpenCode CLI
#   make install-codex        # Install only for Codex CLI
#   make uninstall            # Remove all installations
#   make status               # Show installation status

SHELL := /bin/bash
.PHONY: all install install-copilot install-opencode install-codex uninstall status help clean

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Directories
DEVKIT_DIR := $(shell pwd)
AGENTS_DIR := $(DEVKIT_DIR)/agents
COMMANDS_DIR := $(DEVKIT_DIR)/commands
SKILLS_DIR := $(DEVKIT_DIR)/skills

# Config directories
COPILOT_CONFIG := $(HOME)/.copilot
COPILOT_AGENTS := $(COPILOT_CONFIG)/agents
OPENCODE_CONFIG := $(HOME)/.config/opencode
OPENCODE_AGENTS := $(OPENCODE_CONFIG)/agent
OPENCODE_COMMANDS := $(OPENCODE_CONFIG)/command
OPENCODE_JSON := $(OPENCODE_CONFIG)/opencode.json
CODEX_CONFIG := $(HOME)/.codex
CODEX_INSTRUCTIONS := $(CODEX_CONFIG)/instructions.md
CODEX_PROMPTS := $(CODEX_CONFIG)/prompts

# Backup directory
BACKUP_DIR := $(HOME)/.devkit-backups/$(shell date +%Y%m%d_%H%M%S)

# Default target
all: help

help:
	@echo ""
	@echo -e "$(BLUE)╔═══════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║       Developer Kit - Multi-CLI Installation Tool             ║$(NC)"
	@echo -e "$(BLUE)╚═══════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(GREEN)Usage:$(NC)"
	@echo "  make install              Install for all detected CLIs"
	@echo "  make install-copilot      Install only for GitHub Copilot CLI"
	@echo "  make install-opencode     Install only for OpenCode CLI"
	@echo "  make install-codex        Install only for Codex CLI"
	@echo ""
	@echo -e "$(GREEN)Management:$(NC)"
	@echo "  make status               Show installation status for all CLIs"
	@echo "  make uninstall            Remove all Developer Kit installations"
	@echo "  make backup               Create backup of current configs"
	@echo "  make clean                Remove generated files"
	@echo ""
	@echo -e "$(GREEN)Information:$(NC)"
	@echo "  make list-agents          List available agents"
	@echo "  make list-commands        List available commands"
	@echo "  make list-skills          List available skills"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════

status:
	@echo ""
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)              Developer Kit Installation Status                $(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo -e "$(GREEN)GitHub Copilot CLI:$(NC)"
	@if [ -d "$(COPILOT_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(COPILOT_CONFIG)"; \
		if [ -d "$(COPILOT_AGENTS)" ] && ls "$(COPILOT_AGENTS)"/*.md >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Developer Kit installed$(NC)"; \
			echo "    Agents: $$(ls -1 "$(COPILOT_AGENTS)"/*.md 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Developer Kit not installed"; \
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
	else \
		echo -e "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""
	@echo -e "$(GREEN)Codex CLI:$(NC)"
	@if [ -d "$(CODEX_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(CODEX_CONFIG)"; \
		if [ -f "$(CODEX_INSTRUCTIONS)" ] && grep -q "Developer Kit" "$(CODEX_INSTRUCTIONS)" 2>/dev/null; then \
			echo -e "  ✓ $(GREEN)Developer Kit installed$(NC)"; \
		else \
			echo "  ○ Developer Kit not installed"; \
		fi; \
		if [ -d "$(CODEX_PROMPTS)" ] && ls "$(CODEX_PROMPTS)"/*.md >/dev/null 2>&1; then \
			echo -e "  ✓ $(GREEN)Custom prompts installed$(NC)"; \
			echo "    Prompts: $$(ls -1 "$(CODEX_PROMPTS)"/*.md 2>/dev/null | wc -l | tr -d ' ')"; \
		else \
			echo "  ○ Custom prompts not installed"; \
		fi; \
	else \
		echo -e "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""

# ═══════════════════════════════════════════════════════════════
# INSTALL ALL
# ═══════════════════════════════════════════════════════════════

install: backup
	@echo ""
	@echo -e "$(BLUE)Installing Developer Kit for all detected CLIs...$(NC)"
	@echo ""
	@$(MAKE) -s install-copilot-if-exists
	@$(MAKE) -s install-opencode-if-exists
	@$(MAKE) -s install-codex-if-exists
	@echo ""
	@echo -e "$(GREEN)✓ Installation complete!$(NC)"
	@$(MAKE) -s status

install-copilot-if-exists:
	@if [ -d "$(COPILOT_CONFIG)" ]; then \
		$(MAKE) -s install-copilot; \
	else \
		echo -e "$(YELLOW)⚠ Skipping Copilot CLI (not configured)$(NC)"; \
	fi

install-opencode-if-exists:
	@if [ -d "$(OPENCODE_CONFIG)" ]; then \
		$(MAKE) -s install-opencode; \
	else \
		echo -e "$(YELLOW)⚠ Skipping OpenCode CLI (not configured)$(NC)"; \
	fi

install-codex-if-exists:
	@if [ -d "$(CODEX_CONFIG)" ]; then \
		$(MAKE) -s install-codex; \
	else \
		echo -e "$(YELLOW)⚠ Skipping Codex CLI (not configured)$(NC)"; \
	fi

# ═══════════════════════════════════════════════════════════════
# COPILOT CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-copilot:
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo -e "$(BLUE)Installing Developer Kit for GitHub Copilot CLI$(NC)"
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@mkdir -p $(COPILOT_AGENTS)
	@# Copy agents as custom agent profiles
	@for agent in $(AGENTS_DIR)/*.md; do \
		if [ -f "$$agent" ]; then \
			name=$$(basename "$$agent" .md); \
			cp "$$agent" "$(COPILOT_AGENTS)/$$name.md"; \
			echo "  ✓ Agent: $$name"; \
		fi; \
	done
	@echo ""
	@echo -e "$(GREEN)✓ Copilot CLI installation complete$(NC)"
	@echo "  Agents directory: $(COPILOT_AGENTS)/"
	@echo ""
	@echo -e "$(YELLOW)Usage:$(NC)"
	@echo "  - Use /agent slash command to select an agent"
	@echo "  - Or mention the agent in your prompt: 'Use the code-review agent...'"

# ═══════════════════════════════════════════════════════════════
# OPENCODE CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-opencode:
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo -e "$(BLUE)Installing Developer Kit for OpenCode CLI$(NC)"
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@mkdir -p $(OPENCODE_AGENTS)
	@mkdir -p $(OPENCODE_COMMANDS)
	@# Copy agents as markdown files with proper frontmatter
	@for agent in $(AGENTS_DIR)/*.md; do \
		if [ -f "$$agent" ]; then \
			name=$$(basename "$$agent"); \
			cp "$$agent" "$(OPENCODE_AGENTS)/$$name"; \
			echo "  ✓ Agent: $$name"; \
		fi; \
	done
	@# Copy commands as markdown files
	@for cmd in $(COMMANDS_DIR)/*.md; do \
		if [ -f "$$cmd" ]; then \
			name=$$(basename "$$cmd"); \
			cp "$$cmd" "$(OPENCODE_COMMANDS)/$$name"; \
			echo "  ✓ Command: $$name"; \
		fi; \
	done
	@echo ""
	@echo -e "$(GREEN)✓ OpenCode CLI installation complete$(NC)"
	@echo "  Agents directory: $(OPENCODE_AGENTS)/"
	@echo "  Commands directory: $(OPENCODE_COMMANDS)/"
	@echo ""
	@echo -e "$(YELLOW)Usage:$(NC)"
	@echo "  - Press Tab to cycle through primary agents"
	@echo "  - Use @agent-name to invoke subagents"
	@echo "  - Use /command-name to run custom commands"

# ═══════════════════════════════════════════════════════════════
# CODEX CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-codex:
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo -e "$(BLUE)Installing Developer Kit for Codex CLI$(NC)"
	@echo -e "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@mkdir -p $(CODEX_CONFIG)
	@mkdir -p $(CODEX_PROMPTS)
	@# Copy commands as custom prompts (slash commands)
	@echo -e "$(GREEN)Installing custom prompts (slash commands):$(NC)"
	@for cmd in $(COMMANDS_DIR)/*.md; do \
		if [ -f "$$cmd" ]; then \
			name=$$(basename "$$cmd"); \
			cp "$$cmd" "$(CODEX_PROMPTS)/$$name"; \
			echo "  ✓ Prompt: $$name"; \
		fi; \
	done
	@# Create or update instructions.md with agents context
	@echo ""
	@echo -e "$(GREEN)Creating instructions.md with agents context:$(NC)"
	@echo "# Developer Kit Instructions for Codex CLI" > $(CODEX_INSTRUCTIONS)
	@echo "# Auto-generated by Developer Kit Makefile" >> $(CODEX_INSTRUCTIONS)
	@echo "# Source: $(DEVKIT_DIR)" >> $(CODEX_INSTRUCTIONS)
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@echo "You have access to the Developer Kit, a curated collection of skills and agents" >> $(CODEX_INSTRUCTIONS)
	@echo "for automating development tasks, focusing on Java/Spring Boot patterns." >> $(CODEX_INSTRUCTIONS)
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@echo "## Custom Prompts Available" >> $(CODEX_INSTRUCTIONS)
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@echo "Use \`/prompts:<name>\` to invoke custom commands. Available prompts:" >> $(CODEX_INSTRUCTIONS)
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@for cmd in $(COMMANDS_DIR)/*.md; do \
		if [ -f "$$cmd" ]; then \
			name=$$(basename "$$cmd" .md); \
			desc=$$(grep -m1 "^description:" "$$cmd" 2>/dev/null | sed 's/^description: *//'); \
			echo "- \`/prompts:$$name\` - $$desc" >> $(CODEX_INSTRUCTIONS); \
		fi; \
	done
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@echo "## Specialized Agents" >> $(CODEX_INSTRUCTIONS)
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@for agent in $(AGENTS_DIR)/*.md; do \
		if [ -f "$$agent" ]; then \
			name=$$(basename "$$agent" .md); \
			echo "### $$name" >> $(CODEX_INSTRUCTIONS); \
			echo "" >> $(CODEX_INSTRUCTIONS); \
			head -50 "$$agent" >> $(CODEX_INSTRUCTIONS); \
			echo "" >> $(CODEX_INSTRUCTIONS); \
			echo "---" >> $(CODEX_INSTRUCTIONS); \
			echo "" >> $(CODEX_INSTRUCTIONS); \
		fi; \
	done
	@echo ""
	@echo -e "$(GREEN)✓ Codex CLI installation complete$(NC)"
	@echo "  Instructions file: $(CODEX_INSTRUCTIONS)"
	@echo "  Prompts directory: $(CODEX_PROMPTS)/"
	@echo ""
	@echo -e "$(YELLOW)Usage:$(NC)"
	@echo "  - Type /prompts: to see available custom commands"
	@echo "  - Example: /prompts:devkit.java.code-review [args]"

# ═══════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════

backup:
	@echo -e "$(BLUE)Creating backup of existing configurations...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@if [ -d "$(COPILOT_AGENTS)" ] && ls "$(COPILOT_AGENTS)"/*.md >/dev/null 2>&1; then \
		cp -r "$(COPILOT_AGENTS)" "$(BACKUP_DIR)/copilot-agents" 2>/dev/null || true; \
		echo "  ✓ Backed up Copilot agents"; \
	fi
	@if [ -d "$(OPENCODE_AGENTS)" ]; then \
		cp -r "$(OPENCODE_AGENTS)" "$(BACKUP_DIR)/opencode-agents" 2>/dev/null || true; \
		echo "  ✓ Backed up OpenCode agents"; \
	fi
	@if [ -d "$(OPENCODE_COMMANDS)" ]; then \
		cp -r "$(OPENCODE_COMMANDS)" "$(BACKUP_DIR)/opencode-commands" 2>/dev/null || true; \
		echo "  ✓ Backed up OpenCode commands"; \
	fi
	@if [ -f "$(CODEX_INSTRUCTIONS)" ]; then \
		cp "$(CODEX_INSTRUCTIONS)" "$(BACKUP_DIR)/codex-instructions.md" 2>/dev/null || true; \
		echo "  ✓ Backed up Codex instructions"; \
	fi
	@if [ -d "$(CODEX_PROMPTS)" ] && ls "$(CODEX_PROMPTS)"/*.md >/dev/null 2>&1; then \
		cp -r "$(CODEX_PROMPTS)" "$(BACKUP_DIR)/codex-prompts" 2>/dev/null || true; \
		echo "  ✓ Backed up Codex prompts"; \
	fi
	@echo "  Backup location: $(BACKUP_DIR)"

# ═══════════════════════════════════════════════════════════════
# UNINSTALL
# ═══════════════════════════════════════════════════════════════

uninstall:
	@echo -e "$(BLUE)Removing Developer Kit installations...$(NC)"
	@echo ""
	@# Remove Copilot agents installed from this devkit
	@if [ -d "$(COPILOT_AGENTS)" ]; then \
		for agent in $(AGENTS_DIR)/*.md; do \
			if [ -f "$$agent" ]; then \
				name=$$(basename "$$agent"); \
				if [ -f "$(COPILOT_AGENTS)/$$name" ]; then \
					rm -f "$(COPILOT_AGENTS)/$$name"; \
					echo "  ✓ Removed Copilot agent: $$name"; \
				fi; \
			fi; \
		done; \
	fi
	@# Remove OpenCode agents installed from this devkit
	@if [ -d "$(OPENCODE_AGENTS)" ]; then \
		for agent in $(AGENTS_DIR)/*.md; do \
			if [ -f "$$agent" ]; then \
				name=$$(basename "$$agent"); \
				if [ -f "$(OPENCODE_AGENTS)/$$name" ]; then \
					rm -f "$(OPENCODE_AGENTS)/$$name"; \
					echo "  ✓ Removed OpenCode agent: $$name"; \
				fi; \
			fi; \
		done; \
	fi
	@# Remove OpenCode commands installed from this devkit
	@if [ -d "$(OPENCODE_COMMANDS)" ]; then \
		for cmd in $(COMMANDS_DIR)/*.md; do \
			if [ -f "$$cmd" ]; then \
				name=$$(basename "$$cmd"); \
				if [ -f "$(OPENCODE_COMMANDS)/$$name" ]; then \
					rm -f "$(OPENCODE_COMMANDS)/$$name"; \
					echo "  ✓ Removed OpenCode command: $$name"; \
				fi; \
			fi; \
		done; \
	fi
	@# Remove Codex instructions (only if they contain Developer Kit marker)
	@if [ -f "$(CODEX_INSTRUCTIONS)" ] && grep -q "Developer Kit" "$(CODEX_INSTRUCTIONS)" 2>/dev/null; then \
		rm -f "$(CODEX_INSTRUCTIONS)"; \
		echo "  ✓ Removed Codex instructions"; \
	fi
	@# Remove Codex prompts installed from this devkit
	@if [ -d "$(CODEX_PROMPTS)" ]; then \
		for cmd in $(COMMANDS_DIR)/*.md; do \
			if [ -f "$$cmd" ]; then \
				name=$$(basename "$$cmd"); \
				if [ -f "$(CODEX_PROMPTS)/$$name" ]; then \
					rm -f "$(CODEX_PROMPTS)/$$name"; \
					echo "  ✓ Removed Codex prompt: $$name"; \
				fi; \
			fi; \
		done; \
	fi
	@echo ""
	@echo -e "$(GREEN)✓ Uninstallation complete$(NC)"

# ═══════════════════════════════════════════════════════════════
# LISTING
# ═══════════════════════════════════════════════════════════════

list-agents:
	@echo ""
	@echo -e "$(BLUE)Available Agents:$(NC)"
	@echo ""
	@for agent in $(AGENTS_DIR)/*.md; do \
		if [ -f "$$agent" ]; then \
			name=$$(basename "$$agent" .md); \
			desc=$$(head -10 "$$agent" | grep -E '^>' | head -1 | sed 's/^> //'); \
			printf "  $(GREEN)%-40s$(NC) %s\n" "$$name" "$$desc"; \
		fi; \
	done
	@echo ""

list-commands:
	@echo ""
	@echo -e "$(BLUE)Available Commands:$(NC)"
	@echo ""
	@for cmd in $(COMMANDS_DIR)/*.md; do \
		if [ -f "$$cmd" ]; then \
			name=$$(basename "$$cmd" .md); \
			desc=$$(head -10 "$$cmd" | grep -E '^>' | head -1 | sed 's/^> //'); \
			printf "  $(GREEN)%-45s$(NC) %s\n" "$$name" "$$desc"; \
		fi; \
	done
	@echo ""

list-skills:
	@echo ""
	@echo -e "$(BLUE)Available Skills:$(NC)"
	@echo ""
	@for category in $(SKILLS_DIR)/*/; do \
		if [ -d "$$category" ]; then \
			catname=$$(basename "$$category"); \
			echo -e "  $(YELLOW)$$catname:$(NC)"; \
			for skill in $$category*/; do \
				if [ -d "$$skill" ]; then \
					skillname=$$(basename "$$skill"); \
					echo "    - $$skillname"; \
				fi; \
			done; \
			echo ""; \
		fi; \
	done

# ═══════════════════════════════════════════════════════════════
# CLEAN
# ═══════════════════════════════════════════════════════════════

clean:
	@echo -e "$(BLUE)Cleaning generated files...$(NC)"
	@rm -f $(DEVKIT_DIR)/*.tmp
	@echo -e "$(GREEN)✓ Clean complete$(NC)"
