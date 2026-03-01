#!/bin/bash
# Developer Kit Rules Interactive Installer
# Usage: install-rules.sh [target_path]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
DEVKIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLUGINS_DIR="$DEVKIT_DIR/plugins"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}       Developer Kit Rules Interactive Installer${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Target path from argument or ask interactively
if [[ -n "$1" ]]; then
    project_path="$1"
    echo -e "${GREEN}Target path provided:${NC} $project_path"
else
    echo -e "${GREEN}Step 1: Target Project${NC}"
    read -p "Enter the project path (absolute or relative, or press Enter for current directory): " project_path
    if [[ -z "$project_path" ]]; then
        project_path="."
    fi
fi

# Resolve target path
if [[ ! -d "$project_path" ]]; then
    echo -n -e "${YELLOW}⚠ $project_path does not exist. Create it? (y/N): ${NC}"
    read create_dir
    if [[ "$create_dir" != "y" && "$create_dir" != "Y" ]]; then
        echo -e "${RED}✗ Installation cancelled.${NC}"
        exit 1
    fi
    mkdir -p "$project_path"
fi

TARGET_PROJECT="$(cd "$project_path" && pwd)"
RULES_DIR="$TARGET_PROJECT/.claude/rules"

echo -e "${GREEN}Target Project:${NC} $TARGET_PROJECT"
echo -e "${GREEN}Rules Directory:${NC} $RULES_DIR"
echo ""

# Discover plugins with rules
echo -e "${BLUE}Scanning for available rules...${NC}"
echo ""

declare -a PLUGIN_NAMES
declare -a PLUGIN_RULES_DIRS
declare -a PLUGIN_RULES_COUNTS

plugin_num=0
for plugin_dir in "$PLUGINS_DIR"/*/; do
    if [[ -d "$plugin_dir/rules" ]]; then
        plugin_num=$((plugin_num + 1))
        plugin_name=$(basename "$plugin_dir")
        rule_count=$(ls -1 "$plugin_dir/rules/"*.md 2>/dev/null | wc -l | tr -d ' ')

        PLUGIN_NAMES[$plugin_num]="$plugin_name"
        PLUGIN_RULES_DIRS[$plugin_num]="$plugin_dir/rules"
        PLUGIN_RULES_COUNTS[$plugin_num]="$rule_count"
    fi
done

if [[ $plugin_num -eq 0 ]]; then
    echo -e "${RED}✗ No plugins with rules found.${NC}"
    exit 1
fi

# Show available plugins
echo -e "${GREEN}Available Rule Sets ($plugin_num plugin(s)):${NC}"
echo ""

for i in $(seq 1 $plugin_num); do
    printf "  ${CYAN}%2d)${NC} ${GREEN}%-35s${NC} (%s rules)\n" "$i" "${PLUGIN_NAMES[$i]}" "${PLUGIN_RULES_COUNTS[$i]}"
done

echo ""
echo -e "  ${CYAN} a)${NC} Install all rules"
echo -e "  ${CYAN} l)${NC} List rules for a plugin"
echo -e "  ${CYAN} q)${NC} Quit"
echo ""

read -p "Select option: " selection

# Handle list option
if [[ "$selection" == "l" || "$selection" == "L" ]]; then
    echo ""
    read -p "Enter plugin number to list rules: " list_num
    if [[ "$list_num" =~ ^[0-9]+$ ]] && [[ $list_num -ge 1 ]] && [[ $list_num -le $plugin_num ]]; then
        echo ""
        echo -e "${GREEN}Rules in ${PLUGIN_NAMES[$list_num]}:${NC}"
        echo ""
        for rule_file in "${PLUGIN_RULES_DIRS[$list_num]}"/*.md; do
            if [[ -f "$rule_file" ]]; then
                rule_name=$(basename "$rule_file" .md)
                # Extract globs pattern from frontmatter
                globs=$(head -10 "$rule_file" | grep -E '^globs:' | head -1 | sed 's/^globs: *//' | sed 's/^"//;s/"$//')
                if [[ -z "$globs" ]]; then
                    globs="no pattern"
                fi
                printf "  • ${GREEN}%-40s${NC} %s\n" "$rule_name" "$globs"
            fi
        done
        echo ""
        read -p "Press Enter to continue with installation..."
        # After listing, ask for selection again
        echo ""
        echo -e "${GREEN}Available Rule Sets:${NC}"
        echo ""
        for i in $(seq 1 $plugin_num); do
            printf "  ${CYAN}%2d)${NC} ${GREEN}%-35s${NC} (%s rules)\n" "$i" "${PLUGIN_NAMES[$i]}" "${PLUGIN_RULES_COUNTS[$i]}"
        done
        echo ""
        echo -e "  ${CYAN} a)${NC} Install all rules"
        echo -e "  ${CYAN} q)${NC} Quit"
        echo ""
        read -p "Select plugins to install (comma-separated numbers, or 'all'): " selection
    else
        echo -e "${RED}Invalid plugin number.${NC}"
        exit 1
    fi
fi

# Handle quit option
if [[ "$selection" == "q" || "$selection" == "Q" ]]; then
    echo -e "${YELLOW}Installation cancelled.${NC}"
    exit 0
fi

# Create rules directory
mkdir -p "$RULES_DIR"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}ℹ Installing Rules...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

total_rules=0
installed_plugins=0

for i in $(seq 1 $plugin_num); do
    should_install=false

    if [[ "$selection" == "a" || "$selection" == "A" || "$selection" == "all" ]]; then
        should_install=true
    else
        # Check if this plugin number is in the selection
        for num in $(echo "$selection" | tr ',' ' '); do
            if [[ "$num" == "$i" ]]; then
                should_install=true
                break
            fi
        done
    fi

    if [[ "$should_install" == true ]]; then
        plugin_name="${PLUGIN_NAMES[$i]}"
        plugin_rules_dir="${PLUGIN_RULES_DIRS[$i]}"
        target_plugin_dir="$RULES_DIR/$plugin_name"

        mkdir -p "$target_plugin_dir"

        echo -e "${CYAN}Installing rules from: $plugin_name${NC}"

        plugin_rule_count=0
        for rule_file in "$plugin_rules_dir"/*.md; do
            if [[ -f "$rule_file" ]]; then
                rule_name=$(basename "$rule_file")
                cp "$rule_file" "$target_plugin_dir/"
                echo -e "  ${GREEN}✓${NC} $rule_name"
                plugin_rule_count=$((plugin_rule_count + 1))
            fi
        done

        total_rules=$((total_rules + plugin_rule_count))
        installed_plugins=$((installed_plugins + 1))
        echo ""
    fi
done

if [[ $total_rules -eq 0 ]]; then
    echo -e "${YELLOW}⚠ No rules were installed.${NC}"
    exit 0
fi

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Rules installation complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Installed $total_rules rules from $installed_plugins plugin(s)."
echo ""
echo -e "${CYAN}Location:${NC} $RULES_DIR"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Rules are now active in your project"
echo "  2. Claude Code will automatically apply them to matching files"
echo "  3. Use 'make list-rules' to see all available rules"
echo ""
