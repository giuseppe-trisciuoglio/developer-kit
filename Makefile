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
COPILOT_CONFIG := $(HOME)/.config/github-copilot
COPILOT_INSTRUCTIONS := $(COPILOT_CONFIG)/intellij/global-copilot-instructions.md
OPENCODE_CONFIG := $(HOME)/.config/opencode
OPENCODE_PROMPTS := $(OPENCODE_CONFIG)/prompts
OPENCODE_JSON := $(OPENCODE_CONFIG)/opencode.json
CODEX_CONFIG := $(HOME)/.codex
CODEX_INSTRUCTIONS := $(CODEX_CONFIG)/instructions.md

# Backup directory
BACKUP_DIR := $(HOME)/.devkit-backups/$(shell date +%Y%m%d_%H%M%S)

# Default target
all: help

help:
	@echo ""
	@echo "$(BLUE)╔═══════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║       Developer Kit - Multi-CLI Installation Tool             ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC)"
	@echo "  make install              Install for all detected CLIs"
	@echo "  make install-copilot      Install only for GitHub Copilot CLI"
	@echo "  make install-opencode     Install only for OpenCode CLI"
	@echo "  make install-codex        Install only for Codex CLI"
	@echo ""
	@echo "$(GREEN)Management:$(NC)"
	@echo "  make status               Show installation status for all CLIs"
	@echo "  make uninstall            Remove all Developer Kit installations"
	@echo "  make backup               Create backup of current configs"
	@echo "  make clean                Remove generated files"
	@echo ""
	@echo "$(GREEN)Information:$(NC)"
	@echo "  make list-agents          List available agents"
	@echo "  make list-commands        List available commands"
	@echo "  make list-skills          List available skills"
	@echo ""

# ═══════════════════════════════════════════════════════════════
# STATUS
# ═══════════════════════════════════════════════════════════════

status:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)              Developer Kit Installation Status                $(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)GitHub Copilot CLI:$(NC)"
	@if [ -d "$(COPILOT_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(COPILOT_CONFIG)"; \
		if [ -f "$(COPILOT_INSTRUCTIONS)" ] && grep -q "Developer Kit" "$(COPILOT_INSTRUCTIONS)" 2>/dev/null; then \
			echo "  ✓ $(GREEN)Developer Kit installed$(NC)"; \
		else \
			echo "  ○ Developer Kit not installed"; \
		fi; \
	else \
		echo "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)OpenCode CLI:$(NC)"
	@if [ -d "$(OPENCODE_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(OPENCODE_CONFIG)"; \
		if [ -d "$(OPENCODE_PROMPTS)/devkit" ]; then \
			echo "  ✓ $(GREEN)Developer Kit installed$(NC)"; \
		else \
			echo "  ○ Developer Kit not installed"; \
		fi; \
	else \
		echo "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)Codex CLI:$(NC)"
	@if [ -d "$(CODEX_CONFIG)" ]; then \
		echo "  ✓ Config directory exists: $(CODEX_CONFIG)"; \
		if [ -f "$(CODEX_INSTRUCTIONS)" ] && grep -q "Developer Kit" "$(CODEX_INSTRUCTIONS)" 2>/dev/null; then \
			echo "  ✓ $(GREEN)Developer Kit installed$(NC)"; \
		else \
			echo "  ○ Developer Kit not installed"; \
		fi; \
	else \
		echo "  ✗ $(RED)Not configured$(NC)"; \
	fi
	@echo ""

# ═══════════════════════════════════════════════════════════════
# INSTALL ALL
# ═══════════════════════════════════════════════════════════════

install: backup
	@echo ""
	@echo "$(BLUE)Installing Developer Kit for all detected CLIs...$(NC)"
	@echo ""
	@$(MAKE) -s install-copilot-if-exists
	@$(MAKE) -s install-opencode-if-exists
	@$(MAKE) -s install-codex-if-exists
	@echo ""
	@echo "$(GREEN)✓ Installation complete!$(NC)"
	@$(MAKE) -s status

install-copilot-if-exists:
	@if [ -d "$(COPILOT_CONFIG)" ]; then \
		$(MAKE) -s install-copilot; \
	else \
		echo "$(YELLOW)⚠ Skipping Copilot CLI (not configured)$(NC)"; \
	fi

install-opencode-if-exists:
	@if [ -d "$(OPENCODE_CONFIG)" ]; then \
		$(MAKE) -s install-opencode; \
	else \
		echo "$(YELLOW)⚠ Skipping OpenCode CLI (not configured)$(NC)"; \
	fi

install-codex-if-exists:
	@if [ -d "$(CODEX_CONFIG)" ]; then \
		$(MAKE) -s install-codex; \
	else \
		echo "$(YELLOW)⚠ Skipping Codex CLI (not configured)$(NC)"; \
	fi

# ═══════════════════════════════════════════════════════════════
# COPILOT CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-copilot:
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(BLUE)Installing Developer Kit for GitHub Copilot CLI$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@mkdir -p $(COPILOT_CONFIG)/intellij
	@echo "# Developer Kit for GitHub Copilot" > $(COPILOT_INSTRUCTIONS)
	@echo "# Auto-generated by Developer Kit Makefile" >> $(COPILOT_INSTRUCTIONS)
	@echo "# Source: $(DEVKIT_DIR)" >> $(COPILOT_INSTRUCTIONS)
	@echo "" >> $(COPILOT_INSTRUCTIONS)
	@echo "## Available Agents" >> $(COPILOT_INSTRUCTIONS)
	@echo "" >> $(COPILOT_INSTRUCTIONS)
	@for agent in $(AGENTS_DIR)/*.md; do \
		if [ -f "$$agent" ]; then \
			name=$$(basename "$$agent" .md); \
			echo "### $$name" >> $(COPILOT_INSTRUCTIONS); \
			echo "" >> $(COPILOT_INSTRUCTIONS); \
			cat "$$agent" >> $(COPILOT_INSTRUCTIONS); \
			echo "" >> $(COPILOT_INSTRUCTIONS); \
			echo "---" >> $(COPILOT_INSTRUCTIONS); \
			echo "" >> $(COPILOT_INSTRUCTIONS); \
		fi; \
	done
	@echo "" >> $(COPILOT_INSTRUCTIONS)
	@echo "## Available Commands" >> $(COPILOT_INSTRUCTIONS)
	@echo "" >> $(COPILOT_INSTRUCTIONS)
	@echo "Use these commands by typing the command name:" >> $(COPILOT_INSTRUCTIONS)
	@echo "" >> $(COPILOT_INSTRUCTIONS)
	@for cmd in $(COMMANDS_DIR)/*.md; do \
		if [ -f "$$cmd" ]; then \
			name=$$(basename "$$cmd" .md); \
			echo "- **$$name**: $$(head -5 "$$cmd" | grep -E '^>' | head -1 | sed 's/^> //')" >> $(COPILOT_INSTRUCTIONS); \
		fi; \
	done
	@echo "" >> $(COPILOT_INSTRUCTIONS)
	@echo "$(GREEN)✓ Copilot CLI installation complete$(NC)"
	@echo "  Instructions file: $(COPILOT_INSTRUCTIONS)"

# ═══════════════════════════════════════════════════════════════
# OPENCODE CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-opencode:
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(BLUE)Installing Developer Kit for OpenCode CLI$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@mkdir -p $(OPENCODE_PROMPTS)/devkit
	@# Copy agents as prompt files
	@for agent in $(AGENTS_DIR)/*.md; do \
		if [ -f "$$agent" ]; then \
			name=$$(basename "$$agent" .md); \
			cp "$$agent" "$(OPENCODE_PROMPTS)/devkit/$$name.txt"; \
			echo "  ✓ Agent: $$name"; \
		fi; \
	done
	@# Copy commands as prompt files
	@for cmd in $(COMMANDS_DIR)/*.md; do \
		if [ -f "$$cmd" ]; then \
			name=$$(basename "$$cmd" .md); \
			cp "$$cmd" "$(OPENCODE_PROMPTS)/devkit/$$name.txt"; \
			echo "  ✓ Command: $$name"; \
		fi; \
	done
	@echo ""
	@echo "$(GREEN)✓ OpenCode CLI installation complete$(NC)"
	@echo "  Prompts directory: $(OPENCODE_PROMPTS)/devkit/"
	@echo ""
	@echo "$(YELLOW)Note: Add agents to opencode.json manually:$(NC)"
	@echo '  "agent": {'
	@echo '    "devkit-spring-boot-expert": {'
	@echo '      "description": "Spring Boot Backend Expert",'
	@echo '      "prompt": "{file:./prompts/devkit/spring-boot-backend-development-expert.txt}",'
	@echo '      "tools": {"write": true, "edit": true, "bash": true}'
	@echo '    }'
	@echo '  }'

# ═══════════════════════════════════════════════════════════════
# CODEX CLI INSTALLATION
# ═══════════════════════════════════════════════════════════════

install-codex:
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@echo "$(BLUE)Installing Developer Kit for Codex CLI$(NC)"
	@echo "$(BLUE)━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━$(NC)"
	@mkdir -p $(CODEX_CONFIG)
	@# Create or update instructions.md
	@echo "# Developer Kit Instructions for Codex CLI" > $(CODEX_INSTRUCTIONS)
	@echo "# Auto-generated by Developer Kit Makefile" >> $(CODEX_INSTRUCTIONS)
	@echo "# Source: $(DEVKIT_DIR)" >> $(CODEX_INSTRUCTIONS)
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@echo "You have access to the Developer Kit, a curated collection of skills and agents" >> $(CODEX_INSTRUCTIONS)
	@echo "for automating development tasks, focusing on Java/Spring Boot patterns." >> $(CODEX_INSTRUCTIONS)
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
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@echo "## Available Commands" >> $(CODEX_INSTRUCTIONS)
	@echo "" >> $(CODEX_INSTRUCTIONS)
	@for cmd in $(COMMANDS_DIR)/*.md; do \
		if [ -f "$$cmd" ]; then \
			name=$$(basename "$$cmd" .md); \
			echo "### $$name" >> $(CODEX_INSTRUCTIONS); \
			echo "" >> $(CODEX_INSTRUCTIONS); \
			cat "$$cmd" >> $(CODEX_INSTRUCTIONS); \
			echo "" >> $(CODEX_INSTRUCTIONS); \
			echo "---" >> $(CODEX_INSTRUCTIONS); \
			echo "" >> $(CODEX_INSTRUCTIONS); \
		fi; \
	done
	@echo "$(GREEN)✓ Codex CLI installation complete$(NC)"
	@echo "  Instructions file: $(CODEX_INSTRUCTIONS)"

# ═══════════════════════════════════════════════════════════════
# BACKUP
# ═══════════════════════════════════════════════════════════════

backup:
	@echo "$(BLUE)Creating backup of existing configurations...$(NC)"
	@mkdir -p $(BACKUP_DIR)
	@if [ -f "$(COPILOT_INSTRUCTIONS)" ]; then \
		cp "$(COPILOT_INSTRUCTIONS)" "$(BACKUP_DIR)/copilot-instructions.md" 2>/dev/null || true; \
		echo "  ✓ Backed up Copilot instructions"; \
	fi
	@if [ -d "$(OPENCODE_PROMPTS)/devkit" ]; then \
		cp -r "$(OPENCODE_PROMPTS)/devkit" "$(BACKUP_DIR)/opencode-devkit" 2>/dev/null || true; \
		echo "  ✓ Backed up OpenCode prompts"; \
	fi
	@if [ -f "$(CODEX_INSTRUCTIONS)" ]; then \
		cp "$(CODEX_INSTRUCTIONS)" "$(BACKUP_DIR)/codex-instructions.md" 2>/dev/null || true; \
		echo "  ✓ Backed up Codex instructions"; \
	fi
	@echo "  Backup location: $(BACKUP_DIR)"

# ═══════════════════════════════════════════════════════════════
# UNINSTALL
# ═══════════════════════════════════════════════════════════════

uninstall:
	@echo "$(BLUE)Removing Developer Kit installations...$(NC)"
	@echo ""
	@# Remove Copilot instructions (only if they contain Developer Kit marker)
	@if [ -f "$(COPILOT_INSTRUCTIONS)" ] && grep -q "Developer Kit" "$(COPILOT_INSTRUCTIONS)" 2>/dev/null; then \
		rm -f "$(COPILOT_INSTRUCTIONS)"; \
		echo "  ✓ Removed Copilot instructions"; \
	fi
	@# Remove OpenCode devkit prompts
	@if [ -d "$(OPENCODE_PROMPTS)/devkit" ]; then \
		rm -rf "$(OPENCODE_PROMPTS)/devkit"; \
		echo "  ✓ Removed OpenCode prompts"; \
	fi
	@# Remove Codex instructions (only if they contain Developer Kit marker)
	@if [ -f "$(CODEX_INSTRUCTIONS)" ] && grep -q "Developer Kit" "$(CODEX_INSTRUCTIONS)" 2>/dev/null; then \
		rm -f "$(CODEX_INSTRUCTIONS)"; \
		echo "  ✓ Removed Codex instructions"; \
	fi
	@echo ""
	@echo "$(GREEN)✓ Uninstallation complete$(NC)"

# ═══════════════════════════════════════════════════════════════
# LISTING
# ═══════════════════════════════════════════════════════════════

list-agents:
	@echo ""
	@echo "$(BLUE)Available Agents:$(NC)"
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
	@echo "$(BLUE)Available Commands:$(NC)"
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
	@echo "$(BLUE)Available Skills:$(NC)"
	@echo ""
	@for category in $(SKILLS_DIR)/*/; do \
		if [ -d "$$category" ]; then \
			catname=$$(basename "$$category"); \
			echo "  $(YELLOW)$$catname:$(NC)"; \
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
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	@rm -f $(DEVKIT_DIR)/*.tmp
	@echo "$(GREEN)✓ Clean complete$(NC)"
