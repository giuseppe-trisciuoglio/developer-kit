#!/usr/bin/env python3
"""
Ralph Loop - State Machine Orchestrator

This script manages the Ralph Loop state machine for specification-driven development.
It orchestrates task implementation, review, cleanup, and synchronization.

Usage:
    python3 ralph_loop.py --action=start --spec=docs/specs/001-feature/
    python3 ralph_loop.py --action=loop --spec=docs/specs/001-feature/
    python3 ralph_loop.py --action=status --spec=docs/specs/001-feature/
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


# Supported agents/CLIs and their slash commands
# Note: cmd_prefix is added BEFORE the template, so templates should NOT start with /
# Use {task} placeholder for task ID, {spec} for spec path
SUPPORTED_AGENTS = {
    "claude": {
        "name": "Claude Code",
        "cmd_prefix": "/",
        "task_impl": "developer-kit-specs:specs.task-implementation --spec={spec} --task={task}",
        "task_review": "developer-kit-specs:specs.task-review --spec={spec} --task={task}",
        "spec_sync": "developer-kit-specs:specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "codex": {
        "name": "Codex CLI",
        "cmd_prefix": "$",
        "task_impl": "specs.task-implementation --spec={spec} --task={task}",
        "task_review": "specs.task-review --spec={spec} --task={task}",
        "spec_sync": "specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "copilot": {
        "name": "GitHub Copilot CLI",
        "cmd_prefix": "/",
        "task_impl": "specs.task-implementation --spec={spec} --task={task}",
        "task_review": "specs.task-review --spec={spec} --task={task}",
        "spec_sync": "specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "kimi": {
        "name": "Kimi CLI",
        "cmd_prefix": "/skill:",
        "task_impl": "specs.task-implementation --spec={spec} --task={task}",
        "task_review": "specs.task-review --spec={spec} --task={task}",
        "spec_sync": "specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "gemini": {
        "name": "Gemini CLI",
        "cmd_prefix": "/",
        "task_impl": "specs.task-implementation --spec={spec} --task={task}",
        "task_review": "specs.task-review --spec={spec} --task={task}",
        "spec_sync": "specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "glm4": {
        "name": "GLM-4 CLI",
        "cmd_prefix": "/",
        "task_impl": "developer-kit-specs:specs.task-implementation --spec={spec} --task={task}",
        "task_review": "developer-kit-specs:specs.task-review --spec={spec} --task={task}",
        "spec_sync": "developer-kit-specs:specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "minimax": {
        "name": "MiniMax CLI",
        "cmd_prefix": "/",
        "task_impl": "developer-kit-specs:specs.task-implementation --spec={spec} --task={task}",
        "task_review": "developer-kit-specs:specs.task-review --spec={spec} --task={task}",
        "spec_sync": "developer-kit-specs:specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "openrouter": {
        "name": "OpenRouter CLI",
        "cmd_prefix": "/",
        "task_impl": "developer-kit-specs:specs.task-implementation --spec={spec} --task={task}",
        "task_review": "developer-kit-specs:specs.task-review --spec={spec} --task={task}",
        "spec_sync": "developer-kit-specs:specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
    "qwen": {
        "name": "Qwen Code",
        "cmd_prefix": "/",
        "task_impl": "developer-kit-specs:specs.task-implementation --spec={spec} --task={task}",
        "task_review": "developer-kit-specs:specs.task-review --spec={spec} --task={task}",
        "spec_sync": "developer-kit-specs:specs.spec-sync-with-code --spec={spec} --after-task={task}",
        "code_cleanup": "specs-code-cleanup --spec={spec} --task={task}",
        "ralph_loop": "ralph-loop --action=loop --spec={spec}",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ralph Loop State Machine - Orchestrates specification-driven development"
    )
    parser.add_argument(
        "--action", required=True,
        choices=["start", "loop", "status", "resume", "next"],
        help="Action to execute: start (initialize), loop (run one step), status (show state), resume (continue), next (advance to next step)"
    )
    parser.add_argument(
        "--spec", required=True,
        help="Path to specification folder (e.g. docs/specs/001-feature/)"
    )
    parser.add_argument(
        "--from-task", default=None,
        help="Start task for range filter (e.g. TASK-036)"
    )
    parser.add_argument(
        "--to-task", default=None,
        help="End task for range filter (e.g. TASK-041)"
    )
    parser.add_argument(
        "--agent", default="claude",
        choices=list(SUPPORTED_AGENTS.keys()),
        help="Default agent/CLI to use for tasks"
    )
    parser.add_argument(
        "--no-commit", action="store_true",
        help="Skip git commits (useful for testing)"
    )
    return parser.parse_args()


def validate_spec_path(spec_path: str) -> bool:
    """
    Validates that the spec path follows the correct structure.

    Correct format: docs/specs/[ID-feature]/ or [ID-feature]/
    """
    spec_dir = Path(spec_path).resolve()

    # Check if path exists
    if not spec_dir.exists():
        return False

    # Check if it's a directory
    if not spec_dir.is_dir():
        return False

    # Check if it looks like a spec folder (should contain spec files or tasks/)
    has_spec_files = any(spec_dir.glob("*.md"))
    has_tasks_dir = (spec_dir / "tasks").exists()
    has_ralph_dir = (spec_dir / "_ralph_loop").exists()

    if not (has_spec_files or has_tasks_dir or has_ralph_dir):
        return False

    return True


def get_fix_plan_path(spec_path: str) -> Path:
    """
    Returns the path to fix_plan.json.

    IMPORTANT: The file MUST ALWAYS be in docs/specs/[ID-feature]/_ralph_loop/fix_plan.json
    This is the ONLY valid location to prevent LLMs from creating files in wrong locations.
    """
    spec_dir = Path(spec_path)

    # The ONLY valid location: _ralph_loop subdirectory
    ralph_path = spec_dir / "_ralph_loop" / "fix_plan.json"

    # For backwards compatibility: if file exists in root, warn and migrate
    direct_path = spec_dir / "fix_plan.json"
    if direct_path.exists():
        print(f"⚠️  WARNING: fix_plan.json found in wrong location: {direct_path}")
        print(f"   Valid location is: {ralph_path}")
        print(f"   Please move it manually:")
        print(f"   mkdir -p {spec_dir}/_ralph_loop")
        print(f"   mv {direct_path} {ralph_path}")
        # Still return the old path for now to allow migration
        return direct_path

    return ralph_path


def load_fix_plan(spec_path: str) -> dict:
    """Loads fix_plan.json"""
    fix_plan_path = get_fix_plan_path(spec_path)
    if not fix_plan_path.exists():
        print(f"❌ fix_plan.json not found in {spec_path}")
        print(f"   Run first: --action=start")
        sys.exit(1)

    with open(fix_plan_path) as f:
        return json.load(f)


def save_fix_plan(spec_path: str, data: dict):
    """
    Saves fix_plan.json to the correct location.

    IMPORTANT: The file MUST ALWAYS be in docs/specs/[ID-feature]/_ralph_loop/fix_plan.json
    This function enforces the correct directory structure.
    """
    spec_dir = Path(spec_path)

    # ALWAYS use _ralph_loop subdirectory - this is the ONLY valid location
    ralph_dir = spec_dir / "_ralph_loop"
    fix_plan_path = ralph_dir / "fix_plan.json"

    # Create _ralph_loop directory if it doesn't exist
    ralph_dir.mkdir(parents=True, exist_ok=True)

    # For backwards compatibility: if old file exists in root, migrate it
    old_path = spec_dir / "fix_plan.json"
    if old_path.exists() and not fix_plan_path.exists():
        print(f"📦 Migrating fix_plan.json to correct location...")
        import shutil
        shutil.move(old_path, fix_plan_path)
        print(f"   ✅ Migrated to: {fix_plan_path}")

    # Update timestamp
    data["state"]["last_updated"] = datetime.now().isoformat()

    # Save with proper formatting
    with open(fix_plan_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # Add trailing newline


def find_tasks_file(spec_path: str) -> Optional[Path]:
    """Finds the tasks file in the specification folder"""
    spec_dir = Path(spec_path)

    # Look for files ending with --tasks.md
    for file in spec_dir.glob("*--tasks.md"):
        return file

    # Look in tasks subdirectory
    tasks_subdir = spec_dir / "tasks"
    if tasks_subdir.exists():
        for file in tasks_subdir.glob("*--tasks.md"):
            return file
        tasks_file = tasks_subdir / "tasks.md"
        if tasks_file.exists():
            return tasks_file

    # Look for generic tasks.md
    tasks_file = spec_dir / "tasks.md"
    if tasks_file.exists():
        return tasks_file

    return None


def find_task_files(spec_path: str) -> List[Path]:
    """Finds all individual task files (TASK-XXX.md)"""
    spec_dir = Path(spec_path)
    task_files = []

    # Look in tasks subdirectory (exclude --review and other auxiliary files)
    tasks_dir = spec_dir / "tasks"
    if tasks_dir.exists():
        task_files.extend(sorted(f for f in tasks_dir.glob("TASK-*.md") if "--" not in f.stem))

    return task_files


def parse_task_file(task_file: Path) -> dict:
    """Parses a single task file to extract metadata"""
    with open(task_file) as f:
        content = f.read()

    task_id = task_file.stem  # TASK-XXX
    task_data = {
        "id": task_id,
        "file": str(task_file),
        "title": "",
        "description": "",
        "status": "pending",
        "lang": "",
        "dependencies": [],
        "complexity": "medium",
        "agent": None,
    }

    # Parse YAML frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # Extract fields (strip quotes in case YAML values are quoted)
        id_match = re.search(r'^id:\s*(.+)$', frontmatter, re.MULTILINE)
        if id_match:
            task_data["id"] = id_match.group(1).strip().strip('"\'')

        title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
        if title_match:
            task_data["title"] = title_match.group(1).strip().strip('"\'')

        status_match = re.search(r'^status:\s*(.+)$', frontmatter, re.MULTILINE)
        if status_match:
            task_data["status"] = status_match.group(1).strip().strip('"\'')

        lang_match = re.search(r'^lang(?:uage)?:\s*(.+)$', frontmatter, re.MULTILINE)
        if lang_match:
            task_data["lang"] = lang_match.group(1).strip().strip('"\'')

        deps_match = re.search(r'^dependencies:\s*\[(.*?)\]', frontmatter, re.MULTILINE | re.DOTALL)
        if deps_match:
            deps_str = deps_match.group(1)
            task_data["dependencies"] = [d.strip().strip('"\'') for d in deps_str.split(",") if d.strip()]

        complexity_match = re.search(r'^complexity:\s*(\w+)', frontmatter, re.MULTILINE)
        if complexity_match:
            task_data["complexity"] = complexity_match.group(1).strip()

        agent_match = re.search(r'^agent:\s*(\w+)', frontmatter, re.MULTILINE)
        if agent_match:
            task_data["agent"] = agent_match.group(1).strip().lower()

    # Extract description from first paragraph after frontmatter
    content_without_front = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    desc_match = re.search(r'##?\s*Description\s*\n\s*(.+?)(?:\n\n|\n##|\Z)', content_without_front, re.DOTALL | re.IGNORECASE)
    if desc_match:
        task_data["description"] = desc_match.group(1).strip()[:100]
    else:
        # First paragraph
        first_para = content_without_front.strip().split('\n\n')[0]
        task_data["description"] = first_para[:100] if first_para else ""

    return task_data


def parse_tasks_from_files(spec_path: str) -> List[dict]:
    """Parses all task files from the tasks directory"""
    task_files = find_task_files(spec_path)
    tasks = []

    for task_file in task_files:
        task_data = parse_task_file(task_file)
        tasks.append(task_data)

    # Sort by task ID
    tasks.sort(key=lambda t: t["id"])

    return tasks


def filter_tasks_by_range(tasks: List[dict], from_task: Optional[str], to_task: Optional[str]) -> List[dict]:
    """Filters tasks by range"""
    if not from_task and not to_task:
        return tasks

    def task_num(task_id: str) -> int:
        match = re.search(r'(\d+)', task_id)
        return int(match.group(1)) if match else 0

    from_num = task_num(from_task) if from_task else 0
    to_num = task_num(to_task) if to_task else float('inf')

    filtered = []
    for task in tasks:
        num = task_num(task["id"])
        if from_num <= num <= to_num:
            filtered.append(task)

    return filtered


def get_next_pending_task(fix_plan: dict) -> Optional[dict]:
    """Finds the next pending task with satisfied dependencies"""
    tasks = fix_plan.get("tasks", [])
    completed_tasks = {t["id"] for t in tasks if t["status"] in ["done", "completed", "implemented", "reviewed"]}

    for task in tasks:
        if task["status"] not in ["pending", "in_progress"]:
            continue

        # Check dependencies
        deps_satisfied = all(dep in completed_tasks for dep in task.get("dependencies", []))
        if deps_satisfied:
            return task

    return None


def get_agent_config(fix_plan: dict, args_agent: str = None) -> dict:
    """Returns the agent configuration to use"""
    # 1. Use agent from CLI args if specified
    if args_agent and args_agent in SUPPORTED_AGENTS:
        return SUPPORTED_AGENTS[args_agent]

    # 2. Use agent from current task
    current_task_id = fix_plan.get("state", {}).get("current_task")
    if current_task_id:
        for task in fix_plan.get("tasks", []):
            if task["id"] == current_task_id and task.get("agent"):
                return SUPPORTED_AGENTS.get(task["agent"], SUPPORTED_AGENTS["claude"])

    # 3. Use default agent from fix_plan
    default_agent = fix_plan.get("default_agent", "claude")
    return SUPPORTED_AGENTS.get(default_agent, SUPPORTED_AGENTS["claude"])


def format_command(agent: dict, cmd_type: str, **kwargs) -> str:
    """Formats a command for the specified agent"""
    cmd_template = agent.get(cmd_type, cmd_type)
    cmd = cmd_template.format(**kwargs)
    return f"{agent['cmd_prefix']}{cmd}"


def run_git_commit(spec_path: str, task_id: str, task_title: str, iteration: int) -> bool:
    """Commits changes for a completed task"""
    try:
        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "-C", spec_path, "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        if not result.stdout.strip():
            print(f"   No changes to commit")
            return True

        # Stage all changes
        subprocess.run(
            ["git", "-C", spec_path, "add", "-A"],
            capture_output=True,
            check=True
        )

        # Commit
        commit_msg = f"Ralph iteration {iteration}: {task_id} - {task_title[:50]}"
        subprocess.run(
            ["git", "-C", spec_path, "commit", "-m", commit_msg],
            capture_output=True,
            check=True
        )

        print(f"   Committed: {commit_msg}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Git commit failed: {e}")
        return False
    except FileNotFoundError:
        print(f"   ⚠️  Git not found")
        return False


def update_task_status(fix_plan: dict, task_id: str, new_status: str):
    """Updates the status of a task in the tasks list"""
    for task in fix_plan.get("tasks", []):
        if task["id"] == task_id:
            task["status"] = new_status
            break


def action_start(spec_path: str, from_task: Optional[str], to_task: Optional[str], agent: str = "claude"):
    """Initializes fix_plan.json from task files"""
    print(f"🚀 Ralph Loop | Initializing...")
    print(f"   Spec: {spec_path}")

    # Parse task files
    tasks = parse_tasks_from_files(spec_path)

    if not tasks:
        # Fallback: try to find tasks.md
        tasks_file = find_tasks_file(spec_path)
        if tasks_file:
            print(f"   Tasks file: {tasks_file}")
            print("   ⚠️  No individual task files found. Creating from tasks.md...")
            # Create basic task entries from tasks.md parsing
            # This is a simplified version
        else:
            print("❌ No tasks found. Create task files in tasks/ directory.")
            sys.exit(1)

    print(f"   Found {len(tasks)} tasks")

    # Apply range filter
    filtered_tasks = filter_tasks_by_range(tasks, from_task, to_task)

    # Separate into categories
    pending = [t["id"] for t in filtered_tasks if t["status"] in ["pending", "in_progress"]]
    done = [t["id"] for t in filtered_tasks if t["status"] in ["done", "completed", "implemented", "reviewed"]]

    # Create fix_plan with full structure
    fix_plan = {
        "spec_id": Path(spec_path).name,
        "spec_folder": spec_path,
        "task_range": {
            "from": from_task,
            "to": to_task,
            "from_num": int(re.search(r'(\d+)', from_task).group(1)) if from_task else 0,
            "to_num": int(re.search(r'(\d+)', to_task).group(1)) if to_task else 999,
            "total_in_range": len(filtered_tasks),
        },
        "default_agent": agent,
        "tasks": filtered_tasks,
        "pending": pending,
        "done": done,
        "optional": [],
        "superseded": [],
        "learnings": [],
        "state": {
            "step": "choose_task",
            "current_task": None,
            "current_task_file": None,
            "current_task_lang": None,
            "iteration": 0,
            "retry_count": 0,
            "review_file_retry": 0,    # separate counter for file validation failures
            "review_file_error": None, # last file validation error message
            "last_updated": datetime.now().isoformat(),
            "error": None,
            "range_progress": {
                "done_in_range": len(done),
                "total_in_range": len(filtered_tasks),
            }
        }
    }

    save_fix_plan(spec_path, fix_plan)

    agent_config = SUPPORTED_AGENTS[agent]

    print(f"✅ fix_plan.json created")
    print(f"   Tasks in range: {len(filtered_tasks)}")
    print(f"   Pending: {len(pending)}")
    print(f"   Done: {len(done)}")
    print(f"   Default agent: {agent_config['name']}")
    if from_task or to_task:
        print(f"   Range: {from_task or 'START'} → {to_task or 'END'}")

    print(f"\n📋 Initial state: {fix_plan['state']['step']}")
    print(f"\n➡️  Next: Run loop to start processing")
    ralph_cmd = format_command(agent_config, "ralph_loop", action="loop", spec=spec_path)
    print(f"   {ralph_cmd}")


def action_loop(spec_path: str, args_agent: str = None, no_commit: bool = False):
    """Executes one step of the state machine"""
    fix_plan = load_fix_plan(spec_path)
    state = fix_plan["state"]
    step = state["step"]

    agent_config = get_agent_config(fix_plan, args_agent)

    print(f"🔄 Ralph Loop | Iteration {state['iteration']} | Step: {step}")

    # Handle each step
    if step == "init":
        handle_init(spec_path, fix_plan)

    elif step == "choose_task":
        handle_choose_task(spec_path, fix_plan, agent_config)

    elif step == "implementation":
        handle_implementation(spec_path, fix_plan, agent_config)

    elif step == "review":
        handle_review(spec_path, fix_plan, agent_config)

    elif step == "fix":
        handle_fix(spec_path, fix_plan, agent_config)

    elif step == "cleanup":
        handle_cleanup(spec_path, fix_plan, agent_config)

    elif step == "sync":
        handle_sync(spec_path, fix_plan, agent_config)

    elif step == "update_done":
        handle_update_done(spec_path, fix_plan, agent_config, no_commit)

    elif step == "complete":
        handle_complete(fix_plan)

    elif step == "failed":
        handle_failed(fix_plan)

    else:
        print(f"❌ Unknown state: {step}")
        print(f"   Valid states: init, choose_task, implementation, review, fix, cleanup, sync, update_done, complete, failed")
        
        # Provide helpful guidance for common errors
        if "-" in step:
            suggested = step.replace("-", "_")
            print(f"\n💡 HINT: The state '{step}' uses a dash (-) instead of an underscore (_).")
            print(f"   Did you mean: '{suggested}'?")
            print(f"\n   To fix this, run:")
            print(f"   sed -i 's/\"{step}\"/\"{suggested}\"/g' {get_fix_plan_path(spec_path)}")
        
        sys.exit(1)


def handle_init(spec_path: str, fix_plan: dict):
    """Handle init step - transition to choose_task"""
    print("→ Initializing...")
    fix_plan["state"]["step"] = "choose_task"
    save_fix_plan(spec_path, fix_plan)
    print("→ Initialized | Next: choose_task")


def handle_choose_task(spec_path: str, fix_plan: dict, agent_config: dict):
    """Handle choose_task step - select next task"""
    
    # Mark previous completed task as reviewed if review passed
    done_tasks = fix_plan.get("done", [])
    status_updated = False
    if done_tasks:
        last_done_id = done_tasks[-1]
        for task in fix_plan.get("tasks", []):
            if task["id"] == last_done_id and task.get("status") == "completed":
                review_passed, _ = check_review_result(spec_path, last_done_id)
                if review_passed:
                    task["status"] = "reviewed"
                    print(f"   ✅ {last_done_id} marked as reviewed")
                    status_updated = True
                break
    
    if status_updated:
        save_fix_plan(spec_path, fix_plan)
    
    next_task = get_next_pending_task(fix_plan)

    if not next_task:
        # Check for misalignment: pending list not empty but no pending tasks found
        pending_list = fix_plan.get("pending", [])
        if pending_list:
            # Misalignment detected: pending list has items but task statuses don't match
            print("⚠️  WARNING: Task status misalignment detected!")
            print(f"   Pending list has {len(pending_list)} task(s), but no pending tasks found in task list.")
            
            # Get the first task from pending list
            first_pending_id = pending_list[0]
            tasks = fix_plan.get("tasks", [])
            
            for task in tasks:
                if task["id"] == first_pending_id:
                    next_task = task
                    # Fix the status if it's incorrectly marked as completed
                    if task["status"] == "completed":
                        task["status"] = "pending"
                        print(f"   Fixed {first_pending_id}: status 'completed' → 'pending'")
                        # Save immediately to persist the fix
                        save_fix_plan(spec_path, fix_plan)
                    print(f"   Using first pending task: {first_pending_id}")
                    break
            
            if not next_task:
                print(f"   ⚠️  Task {first_pending_id} not found in task list!")
        
        if not next_task:
            fix_plan["state"]["step"] = "complete"
            save_fix_plan(spec_path, fix_plan)
            print("→ No more tasks in range")
            print("═══════════════════════════════════════════════════════")
            print("Ralph Loop COMPLETE")
            print("═══════════════════════════════════════════════════════")
            return

    task_id = next_task["id"]
    task_title = next_task.get("title", "")

    fix_plan["state"]["current_task"] = task_id
    fix_plan["state"]["current_task_file"] = next_task.get("file", "")
    fix_plan["state"]["current_task_lang"] = next_task.get("lang", "")
    fix_plan["state"]["step"] = "implementation"
    fix_plan["state"]["retry_count"] = 0

    save_fix_plan(spec_path, fix_plan)

    print(f"→ Selected: {task_id}")
    if task_title:
        print(f"   Title: {task_title}")
    deps = next_task.get("dependencies", [])
    if deps:
        print(f"   Dependencies: {', '.join(deps)} ✓")
    print(f"→ Next: implementation")
    print("")
    print("Execute:")
    cmd = format_command(agent_config, "task_impl", spec=spec_path, task=task_id)
    print(f"  {cmd}")


def handle_implementation(spec_path: str, fix_plan: dict, agent_config: dict):
    """Handle implementation step"""
    current_task = fix_plan["state"].get("current_task")
    task_file = fix_plan["state"].get("current_task_file", "")
    task_lang = fix_plan["state"].get("current_task_lang", "")

    if not current_task:
        fix_plan["state"]["step"] = "choose_task"
        save_fix_plan(spec_path, fix_plan)
        print("⚠️  No current task, returning to choose_task")
        return

    # Check for task-specific agent
    task_agent = None
    for task in fix_plan.get("tasks", []):
        if task["id"] == current_task and task.get("agent"):
            task_agent = SUPPORTED_AGENTS.get(task["agent"])
            break

    if task_agent:
        agent_config = task_agent
        print(f"🤖 Using agent: {agent_config['name']}")

    print(f"→ Implementation: {current_task}")
    print("")
    print("Execute:")
    cmd = format_command(agent_config, "task_impl", spec=spec_path, task=current_task)
    print(f"  {cmd}")
    print("")
    print("After execution, update state:")
    print("  python3 ralph_loop.py --action=loop --spec=" + spec_path)


def handle_review(spec_path: str, fix_plan: dict, agent_config: dict):
    """Handle review step"""
    current_task = fix_plan["state"].get("current_task")
    task_file = fix_plan["state"].get("current_task_file", "")
    task_lang = fix_plan["state"].get("current_task_lang", "")

    if not current_task:
        fix_plan["state"]["step"] = "choose_task"
        save_fix_plan(spec_path, fix_plan)
        return

    retry_count = fix_plan["state"].get("retry_count", 0)
    review_file_error = fix_plan["state"].get("review_file_error")
    review_file_retry = fix_plan["state"].get("review_file_retry", 0)

    # Check for task-specific agent
    task_agent = None
    for task in fix_plan.get("tasks", []):
        if task["id"] == current_task and task.get("agent"):
            task_agent = SUPPORTED_AGENTS.get(task["agent"])
            break

    if task_agent:
        agent_config = task_agent

    print(f"→ Review: {current_task} | Retry: {retry_count}/3")

    # If there was a review file error from the previous --action=next, surface it to the agent
    if review_file_error:
        print(f"")
        print(f"⚠️  REVIEW FILE ERROR (attempt {review_file_retry}/3):")
        print(f"   {review_file_error}")
        print(f"")
        print(f"   The review file MUST be created with this exact frontmatter structure:")
        print(f"   ---")
        print(f"   review_status: PASSED   # or FAILED")
        print(f"   critical_issues: 0      # required if FAILED")
        print(f"   major_issues: 0         # required if FAILED")
        print(f"   ---")
        print(f"")
        print(f"   Expected file path: tasks/{current_task}--review.md")
        print(f"")

    print("")
    print("Execute:")
    cmd = format_command(agent_config, "task_review", spec=spec_path, task=current_task)
    print(f"  {cmd}")
    print("")
    print("Review the generated review report, then update state:")
    print("  python3 ralph_loop.py --action=loop --spec=" + spec_path)


def handle_fix(spec_path: str, fix_plan: dict, agent_config: dict):
    """Handle fix step - apply fixes from review"""
    current_task = fix_plan["state"].get("current_task")

    if not current_task:
        fix_plan["state"]["step"] = "choose_task"
        save_fix_plan(spec_path, fix_plan)
        return

    # Check for task-specific agent
    task_agent = None
    for task in fix_plan.get("tasks", []):
        if task["id"] == current_task and task.get("agent"):
            task_agent = SUPPORTED_AGENTS.get(task["agent"])
            break

    if task_agent:
        agent_config = task_agent

    print(f"→ Fix: {current_task}")
    print("")
    print("Steps:")
    print(f"  1. Read review report: {current_task}--review.md")
    print(f"  2. Apply fixes")
    print(f"  3. Update state:")
    print(f"     python3 ralph_loop.py --action=loop --spec=" + spec_path)
    print("")
    print("Or execute directly:")
    cmd = format_command(agent_config, "task_impl", spec=spec_path, task=current_task)
    print(f"  {cmd}")


def handle_cleanup(spec_path: str, fix_plan: dict, agent_config: dict):
    """Handle cleanup step"""
    current_task = fix_plan["state"].get("current_task")
    task_file = fix_plan["state"].get("current_task_file", "")
    task_lang = fix_plan["state"].get("current_task_lang", "")

    if not current_task:
        fix_plan["state"]["step"] = "choose_task"
        save_fix_plan(spec_path, fix_plan)
        return

    # Check for task-specific agent
    task_agent = None
    for task in fix_plan.get("tasks", []):
        if task["id"] == current_task and task.get("agent"):
            task_agent = SUPPORTED_AGENTS.get(task["agent"])
            break

    if task_agent:
        agent_config = task_agent

    print(f"→ Cleanup: {current_task}")
    print("")
    print("Execute:")
    cmd = format_command(agent_config, "code_cleanup", spec=spec_path, task=current_task)
    print(f"  {cmd}")
    print("")
    print("After cleanup, update state:")
    print("  python3 ralph_loop.py --action=loop --spec=" + spec_path)


def handle_sync(spec_path: str, fix_plan: dict, agent_config: dict):
    """Handle sync step"""
    current_task = fix_plan["state"].get("current_task")

    if not current_task:
        fix_plan["state"]["step"] = "choose_task"
        save_fix_plan(spec_path, fix_plan)
        return

    # Check for task-specific agent
    task_agent = None
    for task in fix_plan.get("tasks", []):
        if task["id"] == current_task and task.get("agent"):
            task_agent = SUPPORTED_AGENTS.get(task["agent"])
            break

    if task_agent:
        agent_config = task_agent

    print(f"→ Sync: {current_task}")
    print("")
    print("Execute:")
    cmd = format_command(agent_config, "spec_sync", spec=spec_path, task=current_task)
    print(f"  {cmd}")
    print("")
    print("After sync, update state:")
    print("  python3 ralph_loop.py --action=loop --spec=" + spec_path)


def handle_update_done(spec_path: str, fix_plan: dict, agent_config: dict, no_commit: bool):
    """Handle update_done step - mark task complete and commit"""
    current_task = fix_plan["state"].get("current_task")

    if not current_task:
        fix_plan["state"]["step"] = "choose_task"
        save_fix_plan(spec_path, fix_plan)
        return

    # Find task details
    task_title = ""
    for task in fix_plan.get("tasks", []):
        if task["id"] == current_task:
            task["status"] = "completed"
            task_title = task.get("title", "")
            break

    # Update lists
    if "pending" not in fix_plan:
        fix_plan["pending"] = []
    if "done" not in fix_plan:
        fix_plan["done"] = []
    if current_task in fix_plan["pending"]:
        fix_plan["pending"].remove(current_task)
    if current_task not in fix_plan["done"]:
        fix_plan["done"].append(current_task)

    # Update state
    iteration = fix_plan["state"].get("iteration", 0) + 1
    fix_plan["state"]["iteration"] = iteration
    fix_plan["state"]["current_task"] = None
    fix_plan["state"]["current_task_file"] = None
    fix_plan["state"]["current_task_lang"] = None
    fix_plan["state"]["step"] = "choose_task"
    fix_plan["state"]["retry_count"] = 0

    # Update progress
    done_count = len(fix_plan.get("done", []))
    total_count = fix_plan.get("task_range", {}).get("total_in_range", 0)
    if "range_progress" not in fix_plan["state"]:
        fix_plan["state"]["range_progress"] = {}
    fix_plan["state"]["range_progress"]["done_in_range"] = done_count

    save_fix_plan(spec_path, fix_plan)

    print(f"→ Done: {current_task}")
    if task_title:
        print(f"   {task_title}")

    # Git commit
    if not no_commit:
        print("→ Committing changes...")
        run_git_commit(spec_path, current_task, task_title, iteration)

    progress_pct = (done_count / total_count * 100) if total_count > 0 else 0
    print(f"→ Progress: {done_count}/{total_count} in range ({progress_pct:.0f}%)")
    print(f"→ Iteration: {iteration}")
    print(f"→ Next: choose_task")


def handle_complete(fix_plan: dict):
    """Handle complete state"""
    done_count = len(fix_plan.get("done", []))
    total_count = fix_plan.get("task_range", {}).get("total_in_range", 0)
    iteration = fix_plan["state"].get("iteration", 0)

    print("═══════════════════════════════════════════════════════")
    print("Ralph Loop COMPLETE")
    print("═══════════════════════════════════════════════════════")
    print(f"Task Range: {fix_plan.get('task_range', {}).get('from', 'START')} → {fix_plan.get('task_range', {}).get('to', 'END')}")
    print(f"Tasks Completed: {done_count}/{total_count}")
    print(f"Total Iterations: {iteration}")
    print("")
    print("All tasks in range implemented and verified.")
    print("Run --action=start with a new range to continue.")


def handle_failed(fix_plan: dict):
    """Handle failed state"""
    current_task = fix_plan["state"].get("current_task", "N/A")
    error = fix_plan["state"].get("error", "Unknown error")
    retry_count = fix_plan["state"].get("retry_count", 0)

    print("═══════════════════════════════════════════════════════")
    print("Ralph Loop FAILED")
    print("═══════════════════════════════════════════════════════")
    print(f"Task: {current_task}")
    print(f"Error: {error}")
    print(f"Retry count: {retry_count}/3")
    print("")
    print("Fix the issues manually, then resume:")
    print("  python3 ralph_loop.py --action=loop --spec=" + fix_plan.get("spec_folder", ""))


def action_status(spec_path: str):
    """Shows current status"""
    fix_plan = load_fix_plan(spec_path)
    state = fix_plan["state"]

    print("📊 Ralph Loop Status")
    print("═══════════════════════════════════════════════════════")
    print(f"Spec: {spec_path}")
    print(f"Step: {state['step']}")
    print(f"Iteration: {state['iteration']}")

    if fix_plan.get('default_agent'):
        agent_name = SUPPORTED_AGENTS.get(fix_plan['default_agent'], {}).get('name', fix_plan['default_agent'])
        print(f"Default Agent: {agent_name}")

    if state.get('current_task'):
        print(f"Current Task: {state['current_task']}")
        if state.get('current_task_lang'):
            print(f"Language: {state['current_task_lang']}")
        if state.get('retry_count', 0) > 0:
            print(f"Retry: {state['retry_count']}/3")

    done_count = len(fix_plan.get("done", []))
    pending_count = len(fix_plan.get("pending", []))
    total_count = fix_plan.get("task_range", {}).get("total_in_range", 0)

    print("")
    print(f"Progress: {done_count}/{total_count} done, {pending_count} pending")

    if fix_plan.get("tasks"):
        print("")
        print("Tasks:")
        for task in fix_plan["tasks"]:
            status = task.get("status", "pending")
            icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "done": "✅",
                "completed": "✅",
                "failed": "❌"
            }.get(status, "❓")
            agent_info = f" [{task.get('agent', '')}]" if task.get("agent") else ""
            print(f"   {icon} {task['id']}{agent_info}: {task.get('title', task.get('description', ''))[:40]}")


def action_resume(spec_path: str, args_agent: str = None, no_commit: bool = False):
    """Resumes the loop from current state"""
    fix_plan = load_fix_plan(spec_path)
    state = fix_plan["state"]

    print(f"▶️  Ralph Loop | Resume from {state['step']}")

    if state["step"] in ["complete", "failed"]:
        print(f"   Final state: {state['step']}")
        print("   To restart, use --action=start")
        return

    # Continue with loop
    action_loop(spec_path, args_agent, no_commit)


def validate_review_file(spec_path: str, task_id: str) -> tuple[bool, str]:
    """
    Structural pre-validation of the review file before semantic check.
    Verifies: file exists, has frontmatter delimiters, has valid review_status field.
    Returns: (True, "") if valid, (False, "<error message>") if not.
    """
    spec_dir = Path(spec_path)
    review_file = spec_dir / "tasks" / f"{task_id}--review.md"

    if not review_file.exists():
        return False, (
            f"Review file not found: tasks/{task_id}--review.md. "
            f"The agent must create this file with a valid YAML frontmatter."
        )

    try:
        with open(review_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Cannot read review file: {e}"

    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        return False, (
            f"Review file tasks/{task_id}--review.md has no valid YAML frontmatter. "
            f"The file must start with '---' delimiters containing the frontmatter block."
        )

    frontmatter = frontmatter_match.group(1)
    status_match = re.search(r'^review_status:\s*(\w+)', frontmatter, re.MULTILINE | re.IGNORECASE)
    if not status_match:
        return False, (
            f"Review file tasks/{task_id}--review.md is missing the 'review_status' field. "
            f"Required frontmatter: review_status: PASSED|FAILED"
        )

    review_status = status_match.group(1).upper()
    if review_status not in {"PASSED", "FAILED"}:
        return False, (
            f"Invalid review_status value '{review_status}' in tasks/{task_id}--review.md. "
            f"Allowed values: PASSED or FAILED."
        )

    return True, ""


def check_review_result(spec_path: str, task_id: str) -> tuple[bool, str]:
    """
    Check the review report to determine if review passed or failed.
    
    First tries to parse the YAML frontmatter for structured review_status field.
    Falls back to text pattern matching if YAML frontmatter is not present.
    
    Returns:
        tuple: (passed: bool, reason: str)
        - passed: True if review passed, False if failed
        - reason: Description of the result
    """
    spec_dir = Path(spec_path)
    
    # Look for review report file: tasks/TASK-XXX--review.md
    review_file = spec_dir / "tasks" / f"{task_id}--review.md"
    
    if not review_file.exists():
        # No review report found - assume not implemented
        return False, f"Review report not found: {review_file}"
    
    try:
        with open(review_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        content_lower = content.lower()
        
        # === METHOD 1: Parse YAML frontmatter (preferred, structured approach) ===
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if frontmatter_match:
            frontmatter = frontmatter_match.group(1)
            
            # Extract review_status from frontmatter
            status_match = re.search(r'^review_status:\s*(\w+)', frontmatter, re.MULTILINE | re.IGNORECASE)
            if status_match:
                review_status = status_match.group(1).upper()
                
                if review_status == "PASSED":
                    return True, "Review status: PASSED (from YAML frontmatter)"
                elif review_status == "FAILED":
                    # Check for critical/major issues count
                    critical_match = re.search(r'^critical_issues:\s*(\d+)', frontmatter, re.MULTILINE | re.IGNORECASE)
                    major_match = re.search(r'^major_issues:\s*(\d+)', frontmatter, re.MULTILINE | re.IGNORECASE)
                    
                    critical_count = int(critical_match.group(1)) if critical_match else 0
                    major_count = int(major_match.group(1)) if major_match else 0
                    
                    return False, f"Review status: FAILED with {critical_count} critical, {major_count} major issues"
                elif review_status == "PARTIAL":
                    return False, "Review status: PARTIAL (needs more work)"
                else:
                    return False, f"Unknown review_status: {review_status}"
        
        # === METHOD 2: Fallback to text pattern matching (for legacy reviews) ===
        # Check for common failure indicators in review reports (English + Italian)
        failure_indicators = [
            # English
            "❌ not started",
            "❌ not implemented",
            "❌ fail",
            "❌ failed",
            "❌ missing",
            "implementation status: ❌",
            "implementation: not started",
            "implementation: not implemented",
            "acceptance criteria: 0/",
            "acceptance criteria: 1/",
            "acceptance criteria: 2/",
            "acceptance criteria: 3/",
            "acceptance criteria: 4/",
            "passed: 0/",
            "passed: 1/",
            "passed: 2/",
            "passed: 3/",
            "passed: 4/",
            # Italian
            "❌ non implementato",
            "❌ non iniziato",
            "❌ fallito",
            "❌ mancante",
            "stato implementazione: ❌",
            "implementazione: non iniziata",
            "implementazione: non implementata",
            "criteri di accettazione: 0/",
            "criteri di accettazione: 1/",
            "criteri di accettazione: 2/",
            "criteri di accettazione: 3/",
            "criteri di accettazione: 4/",
            "esito: ❌",
            "non conforme",
            "non soddisfatti",
            "task non implementato",
            "needs revision",
            "need revision",
            "deve essere risolto",
            "correggere",
        ]
        
        success_indicators = [
            # English
            "✅ implemented",
            "✅ complete",
            "✅ pass",
            "✅ passed",
            "implementation status: ✅",
            "implementation: complete",
            "implementation: done",
            "acceptance criteria: 5/5",
            "acceptance criteria: 4/4",
            "acceptance criteria: 3/3",
            "acceptance criteria: 100%",
            "passed: 5/5",
            "passed: 4/4",
            "passed: 3/3",
            "all criteria met",
            "all tests passed",
            "no issues found",
            "review passed",
            # Italian
            "✅ implementato",
            "✅ completato",
            "✅ passato",
            "✅ superato",
            "stato implementazione: ✅",
            "implementazione: completata",
            "implementazione: completato",
            "criteri di accettazione: 5/5",
            "criteri di accettazione: 4/4",
            "criteri di accettazione: 3/3",
            "criteri di accettazione: 100%",
            "criteri: 5/5",
            "criteri: 4/4",
            "criteri: 3/3",
            "tutti i criteri soddisfatti",
            "tutti i test passano",
            "nessun problema trovato",
            "nessun issue",
            "review superata",
            "esito: ✅",
        ]
        
        # Check for critical issues that should fail the review regardless of other indicators
        critical_issue_patterns = [
            r"critical.*issue",
            r"issue.*critical",
            r"problema.*critico",
            r"critico",
            r"blocking issue",
            r"must fix",
            r"deve essere corretto",
            r"deve essere risolto",
            r"blocking",
            r"needs fix",
            r"needs revision",
            r"non conforme",
        ]
        
        for pattern in critical_issue_patterns:
            if re.search(pattern, content_lower):
                return False, f"Found critical issue indicator: '{pattern}'"
        
        # Check for explicit failure indicators FIRST (take precedence over success)
        for indicator in failure_indicators:
            if indicator.lower() in content_lower:
                return False, f"Found failure indicator: '{indicator}'"
        
        # Check for explicit success indicators
        for indicator in success_indicators:
            if indicator.lower() in content_lower:
                return True, f"Found success indicator: '{indicator}'"
        
        # Check acceptance criteria percentage
        # Pattern: "X/Y soddisfatte" or "X/Y satisfied"
        criteria_match = re.search(r'(\d+)\s*/\s*(\d+)\s*(?:soddisfatte|satisfied|pass)', content_lower)
        if criteria_match:
            passed = int(criteria_match.group(1))
            total = int(criteria_match.group(2))
            if passed >= total:
                return True, f"All acceptance criteria met: {passed}/{total}"
            else:
                return False, f"Acceptance criteria not fully met: {passed}/{total}"
        
        # Check for "Not Started" or "Not Implemented"
        if "not started" in content_lower or "not implemented" in content_lower:
            return False, "Implementation not started"
        
        # Default: FAIL rather than pass (safer - require explicit success indicators)
        return False, "Review report exists but no clear success indicators found"
        
    except Exception as e:
        return False, f"Error reading review report: {e}"


def action_next(spec_path: str, args_agent: str = None, no_commit: bool = False):
    """Manually advance to next step (checks review results before advancing)"""
    fix_plan = load_fix_plan(spec_path)
    state = fix_plan["state"]
    current_step = state["step"]

    print(f"⏭️  Ralph Loop | Advancing from '{current_step}' to next step")

    if current_step in ["complete", "failed"]:
        print(f"   Final state: {current_step}")
        print("   Cannot advance further.")
        return

    # Define standard step transitions
    step_transitions = {
        "init": "choose_task",
        "choose_task": "implementation",
        "implementation": "review",
        "fix": "review",
        "cleanup": "sync",
        "sync": "update_done",
        "update_done": "choose_task",
    }
    
    # Special handling for review step - check results before advancing
    if current_step == "review":
        current_task = state.get("current_task")
        retry_count = state.get("retry_count", 0)
        max_retries = 3
        
        if not current_task:
            print("   ⚠️  No current task, returning to choose_task")
            state["step"] = "choose_task"
            save_fix_plan(spec_path, fix_plan)
            return
        
        max_file_retries = 3

        # === PRE-VALIDATION: structural check before semantic review ===
        file_valid, file_error = validate_review_file(spec_path, current_task)

        if not file_valid:
            # Do NOT increment retry_count — this is not a review failure
            review_file_retry = state.get("review_file_retry", 0) + 1
            state["review_file_retry"] = review_file_retry
            state["review_file_error"] = file_error

            print(f"   ⚠️  Review file invalid (attempt {review_file_retry}/{max_file_retries}): {file_error}")

            if review_file_retry >= max_file_retries:
                print(f"   ❌ Max file retries ({max_file_retries}) exceeded - review file never created correctly")
                state["step"] = "failed"
                state["error"] = f"Review file validation failed after {max_file_retries} attempts: {file_error}"
            else:
                print(f"   🔄 Staying on 'review' — agent must create/fix the review file")
                # state["step"] remains "review" — no assignment needed

            save_fix_plan(spec_path, fix_plan)
            print(f"")
            print("Run loop to see next command:")
            print(f"  python3 ralph_loop.py --action=loop --spec={spec_path}")
            return

        # File is structurally valid — reset file retry counters
        state["review_file_retry"] = 0
        state["review_file_error"] = None

        # === SEMANTIC CHECK: check review content ===
        review_passed, reason = check_review_result(spec_path, current_task)

        if review_passed:
            print(f"   ✅ Review passed: {reason}")
            print(f"   Advanced: review → cleanup")
            state["step"] = "cleanup"
            state["retry_count"] = 0
            save_fix_plan(spec_path, fix_plan)
        else:
            print(f"   ❌ Review failed: {reason}")
            retry_count += 1
            state["retry_count"] = retry_count

            if retry_count >= max_retries:
                print(f"   ❌ Max retries ({max_retries}) exceeded")
                print(f"   Advanced: review → failed")
                state["step"] = "failed"
                state["error"] = f"Review failed after {max_retries} retries: {reason}"
                save_fix_plan(spec_path, fix_plan)
            else:
                print(f"   🔄 Retry {retry_count}/{max_retries}")
                print(f"   Advanced: review → fix")
                state["step"] = "fix"
                save_fix_plan(spec_path, fix_plan)

        print(f"")
        print("Run loop to see next command:")
        print(f"  python3 ralph_loop.py --action=loop --spec={spec_path}")
        return

    # Standard transition for other steps
    next_step = step_transitions.get(current_step)

    if not next_step:
        print(f"   Unknown step: {current_step}")
        return

    # Special handling for update_done - need to mark task complete
    if current_step == "update_done":
        handle_update_done(spec_path, fix_plan, get_agent_config(fix_plan, args_agent), no_commit)
        return

    # Update state
    state["step"] = next_step
    save_fix_plan(spec_path, fix_plan)

    print(f"   Advanced: {current_step} → {next_step}")
    print(f"")
    print("Run loop to see next command:")
    print(f"  python3 ralph_loop.py --action=loop --spec={spec_path}")


def main():
    args = parse_args()

    # Validate spec folder structure
    if not validate_spec_path(args.spec):
        print(f"❌ Invalid spec folder: {args.spec}")
        print(f"   Expected format: docs/specs/[ID-feature]/ or [ID-feature]/")
        print(f"   Folder must exist and contain spec files or tasks/ directory")
        sys.exit(1)

    # Ensure _ralph_loop directory exists for clean state
    spec_dir = Path(args.spec).resolve()
    ralph_dir = spec_dir / "_ralph_loop"
    if not ralph_dir.exists():
        ralph_dir.mkdir(parents=True, exist_ok=True)

    if args.action == "start":
        action_start(args.spec, args.from_task, args.to_task, args.agent)
    elif args.action == "loop":
        action_loop(args.spec, args.agent, args.no_commit)
    elif args.action == "status":
        action_status(args.spec)
    elif args.action == "resume":
        action_resume(args.spec, args.agent, args.no_commit)
    elif args.action == "next":
        action_next(args.spec, args.agent, args.no_commit)
    elif args.action == "next":
        action_next(args.spec, args.agent, args.no_commit)


if __name__ == "__main__":
    main()
