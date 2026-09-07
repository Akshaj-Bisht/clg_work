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
PDF_OUTPUT = SITE / "pdfs"
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


def latex_title(path):
    source = path.read_text(encoding="utf-8")
    match = re.search(r"\\title\{([^}]+)\}", source)
    return match.group(1).strip() if match else path.stem.replace("_", " ").title()


def copy_pdf(pdf_path, index, source_path, title, source_download=None):
    relative_pdf = pdf_path.relative_to(ROOT)
    safe_name = f"{index:02d}-latex-{re.sub(r'[^a-z0-9]+', '-', pdf_path.stem.lower()).strip('-')}"
    output_path = PDF_OUTPUT / f"{safe_name}.pdf"
    if pdf_path.resolve() != output_path.resolve():
        shutil.copy2(pdf_path, output_path)
    return {
        "title": title,
        "source": str(source_path.relative_to(ROOT) if source_path else relative_pdf),
        "subject_key": "latex",
        "kind": "latex",
        "pdf": f"pdfs/{output_path.name}",
        "download": f"pdfs/{output_path.name}",
        "source_download": source_download,
    }


def build_latex_document(source_path, index):
    source_path = source_path.resolve()
    source_download_path = DOWNLOAD_OUTPUT / source_path.relative_to(ROOT)
    source_download_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, source_download_path)
    expected_pdf = source_path.parent / "pdfs" / f"{source_path.stem}.pdf"
    if expected_pdf.exists():
        pdf_path = expected_pdf
    else:
        with tempfile.TemporaryDirectory() as temporary_dir:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 "-output-directory", temporary_dir, source_path.name],
                check=True,
                cwd=source_path.parent,
            )
            pdf_path = Path(temporary_dir) / f"{source_path.stem}.pdf"
            generated_pdf = PDF_OUTPUT / f"{index:02d}-latex-{source_path.stem}.pdf"
            shutil.copy2(pdf_path, generated_pdf)
            return copy_pdf(generated_pdf, index, source_path, latex_title(source_path),
                            f"downloads/{source_path.relative_to(ROOT).as_posix()}")

    return copy_pdf(
        pdf_path,
        index,
        source_path,
        latex_title(source_path),
        f"downloads/{source_path.relative_to(ROOT).as_posix()}",
    )


def build_existing_latex_pdf(pdf_path, index):
    pdf_path = pdf_path.resolve()
    return copy_pdf(pdf_path, index, None, pdf_path.stem.replace("_", " ").title())


def resource_timestamp(resource):
    try:
        output = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct", "--", resource["source"]],
            cwd=ROOT,
            text=True,
        ).strip()
        return int(output or 0)
    except (OSError, subprocess.CalledProcessError, ValueError):
        return 0


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
        "kind": "notebook",
        "html": f"notebooks/{safe_name}.html",
        "pdf": f"notebooks/{safe_name}.pdf",
        "download": f"downloads/{relative_path.as_posix()}",
    }


def write_index(notebooks):
    subject_cards = []
    for key, (name, description) in SUBJECTS.items():
        count = sum(notebook["subject_key"] == key for notebook in notebooks)
        subject_cards.append(f"""<button class="subject-card subject-filter" type="button" data-filter="{key}" aria-pressed="false">
  <p class="subject-number">{count:02d}</p>
  <div><h3>{escape(name)}</h3><p>{escape(description)}</p></div>
</button>""")

    cards = []
    for index, notebook in enumerate(notebooks, 1):
        subject_name = SUBJECTS.get(notebook["subject_key"], ("Coursework", ""))[0]
        if notebook["kind"] == "latex":
            actions = f"""<a class="button button-primary" href="{notebook['pdf']}">View PDF</a>
      <a class="button" href="{notebook['download']}" download="{escape(notebook['title'])}.pdf">Download PDF</a>"""
            if notebook.get("source_download"):
                actions += f'\n      <a class="text-link" href="{notebook["source_download"]}" download>Source .tex</a>'
        else:
            actions = f"""<a class="button button-primary" href="{notebook['html']}">View preview</a>
      <a class="button" href="{notebook['pdf']}">Download PDF</a>
      <a class="text-link" href="{notebook['download']}" download="{escape(notebook['source'].split('/')[-1])}">Download notebook</a>"""
        cards.append(f"""<article class="notebook-card resource-card" data-subject="{notebook['subject_key']}">
  <div class="card-index">{index:02d}</div>
  <div class="card-content">
    <p class="eyebrow">{escape(subject_name)}</p>
    <h2>{escape(notebook['title'])}</h2>
    <p class="filename">{escape(notebook['source'])}</p>
    <div class="actions">
            {actions}
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
            <p class="eyebrow">clg_work</p>
            <h1>College coursework</h1>
            <p class="intro">A clear, searchable home for notebooks, reports, and implementations across the course.</p>
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
                                <div><p class="eyebrow">{len(notebooks):02d} published</p><h2 id="library-title">Recent uploads</h2></div>
                <button class="filter-reset is-active" type="button" data-filter="recent">Recent uploads</button>
      </div>
    {''.join(cards)}
        <p class="empty-state is-hidden">No resources in this study area yet.</p>
    </section>
    <footer><span>College Coursework</span><a href="https://github.com/Akshaj-Bisht/clg_work">View source on GitHub</a></footer>
  </main>
    <script>
    const resources = [...document.querySelectorAll('.resource-card')];
    const filters = [...document.querySelectorAll('.subject-filter, .filter-reset')];
    const libraryTitle = document.querySelector('#library-title');
    const emptyState = document.querySelector('.empty-state');
    const subjectNames = {{dip: 'Digital Image Processing', latex: 'LaTeX', 'compiler-design': 'Compiler Design'}};

    function applyFilter(filter) {{
        let visible = 0;
        resources.forEach((resource, index) => {{
            const show = filter === 'recent' ? index < 3 : resource.dataset.subject === filter;
            resource.classList.toggle('is-hidden', !show);
            if (show) visible += 1;
        }});
        filters.forEach((button) => {{
            const active = button.dataset.filter === filter;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
        }});
        libraryTitle.textContent = filter === 'recent' ? 'Recent uploads' : subjectNames[filter] + ' resources';
        emptyState.classList.toggle('is-hidden', visible !== 0);
    }}

    filters.forEach((button) => button.addEventListener('click', () => applyFilter(button.dataset.filter)));
    applyFilter('recent');
</script>
</body>
</html>
"""
    (SITE / "index.html").write_text(index, encoding="utf-8")


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    NOTEBOOK_OUTPUT.mkdir(parents=True)
    DOWNLOAD_OUTPUT.mkdir(parents=True)
    PDF_OUTPUT.mkdir(parents=True)
    shutil.copy2(STYLE_SOURCE, SITE / "site.css")
    shutil.copy2(NOTEBOOK_STYLE_SOURCE, SITE / "notebook.css")
    notebooks = sorted(
        path for path in ROOT.rglob("*.ipynb")
        if ".git" not in path.parts and "site" not in path.parts
    )
    resources = [build_notebook(path, index) for index, path in enumerate(notebooks, 1)]
    latex_sources = sorted(
        path for path in (ROOT / "latex").rglob("*.tex")
        if "pdfs" not in path.parts
    )
    next_index = len(resources) + 1
    represented_pdfs = set()
    for path in latex_sources:
        expected_pdf = path.parent / "pdfs" / f"{path.stem}.pdf"
        if expected_pdf.exists():
            represented_pdfs.add(expected_pdf.resolve())
        resources.append(build_latex_document(path, next_index))
        next_index += 1
    for path in sorted((ROOT / "latex" / "pdfs").rglob("*.pdf")):
        if path.resolve() not in represented_pdfs:
            resources.append(build_existing_latex_pdf(path, next_index))
            next_index += 1
    resources.sort(key=resource_timestamp, reverse=True)
    write_index(resources)


if __name__ == "__main__":
    main()