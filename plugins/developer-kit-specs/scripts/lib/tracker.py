"""
ralph-loop-v2 — Job Tracker

Wraps business logic with automatic job-file lifecycle management.
Job files live at: <workspace_root>/.jobs/<job_id>.json

Lifecycle: queued → running → completed | failed

The update(phase, progress) callback lets business logic report
progress without knowing anything about the file format.
"""

import json
import os
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _job_path(workspace_root: str, job_id: str) -> Path:
    return Path(workspace_root) / ".jobs" / f"{job_id}.json"


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_tracked_job(
    job_id: str,
    workspace_root: str,
    meta: dict,
    business_logic: Callable[[Callable[[str, int], None]], Any],
) -> Any:
    """
    Run a tracked job.

    Args:
        job_id:         Unique job identifier.
        workspace_root: Project root; job file stored under .jobs/.
        meta:           Extra fields merged into the job file (spec_folder, task_range, …).
        business_logic: Callable(update) → result.
                        update(phase: str, progress: int) persists progress.

    Returns:
        The value returned by business_logic.
    """
    file_path = _job_path(workspace_root, job_id)

    # 1. Mark as running
    job = {
        "id":           job_id,
        "status":       "running",
        "pid":          os.getpid(),
        "createdAt":    meta.get("createdAt", _now()),
        "startedAt":    _now(),
        "completedAt":  None,
        "phase":        "starting",
        "progress":     0,
        "errorMessage": None,
        **{k: v for k, v in meta.items() if k != "createdAt"},
    }
    _write(file_path, job)

    # 2. Progress callback
    def update(phase: str, progress: int) -> None:
        job["phase"]    = phase
        job["progress"] = progress
        _write(file_path, job)

    try:
        result = business_logic(update)

        # 3. Success
        job.update(status="completed", pid=None,
                   completedAt=_now(), progress=100, result=result)
        _write(file_path, job)
        return result

    except Exception as exc:
        # 4. Failure — clear PID so status can detect zombie jobs
        job.update(status="failed", pid=None, errorMessage=str(exc))
        _write(file_path, job)
        raise


def queue_job(job_id: str, workspace_root: str, meta: dict | None = None) -> str:
    """
    Write an initial 'queued' job file before the process starts.
    Returns the path to the job file.
    """
    file_path = _job_path(workspace_root, job_id)
    job = {
        "id":           job_id,
        "status":       "queued",
        "pid":          None,
        "createdAt":    _now(),
        "startedAt":    None,
        "completedAt":  None,
        "phase":        "queued",
        "progress":     0,
        "errorMessage": None,
        **(meta or {}),
    }
    _write(file_path, job)
    return str(file_path)


def read_job(job_id: str, workspace_root: str) -> Optional[dict]:
    """Read a job file. Returns None if not found."""
    file_path = _job_path(workspace_root, job_id)
    if not file_path.exists():
        return None
    return _read(file_path)


def list_jobs(workspace_root: str) -> list[dict]:
    """
    List all job files under <workspace_root>/.jobs/.
    Returns parsed job objects sorted by createdAt descending.
    """
    jobs_dir = Path(workspace_root) / ".jobs"
    if not jobs_dir.exists():
        return []

    jobs = []
    for f in jobs_dir.glob("*.json"):
        try:
            jobs.append(_read(f))
        except Exception:
            pass

    return sorted(jobs, key=lambda j: j.get("createdAt", ""), reverse=True)


def reap_zombies(workspace_root: str) -> list[str]:
    """
    Detect zombie jobs (status=running but PID no longer alive).
    Marks them as failed and returns the list of affected job IDs.
    """
    reaped = []
    for job in list_jobs(workspace_root):
        if job.get("status") != "running" or not job.get("pid"):
            continue

        alive = False
        try:
            os.kill(job["pid"], 0)  # signal 0 = existence check
            alive = True
        except (ProcessLookupError, PermissionError):
            pass

        if not alive:
            job.update(
                status="failed",
                pid=None,
                errorMessage=f"Process {job['pid']} no longer running (zombie detected)",
            )
            _write(_job_path(workspace_root, job["id"]), job)
            reaped.append(job["id"])

    return reaped


def cancel_job(job_id: str, workspace_root: str) -> bool:
    """
    Cancel a running job by sending SIGTERM to its PID.
    Updates the job file to status=failed.
    Returns True if the signal was sent, False if job not found / not running.
    """
    job = read_job(job_id, workspace_root)
    if not job or job.get("status") != "running" or not job.get("pid"):
        return False

    try:
        os.kill(job["pid"], signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass  # process may have already exited

    job.update(status="failed", pid=None, errorMessage="Cancelled by user")
    _write(_job_path(workspace_root, job_id), job)
    return True
