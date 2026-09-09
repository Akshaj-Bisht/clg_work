"""Validate the coursework import manifest without copying source files."""

import argparse
import json
from pathlib import Path


RESOURCE_KINDS = {"practical", "note", "book", "guideline", "notebook", "pdf", "document"}
MAX_FILE_SIZE = 100 * 1024 * 1024
SUBJECTS = {"dip", "latex", "compiler-design"}


def expected_kind(path: Path) -> str:
    return {".ipynb": "notebook", ".tex": "practical", ".pdf": "pdf", ".md": "document"}.get(
        path.suffix.lower(), "document"
    )


def validate_manifest(root: Path, manifest_path: Path) -> list[Path]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list) or not manifest:
        raise ValueError("import manifest must be a non-empty list")

    seen: set[str] = set()
    imported = []
    for entry in manifest:
        relative_path = entry.get("path")
        subject = entry.get("subject")
        kind = entry.get("kind")
        if subject not in SUBJECTS or not isinstance(relative_path, str):
            raise ValueError(f"invalid subject or path: {entry}")
        if kind not in RESOURCE_KINDS:
            raise ValueError(f"unsupported resource kind for {relative_path}: {kind}")
        if relative_path in seen:
            raise ValueError(f"duplicate manifest path: {relative_path}")
        seen.add(relative_path)

        path = (root / relative_path).resolve()
        if root.resolve() not in path.parents:
            raise ValueError(f"manifest path escapes repository: {relative_path}")
        if not path.is_file():
            raise ValueError(f"missing coursework file: {relative_path}")
        if path.stat().st_size <= 0 or path.stat().st_size > MAX_FILE_SIZE:
            raise ValueError(f"invalid file size: {relative_path}")
        pdf_kind = path.suffix.lower() == ".pdf" and kind in {"book", "guideline", "pdf"}
        extensionless_guideline = path.name == "dip_guidelinespdf" and kind == "guideline"
        if kind != expected_kind(path) and not pdf_kind and not extensionless_guideline:
            raise ValueError(f"kind mismatch for {relative_path}: got {kind}")
        imported.append(path)

    expected_files = {
        path.relative_to(root).as_posix()
        for subject in SUBJECTS
        for path in (root / subject).rglob("*")
        if path.is_file()
    }
    missing_entries = expected_files - seen
    if missing_entries:
        raise ValueError(f"coursework files missing from manifest: {sorted(missing_entries)}")
    return imported


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).parents[1])
    parser.add_argument("--manifest", type=Path, default=Path(__file__).parents[1] / "tests/fixtures/coursework_import.json")
    args = parser.parse_args()
    print(f"Validated coursework import manifest: {len(validate_manifest(args.root, args.manifest))} files")


if __name__ == "__main__":
    main()