"""Process one resource file with retryable, persisted state transitions."""

import hashlib
from pathlib import Path

from processing.job_store import JobStore
from processing.models import ProcessingJob, ProcessingStatus
from processing.processors import ProcessingError, processor_for


def _checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def process_job(job, store, processor_factory=processor_for):
    input_path = Path(job.input_path)
    try:
        job.checksum = _checksum(input_path)
        current = store.get(job.resource_file_id)
        if current and current.checksum == job.checksum and current.status == ProcessingStatus.READY:
            return current

        job.status = ProcessingStatus.PROCESSING
        job.error_message = None
        job.attempts += 1
        store.save(job)
        artifacts = processor_factory(input_path).process(input_path, Path(job.output_dir))
        job.artifacts = artifacts.files
        job.status = ProcessingStatus.READY
        store.save(job)
        return job
    except (OSError, ProcessingError, ValueError) as error:
        job.status = ProcessingStatus.FAILED
        job.error_message = str(error)[-2000:]
        store.save(job)
        return job


def run_once(resource_file_id, input_path, output_dir, jobs_path):
    store = JobStore(jobs_path)
    job = store.get(resource_file_id) or ProcessingJob(
        resource_file_id=resource_file_id,
        input_path=str(input_path),
        output_dir=str(output_dir),
    )
    return process_job(job, store)