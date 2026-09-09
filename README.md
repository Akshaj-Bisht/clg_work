# Digital Image Processing

This repository contains college coursework, projects, experiments, and implementations related to digital image processing.

Topics may include image enhancement, filtering, segmentation, feature extraction, transformations, and computer vision techniques.

## Notebook preview site

The rendered notebook website is available at **[Open the notebook library](https://akshaj-bisht.github.io/clg_work/)**. It includes syntax-highlighted code, saved outputs, browser previews, PDF downloads, and the original `.ipynb` files. Colab-only cells are removed from the published preview; the source notebooks are unchanged.

Coursework is organized into subject folders such as `dip/`, `latex/`,
`compiler-design/`, and `cyber_forensics/`. Inside each subject, use
`practicals/`, `notes/`, `books/`, `guidelines/`, `notebooks/`, and `assets/`.
Add a resource to the relevant folder and push to `main`; the preview site updates
automatically.

## Obsidian and Git workflow

Use this repository as the coursework vault or keep it as a synced coursework
folder inside your vault. Create subjects as top-level folders and place notes,
practicals, books, guidelines, PDFs, notebooks, and attachments inside the
matching subject. Commit and push with the Obsidian Git plugin; GitHub Actions
builds and deploys the updated static site automatically.

Recommended Obsidian Git settings:

1. Pull before committing.
2. Commit with a descriptive message such as `add dip practical 02`.
3. Push after reviewing the changed files.

The generated `site/` directory is build output and should not be edited by hand.

Each subject also has its own fast GitHub Action check. Only the Action for the changed subject runs, while the shared Pages Action rebuilds the complete website.

## Colab notebooks

Upload a notebook exported from Google Colab as an `.ipynb` file anywhere in this repository. GitHub automatically renders committed notebooks in its **Preview** view, including saved outputs.

### Available notebooks

| Notebook    | Preview                                                                                          | PDF                                                                                     | Download                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Practical 1 | Generated from the notebook in `dip/notebooks/` after the next Pages build | Generated PDF preview | [Download `.ipynb`](https://raw.githubusercontent.com/Akshaj-Bisht/clg_work/main/dip/notebooks/dip_prac_1.ipynb) |

The `Build and publish notebook previews` GitHub Action validates every `.ipynb` file and publishes the preview site automatically whenever notebooks or the site builder change.

The **Preview** link above opens the rendered notebook directly from this README. The **Download** link downloads the original notebook for Colab or Jupyter. To continue working in Colab, use **File > Open notebook > GitHub** and select the repository notebook.

## LaTeX practicals

PDFs placed in `latex/pdfs/` are used directly and are not rebuilt. If a `.tex` practical does not have a matching PDF in `latex/pdfs/`, the GitHub Action compiles it automatically. Both types appear on the website with browser preview and download links.
