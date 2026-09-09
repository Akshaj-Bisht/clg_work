# Multi-Agent Development Plan

This file is the operating plan for evolving `clg_work` into a static coursework
library authored through Obsidian and synchronized with Git.

The current target architecture is static GitHub Pages. Do not extend the
experimental Next.js/Supabase application unless the user explicitly changes this
decision.

## Coordination Rules

- The coordinator owns `main`, integration, releases, and conflict resolution.
- No agent works directly on `main`.
- Every agent gets a dedicated branch and Git worktree created from the same clean
  baseline commit.
- An agent must only edit the paths listed in its ownership section. Shared files
  are changed by the coordinator during integration unless explicitly assigned.
- Agents must not rewrite, delete, or reformat another agent's files.
- Each agent commits only its own focused changes and reports the commit hash,
  changed paths, validation commands, and known limitations.
- The coordinator merges in dependency order and runs the integration checks after
  every merge. Do not merge unrelated branches together with a single squashed
  mega-change.
- Existing untracked coursework files are user-owned. Do not delete, move, or
  modify them unless the user explicitly requests it.

## Agent Assignments

### Agent 0: Coordinator and architecture

Owns: `AGENTS.md`, architecture notes, root configuration, integration, and
release documentation.

Tasks:

- Define the first static slice: discover subject, render resource, preview, and
  download resource.
- Decide repository folders, frontmatter, supported file types, and build output
  conventions before implementation agents begin.
- Maintain the migration checklist from the current static site.
- Merge branches in the order below, resolve conflicts, and run end-to-end checks.

Must not implement backend or frontend features in another agent's ownership area
unless integration is blocked.

Prompt to send:

> You are Agent 0, the coordinator for `clg_work`. Work only in the coordinator
> worktree on `main`. Read `AGENTS.md`, define the static content/build contracts,
> then coordinate the specialist branches. Do not edit specialist-owned paths.
> Report decisions, merge order, validation results, and blockers.

### Agent 1: Static builder and resource discovery

Owns: `scripts/build_site.py`, static resource models, and builder tests.

Tasks:

- Discover subjects and resources without a hardcoded subject registry.
- Add Markdown/frontmatter, PDF, image, text, and ordinary document handling.
- Generate stable resource metadata and links for the static site.
- Preserve notebook and LaTeX behavior while extending the builder.
- Add builder tests for supported and unsupported files.

Dependencies: Agent 0's static content contract.

Prompt to send:

> You are Agent 1, static builder. Work only in the `agent/builder` worktree. Read
> `AGENTS.md` and extend `scripts/build_site.py` for recursive resource discovery,
> Markdown/frontmatter, PDFs, images, text, and ordinary documents. Add builder
> tests and preserve notebook/LaTeX behavior. Do not edit UI, Obsidian, or original
> coursework files. Commit your work and report the commit hash and validation
> commands.

### Agent 2: Static site UI

Owns: `scripts/site.css`, generated page templates, and static UI tests.

Tasks:

- Build responsive subject/resource pages and mobile navigation.
- Add client-side search and filters to the generated library.
- Add resource type badges, preview states, and download actions.
- Add browser-level checks for the generated static site.

Dependencies: Agent 1's generated resource metadata.

Prompt to send:

> You are Agent 2, static UI. Work only in the `agent/ui` worktree. Read `AGENTS.md`
> and build responsive subject/resource templates, mobile navigation, search,
> filters, type badges, preview states, download actions, and static UI tests from
> Agent 1's generated metadata. Own only `scripts/site.css`, generated templates,
> and static UI tests. Do not edit builder logic or original coursework files.
> Commit your work and report the commit hash and validation commands.

### Agent 3: File processing and preview pipeline

Owns: `workers/`, `processing/`, `scripts/processing/`, and processing tests.

Tasks:

- Extract the reusable notebook and LaTeX conversion behavior from
  `scripts/build_site.py` without breaking the current static publisher.
- Define local build processing states: pending, processing, ready, and failed.
- Generate HTML/PDF previews and report processing errors clearly in the build.
- Preserve the existing GitHub Pages build until the new pipeline is verified.

Dependencies: Agent 1's resource discovery contract. This agent must not change
the static site templates or move source coursework without coordinator approval.

Prompt to send:

> You are Agent 3, processing pipeline. Work only in the `agent/processing`
> worktree. Read `AGENTS.md` and extract reusable notebook/LaTeX processing from
> `scripts/build_site.py`, add local preview generation and clear build failures,
> and test retries. Own only `workers/`, `processing/`,
> `scripts/processing/`, and processing tests. Preserve the current static publisher
> and do not edit UI or database code. Commit your work and report the commit hash
> and validation commands.

### Agent 4: Obsidian integration

Owns: `integrations/obsidian/`, `obsidian/`, sync documentation, and sync tests.

Tasks:

- Define Markdown export with stable frontmatter for subjects and resources.
- Export attachments using relative links and deterministic paths.
- Implement the first sync strategy as explicit Markdown export or Git export;
  do not assume a browser can write directly into a local vault.
- Add conflict handling, idempotency, and a dry-run mode before considering an
  Obsidian plugin.

Dependencies: Agent 1's resource metadata. This agent must not introduce a
database or alter source coursework outside managed export paths.

Prompt to send:

> You are Agent 4, Obsidian integration. Work only in the `agent/obsidian`
> worktree. Read `AGENTS.md` and document deterministic subject folders,
> Markdown/frontmatter conventions, relative attachments, and Obsidian Git pull,
> commit, and push settings. Own only `integrations/obsidian/`, `obsidian/`, sync
> documentation, and sync tests. Do not add a web API or database. Commit your work
> and report the commit hash and validation commands.

### Agent 5: Verification and migration

Owns: `tests/`, migration scripts, import reports, and CI additions. It may add
tests near another module only with that module agent's approval.

Tasks:

- Import existing `dip/`, `latex/`, and `compiler-design/` resources into static
  fixtures without deleting source files.
- Verify notebook, LaTeX, PDF, and ordinary document handling.
- Add CI checks for builder validation, static output, and migration safety.
- Run the complete acceptance checklist after integration.

Dependencies: Agents 1, 2, and 3. Agent 4 is included once its export contract
exists.

Prompt to send:

> You are Agent 5, verification and migration. Work only in the
> `agent/verification` worktree. Read `AGENTS.md`, create safe static import
> fixtures for the existing `dip/`, `latex/`, and `compiler-design/` resources,
> verify file types, and add CI checks for the builder and generated site. Do not
> delete or modify original coursework files. Commit your work and report the
> commit hash, validation commands, and remaining risks.

## Worktree Setup

Run these commands from the repository root after committing or otherwise
recording the baseline. Use paths outside the repository so worktrees do not
overlap:

```sh
git fetch origin
git switch main
git pull --ff-only origin main

git worktree add ../clg_work-agent-builder -b agent/builder main
git worktree add ../clg_work-agent-ui -b agent/ui main
git worktree add ../clg_work-agent-processing -b agent/processing main
git worktree add ../clg_work-agent-obsidian -b agent/obsidian main
git worktree add ../clg_work-agent-verification -b agent/verification main
```

The coordinator keeps the primary checkout at `main`. Each agent runs tests in its
own worktree, commits there, and sends the coordinator the commit hash. Do not
share generated `node_modules`, virtual environments, build output, or local
`.env` files between worktrees.

## Merge Order

1. Agent 0 records the architecture and contracts.
2. Agent 1 merges resource discovery and builder tests.
3. Agent 3 merges notebook and LaTeX processing improvements.
4. Agent 2 merges static templates, search, filters, and responsive UI.
5. Agent 4 merges Obsidian Git documentation and conventions.
6. Agent 5 merges static fixtures and CI verification.
7. Agent 0 runs the complete acceptance checklist and updates documentation.

For each branch:

```sh
git switch main
git merge --no-ff agent/<name>
# run the focused checks for the merged area
# run the full checks before the next merge
```

If a conflict crosses ownership boundaries, stop the merge, preserve both agents'
behavior, and let the coordinator resolve it. Never resolve a conflict by
discarding a branch wholesale.

## Acceptance Checklist

- A user can sign in from a desktop or phone.
- A user can create, rename, and archive a subject.
- A user can upload a practical, note, book, guideline, notebook, or PDF from a
  phone.
- Uploads show progress and recover from failure.
- A resource can be opened, previewed when supported, downloaded, searched, and
  filtered by subject/type/tag.
- Notebook and LaTeX processing failures are visible and retryable.
- Existing static GitHub Pages publishing still works during migration.
- Obsidian export creates deterministic Markdown, frontmatter, and attachment
  links without overwriting unrelated vault files.
- Authentication and storage rules prevent one user from reading another user's
  private resources.
- Typecheck, lint, unit, integration, and migration checks pass on CI.

## Branch Cleanup

After successful integration and when no rollback is needed:

```sh
git worktree remove ../clg_work-agent-builder
git worktree remove ../clg_work-agent-ui
git worktree remove ../clg_work-agent-processing
git worktree remove ../clg_work-agent-obsidian
git worktree remove ../clg_work-agent-verification
git branch -d agent/builder agent/ui agent/processing agent/obsidian agent/verification
```

Only the coordinator performs cleanup, and only after confirming the merged commits
are present on `main`.