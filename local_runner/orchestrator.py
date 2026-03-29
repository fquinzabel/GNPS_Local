"""
Orchestrator - replaces ProteoSAFe job engine for single-user local use.
Manages job lifecycle: queued -> running -> done/failed
All subprocess calls run in WSL2/Linux context (repo is on /mnt/d/).
"""

import uuid
import json
import subprocess
import threading
import traceback
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Optional

# Absolute path to the repo on the Windows filesystem, accessed via WSL2 mount
REPO_ROOT = Path("/mnt/d/Samarth/Code/CHEM_3189/GNPS_Workflows")

# Where all job I/O lives (inside WSL2 home for speed)
JOBS_ROOT = Path.home() / "gnps_jobs"
JOBS_ROOT.mkdir(exist_ok=True)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


class Job:
    def __init__(self, workflow: str, params: dict):
        self.id = str(uuid.uuid4())[:8]
        self.workflow = workflow
        self.params = params
        self.status = JobStatus.QUEUED
        self.created_at = datetime.now().isoformat()
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None
        self.error: Optional[str] = None

        # Directories
        self.job_dir = JOBS_ROOT / self.id
        self.input_dir = self.job_dir / "input"
        self.output_dir = self.job_dir / "output"
        self.log_file = self.job_dir / "run.log"

        self.job_dir.mkdir(parents=True, exist_ok=True)
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        self._save_state()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "workflow": self.workflow,
            "params": self.params,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
        }

    def _save_state(self):
        with open(self.job_dir / "state.json", "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    def log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        with open(self.log_file, "a") as f:
            f.write(line)

    def run_step(self, step_name: str, cmd: list[str], cwd: Optional[Path] = None, timeout: int = 3600) -> bool:
        """Run a single pipeline step. Returns True on success."""
        self.log(f"--- STEP: {step_name} ---")
        self.log(f"CMD: {' '.join(str(c) for c in cmd)}")
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd or REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=timeout,  # Customizable timeout per step
            )
            if result.stdout:
                self.log(result.stdout)
            if result.stderr:
                self.log(f"STDERR: {result.stderr}")
            if result.returncode != 0:
                self.log(f"STEP FAILED (exit {result.returncode})")
                return False
            self.log(f"STEP OK")
            return True
        except subprocess.TimeoutExpired:
            self.log(f"STEP TIMED OUT after {timeout} seconds")
            return False
        except Exception as e:
            self.log(f"STEP ERROR: {e}")
            return False

    def mark_running(self):
        self.status = JobStatus.RUNNING
        self.started_at = datetime.now().isoformat()
        self._save_state()

    def mark_done(self):
        self.status = JobStatus.DONE
        self.finished_at = datetime.now().isoformat()
        self._save_state()

    def mark_failed(self, error: str):
        self.status = JobStatus.FAILED
        self.finished_at = datetime.now().isoformat()
        self.error = error
        self._save_state()


# In-memory job registry (single-user, no DB needed)
_jobs: dict[str, Job] = {}
_lock = threading.Lock()


def create_job(workflow: str, params: dict) -> Job:
    """Create and register a job WITHOUT starting it.
    Call start_job() only after all input files have been saved to disk."""
    job = Job(workflow, params)
    with _lock:
        _jobs[job.id] = job
    return job


def start_job(job: Job):
    """Start a previously created job in a background thread."""
    thread = threading.Thread(target=_run_job, args=(job,), daemon=True)
    thread.start()


def submit_job(workflow: str, params: dict) -> Job:
    """Create, register, and immediately start a job.
    Only safe when there are no files to upload first (legacy callers)."""
    job = create_job(workflow, params)
    start_job(job)
    return job


def get_job(job_id: str) -> Optional[Job]:
    # Try memory first, then disk
    with _lock:
        if job_id in _jobs:
            return _jobs[job_id]
    # Reconstruct from disk if server restarted
    state_file = JOBS_ROOT / job_id / "state.json"
    if state_file.exists():
        with open(state_file) as f:
            data = json.load(f)
        job = Job.__new__(Job)
        job.__dict__.update(data)
        job.job_dir = JOBS_ROOT / job_id
        job.input_dir = job.job_dir / "input"
        job.output_dir = job.job_dir / "output"
        job.log_file = job.job_dir / "run.log"
        with _lock:
            _jobs[job_id] = job
        return job
    return None


def list_jobs() -> list[dict]:
    """List all jobs from disk (survives restarts)."""
    jobs = []
    for state_file in sorted(JOBS_ROOT.glob("*/state.json"), reverse=True):
        try:
            with open(state_file) as f:
                jobs.append(json.load(f))
        except Exception:
            pass
    return jobs


def get_log(job_id: str) -> str:
    log_file = JOBS_ROOT / job_id / "run.log"
    if log_file.exists():
        return log_file.read_text()
    return ""


def get_output_files(job_id: str) -> list[dict]:
    output_dir = JOBS_ROOT / job_id / "output"
    if not output_dir.exists():
        return []
    files = []
    for f in sorted(output_dir.rglob("*")):
        if f.is_file():
            files.append({
                "name": f.name,
                "path": str(f.relative_to(output_dir)),
                "size": f.stat().st_size,
            })
    return files


def _run_job(job: Job):
    """Dispatch job to the correct workflow runner."""
    from workflows import molecular_networking, fbmn, mshub_gc

    job.mark_running()
    job.log(f"Starting workflow: {job.workflow}")

    try:
        runners = {
            "molecular_networking": molecular_networking.run,
            "fbmn": fbmn.run,
            "mshub_gc": mshub_gc.run,
        }
        runner = runners.get(job.workflow)
        if not runner:
            raise ValueError(f"Unknown workflow: {job.workflow}")

        success = runner(job)
        if success:
            job.mark_done()
            job.log("Workflow completed successfully.")
        else:
            job.mark_failed("One or more steps failed. Check log for details.")
    except Exception as e:
        job.mark_failed(str(e))
        job.log(f"FATAL: {traceback.format_exc()}")