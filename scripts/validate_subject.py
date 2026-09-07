import argparse
import json
from pathlib import Path


def validate_notebook(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(notebook, dict):
        raise ValueError("notebook root must be an object")
    missing = {"cells", "metadata", "nbformat"} - notebook.keys()
    if missing:
        raise ValueError(f"missing required keys: {sorted(missing)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", choices=("dip", "latex", "compiler-design"))
    args = parser.parse_args()
    subject_path = Path(args.subject)
    files = [path for path in subject_path.rglob("*") if path.is_file()]

    for path in sorted(subject_path.rglob("*.ipynb")):
        validate_notebook(path)
        print(f"Validated notebook: {path}")

    if args.subject == "latex":
        for path in sorted(subject_path.rglob("*.tex")):
            content = path.read_text(encoding="utf-8")
            if "\\documentclass" not in content:
                raise ValueError(f"{path}: missing \\documentclass")
            print(f"Validated LaTeX source: {path}")

    print(f"Validated {args.subject}: {len(files)} files")


if __name__ == "__main__":
    main()