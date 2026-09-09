import { createHash } from "node:crypto";
import { mkdir, readFile, writeFile, copyFile, stat } from "node:fs/promises";
import path from "node:path";

export type ResourceKind =
  | "practical"
  | "note"
  | "book"
  | "guideline"
  | "notebook"
  | "pdf"
  | "document";

export type ResourceFile = {
  id: string;
  kind: "original" | "preview_html" | "preview_pdf" | "attachment";
  filename: string;
  storagePath: string;
};

export type ExportResource = {
  id: string;
  title: string;
  description?: string;
  subject: { id: string; name: string };
  kind: ResourceKind;
  processingStatus: "pending" | "processing" | "ready" | "failed";
  files?: ResourceFile[];
};

export type AttachmentSource = ResourceFile & { localPath: string };

export type ExportInput = ExportResource & { attachments?: AttachmentSource[] };

export type ExportOptions = {
  vaultPath: string;
  dryRun?: boolean;
};

export type ExportAction = "created" | "updated" | "unchanged" | "conflict" | "skipped";

export type ExportResult = {
  resourceId: string;
  markdownPath: string;
  action: ExportAction;
  attachmentActions: Array<{ path: string; action: ExportAction }>;
};

const MANAGED_MARKER = "coursework-library";
const MANAGED_DIRECTORY = "Coursework";

export function slugify(value: string): string {
  const slug = value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "untitled";
}

function safeFilename(value: string): string {
  const basename = path.basename(value).replace(/[^a-zA-Z0-9._-]+/g, "-");
  return basename.replace(/^-+|-+$/g, "") || "attachment";
}

function yamlString(value: string): string {
  return JSON.stringify(value);
}

function bodyFor(resource: ExportInput, attachmentNames: string[]): string {
  const lines = [
    `# ${resource.title}`,
    "",
    resource.description?.trim() || "",
    ...(attachmentNames.length > 0
      ? ["", "## Attachments", "", ...attachmentNames.map((name) => `- [${name}](attachments/${name})`)]
      : []),
    "",
  ];
  return lines.join("\n");
}

function contentHash(body: string): string {
  return createHash("sha256").update(body).digest("hex");
}

function markdownFor(resource: ExportInput, body: string, hash: string): string {
  return [
    "---",
    `id: ${yamlString(resource.id)}`,
    `title: ${yamlString(resource.title)}`,
    `subject: ${yamlString(resource.subject.name)}`,
    `type: ${resource.kind}`,
    `status: ${resource.processingStatus}`,
    `managed-by: ${MANAGED_MARKER}`,
    `content-hash: ${hash}`,
    "---",
    "",
    body,
  ].join("\n");
}

function managedHash(markdown: string): string | undefined {
  const match = markdown.match(/^content-hash:\s*([a-f0-9]{64})\s*$/m);
  return match?.[1];
}

function isManaged(markdown: string): boolean {
  return /^managed-by:\s*coursework-library\s*$/m.test(markdown);
}

async function existingAction(filePath: string, expected: string, dryRun: boolean): Promise<ExportAction> {
  let current: string;
  try {
    current = await readFile(filePath, "utf8");
  } catch {
    if (!dryRun) {
      await mkdir(path.dirname(filePath), { recursive: true });
      await writeFile(filePath, expected, "utf8");
    }
    return "created";
  }

  if (current === expected) return "unchanged";
  const bodyStart = current.indexOf("\n---\n\n");
  const currentBody = bodyStart === -1 ? undefined : current.slice(bodyStart + "\n---\n\n".length);
  if (!isManaged(current) || !currentBody || managedHash(current) !== contentHash(currentBody)) return "conflict";
  if (!dryRun) await writeFile(filePath, expected, "utf8");
  return "updated";
}

async function copyAttachment(source: AttachmentSource, destination: string, dryRun: boolean): Promise<ExportAction> {
  try {
    await stat(destination);
    const [sourceContents, destinationContents] = await Promise.all([
      readFile(source.localPath),
      readFile(destination),
    ]);
    if (sourceContents.equals(destinationContents)) return "unchanged";
    return "conflict";
  } catch {
    if (!dryRun) {
      await mkdir(path.dirname(destination), { recursive: true });
      await copyFile(source.localPath, destination);
    }
    return "created";
  }
}

export async function exportResource(resource: ExportInput, options: ExportOptions): Promise<ExportResult> {
  const dryRun = options.dryRun === true;
  const subjectDirectory = path.join(options.vaultPath, MANAGED_DIRECTORY, slugify(resource.subject.name));
  const resourcePath = path.join(subjectDirectory, `${slugify(resource.title)}.md`);
  const attachments = resource.attachments ?? [];
  const attachmentNames = attachments.map((attachment) => safeFilename(attachment.filename));
  const body = bodyFor(resource, attachmentNames);
  const markdown = markdownFor(resource, body, contentHash(body));
  const action = await existingAction(resourcePath, markdown, dryRun);
  const attachmentActions: Array<{ path: string; action: ExportAction }> = [];

  if (action !== "conflict") {
    for (const [index, attachment] of attachments.entries()) {
      const name = attachmentNames[index];
      const destination = path.join(subjectDirectory, "attachments", name);
      const attachmentAction = await copyAttachment(attachment, destination, dryRun);
      attachmentActions.push({ path: destination, action: attachmentAction });
    }
  }

  return { resourceId: resource.id, markdownPath: resourcePath, action, attachmentActions };
}

export async function exportResources(resources: ExportInput[], options: ExportOptions): Promise<ExportResult[]> {
  return Promise.all(resources.map((resource) => exportResource(resource, options)));
}