import json
import tempfile
import unittest
from pathlib import Path

from processing.job_store import JobStore
from processing.models import ProcessingJob, ProcessingStatus, PreviewArtifacts
from processing.processors import (
    LatexProcessor,
    NotebookProcessor,
    PdfProcessor,
    UnsupportedFileError,
    processor_for,
)
from workers.processing_worker import process_job


class FakeNotebookProcessor:
    def process(self, input_path, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "resource.html").write_text("<p>preview</p>", encoding="utf-8")
        (output_dir / "resource.pdf").write_bytes(b"pdf")
        return PreviewArtifacts({"preview_html": "resource.html", "preview_pdf": "resource.pdf"})


class ProcessingTests(unittest.TestCase):
    def test_notebook_processor_removes_colab_cells_and_runs_both_exports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            notebook = root / "lesson.ipynb"
            notebook.write_text(json.dumps({
                "cells": [
                    {"cell_type": "markdown", "source": ["# Lesson"]},
                    {"cell_type": "code", "source": ["https://colab.research.google.com/"]},
                ],
                "metadata": {"colab": {"name": "lesson"}},
            }), encoding="utf-8")
            commands = []
            sanitized_notebook = {}

            def runner(command, cwd=None):
                commands.append(command)
                source_argument = command[command.index("--output-dir") + 2]
                sanitized_notebook.update(
                    json.loads(Path(source_argument).read_text(encoding="utf-8"))
                )
                output_dir = Path(command[command.index("--output-dir") + 1])
                stem = command[command.index("--output") + 1]
                extension = ".html" if command[3] == "html" else ".pdf"
                (output_dir / f"{stem}{extension}").write_bytes(b"preview")

            artifacts = NotebookProcessor(runner=runner).process(notebook, root / "out")
            self.assertEqual(len(sanitized_notebook["cells"]), 1)
            self.assertNotIn("colab", sanitized_notebook["metadata"])
            self.assertEqual(set(artifacts.files), {"preview_html", "preview_pdf"})
            self.assertEqual(len(commands), 2)

    def test_pdf_processor_copies_browser_preview(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "guide.pdf"
            source.write_bytes(b"pdf")
            artifacts = PdfProcessor().process(source, root / "out")
            self.assertEqual((root / "out" / "guide.pdf").read_bytes(), b"pdf")
            self.assertEqual(artifacts.files, {"preview_pdf": "guide.pdf"})

    def test_latex_processor_copies_compiled_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "report.tex"
            source.write_text("\\documentclass{article}", encoding="utf-8")

            def runner(command, cwd=None):
                output_dir = Path(command[command.index("-output-directory") + 1])
                (output_dir / "report.pdf").write_bytes(b"compiled")

            artifacts = LatexProcessor(runner=runner).process(source, root / "out")
            self.assertEqual((root / "out" / "report.pdf").read_bytes(), b"compiled")
            self.assertEqual(artifacts.files, {"preview_pdf": "report.pdf"})

    def test_worker_persists_failure_and_allows_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "lesson.txt"
            source.write_text("source", encoding="utf-8")
            store = JobStore(root / "jobs.json")
            job = ProcessingJob("file-1", str(source), str(root / "out"))
            failed = process_job(job, store)
            self.assertEqual(failed.status, ProcessingStatus.FAILED)
            self.assertTrue(failed.error_message)

            retried = process_job(failed, store, lambda path: FakeNotebookProcessor())
            self.assertEqual(retried.status, ProcessingStatus.READY)
            self.assertEqual(retried.attempts, 2)

    def test_unknown_extension_is_explicit(self):
        with self.assertRaises(UnsupportedFileError):
            processor_for(Path("notes.docx"))


if __name__ == "__main__":
    unittest.main()