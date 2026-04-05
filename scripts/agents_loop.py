#!/usr/bin/env python3
"""
agents_loop.py — Universal Ralph Loop automation for multiple AI agents.

Supports: claude, kimi, codex, copilot, gemini

Usage:
    agents_loop --spec=docs/specs/001-feature --agent=claude
    agents_loop --spec=docs/specs/001-feature --agent=codex --delay=10
    agents_loop --spec=docs/specs/001-feature --agent=kimi --max-iterations=50

The script automates the Ralph Loop workflow:
    1. ralph_loop.py --action=loop  → Get command to execute
    2. Execute with chosen agent    → Run the command
    3. ralph_loop.py --action=next  → Advance state
    4. Repeat until complete/failed
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Optional, Tuple


# Agent configurations
# Each agent defines how to run it in non-interactive mode
AGENTS = {
    "claude": {
        "name": "Claude Code",
        "cmd": ["claude"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "model_flag": "--model",
        "yolo_flag": "--dangerously-skip-permissions",
        "prompt_arg": True,
        "prompt_flag": "-p",
    },
    "glm4": {
        "name": "GLM-4 CLI",
        "cmd": ["glm4"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "model_flag": "--model",
        "yolo_flag": "--dangerously-skip-permissions",
        "prompt_arg": True,
        "prompt_flag": "-p",
    },
    "minimax": {
        "name": "MiniMax CLI",
        "cmd": ["minimax"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "model_flag": "--model",
        "yolo_flag": "--dangerously-skip-permissions",
        "prompt_arg": True,
        "prompt_flag": "-p",
    },
    "kimi": {
        "name": "Kimi CLI",
        "cmd": ["kimi"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "model_flag": "-m",
        "yolo_flag": "-y",  # --yolo doesn't exist, use -y (or --yes / --auto-approve)
        "print_flag": "--print",  # Required for non-interactive mode
        "prompt_arg": True,
        "prompt_flag": "-p",
    },
    "codex": {
        "name": "Codex CLI",
        "cmd": ["codex", "exec"],
        "stdin_mode": True,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "model_flag": "--model",
        "yolo_flag": "--dangerously-bypass-approvals-and-sandbox",
        "prompt_arg": False,
    },
    "copilot": {
        "name": "GitHub Copilot CLI",
        "cmd": ["copilot"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "model_flag": "--model",
        "yolo_flag": "--allow-all",
        "prompt_arg": True,
        "prompt_flag": "-p",
    },
    "gemini": {
        "name": "Gemini CLI",
        "cmd": ["gemini"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "model_flag": "-m",
        "yolo_flag": "-y",  # Gemini uses -y for yolo
        "prompt_arg": True,
        "prompt_flag": "-p",  # Must be before prompt value
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Universal Ralph Loop automation for multiple AI agents."
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Spec folder path (e.g. docs/specs/001-feature).",
    )
    parser.add_argument(
        "--agent",
        default="codex",
        choices=list(AGENTS.keys()),
        help="AI agent to use: claude, kimi, codex, copilot, gemini, glm4, minimax (default: codex)",
    )
    parser.add_argument(
        "--action",
        default="loop",
        help="Ralph loop action: start, loop, status, resume (default: loop).",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=10,
        help="Seconds to wait between iterations (default: 10).",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Maximum number of iterations before aborting (default: 100).",
    )
    parser.add_argument(
        "--dangerously-bypass-approvals",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable YOLO mode (bypass all approvals). Uses agent-specific flag: codex (--dangerously-bypass-approvals-and-sandbox), claude/glm4/minimax (--dangerously-skip-permissions), gemini (-y), kimi (--yolo), copilot (--allow-all). (default: enabled).",
    )
    parser.add_argument(
        "--full-auto",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="(Codex only) Pass --full-auto (default: enabled).",
    )
    parser.add_argument(
        "--yolo",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable YOLO mode for all agents (default: enabled). Same as --dangerously-bypass-approvals.",
    )
    parser.add_argument(
        "--model",
        help="Model to use (e.g. claude: sonnet/opus/haiku, codex: gpt-5.4/o3, gemini: gemini-2.5-pro, kimi: kimi-k1.5, glm4: glm-4-plus, minimax: abab6.5s, copilot: gpt-4).",
    )
    parser.add_argument(
        "-C", "--workdir",
        default=".",
        help="Project working directory (default: current directory).",
    )
    parser.add_argument(
        "--ralph-script",
        default="~/.agents/skills/ralph-loop/scripts/ralph_loop.py",
        help="Path to ralph_loop.py script.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing them.",
    )
    return parser.parse_args()


def normalize_state(plan: dict) -> dict:
    """Extract normalized state from fix_plan.json."""
    raw_state = plan.get("state")

    if isinstance(raw_state, dict):
        return {
            "step": raw_state.get("step", "unknown"),
            "current_task": raw_state.get("current_task", "N/A"),
            "iteration": raw_state.get("iteration", 0),
            "task_range": raw_state.get("task_range", {}),
        }

    # Legacy format
    step = raw_state if isinstance(raw_state, str) else "unknown"
    tasks = plan.get("tasks", [])
    current_task = "N/A"
    task_range = {}

    if tasks:
        task_range = {"from": tasks[0].get("id"), "to": tasks[-1].get("id")}
        for t in tasks:
            if t.get("status") not in ("completed", "done"):
                current_task = t.get("id", "N/A")
                break
        if current_task == "N/A" and tasks:
            current_task = tasks[-1].get("id", "N/A")

    return {
        "step": step,
        "current_task": current_task,
        "iteration": plan.get("iteration", 0),
        "task_range": task_range,
    }


def read_fix_plan(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_ralph_loop(script_path: str, spec_path: str, action: str, agent: str) -> Tuple[str, str, int]:
    """Run ralph_loop.py with given action. Returns (stdout, stderr, exit_code)."""
    cmd = ["python3", script_path, f"--action={action}", f"--spec={spec_path}", f"--agent={agent}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1


def extract_command_from_output(stdout: str, agent: str) -> Optional[str]:
    """Extract the command to execute from ralph_loop.py output."""
    lines = stdout.split('\n')
    in_execute_block = False
    
    for line in lines:
        stripped = line.strip()
        if stripped == "Execute:":
            in_execute_block = True
            continue
        if in_execute_block and stripped:
            # Clean up the command
            cmd = stripped.strip('`').strip()
            # Remove leading $ if present
            if cmd.startswith('$'):
                cmd = cmd[1:].strip()
            # For agents that don't use / prefix, remove it
            if agent in ("codex", "copilot") and cmd.startswith('/'):
                cmd = cmd[1:]
            return cmd
    
    # Fallback: search for command patterns
    for line in lines:
        if agent in ("claude", "kimi", "gemini"):
            match = re.search(r'(/[\w:-]+[^\n`]+)', line)
        else:
            match = re.search(r'([\w-]+:[\w-]+[^\n`]+)', line) or re.search(r'(task-\w+[^\n`]+)', line)
        if match:
            cmd = match.group(1).strip()
            if agent in ("codex", "copilot") and cmd.startswith('/'):
                cmd = cmd[1:]
            return cmd
    
    return None


def run_agent(agent: str, prompt: str, args) -> int:
    """Run the specified agent with the given prompt."""
    agent_config = AGENTS[agent]
    
    if args.dry_run:
        model_str = ""
        if args.model and agent_config.get("supports_model"):
            model_str = f" {agent_config['model_flag']} {args.model}"
        if agent_config.get("prompt_arg"):
            print(f"  [DRY RUN] Would execute: {' '.join(agent_config['cmd'])}{model_str} '{prompt[:50]}...'")
        else:
            print(f"  [DRY RUN] Would execute: echo '{prompt[:50]}...' | {' '.join(agent_config['cmd'])}{model_str}")
        return 0
    
    cmd = list(agent_config["cmd"])
    
    # Add print/non-interactive flag if supported (Kimi requires --print)
    if agent_config.get("print_flag"):
        cmd.append(agent_config["print_flag"])
    
    # Add YOLO flag if enabled and supported
    yolo_enabled = getattr(args, 'yolo', args.dangerously_bypass_approvals)
    if yolo_enabled and agent_config.get("supports_yolo"):
        yolo_flag = agent_config.get("yolo_flag")
        if yolo_flag:
            cmd.append(yolo_flag)
    
    # Add agent-specific flags (Codex specific)
    if agent == "codex" and agent_config["supports_flags"]:
        # YOLO already handled above, add full-auto if not in yolo mode
        if not yolo_enabled and args.full_auto:
            cmd.append("--full-auto")
        if args.workdir and args.workdir != ".":
            cmd.extend(["-C", args.workdir])
    
    # Add model flag if supported and provided
    if args.model and agent_config.get("supports_model"):
        model_flag = agent_config.get("model_flag", "--model")
        cmd.extend([model_flag, args.model])
    
    # Handle different prompt passing modes
    if agent_config.get("prompt_arg"):
        # Agents that take prompt as argument (claude, gemini, copilot, glm4, minimax)
        # Some agents need -p flag before prompt (gemini)
        if agent_config.get("prompt_flag"):
            cmd.append(agent_config["prompt_flag"])
        cmd.append(prompt)
        print(f"  → Spawning: {' '.join(cmd[:3])} ... '{prompt[:60]}...'")
    else:
        # Agents that read from stdin (kimi, codex)
        cmd.append("-")  # Read from stdin
        print(f"  → Spawning: {' '.join(cmd)}")
        print(f"  → Prompt: {prompt[:80]}...")
    
    try:
        if agent_config.get("prompt_arg"):
            result = subprocess.run(cmd)
        else:
            result = subprocess.run(cmd, input=prompt, text=True)
        return result.returncode
    except FileNotFoundError:
        print(f"ERROR: '{cmd[0]}' command not found. Make sure {AGENTS[agent]['name']} is installed.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR running {agent}: {e}", file=sys.stderr)
        return 1


def print_header(agent: str, spec_path: str, workdir: str):
    """Print script header with agent info."""
    agent_name = AGENTS[agent]["name"]
    print("=" * 60)
    print(f"🔄 Ralph Loop | {agent_name}")
    print(f"📁 Spec: {spec_path}")
    print(f"📂 Workdir: {workdir}")
    print("=" * 60)


def main():
    args = parse_args()

    spec_path = args.spec
    workdir = os.path.abspath(args.workdir)
    spec_abs = os.path.join(workdir, spec_path)
    fix_plan_path = os.path.join(spec_abs, "_ralph_loop", "fix_plan.json")
    ralph_script = os.path.expanduser(args.ralph_script)
    if not os.path.isabs(ralph_script):
        ralph_script = os.path.join(workdir, ralph_script)
    agent = args.agent

    # Validate agent
    if agent not in AGENTS:
        print(f"ERROR: Unknown agent '{agent}'", file=sys.stderr)
        print(f"Supported agents: {', '.join(AGENTS.keys())}", file=sys.stderr)
        sys.exit(1)

    # Check ralph script exists
    if not os.path.isfile(ralph_script):
        print(f"ERROR: ralph_loop.py not found at {ralph_script}", file=sys.stderr)
        sys.exit(1)

    # Bootstrap: initialize if needed
    if args.action == "start":
        print_header(agent, spec_path, workdir)
        print("[bootstrap] Initializing fix_plan.json...")
        stdout, stderr, exit_code = run_ralph_loop(ralph_script, spec_path, "start", agent)
        print(stdout)
        if stderr:
            print(f"  ⚠️  stderr: {stderr}", file=sys.stderr)
        if exit_code != 0:
            sys.exit(exit_code)
        time.sleep(2)

    if not os.path.isfile(fix_plan_path):
        print(f"ERROR: fix_plan.json not found at {fix_plan_path}", file=sys.stderr)
        print("Hint: run with --action=start first.", file=sys.stderr)
        sys.exit(1)

    print_header(agent, spec_path, workdir)
    print(f"Monitoring: {fix_plan_path}")
    print("-" * 60)

    iteration = 1
    
    while True:
        # Read current state
        plan = read_fix_plan(fix_plan_path)
        norm = normalize_state(plan)
        step = norm["step"]
        current_task = norm["current_task"]
        task_range = norm["task_range"]
        range_str = f"{task_range.get('from', '?')}→{task_range.get('to', '?')}"

        # Print status
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        print(f"\n[{now}] Iteration {iteration} | Task: {current_task} | Step: {step} | Range: {range_str}")
        sys.stdout.flush()

        # Check for completion
        if step in ("complete", "failed"):
            print(f"\n{'=' * 60}")
            if step == "complete":
                print("✅ LOOP COMPLETE — All tasks processed successfully!")
            else:
                print(f"❌ LOOP FAILED — Check {fix_plan_path} for details.")
            print(f"{'=' * 60}")
            break

        # Safety limit
        if iteration > args.max_iterations:
            print(f"\n⚠️  SAFETY STOP: Max iterations ({args.max_iterations}) reached.")
            sys.exit(2)

        # Step 1: Get command from ralph_loop.py
        print("  → Getting command from ralph_loop.py...")
        stdout, stderr, exit_code = run_ralph_loop(ralph_script, spec_path, "loop", agent)
        
        if exit_code != 0:
            print(f"  ❌ ralph_loop.py failed: {stderr}", file=sys.stderr)
            time.sleep(args.delay)
            iteration += 1
            continue
        
        print(stdout)
        
        # Step 2: Extract command
        command = extract_command_from_output(stdout, agent)
        
        if not command:
            print("  ⚠️  Could not extract command. Retrying...", file=sys.stderr)
            time.sleep(args.delay)
            iteration += 1
            continue
        
        # Step 3: Execute with agent
        print(f"  → Executing with {AGENTS[agent]['name']}...")
        exit_code = run_agent(agent, command, args)
        
        if exit_code != 0:
            print(f"  ⚠️  Agent exited with code {exit_code}", file=sys.stderr)
            # Continue anyway - partial success is possible
        
        # Step 4: Advance state
        print("  → Advancing state...")
        stdout, stderr, exit_code = run_ralph_loop(ralph_script, spec_path, "next", agent)
        
        if exit_code != 0:
            print(f"  ❌ Failed to advance state: {stderr}", file=sys.stderr)
        else:
            # Print just the advancement line
            for line in stdout.split('\n'):
                if 'Advanced' in line or '→' in line:
                    print(f"  {line.strip()}")
                    break

        print(f"  ⏳ Sleeping {args.delay}s...")
        time.sleep(args.delay)
        iteration += 1


if __name__ == "__main__":
    main()
