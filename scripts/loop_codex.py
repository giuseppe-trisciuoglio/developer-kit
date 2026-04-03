#!/usr/bin/env python3
"""
loop_codex.py — Automates the Ralph Loop with Codex CLI.

Usage:
    specs_codex_loop --spec=docs/specs/004-jwt-lambda-authorizer --action=loop --full-auto

The script locates fix_plan.json in the spec folder and keeps invoking
`codex exec` until the state becomes "complete" or "failed".
It prints progress to stdout so you know it is alive.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone


def parse_args():
    parser = argparse.ArgumentParser(
        description="Ralph Loop automation for Codex CLI. "
                    "Keeps invoking codex exec until fix_plan.json reports complete/failed."
    )
    parser.add_argument(
        "--spec",
        required=True,
        help="Spec folder path (e.g. docs/specs/004-jwt-lambda-authorizer).",
    )
    parser.add_argument(
        "--action",
        default="loop",
        help="Ralph loop action: start, loop, status, resume (default: loop).",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=5,
        help="Seconds to wait between iterations (default: 5).",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=100,
        help="Maximum number of iterations before aborting as a safety limit (default: 100).",
    )
    parser.add_argument(
        "--dangerously-bypass-approvals",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Pass --dangerously-bypass-approvals-and-sandbox to codex exec (default: enabled).",
    )
    parser.add_argument(
        "--full-auto",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Pass --full-auto to codex exec (default: enabled).",
    )
    parser.add_argument(
        "--model",
        help="Model to use with codex exec (e.g. o3, gpt-5.3-codex).",
    )
    parser.add_argument(
        "-C", "--workdir",
        default=".",
        help="Project working directory where codex should run (default: current directory).",
    )
    return parser.parse_args()


def normalize_state(plan: dict) -> dict:
    """
    Support both documented format (state as object) and legacy/example format
    (state as string + tasks array).
    """
    raw_state = plan.get("state")

    # Format 1: documented skill format
    if isinstance(raw_state, dict):
        return {
            "step": raw_state.get("step", "unknown"),
            "current_task": raw_state.get("current_task", "N/A"),
            "iteration": raw_state.get("iteration", 0),
            "task_range": raw_state.get("task_range", {}),
        }

    # Format 2: legacy/example format (state is a string)
    step = raw_state if isinstance(raw_state, str) else "unknown"
    tasks = plan.get("tasks", [])
    current_task = "N/A"
    task_range = {}

    if tasks:
        task_range = {
            "from": tasks[0].get("id"),
            "to": tasks[-1].get("id"),
        }
        idx = plan.get("currentTaskIndex")
        if isinstance(idx, int) and 0 <= idx < len(tasks):
            current_task = tasks[idx].get("id", "N/A")
        else:
            for t in tasks:
                if t.get("status") != "completed":
                    current_task = t.get("id", "N/A")
                    break
            if current_task == "N/A" and tasks:
                current_task = tasks[-1].get("id", "N/A")

    iteration = plan.get("iteration", plan.get("currentTaskIndex", 0))

    return {
        "step": step,
        "current_task": current_task,
        "iteration": iteration,
        "task_range": task_range,
    }


def read_fix_plan(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_codex_prompt(spec_path: str, action: str) -> str:
    """Return the minimal skill invocation prompt for Codex."""
    # Ensure trailing slash for consistency with skill expectations
    normalized_spec = spec_path if spec_path.endswith("/") else f"{spec_path}/"
    return f'$specs.ralph-loop --action={action} --spec="{normalized_spec}"'


def run_codex(prompt: str, args) -> int:
    """Run codex exec with the given prompt and return its exit code."""
    cmd = ["codex", "exec"]

    # These two flags are mutually exclusive in codex exec.
    # dangerously-bypass-approvals-and-sandbox is the "max yolo" mode,
    # so it takes precedence over --full-auto.
    if args.dangerously_bypass_approvals:
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    elif args.full_auto:
        cmd.append("--full-auto")

    if args.model:
        cmd.extend(["--model", args.model])
    if args.workdir and args.workdir != ".":
        cmd.extend(["-C", args.workdir])

    # codex exec reads from stdin when prompt arg is "-" or absent and stdin is piped.
    cmd.append("-")

    print(f"  → Spawning: {' '.join(cmd)}")
    print(f"  → Prompt: {prompt}")
    try:
        result = subprocess.run(cmd, input=prompt, text=True)
        return result.returncode
    except FileNotFoundError:
        print("ERROR: 'codex' command not found. Make sure Codex CLI is installed and in PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR running codex: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    args = parse_args()

    spec_path = args.spec
    workdir = os.path.abspath(args.workdir)
    spec_abs = os.path.join(workdir, spec_path)
    fix_plan_path = os.path.join(spec_abs, "_ralph_loop", "fix_plan.json")

    # If action is "start", run it once first (fix_plan.json may not exist yet).
    # After that we automatically switch to looping with "loop".
    current_action = args.action
    if current_action == "start":
        print(f"Ralph Loop | Codex CLI | Workdir: {workdir}")
        print(f"Spec: {spec_path}")
        print("-" * 60)
        print("[bootstrap] Running --action=start to initialize fix_plan.json")
        codex_prompt = build_codex_prompt(spec_path, "start")
        exit_code = run_codex(codex_prompt, args)
        if exit_code != 0:
            print(f"  ⚠️  codex exec exited with code {exit_code}", file=sys.stderr)
            sys.exit(exit_code)
        # Give a small grace period for filesystem sync
        time.sleep(2)
        current_action = "loop"

    if not os.path.isfile(fix_plan_path):
        print(f"ERROR: fix_plan.json not found at {fix_plan_path}", file=sys.stderr)
        print("Hint: run with --action=start first.", file=sys.stderr)
        sys.exit(1)

    iteration = 1
    print(f"Ralph Loop | Codex CLI | Workdir: {workdir}")
    print(f"Spec: {spec_path}")
    print(f"Monitoring: {fix_plan_path}")
    print("-" * 60)

    while True:
        plan = read_fix_plan(fix_plan_path)
        norm = normalize_state(plan)
        step = norm["step"]
        current_task = norm["current_task"]
        task_range = norm["task_range"]
        range_str = f"{task_range.get('from', '?')}→{task_range.get('to', '?')}"

        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        status_line = (
            f"[{now}] Ralph Loop | Iteration {iteration} | "
            f"Task {current_task} | Step: {step} | Range: {range_str}"
        )
        print(status_line)
        sys.stdout.flush()

        if step in ("complete", "failed"):
            print(f"\n{'=' * 60}")
            print(f"Loop finished with state: {step.upper()}")
            if step == "complete":
                print("All tasks have been processed successfully.")
            else:
                print("Processing stopped due to a failure.")
            print(f"{'=' * 60}")
            break

        if iteration > args.max_iterations:
            print(f"\n{'=' * 60}")
            print(f"SAFETY STOP: reached max iterations ({args.max_iterations}).")
            print("This may indicate an infinite loop. Inspect fix_plan.json and resume manually.")
            print(f"{'=' * 60}")
            sys.exit(2)

        codex_prompt = build_codex_prompt(spec_path, current_action)
        exit_code = run_codex(codex_prompt, args)

        if exit_code != 0:
            print(f"  ⚠️  codex exec exited with code {exit_code}", file=sys.stderr)

        print(f"  → Sleeping {args.delay}s before next iteration...\n")
        sys.stdout.flush()
        time.sleep(args.delay)
        iteration += 1


if __name__ == "__main__":
    main()
