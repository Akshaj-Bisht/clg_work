"""Data contracts shared by processors and workers."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


@dataclass
class PreviewArtifacts:
    """Paths are relative to the job's output directory."""

    files: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProcessingJob:
    resource_file_id: str
    input_path: str
    output_dir: str
    checksum: Optional[str] = None
    status: ProcessingStatus = ProcessingStatus.PENDING
    error_message: Optional[str] = None
    artifacts: Dict[str, str] = field(default_factory=dict)
    attempts: int = 0

    def as_dict(self):
        return {
            "resource_file_id": self.resource_file_id,
            "input_path": self.input_path,
            "output_dir": self.output_dir,
            "checksum": self.checksum,
            "status": self.status.value,
            "error_message": self.error_message,
            "artifacts": self.artifacts,
            "attempts": self.attempts,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            resource_file_id=data["resource_file_id"],
            input_path=data["input_path"],
            output_dir=data["output_dir"],
            checksum=data.get("checksum"),
            status=ProcessingStatus(data.get("status", ProcessingStatus.PENDING)),
            error_message=data.get("error_message"),
            artifacts=dict(data.get("artifacts", {})),
            attempts=int(data.get("attempts", 0)),
        )