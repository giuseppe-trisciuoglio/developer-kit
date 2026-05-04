#!/usr/bin/env python3
"""
ralph-loop-v2 — Main Orchestrator

Wraps the ralph-loop state machine inside a tracked job so every run
is observable via status/cancel commands.

Usage:
    python3 scripts/main.py start  --spec=docs/specs/001/ [--from-task=TASK-001] [--to-task=TASK-010] [--agent=claude]
    python3 scripts/main.py loop   --spec=docs/specs/001/
    python3 scripts/main.py next   --spec=docs/specs/001/
    python3 scripts/main.py status [--job-id=<id>]
    python3 scripts/main.py cancel --job-id=<id>
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Allow running from any directory
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "lib"))

from tracker import (
    cancel_job, list_jobs, queue_job, read_job, reap_zombies, run_tracked_job,
)

# ---------------------------------------------------------------------------
# Re-use the v1 state-machine logic from ralph_loop.py
# ---------------------------------------------------------------------------
_RALPH_V1 = _HERE.parent.parent / "ralph-loop" / "scripts" / "ralph_loop.py"

def _load_v1():
    """Dynamically import the v1 ralph_loop module."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ralph_loop", _RALPH_V1)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_start(args):
    """Queue a new job and immediately start it (foreground or background)."""
    workspace = os.getcwd()
    job_id    = f"job_{int(time.time() * 1000)}"

    meta = {
        "specFolder":   args.spec,
        "taskRange":    {"from": args.from_task, "to": args.to_task},
        "defaultAgent": args.agent,
    }

    if args.background:
        # Write queued state, then spawn detached child
        job_file = queue_job(job_id, workspace, meta)
        _spawn_background(job_id, args)
        print(f"Job queued in background.")
        print(f"  ID   : {job_id}")
        print(f"  File : {job_file}")
        print(f"  Use  : python3 main.py status --job-id={job_id}")
    else:
        # Run inline (foreground)
        rl = _load_v1()
        rl.action_start(args.spec, args.from_task, args.to_task, args.agent)
        print(f"\nJob ID: {job_id}  (no background tracking for foreground start)")


def cmd_loop(args):
    """Execute one state-machine step, tracked in a job file."""
    workspace = os.getcwd()
    job_id    = f"job_{int(time.time() * 1000)}"
    rl        = _load_v1()

    meta = {"specFolder": args.spec}

    def logic(update):
        step = rl.load_fix_plan(args.spec)["state"]["step"]
        update(f"step:{step}", 0)
        rl.action_loop(args.spec, args.agent, args.no_commit)
        new_step = rl.load_fix_plan(args.spec)["state"]["step"]
        update(f"step:{new_step}", 50)
        return {"step": new_step}

    run_tracked_job(job_id, workspace, meta, logic)


def cmd_next(args):
    """Advance the state machine to the next step."""
    rl = _load_v1()
    rl.action_next(args.spec, args.agent, args.no_commit)


def cmd_status(args):
    """Show job status. If --job-id given, show that job; otherwise list recent jobs."""
    workspace = os.getcwd()
    reap_zombies(workspace)

    if args.job_id:
        job = read_job(args.job_id, workspace)
        if not job:
            print(f"Job not found: {args.job_id}")
            sys.exit(1)
        _print_job(job)
    else:
        jobs = list_jobs(workspace)
        if not jobs:
            print("No jobs found.")
            return
        for job in jobs[:10]:
            _print_job(job, compact=True)


def cmd_cancel(args):
    """Cancel a running job."""
    workspace = os.getcwd()
    if cancel_job(args.job_id, workspace):
        print(f"✅ Job {args.job_id} cancelled.")
    else:
        job = read_job(args.job_id, workspace)
        if not job:
            print(f"❌ Job not found: {args.job_id}")
        else:
            print(f"⚠️  Job {args.job_id} is not running (status: {job['status']})")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_job(job: dict, compact: bool = False) -> None:
    status_icon = {"queued": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}.get(
        job.get("status", ""), "❓"
    )
    if compact:
        print(f"{status_icon} {job['id']}  [{job.get('status')}]  phase={job.get('phase')}  progress={job.get('progress', 0)}%")
        return

    print("─" * 56)
    print(f"ID       : {job['id']}")
    print(f"Status   : {status_icon} {job.get('status')}")
    print(f"Phase    : {job.get('phase')}")
    print(f"Progress : {job.get('progress', 0)}%")
    print(f"PID      : {job.get('pid')}")
    print(f"Created  : {job.get('createdAt')}")
    print(f"Started  : {job.get('startedAt')}")
    print(f"Completed: {job.get('completedAt')}")
    if job.get("errorMessage"):
        print(f"Error    : {job['errorMessage']}")
    if job.get("result"):
        print(f"Result   : {job['result']}")
    print("─" * 56)


def _spawn_background(job_id: str, args) -> None:
    """Spawn a detached child process that runs the loop."""
    import subprocess
    cmd = [
        sys.executable, __file__, "loop",
        f"--spec={args.spec}",
        f"--agent={args.agent}",
    ]
    if args.no_commit:
        cmd.append("--no-commit")

    # Detach from parent (double-fork not needed on macOS/Linux with start_new_session)
    subprocess.Popen(
        cmd,
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="ralph-loop-v2 orchestrator")
    sub = p.add_subparsers(dest="command", required=True)

    # start
    s = sub.add_parser("start", help="Initialize and optionally start a job")
    s.add_argument("--spec",       required=True)
    s.add_argument("--from-task",  default=None, dest="from_task")
    s.add_argument("--to-task",    default=None, dest="to_task")
    s.add_argument("--agent",      default="claude")
    s.add_argument("--background", action="store_true", help="Run in background")
    s.add_argument("--no-commit",  action="store_true", dest="no_commit")

    # loop
    lo = sub.add_parser("loop", help="Execute one state-machine step")
    lo.add_argument("--spec",      required=True)
    lo.add_argument("--agent",     default=None)
    lo.add_argument("--no-commit", action="store_true", dest="no_commit")

    # next
    nx = sub.add_parser("next", help="Advance to next step")
    nx.add_argument("--spec",      required=True)
    nx.add_argument("--agent",     default=None)
    nx.add_argument("--no-commit", action="store_true", dest="no_commit")

    # status
    st = sub.add_parser("status", help="Show job status")
    st.add_argument("--job-id", default=None, dest="job_id")

    # cancel
    ca = sub.add_parser("cancel", help="Cancel a running job")
    ca.add_argument("--job-id", required=True, dest="job_id")

    return p


def main():
    args = build_parser().parse_args()
    dispatch = {
        "start":  cmd_start,
        "loop":   cmd_loop,
        "next":   cmd_next,
        "status": cmd_status,
        "cancel": cmd_cancel,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
