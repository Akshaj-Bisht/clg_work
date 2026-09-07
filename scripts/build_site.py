import json
import re
import shutil
import subprocess
import tempfile
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
NOTEBOOK_OUTPUT = SITE / "notebooks"
DOWNLOAD_OUTPUT = SITE / "downloads"
STYLE_SOURCE = ROOT / "scripts" / "site.css"
NOTEBOOK_STYLE_SOURCE = ROOT / "scripts" / "notebook.css"
SUBJECTS = {
    "dip": ("Digital Image Processing", "Image analysis, enhancement, and computer vision practicals."),
    "latex": ("LaTeX", "Reports, notes, and typeset coursework."),
    "compiler-design": ("Compiler Design", "Parsing, language theory, and compiler implementations."),
}


def notebook_title(path, notebook):
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        source = "".join(cell.get("source", []))
        match = re.search(r"^#\s+(.+)$", source, re.MULTILINE)
        if match:
            return re.sub(r"[*_`]", "", match.group(1)).strip()
    return path.stem.replace("_", " ").title()


def remove_colab_cells(notebook):
    notebook["cells"] = [
        cell
        for cell in notebook.get("cells", [])
        if "colab.research.google.com" not in "".join(cell.get("source", []))
    ]
    notebook.get("metadata", {}).pop("colab", None)
    return notebook


def run_nbconvert(notebook, output_dir, output_name, export_format):
    command = [
        "jupyter", "nbconvert", "--to", export_format,
        "--output", output_name, "--output-dir", str(output_dir), str(notebook),
    ]
    if export_format == "webpdf":
        command.append("--allow-chromium-download")
    subprocess.run(command, check=True, cwd=ROOT)


def add_notebook_style(path):
    html = path.read_text(encoding="utf-8")
    link = '<link rel="stylesheet" href="../notebook.css">'
    path.write_text(html.replace("</head>", f"{link}</head>", 1), encoding="utf-8")


def build_notebook(source_path, index):
    notebook = json.loads(source_path.read_text(encoding="utf-8"))
    title = notebook_title(source_path, notebook)
    relative_path = source_path.relative_to(ROOT)
    relative_slug = "-".join(relative_path.with_suffix("").parts)
    safe_name = f"{index:02d}-{re.sub(r'[^a-z0-9]+', '-', relative_slug.lower()).strip('-')}"

    with tempfile.TemporaryDirectory() as temporary_dir:
        sanitized_path = Path(temporary_dir) / source_path.name
        sanitized_path.write_text(
            json.dumps(remove_colab_cells(notebook), ensure_ascii=False), encoding="utf-8"
        )
        run_nbconvert(sanitized_path, NOTEBOOK_OUTPUT, safe_name, "html")
        run_nbconvert(sanitized_path, NOTEBOOK_OUTPUT, safe_name, "webpdf")
    add_notebook_style(NOTEBOOK_OUTPUT / f"{safe_name}.html")

    download_path = DOWNLOAD_OUTPUT / relative_path
    download_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, download_path)
    return {
        "title": title,
        "source": str(relative_path),
        "subject_key": relative_path.parts[0] if relative_path.parts else "other",
        "html": f"notebooks/{safe_name}.html",
        "pdf": f"notebooks/{safe_name}.pdf",
        "download": f"downloads/{relative_path.as_posix()}",
    }


def write_index(notebooks):
    subject_cards = []
    for key, (name, description) in SUBJECTS.items():
        count = sum(notebook["subject_key"] == key for notebook in notebooks)
        subject_cards.append(f"""<article class="subject-card">
  <p class="subject-number">{count:02d}</p>
  <div><h3>{escape(name)}</h3><p>{escape(description)}</p></div>
</article>""")

    cards = []
    for index, notebook in enumerate(notebooks, 1):
        subject_name = SUBJECTS.get(notebook["subject_key"], ("Coursework", ""))[0]
        cards.append(f"""<article class="notebook-card">
  <div class="card-index">{index:02d}</div>
  <div class="card-content">
    <p class="eyebrow">{escape(subject_name)}</p>
    <h2>{escape(notebook['title'])}</h2>
    <p class="filename">{escape(notebook['source'])}</p>
    <div class="actions">
      <a class="button button-primary" href="{notebook['html']}">View preview</a>
      <a class="button" href="{notebook['pdf']}">Download PDF</a>
      <a class="text-link" href="{notebook['download']}">Notebook file</a>
    </div>
  </div>
</article>""")

    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>clg_work | College Coursework</title>
  <link rel="stylesheet" href="site.css">
</head>
<body>
  <main class="shell">
    <header class="hero">
            <p class="eyebrow">clg_work / college coursework</p>
            <h1>Study, rendered.</h1>
            <p class="intro">A living archive of practical notebooks, reports, and implementations across the subjects that make up the course.</p>
      <div class="hero-rule"></div>
    </header>
        <section class="subjects" aria-labelledby="subjects-title">
            <div class="section-heading">
                <div><p class="eyebrow">The curriculum</p><h2 id="subjects-title">Study areas</h2></div>
                <p class="updated">Three folders, one evolving archive</p>
            </div>
            <div class="subject-grid">{''.join(subject_cards)}</div>
        </section>
    <section class="library" aria-labelledby="library-title">
      <div class="section-heading">
                <div><p class="eyebrow">{len(notebooks):02d} published</p><h2 id="library-title">Notebook previews</h2></div>
        <p class="updated">Built automatically from <code>.ipynb</code> files</p>
      </div>
      {''.join(cards)}
    </section>
    <footer><span>College Coursework</span><a href="https://github.com/Akshaj-Bisht/clg_work">View source on GitHub</a></footer>
  </main>
</body>
</html>
"""
    (SITE / "index.html").write_text(index, encoding="utf-8")


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    NOTEBOOK_OUTPUT.mkdir(parents=True)
    DOWNLOAD_OUTPUT.mkdir(parents=True)
    shutil.copy2(STYLE_SOURCE, SITE / "site.css")
    shutil.copy2(NOTEBOOK_STYLE_SOURCE, SITE / "notebook.css")
    notebooks = sorted(
        path for path in ROOT.rglob("*.ipynb")
        if ".git" not in path.parts and "site" not in path.parts
    )
    write_index([build_notebook(path, index) for index, path in enumerate(notebooks, 1)])


if __name__ == "__main__":
    main()