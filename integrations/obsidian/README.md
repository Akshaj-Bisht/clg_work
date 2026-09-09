# Obsidian export

The application database remains the source of truth. This integration performs
an explicit filesystem export into the managed `Coursework/` directory of a
vault; it does not require an Obsidian plugin or browser access to a local vault.

Resources are written to `Coursework/<subject-slug>/<resource-slug>.md` and
attachments to the matching `attachments/` directory. Slugs and attachment
names are deterministic. Generated Markdown includes a content hash so a
repeated export is idempotent and a locally edited generated file is reported as
a conflict instead of being silently overwritten.

Use `dryRun: true` to calculate actions without creating or changing files.