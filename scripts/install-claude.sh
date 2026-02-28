#!/bin/bash
# Claude Code Interactive Developer Kit Installer Script
# Usage: install-claude.sh "<plugin_json_files>"

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get plugin files from argument
PLUGIN_JSON_FILES="$1"
DEVKIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Confirm installation
read -p "Are you installing for Claude Code? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo -e "${RED}✗ Installation cancelled.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Step 1: Target Project${NC}"
read -p "Enter the project path (absolute or relative, or press Enter for current directory): " project_path

if [[ -z "$project_path" ]]; then
    project_path="."
fi

if [[ ! -d "$project_path" ]]; then
    echo -n "  ⚠ $project_path does not exist. Create it? (y/N): "
    read create_dir
    if [[ "$create_dir" != "y" && "$create_dir" != "Y" ]]; then
        echo -e "${RED}✗ Installation cancelled.${NC}"
        exit 1
    fi
    mkdir -p "$project_path"
fi

TARGET_PROJECT="$(cd "$project_path" && pwd)"
TARGET_DIR="$TARGET_PROJECT/.claude"

mkdir -p "$TARGET_DIR/agents"
mkdir -p "$TARGET_DIR/commands"
mkdir -p "$TARGET_DIR/skills"
mkdir -p "$TARGET_DIR/rules"

echo "  → Target: $TARGET_PROJECT"
echo ""

# List available plugins
echo -e "${GREEN}Step 2: Available Plugins${NC}"
echo ""

declare -a PLUGIN_NAMES
declare -a PLUGIN_PATHS
declare -a PLUGIN_DIRS
declare -a PLUGIN_BASE_DIRS

plugin_num=0
for plugin_json in $PLUGIN_JSON_FILES; do
    if [[ -f "$plugin_json" ]]; then
        plugin_num=$((plugin_num + 1))
        plugin_name=$(jq -r '.name' "$plugin_json" 2>/dev/null || echo "unknown")
        plugin_desc=$(jq -r '.description' "$plugin_json" 2>/dev/null || echo "")
        num_agents=$(jq -r '.agents | length' "$plugin_json" 2>/dev/null || echo "0")
        num_commands=$(jq -r '.commands | length' "$plugin_json" 2>/dev/null || echo "0")
        num_skills=$(jq -r '.skills | length' "$plugin_json" 2>/dev/null || echo "0")
        num_rules=$(jq -r '.rules | length' "$plugin_json" 2>/dev/null || echo "0")

        PLUGIN_NAMES[$plugin_num]="$plugin_name"
        PLUGIN_PATHS[$plugin_num]="$plugin_json"
        PLUGIN_DIRS[$plugin_num]=$(dirname "$plugin_json")
        PLUGIN_BASE_DIRS[$plugin_num]=$(dirname "$(dirname "$plugin_json")")

        printf "  %2d) ${GREEN}%s${NC}\n" "$plugin_num" "$plugin_name"
        echo "      $plugin_desc"
        echo "      Components: $num_agents agents, $num_commands commands, $num_skills skills, $num_rules rules"
        echo ""
    fi
done

if [[ $plugin_num -eq 0 ]]; then
    echo -e "${RED}✗ No plugins found.${NC}"
    exit 1
fi

read -p "Select plugins to install (comma-separated numbers, or 'all'): " selected_plugins

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}ℹ Starting Installation...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

installed_count=0
skipped_count=0

# Install selected plugins
for ((i=1; i<=plugin_num; i++)); do
    should_install=0

    if [[ "$selected_plugins" == "all" ]]; then
        should_install=1
    else
        # Check if current plugin number is in selected list
        for num in $(echo "$selected_plugins" | tr ',' ' '); do
            if [[ "$num" == "$i" ]]; then
                should_install=1
                break
            fi
        done
    fi

    if [[ "$should_install" == "1" ]]; then
        plugin_json="${PLUGIN_PATHS[$i]}"
        base_dir="${PLUGIN_BASE_DIRS[$i]}"
        plugin_name="${PLUGIN_NAMES[$i]}"

        echo ""
        echo -e "${CYAN}Installing from: $plugin_name${NC}"

        # Install agents
        agents=$(jq -r '.agents[]? // empty' "$plugin_json" 2>/dev/null)
        if [[ -n "$agents" ]]; then
            for agent in $agents; do
                agent_path="$base_dir/$agent"
                if [[ -f "$agent_path" ]]; then
                    agent_name=$(basename "$agent")
                    target_file="$TARGET_DIR/agents/$agent_name"

                    if [[ -f "$target_file" ]]; then
                        echo -n "  ⚠ $agent_name already exists. [O]verwrite, [S]kip, [R]ename? "
                        read -n 1 conflict_action
                        echo ""
                        case $conflict_action in
                            O|o)
                                cp "$agent_path" "$target_file"
                                echo "    ✓ Overwritten: $agent_name"
                                installed_count=$((installed_count + 1))
                                ;;
                            R|r)
                                read -p "    Enter new name: " new_name
                                cp "$agent_path" "$TARGET_DIR/agents/$new_name.md"
                                echo "    ✓ Installed as: $new_name.md"
                                installed_count=$((installed_count + 1))
                                ;;
                            *)
                                echo "    ○ Skipped: $agent_name"
                                skipped_count=$((skipped_count + 1))
                                ;;
                        esac
                    else
                        cp "$agent_path" "$target_file"
                        echo "  ✓ Agent: $agent_name"
                        installed_count=$((installed_count + 1))
                    fi
                fi
            done
        fi

        # Install commands
        commands=$(jq -r '.commands[]? // empty' "$plugin_json" 2>/dev/null)
        if [[ -n "$commands" ]]; then
            for cmd in $commands; do
                cmd_path="$base_dir/$cmd"
                if [[ -f "$cmd_path" ]]; then
                    cmd_name=$(basename "$cmd")
                    cmd_subdir=$(dirname "$cmd")
                    cmd_subdir_rel=""

                    if [[ "$cmd_subdir" != "." ]]; then
                        cmd_subdir_rel=$(echo "$cmd_subdir" | sed 's|^\./commands||' | sed 's|^\./commands/||')
                        if [[ -n "$cmd_subdir_rel" ]]; then
                            mkdir -p "$TARGET_DIR/commands/$cmd_subdir_rel"
                            target_file="$TARGET_DIR/commands/$cmd_subdir_rel/$cmd_name"
                        else
                            target_file="$TARGET_DIR/commands/$cmd_name"
                        fi
                    else
                        target_file="$TARGET_DIR/commands/$cmd_name"
                    fi

                    if [[ -f "$target_file" ]]; then
                        echo -n "  ⚠ $cmd_name already exists. [O]verwrite, [S]kip, [R]ename? "
                        read -n 1 conflict_action
                        echo ""
                        case $conflict_action in
                            O|o)
                                cp "$cmd_path" "$target_file"
                                echo "    ✓ Overwritten: $cmd_name"
                                installed_count=$((installed_count + 1))
                                ;;
                            R|r)
                                read -p "    Enter new name: " new_name
                                if [[ -n "$cmd_subdir_rel" ]]; then
                                    cp "$cmd_path" "$TARGET_DIR/commands/$cmd_subdir_rel/$new_name.md"
                                else
                                    cp "$cmd_path" "$TARGET_DIR/commands/$new_name.md"
                                fi
                                echo "    ✓ Installed as: $new_name.md"
                                installed_count=$((installed_count + 1))
                                ;;
                            *)
                                echo "    ○ Skipped: $cmd_name"
                                skipped_count=$((skipped_count + 1))
                                ;;
                        esac
                    else
                        cp "$cmd_path" "$target_file"
                        echo "  ✓ Command: $cmd_name"
                        installed_count=$((installed_count + 1))
                    fi
                fi
            done
        fi

        # Install skills
        skills=$(jq -r '.skills[]? // empty' "$plugin_json" 2>/dev/null)
        if [[ -n "$skills" ]]; then
            for skill_pattern in $skills; do
                for skill_dir in $base_dir/$skill_pattern; do
                    if [[ -d "$skill_dir" ]]; then
                        skill_name=$(basename "$skill_dir")
                        target_skill_dir="$TARGET_DIR/skills/$skill_name"

                        if [[ -d "$target_skill_dir" ]]; then
                            echo -n "  ⚠ $skill_name already exists. [O]verwrite, [S]kip, [R]ename? "
                            read -n 1 conflict_action
                            echo ""
                            case $conflict_action in
                                O|o)
                                    rm -rf "$target_skill_dir"
                                    cp -r "$skill_dir" "$target_skill_dir"
                                    echo "    ✓ Overwritten: $skill_name"
                                    installed_count=$((installed_count + 1))
                                    ;;
                                R|r)
                                    read -p "    Enter new name: " new_name
                                    cp -r "$skill_dir" "$TARGET_DIR/skills/$new_name"
                                    echo "    ✓ Installed as: $new_name"
                                    installed_count=$((installed_count + 1))
                                    ;;
                                *)
                                    echo "    ○ Skipped: $skill_name"
                                    skipped_count=$((skipped_count + 1))
                                    ;;
                            esac
                        else
                            cp -r "$skill_dir" "$target_skill_dir"
                            echo "  ✓ Skill: $skill_name"
                            installed_count=$((installed_count + 1))
                        fi
                    fi
                done
            done
        fi

        # Install rules
        rules=$(jq -r '.rules[]? // empty' "$plugin_json" 2>/dev/null)
        if [[ -n "$rules" ]]; then
            rules_target_dir="$TARGET_DIR/rules/$plugin_name"
            mkdir -p "$rules_target_dir"
            for rule in $rules; do
                rule_path="$base_dir/$rule"
                if [[ -f "$rule_path" ]]; then
                    rule_name=$(basename "$rule")
                    target_file="$rules_target_dir/$rule_name"

                    if [[ -f "$target_file" ]]; then
                        echo -n "  ⚠ Rule $rule_name already exists. [O]verwrite, [S]kip? "
                        read -n 1 conflict_action
                        echo ""
                        case $conflict_action in
                            O|o)
                                cp "$rule_path" "$target_file"
                                echo "    ✓ Overwritten: $rule_name"
                                installed_count=$((installed_count + 1))
                                ;;
                            *)
                                echo "    ○ Skipped: $rule_name"
                                skipped_count=$((skipped_count + 1))
                                ;;
                        esac
                    else
                        cp "$rule_path" "$target_file"
                        echo "  ✓ Rule: $plugin_name/$rule_name"
                        installed_count=$((installed_count + 1))
                    fi
                fi
            done
        fi
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  Target directory: $TARGET_DIR/"
echo "  Files installed:  $installed_count"
echo "  Files skipped:    $skipped_count"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Navigate to your project: cd $TARGET_PROJECT"
echo "  2. Start Claude Code in the project directory"
echo "  3. Your skills, agents, and commands are now available!"
echo ""
echo -e "${YELLOW}Usage:${NC}"
echo "  - Skills are automatically discovered by Claude"
echo "  - Rules are loaded from .claude/rules/ to enforce coding standards"
echo "  - Use @agent-name to invoke agents"
echo "  - Use /command-name to run commands"
echo ""
