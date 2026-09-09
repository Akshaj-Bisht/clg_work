# Multi-Agent Development Plan

This file is the operating plan for evolving `clg_work` from a static GitHub Pages
publisher into a coursework library with mobile uploads, subject management, and
Obsidian integration.

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

- Define the first vertical slice: create subject, upload resource, view/download
  resource.
- Decide database entities, authentication boundary, storage contract, and API
  conventions before implementation agents begin.
- Maintain the migration checklist from the current static site.
- Merge branches in the order below, resolve conflicts, and run end-to-end checks.

Must not implement backend or frontend features in another agent's ownership area
unless integration is blocked.

Prompt to send:

> You are Agent 0, the coordinator for `clg_work`. Work only in the coordinator
> worktree on `main`. Read `AGENTS.md`, define the first vertical slice and API/data
> contracts, then coordinate the specialist branches. Do not edit specialist-owned
> paths. Report decisions, merge order, validation results, and blockers.

### Agent 1: Application foundation and backend

Owns: `app/`, `server/`, `supabase/`, `db/`, backend configuration, and backend
tests. If the new application does not exist yet, this agent may create the
minimal Next.js project structure in these paths.

Tasks:

- Set up the Next.js/TypeScript application foundation and environment variable
  contract.
- Add Supabase schema/migrations for users, subjects, resources, files, and tags.
- Implement authenticated subject CRUD and resource metadata APIs.
- Implement protected file-upload metadata handling and storage integration.
- Add validation, authorization, and backend tests.

Dependencies: Agent 0's API and data contract.

Prompt to send:

> You are Agent 1, backend. Work only in the `agent/backend` worktree. Read
> `AGENTS.md` and implement the Next.js/Supabase foundation, schema, authenticated
> subject/resource APIs, storage integration, and backend tests. Own only `app/`,
> `server/`, `supabase/`, `db/`, backend configuration, and backend tests. Do not
> edit frontend, processing, Obsidian, or migration-owned files. Commit your work
> and report the commit hash and validation commands.

### Agent 2: Web and mobile frontend

Owns: `components/`, `app/(dashboard)/`, `app/(auth)/`, `public/`, and frontend
tests. It may consume Agent 1 APIs but must not edit database migrations or backend
logic.

Tasks:

- Build responsive dashboard, subject list/detail, resource list/detail, and
  add-subject/upload flows.
- Make file selection and upload usable on narrow phone screens.
- Add loading, empty, error, permission, and upload-progress states.
- Add search/filter controls without duplicating server-side authorization.
- Add component and browser-level tests for the first vertical slice.

Dependencies: Agent 1's API contract and authentication behavior.

Prompt to send:

> You are Agent 2, frontend. Work only in the `agent/frontend` worktree. Read
> `AGENTS.md` and build the responsive dashboard, subject pages, resource pages,
> mobile upload flow, search/filter UI, and frontend tests against Agent 1's
> documented contract. Own only `components/`, `app/(dashboard)/`, `app/(auth)/`,
> `public/`, and frontend tests. Do not edit backend or database files. Commit your
> work and report the commit hash and validation commands.

### Agent 3: File processing and preview pipeline

Owns: `workers/`, `processing/`, `scripts/processing/`, and processing tests.

Tasks:

- Extract the reusable notebook and LaTeX conversion behavior from
  `scripts/build_site.py` without breaking the current static publisher.
- Define asynchronous processing states: pending, processing, ready, and failed.
- Generate HTML/PDF previews and store processing errors safely.
- Preserve the existing GitHub Pages build until the new pipeline is verified.

Dependencies: Agent 1's resource/file status contract. This agent must not change
the dashboard UI or database schema without coordinator approval.

Prompt to send:

> You are Agent 3, processing pipeline. Work only in the `agent/processing`
> worktree. Read `AGENTS.md` and extract reusable notebook/LaTeX processing from
> `scripts/build_site.py`, add asynchronous processing states and preview generation,
> and test failures/retries. Own only `workers/`, `processing/`,
> `scripts/processing/`, and processing tests. Preserve the current static publisher
> and do not edit UI or database migrations. Commit your work and report the commit
> hash and validation commands.

### Agent 4: Obsidian integration

Owns: `integrations/obsidian/`, `obsidian/`, sync documentation, and sync tests.

Tasks:

- Define Markdown export with stable frontmatter for subjects and resources.
- Export attachments using relative links and deterministic paths.
- Implement the first sync strategy as explicit Markdown export or Git export;
  do not assume a browser can write directly into a local vault.
- Add conflict handling, idempotency, and a dry-run mode before considering an
  Obsidian plugin.

Dependencies: Agent 1's resource model. This agent must not alter the primary
database source of truth.

Prompt to send:

> You are Agent 4, Obsidian integration. Work only in the `agent/obsidian`
> worktree. Read `AGENTS.md` and implement deterministic Markdown/frontmatter export,
> relative attachment links, idempotency, conflict handling, and dry-run tests.
> Own only `integrations/obsidian/`, `obsidian/`, sync documentation, and sync tests.
> Treat the application database as the source of truth and do not edit its schema.
> Commit your work and report the commit hash and validation commands.

### Agent 5: Verification and migration

Owns: `tests/`, migration scripts, import reports, and CI additions. It may add
tests near another module only with that module agent's approval.

Tasks:

- Import existing `dip/`, `latex/`, and `compiler-design/` resources into a
  staging database or fixture set without deleting source files.
- Verify notebook, LaTeX, PDF, and ordinary document handling.
- Add CI checks for typechecking, linting, unit tests, and migration safety.
- Run the complete acceptance checklist after integration.

Dependencies: Agents 1, 2, and 3. Agent 4 is included once its export contract
exists.

Prompt to send:

> You are Agent 5, verification and migration. Work only in the
> `agent/verification` worktree. Read `AGENTS.md`, create safe import fixtures for
> the existing `dip/`, `latex/`, and `compiler-design/` resources, verify file types,
> and add CI checks for typecheck, lint, tests, and migration safety. Do not delete
> or modify original coursework files. Commit your work and report the commit hash,
> validation commands, and remaining risks.

## Worktree Setup

Run these commands from the repository root after committing or otherwise
recording the baseline. Use paths outside the repository so worktrees do not
overlap:

```sh
git fetch origin
git switch main
git pull --ff-only origin main

git worktree add ../clg_work-agent-backend -b agent/backend main
git worktree add ../clg_work-agent-frontend -b agent/frontend main
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
2. Agent 1 merges the application foundation, schema, APIs, and backend tests.
3. Agent 3 merges processing states and preview workers.
4. Agent 2 merges the UI against the verified API and processing contracts.
5. Agent 4 merges Obsidian export/sync.
6. Agent 5 merges migration fixtures and CI verification.
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
git worktree remove ../clg_work-agent-backend
git worktree remove ../clg_work-agent-frontend
git worktree remove ../clg_work-agent-processing
git worktree remove ../clg_work-agent-obsidian
git worktree remove ../clg_work-agent-verification
git branch -d agent/backend agent/frontend agent/processing agent/obsidian agent/verification
```

Only the coordinator performs cleanup, and only after confirming the merged commits
are present on `main`.