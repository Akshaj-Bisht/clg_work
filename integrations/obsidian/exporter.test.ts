import { mkdtemp, readFile, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { exportResource, slugify, type ExportInput } from "./exporter";

const resource: ExportInput = {
  id: "resource-123",
  title: "Signals & Systems",
  subject: { id: "subject-123", name: "Digital Signal Processing" },
  kind: "note",
  processingStatus: "ready",
  attachments: [],
};

describe("Obsidian export", () => {
  it("creates deterministic paths and stable frontmatter", async () => {
    const vaultPath = await mkdtemp(path.join(os.tmpdir(), "obsidian-export-"));
    const result = await exportResource(resource, { vaultPath });
    const markdown = await readFile(result.markdownPath, "utf8");

    expect(result.action).toBe("created");
    expect(result.markdownPath).toBe(
      path.join(vaultPath, "Coursework", "digital-signal-processing", "signals-systems.md"),
    );
    expect(markdown).toContain('id: "resource-123"');
    expect(markdown).toContain('subject: "Digital Signal Processing"');
    expect(markdown).toContain("managed-by: coursework-library");
  });

  it("is idempotent and supports dry runs", async () => {
    const vaultPath = await mkdtemp(path.join(os.tmpdir(), "obsidian-export-"));
    await exportResource(resource, { vaultPath });
    const dryRun = await exportResource(resource, { vaultPath, dryRun: true });
    const repeated = await exportResource(resource, { vaultPath });

    expect(dryRun.action).toBe("unchanged");
    expect(repeated.action).toBe("unchanged");
  });

  it("reports local edits as conflicts", async () => {
    const vaultPath = await mkdtemp(path.join(os.tmpdir(), "obsidian-export-"));
    const first = await exportResource(resource, { vaultPath });
    await writeFile(first.markdownPath, `${await readFile(first.markdownPath, "utf8")}Local edit\n`);

    const result = await exportResource(resource, { vaultPath });
    expect(result.action).toBe("conflict");
  });

  it("copies attachments under the subject export directory", async () => {
    const vaultPath = await mkdtemp(path.join(os.tmpdir(), "obsidian-export-"));
    const sourcePath = path.join(vaultPath, "source file.pdf");
    await writeFile(sourcePath, "attachment contents");

    const result = await exportResource(
      {
        ...resource,
        attachments: [
          {
            id: "file-123",
            kind: "attachment",
            filename: "report final.pdf",
            storagePath: "resource-123/report final.pdf",
            localPath: sourcePath,
          },
        ],
      },
      { vaultPath },
    );
    const markdown = await readFile(result.markdownPath, "utf8");

    expect(markdown).toContain("- [report-final.pdf](attachments/report-final.pdf)");
    expect(result.attachmentActions[0]?.action).toBe("created");
    expect(await readFile(result.attachmentActions[0].path, "utf8")).toBe("attachment contents");
  });

  it("normalizes slugs without producing empty names", () => {
    expect(slugify("  C++ / DSP  ")).toBe("c-dsp");
    expect(slugify("日本語")).toBe("untitled");
  });
});