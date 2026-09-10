import json
import mimetypes
import re
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PREVIEW_OUTPUT = SITE / "previews"
DOWNLOAD_OUTPUT = SITE / "downloads"
STYLE_SOURCE = ROOT / "scripts" / "site.css"
NOTEBOOK_STYLE_SOURCE = ROOT / "scripts" / "notebook.css"
IGNORED_PARTS = {".git", "site", ".next", "node_modules", ".venv"}
IGNORED_ROOTS = {"scripts", ".github", "integrations", "app", "components", "server", "supabase", "processing", "workers", "tests"}
CATEGORY_NAMES = {
    "practicals": "Practicals",
    "notes": "Notes",
    "books": "Books",
    "guidelines": "Guidelines",
    "notebooks": "Notebooks",
    "pdfs": "PDFs",
    "assets": "Assets",
}
CATEGORY_TYPES = {
    "practicals": "practical",
    "notes": "note",
    "books": "book",
    "guidelines": "guideline",
    "notebooks": "notebook",
    "pdfs": "pdf",
    "assets": "asset",
}
SUPPORTED_TEXT = {".md", ".markdown", ".txt", ".py", ".c", ".cpp", ".h", ".java", ".js", ".ts", ".html", ".css", ".tex"}
SKIP_NAMES = {"README.md"}


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "resource"


def title_from_path(path):
    return path.stem.replace("_", " ").replace("-", " ").title()


def subject_key(path):
    return path.relative_to(ROOT).parts[0]


def subject_name(key):
    return key.replace("-", " ").title()


def parse_frontmatter(source):
    if not source.startswith("---\n"):
        return {}, source
    end = source.find("\n---", 4)
    if end == -1:
        raise ValueError("frontmatter starts with --- but has no closing ---")
    metadata = {}
    for line in source[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        if value.startswith("[") and value.endswith("]"):
            value = [item.strip().strip('"').strip("'") for item in value[1:-1].split(",") if item.strip()]
        metadata[key.strip()] = value
    return metadata, source[end + 4:].lstrip("\n")


def markdown_to_html(source):
    escaped = escape(source)
    escaped = re.sub(r"^### (.+)$", r"<h3>\1</h3>", escaped, flags=re.MULTILINE)
    escaped = re.sub(r"^## (.+)$", r"<h2>\1</h2>", escaped, flags=re.MULTILINE)
    escaped = re.sub(r"^# (.+)$", r"<h1>\1</h1>", escaped, flags=re.MULTILINE)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    blocks = []
    for block in re.split(r"\n{2,}", escaped):
        if block.startswith("<h"):
            blocks.append(block)
        else:
            blocks.append(f"<p>{block.replace(chr(10), '<br>')}</p>")
    return "\n".join(blocks)


def copy_download(source_path):
    relative = source_path.relative_to(ROOT)
    destination = DOWNLOAD_OUTPUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination)
    return f"downloads/{relative.as_posix()}"


def write_preview_page(resource, body, filename):
    path = PREVIEW_OUTPUT / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(resource['title'])} | clg_work</title><link rel="stylesheet" href="../site.css"></head>
<body><main class="preview-shell"><a class="back-link" href="../index.html">Back to library</a>
<header class="preview-header"><p class="eyebrow">{escape(resource['subject_name'])} / {escape(resource['kind'])}</p><h1>{escape(resource['title'])}</h1><p class="filename">{escape(resource['source'])}</p></header>
<article class="preview-content">{body}</article></main></body></html>""", encoding="utf-8")
    return f"previews/{filename}"


def notebook_title(path, notebook):
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "markdown":
            match = re.search(r"^#\s+(.+)$", "".join(cell.get("source", [])), re.MULTILINE)
            if match:
                return re.sub(r"[*_`]", "", match.group(1)).strip()
    return title_from_path(path)


def remove_colab_cells(notebook):
    notebook["cells"] = [cell for cell in notebook.get("cells", []) if "colab.research.google.com" not in "".join(cell.get("source", []))]
    notebook.get("metadata", {}).pop("colab", None)
    return notebook


def run_nbconvert(notebook, output_name, export_format):
    command = [sys.executable, "-m", "jupyter", "nbconvert", "--to", export_format, "--output", output_name, "--output-dir", str(PREVIEW_OUTPUT), str(notebook)]
    if export_format == "webpdf":
        command.append("--allow-chromium-download")
    subprocess.run(command, check=True, cwd=ROOT)


def build_latex(source_path, resource, safe_name):
    subject_root = ROOT / subject_key(source_path)
    expected_pdf = subject_root / "pdfs" / f"{source_path.stem}.pdf"
    if expected_pdf.exists():
        resource["pdf"] = copy_download(expected_pdf)
        return
    try:
        with tempfile.TemporaryDirectory() as temporary_dir:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
                 "-output-directory", temporary_dir, source_path.name],
                check=True,
                cwd=source_path.parent,
            )
            generated_pdf = Path(temporary_dir) / f"{source_path.stem}.pdf"
            destination = PREVIEW_OUTPUT / f"{safe_name}.pdf"
            shutil.copy2(generated_pdf, destination)
            resource["pdf"] = f"previews/{destination.name}"
    except (FileNotFoundError, subprocess.CalledProcessError):
        resource["processing_error"] = "PDF preview will be generated in GitHub Actions."


def build_notebook(source_path, index):
    notebook = remove_colab_cells(json.loads(source_path.read_text(encoding="utf-8")))
    relative = source_path.relative_to(ROOT)
    safe_name = f"{index:02d}-{slug('-'.join(relative.with_suffix('').parts))}"
    with tempfile.TemporaryDirectory() as temporary_dir:
        sanitized = Path(temporary_dir) / source_path.name
        sanitized.write_text(json.dumps(notebook, ensure_ascii=False), encoding="utf-8")
        run_nbconvert(sanitized, safe_name, "html")
        try:
            run_nbconvert(sanitized, safe_name, "webpdf")
        except (FileNotFoundError, RuntimeError, subprocess.CalledProcessError):
            pass
    html_path = PREVIEW_OUTPUT / f"{safe_name}.html"
    html = html_path.read_text(encoding="utf-8")
    html_path.write_text(html.replace("</head>", '<link rel="stylesheet" href="../notebook.css"></head>', 1), encoding="utf-8")
    key = subject_key(source_path)
    resource = {"title": notebook_title(source_path, notebook), "source": str(relative), "kind": "notebook", "subject_key": key, "subject_name": subject_name(key), "tags": [], "html": f"previews/{safe_name}.html", "download": copy_download(source_path)}
    if (PREVIEW_OUTPUT / f"{safe_name}.pdf").exists():
        resource["pdf"] = f"previews/{safe_name}.pdf"
    return resource


def build_resource(source_path, index):
    extension = source_path.suffix.lower()
    relative = source_path.relative_to(ROOT)
    key = subject_key(source_path)
    metadata = {}
    content = None
    if extension in {".md", ".markdown"}:
        metadata, content = parse_frontmatter(source_path.read_text(encoding="utf-8"))
    title = str(metadata.get("title", title_from_path(source_path)))
    kind = str(metadata.get("type", CATEGORY_TYPES.get(source_path.parent.name, extension.lstrip(".").lower()))).lower()
    resource = {"title": title, "source": str(relative), "kind": kind, "subject_key": key, "subject_name": subject_name(key), "tags": metadata.get("tags", [])}
    resource["download"] = copy_download(source_path)
    safe_name = f"{index:02d}-{slug('-'.join(relative.with_suffix('').parts))}"
    if extension in {".md", ".markdown"}:
        resource["html"] = write_preview_page(resource, markdown_to_html(content), f"{safe_name}.html")
    elif extension in SUPPORTED_TEXT:
        text = source_path.read_text(encoding="utf-8", errors="replace")
        resource["html"] = write_preview_page(resource, f"<pre class=\"code-preview\">{escape(text)}</pre>", f"{safe_name}.html")
    elif extension == ".pdf":
        resource["pdf"] = resource["download"]
    elif extension in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
        resource["html"] = write_preview_page(resource, f"<img class=\"image-preview\" src=\"../{resource['download']}\" alt=\"{escape(title)}\">", f"{safe_name}.html")
    else:
        resource["html"] = write_preview_page(resource, f"<p>This file is available for download.</p><p class=\"filename\">{escape(relative.as_posix())}</p>", f"{safe_name}.html")
    if extension == ".tex":
        build_latex(source_path, resource, safe_name)
    return resource


def discover_resources():
    paths = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        relative_parts = path.relative_to(ROOT).parts
        if len(relative_parts) < 2 or relative_parts[0] in IGNORED_ROOTS or path.name in SKIP_NAMES:
            continue
        if path.suffix.lower() in {".ipynb", ".tex", ".pdf", ".md", ".markdown", ".txt", ".py", ".c", ".cpp", ".h", ".java", ".js", ".ts", ".html", ".css", ".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            paths.append(path)
    return sorted(paths)


def resource_timestamp(resource):
    try:
        return int(subprocess.check_output(["git", "log", "-1", "--format=%ct", "--", resource["source"]], cwd=ROOT, text=True).strip() or 0)
    except (OSError, subprocess.CalledProcessError, ValueError):
        return 0


def write_index(resources):
    subjects = {}
    for resource in resources:
        subjects.setdefault(resource["subject_key"], []).append(resource)
    subject_cards = "".join(f'<button class="subject-card subject-filter" type="button" data-filter="{escape(key)}" aria-pressed="false"><p class="subject-number">{len(items):02d}</p><div><h3>{escape(subject_name(key))}</h3><p>{escape(key.replace("-", " ").title())} resources</p></div></button>' for key, items in sorted(subjects.items()))
    cards = []
    for index, resource in enumerate(resources, 1):
        actions = []
        if resource.get("html"): actions.append(f'<a class="button button-primary" href="{resource["html"]}">View resource</a>')
        if resource.get("pdf"): actions.append(f'<a class="button" href="{resource["pdf"]}">View PDF</a>')
        actions.append(f'<a class="text-link" href="{resource["download"]}" download>Download file</a>')
        tags = " ".join(resource.get("tags", []))
        cards.append(f'<article class="resource-card" data-subject="{escape(resource["subject_key"])}" data-type="{escape(resource["kind"])}" data-search="{escape((resource["title"] + " " + resource["source"] + " " + tags).lower())}"><div class="card-index">{index:02d}</div><div class="card-content"><p class="eyebrow">{escape(resource["subject_name"])} / {escape(resource["kind"])}</p><h2>{escape(resource["title"])}</h2><p class="filename">{escape(resource["source"])}</p><div class="actions">{"".join(actions)}</div></div></article>')
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>clg_work | Coursework Library</title><link rel="stylesheet" href="site.css"></head><body><main class="shell"><header class="hero"><p class="eyebrow">clg_work / static library</p><h1>Everything<br><em>in its place.</em></h1><p class="intro">A quiet, searchable home for practicals, notes, books, guidelines, and experiments. Edited in Obsidian, published by Git.</p></header><section class="subjects"><div class="section-heading"><div><p class="eyebrow">The curriculum</p><h2>Subjects</h2></div><p class="updated">{len(resources):02d} resources / {len(subjects):02d} subjects</p></div><div class="subject-grid">{subject_cards}</div></section><section class="library"><div class="section-heading"><div><p class="eyebrow">Browse the archive</p><h2 id="library-title">Recent resources</h2></div><div class="library-tools"><label class="search-label" for="search">Search</label><input id="search" type="search" placeholder="Title, file, or tag"></div></div><div class="filter-row"><button class="filter-reset is-active" type="button" data-filter="recent">Recent</button><button class="filter-reset" type="button" data-filter="all">All resources</button><button class="filter-reset" type="button" data-filter="practical">Practicals</button><button class="filter-reset" type="button" data-filter="note">Notes</button><button class="filter-reset" type="button" data-filter="book">Books</button><button class="filter-reset" type="button" data-filter="guideline">Guidelines</button></div>{"".join(cards)}<p class="empty-state is-hidden">No resources match this view.</p></section><footer><span>Edited in Obsidian / published with GitHub Actions</span><a href="https://github.com/Akshaj-Bisht/clg_work">View source</a></footer></main><script>const resources=[...document.querySelectorAll('.resource-card')];const filters=[...document.querySelectorAll('[data-filter]')];const search=document.querySelector('#search');const empty=document.querySelector('.empty-state');const title=document.querySelector('#library-title');let active='recent';function apply(){{const query=search.value.toLowerCase();let visible=0;resources.forEach((item,index)=>{{const matchesSearch=item.dataset.search.includes(query);const matches=active==='recent'?index<6:active==='all'||item.dataset.subject===active||item.dataset.type===active;const show=matches&&matchesSearch;item.classList.toggle('is-hidden',!show);if(show)visible++}});filters.forEach(button=>{{const selected=button.dataset.filter===active;button.classList.toggle('is-active',selected);button.setAttribute('aria-pressed',selected)}});title.textContent=active==='recent'?'Recent resources':active==='all'?'All resources':active[0].toUpperCase()+active.slice(1)+'s';empty.classList.toggle('is-hidden',visible>0)}}filters.forEach(button=>button.addEventListener('click',()=>{{active=button.dataset.filter;apply()}}));search.addEventListener('input',apply);apply();</script></body></html>'''
    (SITE / "index.html").write_text(html, encoding="utf-8")


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    PREVIEW_OUTPUT.mkdir(parents=True)
    DOWNLOAD_OUTPUT.mkdir(parents=True)
    shutil.copy2(STYLE_SOURCE, SITE / "site.css")
    shutil.copy2(NOTEBOOK_STYLE_SOURCE, SITE / "notebook.css")
    resources = []
    for index, path in enumerate(discover_resources(), 1):
        if path.suffix.lower() == ".ipynb":
            resources.append(build_notebook(path, index))
        elif path.suffix.lower() == ".tex":
            resources.append(build_resource(path, index))
        else:
            resources.append(build_resource(path, index))
    resources.sort(key=resource_timestamp, reverse=True)
    write_index(resources)


if __name__ == "__main__":
    main()
