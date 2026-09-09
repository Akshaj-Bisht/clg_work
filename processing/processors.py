"""File processors used by both workers and local migration scripts."""

import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .models import PreviewArtifacts


class ProcessingError(RuntimeError):
    """Raised when a supported file cannot be converted."""


class UnsupportedFileError(ProcessingError):
    """Raised when no preview processor exists for a file type."""


def _safe_stem(path):
    return re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-") or "resource"


def _run(command, *, cwd=None):
    try:
        return subprocess.run(
            command, cwd=cwd, check=True, capture_output=True, text=True
        )
    except FileNotFoundError as error:
        raise ProcessingError(f"Required converter is unavailable: {command[0]}") from error
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "conversion failed").strip()
        raise ProcessingError(detail[-2000:]) from error


def _remove_colab_cells(notebook):
    notebook["cells"] = [
        cell
        for cell in notebook.get("cells", [])
        if "colab.research.google.com" not in "".join(cell.get("source", []))
    ]
    notebook.setdefault("metadata", {}).pop("colab", None)
    return notebook


@dataclass
class NotebookProcessor:
    runner: Callable = _run

    def process(self, input_path: Path, output_dir: Path) -> PreviewArtifacts:
        try:
            notebook = json.loads(input_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ProcessingError(f"Invalid notebook: {input_path.name}") from error

        output_dir.mkdir(parents=True, exist_ok=True)
        stem = _safe_stem(input_path)
        with tempfile.TemporaryDirectory() as temporary_dir:
            sanitized = Path(temporary_dir) / input_path.name
            sanitized.write_text(
                json.dumps(_remove_colab_cells(notebook), ensure_ascii=False),
                encoding="utf-8",
            )
            self._convert(sanitized, output_dir, stem, "html")
            self._convert(sanitized, output_dir, stem, "webpdf")
        return PreviewArtifacts({
            "preview_html": f"{stem}.html",
            "preview_pdf": f"{stem}.pdf",
        })

    def _convert(self, source, output_dir, stem, export_format):
        command = [
            "jupyter", "nbconvert", "--to", export_format,
            "--output", stem, "--output-dir", str(output_dir), str(source),
        ]
        if export_format == "webpdf":
            command.append("--allow-chromium-download")
        self.runner(command, cwd=Path.cwd())


@dataclass
class LatexProcessor:
    runner: Callable = _run

    def process(self, input_path: Path, output_dir: Path) -> PreviewArtifacts:
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / f"{_safe_stem(input_path)}.pdf"
        with tempfile.TemporaryDirectory() as temporary_dir:
            self.runner(
                [
                    "pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                    "-output-directory", temporary_dir, input_path.name,
                ],
                cwd=input_path.parent,
            )
            generated = Path(temporary_dir) / f"{input_path.stem}.pdf"
            if not generated.exists():
                raise ProcessingError("LaTeX completed without producing a PDF")
            shutil.copy2(generated, target)
        return PreviewArtifacts({"preview_pdf": target.name})


class PdfProcessor:
    def process(self, input_path: Path, output_dir: Path) -> PreviewArtifacts:
        output_dir.mkdir(parents=True, exist_ok=True)
        target = output_dir / f"{_safe_stem(input_path)}.pdf"
        shutil.copy2(input_path, target)
        return PreviewArtifacts({"preview_pdf": target.name})


def processor_for(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".ipynb":
        return NotebookProcessor()
    if suffix in {".tex", ".latex"}:
        return LatexProcessor()
    if suffix == ".pdf":
        return PdfProcessor()
    raise UnsupportedFileError(f"No preview processor for {suffix or 'extensionless file'}")