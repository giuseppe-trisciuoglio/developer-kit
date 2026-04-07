#!/usr/bin/env python3
"""
agents_loop.py — Universal Ralph Loop automation for multiple AI agents.

Supports: claude, kimi, codex, copilot, gemini, glm4, minimax, openrouter

Usage:
    agents_loop --spec=docs/specs/001-feature --agent=claude
    agents_loop --spec=docs/specs/001-feature --agent=codex --delay=10
    agents_loop --spec=docs/specs/001-feature --agent=kimi --max-iterations=50
    agents_loop --spec=docs/specs/001-feature --agent=auto              # Auto-select agent by phase
    agents_loop --spec=docs/specs/001-feature --agent=claude --verbose  # Enable debug output
    agents_loop --spec=docs/specs/001-feature --agent=claude --fast     # Fast mode: skip cleanup/sync

The script automates the Ralph Loop workflow:
    1. ralph_loop.py --action=loop  → Get command to execute
    2. Execute with chosen agent    → Run the command
    3. ralph_loop.py --action=next  → Advance state
    4. Repeat until complete/failed

AUTO MODE (--agent=auto):
    Automatically selects the best agent for each phase:
    - review:       copilot (specialized for code review)
    - sync:         gemini (powerful context analysis)
    - implementation/fix/cleanup: rotates between claude, kimi, codex
    - other steps:  claude (default)

DEBUGGING:
    Use --verbose to enable detailed output:
    - Full command execution
    - Agent stdout/stderr streaming in real-time
    - Execution timing with progress indicators
    - Timeout monitoring
    - Per-iteration log files in .agents_loop_logs/

    Use --agent-timeout to set custom timeout (default: 600s)
    Use --debug-stream to force real-time output even without --verbose

FAST MODE (--fast):
    Skips cleanup and sync steps for faster iteration:
    - Normal: review → cleanup → sync → update_done
    - Fast:   review → update_done
    
    Use when you want rapid implementation→review cycles without
the overhead of code cleanup and spec synchronization.
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Optional, Tuple, IO
from pathlib import Path


# Global flag for graceful shutdown
_should_exit = False

# Global stats for monitoring
_agent_stats = {
    "start_time": None,
    "last_output_time": None,
    "output_line_count": 0,
    "output_char_count": 0,
}


def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m{secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h{minutes}m"


def get_log_dir(spec_path: str) -> Path:
    """Get or create log directory for agent outputs."""
    log_dir = Path(".agents_loop_logs") / Path(spec_path).name
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def signal_handler(signum, frame):
    """Handle SIGINT (Ctrl+C) for graceful shutdown."""
    global _should_exit
    print("\n\n⚠️  Interruzione richiesta (Ctrl+C). Terminazione in corso...")
    _should_exit = True


# Register signal handler for SIGINT (Ctrl+C / Cmd+C)
signal.signal(signal.SIGINT, signal_handler)


# Agent configurations
# Each agent defines how to run it in non-interactive mode
AGENTS = {
    # Special "auto" mode - selects agent dynamically based on workflow phase
    "auto": None,  # Placeholder, handled specially in code
    "claude": {
        "name": "Claude Code",
        "cmd": ["claude"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "supports_streaming": True,
        "model_flag": "--model",
        "yolo_flag": "--dangerously-skip-permissions",
        "prompt_arg": True,
        "prompt_flag": "-p",
        "streaming_flags": ["--output-format=stream-json", "--include-partial-messages"],
    },
    "glm4": {
        "name": "GLM-4 CLI",
        "cmd": ["glm4"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "supports_streaming": False,  # Disabled - wrapper adds --print automatically which conflicts with stream-json
        "print_flag": "--print",  # Required for non-interactive mode
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
        "supports_streaming": False,  # Disabled - wrapper adds --print automatically which conflicts with stream-json
        "print_flag": "--print",  # Required for non-interactive mode
        "model_flag": "--model",
        "yolo_flag": "--dangerously-skip-permissions",
        "prompt_arg": True,
        "prompt_flag": "-p",
    },
    "openrouter": {
        "name": "OpenRouter CLI",
        "cmd": ["openrouter"],
        "stdin_mode": False,
        "supports_flags": True,
        "supports_model": True,
        "supports_yolo": True,
        "supports_streaming": False,  # Disabled - wrapper adds --print automatically which conflicts with stream-json
        "print_flag": "--print",  # Required for non-interactive mode
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
        "supports_streaming": False,  # Explicitly disable - Kimi doesn't support stream-json
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
        "supports_streaming": False,  # Uses stdin mode, not streaming
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
        "supports_streaming": False,  # Uses standard subprocess
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
        "supports_streaming": False,  # Uses standard subprocess
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
        help="AI agent to use: claude, kimi, codex, copilot, gemini, glm4, minimax, openrouter, auto (default: codex). Use 'auto' for intelligent agent selection by workflow phase.",
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
        help="Model to use (e.g. claude: sonnet/opus/haiku, codex: gpt-5.4/o3, gemini: gemini-3-pro, kimi: kimi-k1.5, glm4: glm-4-plus, minimax: abab6.5s, copilot: gpt-4).",
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
    parser.add_argument(
        "--no-commit",
        action="store_true",
        default=True,
        help="Skip git commits during task completion (default: enabled).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable verbose output for debugging (default: disabled).",
    )
    parser.add_argument(
        "--agent-timeout",
        type=int,
        default=600,
        help="Timeout in seconds for agent execution (default: 600).",
    )
    parser.add_argument(
        "--debug-stream",
        action="store_true",
        default=False,
        help="Force real-time streaming output even without --verbose (default: disabled).",
    )
    parser.add_argument(
        "--no-log-files",
        action="store_true",
        default=False,
        help="Disable writing log files to .agents_loop_logs/ (default: logs enabled).",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        default=False,
        help="Fast mode: skip cleanup and sync steps, go directly from review to update_done (default: disabled).",
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


def save_fix_plan(path: str, data: dict):
    """Save fix_plan.json with proper formatting."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # Add trailing newline like ralph_loop.py does


def run_ralph_loop(script_path: str, spec_path: str, action: str, agent: str, no_commit: bool = True) -> Tuple[str, str, int]:
    """Run ralph_loop.py with given action. Returns (stdout, stderr, exit_code)."""
    cmd = ["python3", script_path, f"--action={action}", f"--spec={spec_path}", f"--agent={agent}"]
    if no_commit:
        cmd.append("--no-commit")
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


# Non-interactive mode instructions - prepended to all prompts
# This ensures agents don't ask questions when there's no human in the loop
NON_INTERACTIVE_PREFIX = """[CRITICAL: NON-INTERACTIVE MODE]
You are running in FULLY AUTOMATED mode. There is NO human in the loop to answer questions.

STRICT RULES:
1. DO NOT ask the user any questions
2. DO NOT use AskUserQuestion or similar tools
3. DO NOT prompt for confirmation or choices (A/B/C/D)
4. ALWAYS proceed with the RECOMMENDED or DEFAULT option
5. If multiple options exist, choose the SAFEST and MOST CONSERVATIVE approach
6. Make your best judgment and EXECUTE immediately
7. Report what you did, don't ask what to do

If you encounter ambiguities, use your expertise to decide and proceed.
If you need clarification, make a reasonable assumption and document it.

---

"""


def run_agent(agent: str, prompt: str, args) -> int:
    """Run the specified agent with the given prompt.
    
    For claude-based agents (claude, glm4, minimax, openrouter), this uses
    real-time streaming output with progress indicators and optional log files.
    """
    agent_config = AGENTS[agent]

    # Prepend non-interactive instructions to prevent questions
    full_prompt = NON_INTERACTIVE_PREFIX + prompt

    if args.dry_run:
        model_str = ""
        if args.model and agent_config.get("supports_model"):
            model_str = f" {agent_config['model_flag']} {args.model}"
        if agent_config.get("prompt_arg"):
            print(f"  [DRY RUN] Would execute: {' '.join(agent_config['cmd'])}{model_str} '{full_prompt[:50]}...'")
        else:
            print(f"  [DRY RUN] Would execute: echo '{full_prompt[:50]}...' | {' '.join(agent_config['cmd'])}{model_str}")
        return 0

    cmd = list(agent_config["cmd"])

    # Add print/non-interactive flag if supported (Kimi and Claude wrappers require --print)
    if agent_config.get("print_flag"):
        cmd.append(agent_config["print_flag"])
    
    # Add verbose flag if enabled (required for streaming output on Claude wrappers)
    if verbose and agent_config.get("supports_streaming"):
        cmd.append("--verbose")

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

    # Add streaming flags for agents that support it (for real-time output)
    if agent_config.get("supports_streaming"):
        streaming_flags = agent_config.get("streaming_flags", [])
        for flag in streaming_flags:
            cmd.append(flag)

    # Handle different prompt passing modes
    if agent_config.get("prompt_arg"):
        # Agents that take prompt as argument (claude, gemini, copilot, glm4, minimax)
        # Some agents need -p flag before prompt (gemini)
        if agent_config.get("prompt_flag"):
            cmd.append(agent_config["prompt_flag"])
        cmd.append(full_prompt)
        # Truncate for display (skip the prefix in display)
        display_prompt = prompt[:60] if len(prompt) > 60 else prompt
        print(f"  → Spawning: {' '.join(cmd[:3])} ... '{display_prompt}...'")
    else:
        # Agents that read from stdin (kimi, codex)
        cmd.append("-")  # Read from stdin
        print(f"  → Spawning: {' '.join(cmd)}")
        # Truncate for display (skip the prefix in display)
        display_prompt = prompt[:80] if len(prompt) > 80 else prompt
        print(f"  → Prompt: {display_prompt}...")

    # Get timeout and debug settings from args
    timeout = getattr(args, 'agent_timeout', 600)
    verbose = getattr(args, 'verbose', False)
    debug_stream = getattr(args, 'debug_stream', False)
    enable_streaming = verbose or debug_stream

    if verbose:
        print(f"  🔍 Verbose mode: Full command: {' '.join(cmd)}")
        print(f"  ⏱️  Timeout set to {timeout}s")

    try:
        # For claude-based agents, use real-time streaming
        if agent in ("claude", "glm4", "minimax", "openrouter"):
            return _run_agent_streaming(agent, cmd, full_prompt, timeout, enable_streaming, args)
        else:
            # For other agents, use standard subprocess with timeout
            return _run_agent_standard(agent_config, cmd, full_prompt, timeout, enable_streaming)

    except subprocess.TimeoutExpired as e:
        elapsed = time.time() - _agent_stats["start_time"] if _agent_stats["start_time"] else timeout
        print(f"\n  ⏱️  TIMEOUT after {format_duration(elapsed)}: Agent {agent} exceeded {timeout}s limit.", file=sys.stderr)
        print(f"  📊 Stats: {_agent_stats['output_line_count']} lines, {_agent_stats['output_char_count']} chars output", file=sys.stderr)
        print(f"  💡 The agent might be stuck in a loop. Check the task manually.", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"ERROR: '{cmd[0]}' command not found. Make sure {AGENTS[agent]['name']} is installed.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR running {agent}: {e}", file=sys.stderr)
        import traceback
        if verbose:
            print(f"  📋 Traceback:", file=sys.stderr)
            traceback.print_exc()
        return 1


def _run_agent_streaming(agent: str, cmd: list, prompt: str, timeout: int, enable_streaming: bool, args) -> int:
    """Run agent with real-time output streaming and optional logging."""
    global _agent_stats
    
    _agent_stats = {
        "start_time": time.time(),
        "last_output_time": time.time(),
        "output_line_count": 0,
        "output_char_count": 0,
    }
    
    # Setup log file if enabled
    log_file: Optional[IO] = None
    log_path: Optional[Path] = None
    if not getattr(args, 'no_log_files', False) and getattr(args, 'spec', None):
        try:
            log_dir = get_log_dir(args.spec)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            log_filename = f"{agent}_{timestamp}.log"
            log_path = log_dir / log_filename
            log_file = open(log_path, 'w', encoding='utf-8')
            log_file.write(f"# Agent: {agent}\n")
            log_file.write(f"# Started: {datetime.now(timezone.utc).isoformat()}\n")
            log_file.write(f"# Command: {' '.join(cmd)}\n")
            log_file.write(f"# Timeout: {timeout}s\n")
            log_file.write("=" * 60 + "\n\n")
            log_file.flush()
        except Exception as e:
            if enable_streaming:
                print(f"  ⚠️  Could not create log file: {e}")
    
    agent_config = AGENTS[agent]
    stdout_lines = []
    stderr_lines = []
    
    try:
        if agent_config.get("prompt_arg"):
            # Prompt-based agents: run with Popen and stream output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
        else:
            # Stdin-based agents
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            # Send prompt to stdin
            if process.stdin:
                process.stdin.write(prompt)
                process.stdin.close()
        
        # Create threads to read stdout and stderr in real-time
        # Enable JSON parsing for agents that use --output-format=stream-json
        parse_json = agent_config.get("supports_streaming", False)
        
        stdout_thread = threading.Thread(
            target=_stream_reader,
            args=(process.stdout, "stdout", enable_streaming, log_file, stdout_lines, parse_json)
        )
        stderr_thread = threading.Thread(
            target=_stream_reader,
            args=(process.stderr, "stderr", enable_streaming, log_file, stderr_lines, False)  # stderr is not JSON
        )
        
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()
        
        # Progress monitoring loop
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        spinner_idx = 0
        last_status_update = time.time()
        status_interval = 5.0  # Update status every 5 seconds
        
        if enable_streaming:
            print(f"  🚀 Agent started with streaming output...")
            if log_path:
                print(f"  📝 Logging to: {log_path}")
        
        while process.poll() is None:
            # Check for timeout
            elapsed = time.time() - _agent_stats["start_time"]
            if elapsed > timeout:
                process.terminate()
                time.sleep(0.5)
                if process.poll() is None:
                    process.kill()
                raise subprocess.TimeoutExpired(cmd, timeout)
            
            # Show progress indicator
            current_time = time.time()
            time_since_output = current_time - _agent_stats["last_output_time"]
            
            if enable_streaming and current_time - last_status_update >= status_interval:
                spinner = spinner_chars[spinner_idx % len(spinner_chars)]
                spinner_idx += 1
                
                # Show different indicator based on activity
                if time_since_output > 30:
                    # No output for 30+ seconds - possible hang
                    status_icon = "⏸️ "
                    status_msg = f"no output for {format_duration(time_since_output)}"
                elif time_since_output > 10:
                    # No output for 10+ seconds - slow
                    status_icon = "🐌"
                    status_msg = f"slow ({format_duration(time_since_output)} since last output)"
                else:
                    # Normal progress
                    status_icon = spinner
                    status_msg = f"running ({format_duration(elapsed)})"
                
                lines = _agent_stats['output_line_count']
                chars = _agent_stats['output_char_count']
                print(f"\r  {status_icon} {AGENTS[agent]['name']}: {status_msg} | {lines} lines, {chars} chars", end="", flush=True)
                last_status_update = current_time
            
            time.sleep(0.1)
        
        # Wait for reader threads to finish
        stdout_thread.join(timeout=2.0)
        stderr_thread.join(timeout=2.0)
        
        # Clear progress line
        if enable_streaming:
            print("\r" + " " * 80 + "\r", end="")  # Clear line
        
        elapsed = time.time() - _agent_stats["start_time"]
        lines = _agent_stats['output_line_count']
        chars = _agent_stats['output_char_count']
        
        # Print summary
        if enable_streaming:
            if process.returncode == 0:
                print(f"  ✅ Completed in {format_duration(elapsed)} ({lines} lines, {chars} chars)")
            else:
                print(f"  ❌ Failed in {format_duration(elapsed)} with exit code {process.returncode}")
        
        # Close log file
        if log_file:
            log_file.write(f"\n\n{'=' * 60}\n")
            log_file.write(f"# Exit code: {process.returncode}\n")
            log_file.write(f"# Duration: {format_duration(elapsed)}\n")
            log_file.write(f"# Lines: {lines}, Chars: {chars}\n")
            log_file.write(f"# Ended: {datetime.now(timezone.utc).isoformat()}\n")
            log_file.close()
        
        return process.returncode
        
    except Exception:
        if log_file:
            log_file.close()
        raise


def _stream_reader(pipe, stream_name: str, enable_streaming: bool, log_file: Optional[IO], storage_list: list, parse_json: bool = False):
    """Read from a pipe and print/log output in real-time.
    
    Args:
        pipe: The pipe to read from
        stream_name: Name of the stream (stdout/stderr)
        enable_streaming: Whether to print output in real-time
        log_file: Optional file handle for logging
        storage_list: List to store all lines
        parse_json: If True, parse each line as JSON (for Claude Code stream-json format)
    """
    global _agent_stats
    
    try:
        for line in iter(pipe.readline, ''):
            if not line:
                break
            
            line_stripped = line.rstrip('\n\r')
            storage_list.append(line_stripped)
            
            # Update stats
            _agent_stats["last_output_time"] = time.time()
            _agent_stats["output_line_count"] += 1
            _agent_stats["output_char_count"] += len(line)
            
            # Write raw line to log file (always log the raw JSON)
            if log_file:
                log_file.write(line)
                log_file.flush()
            
            # Parse JSON stream for Claude Code output-format=stream-json
            display_line = line_stripped
            if parse_json and line_stripped:
                try:
                    import json
                    event = json.loads(line_stripped)
                    # Extract content from message events
                    if event.get("type") == "message":
                        content = event.get("content", "")
                        if content:
                            display_line = content
                        else:
                            # Skip empty content messages
                            continue
                    elif event.get("type") == "error":
                        error_msg = event.get("error", "Unknown error")
                        display_line = f"[ERROR] {error_msg}"
                    elif "partial_content" in event:
                        # Handle partial message chunks
                        display_line = event.get("partial_content", "")
                        if not display_line:
                            continue
                    else:
                        # Other event types - skip or show minimally
                        continue
                except json.JSONDecodeError:
                    # Not valid JSON, show as-is
                    pass
                except Exception:
                    # Any other error, show raw line
                    pass
            
            # Print in real-time if enabled
            if enable_streaming and display_line:
                prefix = "   " if stream_name == "stdout" else "  ⚠️ "
                print(f"\r{prefix}{display_line}")
                
    except Exception as e:
        if enable_streaming:
            print(f"\n  ⚠️  Error reading {stream_name}: {e}")
    finally:
        pipe.close()


def _run_agent_standard(agent_config: dict, cmd: list, prompt: str, timeout: int, verbose: bool = False) -> int:
    """Run agent with standard subprocess (for non-claude-based agents).
    
    In verbose mode, streams output in real-time.
    """
    # If verbose mode and agent supports prompt_arg, use streaming
    if verbose and agent_config.get("prompt_arg"):
        return _run_agent_streaming_simple(cmd, timeout)
    
    # Standard execution
    if agent_config.get("prompt_arg"):
        result = subprocess.run(cmd, timeout=timeout)
    else:
        result = subprocess.run(cmd, input=prompt, text=True, timeout=timeout)
    return result.returncode


def _run_agent_streaming_simple(cmd: list, timeout: int) -> int:
    """Simple streaming runner for verbose mode - pipes output but prints in real-time."""
    import select
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    start_time = time.time()
    
    try:
        # Read output line by line as it comes
        while process.poll() is None:
            # Check timeout
            if time.time() - start_time > timeout:
                process.terminate()
                time.sleep(0.5)
                if process.poll() is None:
                    process.kill()
                raise subprocess.TimeoutExpired(cmd, timeout)
            
            # Try to read a line from stdout (non-blocking)
            if process.stdout:
                line = process.stdout.readline()
                if line:
                    print(f"   {line.rstrip()}")
            
            # Small delay to prevent CPU spinning
            time.sleep(0.01)
        
        # Read any remaining output
        remaining_stdout, remaining_stderr = process.communicate(timeout=1)
        if remaining_stdout:
            for line in remaining_stdout.split('\n'):
                if line:
                    print(f"   {line}")
        if remaining_stderr:
            for line in remaining_stderr.split('\n'):
                if line:
                    print(f"  ⚠️  {line}")
        
        return process.returncode
        
    except subprocess.TimeoutExpired:
        process.kill()
        raise


def is_git_repo(workdir: str) -> bool:
    """Check if the working directory is a git repository."""
    try:
        result = subprocess.run(
            ["git", "-C", workdir, "rev-parse", "--git-dir"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def git_checkpoint(workdir: str, iteration: int, task: str, agent: str) -> bool:
    """Create a git checkpoint commit.
    
    Returns True if checkpoint was created or no changes were needed.
    Returns False if there was an error.
    """
    try:
        # Check if there are any changes to commit
        status_result = subprocess.run(
            ["git", "-C", workdir, "status", "--porcelain"],
            capture_output=True,
            text=True
        )
        
        if status_result.returncode != 0:
            print(f"  ⚠️  Failed to check git status", file=sys.stderr)
            return False
        
        # If no changes, nothing to commit
        if not status_result.stdout.strip():
            print(f"  ℹ️  No changes to checkpoint")
            return True
        
        # Stage all changes
        add_result = subprocess.run(
            ["git", "-C", workdir, "add", "-A"],
            capture_output=True,
            text=True
        )
        
        if add_result.returncode != 0:
            print(f"  ⚠️  Failed to stage changes: {add_result.stderr}", file=sys.stderr)
            return False
        
        # Create commit with conventional format: type(scope): subject
        # scope must be lowercase without numbers, so we put iteration in subject
        # Note: Extract just the task number to avoid TASK-XXX pattern rejection
        task_num = task.replace("TASK-", "") if task and task.startswith("TASK-") else (task or "unknown")
        commit_msg = f"chore(checkpoint): iteration {iteration} - {agent} completed task {task_num}"
        commit_result = subprocess.run(
            ["git", "-C", workdir, "commit", "-m", commit_msg],
            capture_output=True,
            text=True
        )
        
        if commit_result.returncode == 0:
            # Get the short commit hash
            hash_result = subprocess.run(
                ["git", "-C", workdir, "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True
            )
            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"
            print(f"  ✅ Git checkpoint: {commit_hash} - {commit_msg}")
            return True
        else:
            print(f"  ⚠️  Failed to create checkpoint: {commit_result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"  ⚠️  Git checkpoint error: {e}", file=sys.stderr)
        return False


# Auto-mode agent selection strategy
# Maps workflow steps to preferred agents
AUTO_MODE_STRATEGY = {
    # Code review: copilot is specialized for code review tasks
    "review": "copilot",
    # Sync: gemini is great at context analysis and synchronization
    "sync": "gemini",
    # Implementation phases: rotate between these agents for diversity
    "implementation": ["claude", "kimi", "codex"],
    "fix": ["claude", "kimi", "codex"],
    "cleanup": ["claude", "kimi", "codex"],
    # Default fallback
    "default": "claude",
}

# Rotation index for implementation agents (global to maintain state across iterations)
_auto_mode_impl_index = 0


def select_auto_agent(step: str) -> str:
    """
    Select the best agent for the given workflow step in auto mode.
    
    Strategy:
    - review: copilot (code review specialist)
    - sync: gemini (powerful context analysis)
    - implementation/fix/cleanup: rotate between claude, kimi, codex
    - other steps: claude (default)
    """
    global _auto_mode_impl_index
    
    # Direct mapping for specialized phases
    if step in ("review",):
        return AUTO_MODE_STRATEGY["review"]
    
    if step in ("sync",):
        return AUTO_MODE_STRATEGY["sync"]
    
    # Rotation for implementation phases
    if step in ("implementation", "fix", "cleanup"):
        agents = AUTO_MODE_STRATEGY["implementation"]
        selected = agents[_auto_mode_impl_index % len(agents)]
        _auto_mode_impl_index += 1
        return selected
    
    # Default for all other steps
    return AUTO_MODE_STRATEGY["default"]


def get_effective_agent(agent: str, step: str) -> str:
    """Get the actual agent to use, resolving 'auto' mode."""
    if agent == "auto":
        return select_auto_agent(step)
    return agent


def print_header(agent: str, spec_path: str, workdir: str, step: str = None, fast_mode: bool = False):
    """Print script header with agent info."""
    if agent == "auto":
        effective_agent = select_auto_agent(step) if step else "auto"
        agent_name = f"🎛️  AUTO MODE (current: {AGENTS[effective_agent]['name']})"
    else:
        agent_name = AGENTS[agent]["name"]
    print("=" * 60)
    mode_str = " | ⚡ FAST MODE" if fast_mode else ""
    print(f"🔄 Ralph Loop | {agent_name}{mode_str}")
    print(f"📁 Spec: {spec_path}")
    print(f"📂 Workdir: {workdir}")
    if agent == "auto" and step:
        print(f"📍 Current step: {step}")
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

    # Validate agent (allow 'auto' as special value)
    if agent not in AGENTS:
        print(f"ERROR: Unknown agent '{agent}'", file=sys.stderr)
        valid_agents = [a for a in AGENTS.keys() if a is not None]
        print(f"Supported agents: {', '.join(valid_agents)}", file=sys.stderr)
        sys.exit(1)

    # Check ralph script exists
    if not os.path.isfile(ralph_script):
        print(f"ERROR: ralph_loop.py not found at {ralph_script}", file=sys.stderr)
        sys.exit(1)

    # Bootstrap: initialize if needed
    if args.action == "start":
        print_header(agent, spec_path, workdir, step="init", fast_mode=args.fast)
        print("[bootstrap] Initializing fix_plan.json...")
        # For start action, use default agent or first rotation
        start_agent = get_effective_agent(agent, "init")
        stdout, stderr, exit_code = run_ralph_loop(ralph_script, spec_path, "start", start_agent, args.no_commit)
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

    # Get initial state for header
    initial_plan = read_fix_plan(fix_plan_path)
    initial_norm = normalize_state(initial_plan)
    initial_step = initial_norm["step"]
    
    print_header(agent, spec_path, workdir, step=initial_step, fast_mode=args.fast)
    print(f"Monitoring: {fix_plan_path}")
    if agent == "auto":
        print("-" * 60)
    
    # Print debug options hint
    if not getattr(args, 'verbose', False) and not getattr(args, 'debug_stream', False):
        print("💡 Debug tip: Add --verbose for full output, or --debug-stream for real-time progress")
        print("   Logs are saved to: .agents_loop_logs/")
    else:
        mode = "verbose" if getattr(args, 'verbose', False) else "streaming"
        print(f"🐛 Debug mode: {mode} (logs: .agents_loop_logs/)")
        print("🎛️  AUTO MODE Strategy:")
        print("   • review:  copilot (code review specialist)")
        print("   • sync:    gemini (context analysis)")
        print("   • impl/fix/cleanup: rotate claude → kimi → codex")
        print("   • other:   claude (default)")
    print("-" * 60)

    iteration = 1
    
    while not _should_exit:
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

        # Determine effective agent for this step (resolves 'auto' mode)
        effective_agent = get_effective_agent(agent, step)
        if agent == "auto":
            print(f"  🤖 Auto-selected agent: {AGENTS[effective_agent]['name']} (for step: {step})")
        
        # Step 1: Get command from ralph_loop.py
        print("  → Getting command from ralph_loop.py...")
        stdout, stderr, exit_code = run_ralph_loop(ralph_script, spec_path, "loop", effective_agent, args.no_commit)
        
        if exit_code != 0:
            print(f"  ❌ ralph_loop.py failed: {stderr}", file=sys.stderr)
            time.sleep(args.delay)
            iteration += 1
            continue
        
        print(stdout)
        
        # Step 2: Extract command
        command = extract_command_from_output(stdout, effective_agent)
        
        if not command:
            print("  ⚠️  Could not extract command. Retrying...", file=sys.stderr)
            time.sleep(args.delay)
            iteration += 1
            continue
        
        # Step 3: Execute with effective agent
        print(f"  → Executing with {AGENTS[effective_agent]['name']}...")
        print(f"  📝 Command preview: {command[:100]}{'...' if len(command) > 100 else ''}")
        
        exit_code = run_agent(effective_agent, command, args)
        
        if exit_code != 0:
            print(f"  ⚠️  Agent exited with code {exit_code}", file=sys.stderr)
            print(f"  💡 Tip: Use --verbose to see full output, or check .agents_loop_logs/ for details")
            print(f"  ⏳ Retrying same step in {args.delay}s...")
            time.sleep(args.delay)
            iteration += 1
            continue
        
        # Step 4: Advance state (use same effective agent)
        print("  → Advancing state...")
        stdout, stderr, exit_code = run_ralph_loop(ralph_script, spec_path, "next", effective_agent, args.no_commit)
        
        if exit_code != 0:
            print(f"  ❌ Failed to advance state: {stderr}", file=sys.stderr)
        else:
            # Print just the advancement line
            for line in stdout.split('\n'):
                if 'Advanced' in line or '→' in line:
                    print(f"  {line.strip()}")
                    break
        
        # Step 4b: Fast mode - skip cleanup and sync steps
        if args.fast and exit_code == 0:
            plan = read_fix_plan(fix_plan_path)
            current_step = plan.get("state", {}).get("step", "")
            
            # In fast mode, skip cleanup and sync and go directly to update_done
            if current_step in ("cleanup", "sync"):
                skipped_steps = []
                while plan.get("state", {}).get("step") in ("cleanup", "sync"):
                    skipped_steps.append(plan["state"]["step"])
                    plan["state"]["step"] = "update_done"
                    save_fix_plan(fix_plan_path, plan)
                
                if skipped_steps:
                    print(f"  ⚡ Fast mode: skipped {', '.join(skipped_steps)} → update_done")

        # Step 5: Git checkpoint (if in a git repository)
        if is_git_repo(workdir):
            git_checkpoint(workdir, iteration, current_task, effective_agent)

        print(f"  ⏳ Sleeping {args.delay}s...")
        try:
            time.sleep(args.delay)
        except KeyboardInterrupt:
            print("\n\n⚠️  Interruzione richiesta. Terminazione in corso...")
            break
        iteration += 1

    print(f"\n{'=' * 60}")
    print("🛑 Loop terminato dall'utente.")
    print(f"{'=' * 60}")
    sys.exit(0)


if __name__ == "__main__":
    main()
