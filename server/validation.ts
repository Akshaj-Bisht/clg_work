import { z } from "zod";

export const subjectCreateSchema = z.object({
  name: z.string().trim().min(1).max(120),
  description: z.string().trim().max(500).optional().default(""),
});

export const subjectUpdateSchema = subjectCreateSchema.partial().extend({
  archived: z.boolean().optional(),
});

export const resourceKindSchema = z.enum(["practical", "note", "book", "guideline", "notebook", "pdf", "document"]);
export const resourceCreateSchema = z.object({
  subject_id: z.string().uuid(),
  title: z.string().trim().min(1).max(200),
  description: z.string().trim().max(2000).optional().default(""),
  kind: resourceKindSchema,
  tags: z.array(z.string().trim().min(1).max(50)).max(20).optional().default([]),
});

export const resourceUpdateSchema = resourceCreateSchema.omit({ subject_id: true }).partial();

export const fileMetadataSchema = z.object({
  resource_id: z.string().uuid(),
  filename: z.string().trim().min(1).max(255),
  content_type: z.string().trim().min(1).max(255),
  size_bytes: z.number().int().positive().max(100 * 1024 * 1024),
});

export async function parseJson<T extends z.ZodType>(request: Request, schema: T): Promise<z.infer<T>> {
  return schema.parse(await request.json());
}
