"""Small atomic JSON store for local workers and development deployments."""

import json
import os
import tempfile
from pathlib import Path

from .models import ProcessingJob


class JobStore:
    def __init__(self, path):
        self.path = Path(path)

    def get(self, resource_file_id):
        data = self._read()
        record = data.get(resource_file_id)
        return ProcessingJob.from_dict(record) if record else None

    def save(self, job):
        data = self._read()
        data[job.resource_file_id] = job.as_dict()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            prefix=f".{self.path.name}.", dir=self.path.parent
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2, sort_keys=True)
                handle.write("\n")
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def _read(self):
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Cannot read processing jobs: {self.path}") from error