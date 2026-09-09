import { describe, expect, it } from "vitest";
import { fileMetadataSchema, resourceCreateSchema, subjectCreateSchema } from "./validation";

describe("request validation", () => {
  it("accepts a valid subject", () => {
    expect(subjectCreateSchema.parse({ name: "Digital Image Processing" })).toMatchObject({
      name: "Digital Image Processing",
      description: "",
    });
  });

  it("rejects oversized files", () => {
    expect(() => fileMetadataSchema.parse({
      resource_id: "00000000-0000-0000-0000-000000000000",
      filename: "notes.pdf",
      content_type: "application/pdf",
      size_bytes: 100 * 1024 * 1024 + 1,
    })).toThrow();
  });

  it("requires a subject and supported resource kind", () => {
    expect(() => resourceCreateSchema.parse({ title: "Practical" })).toThrow();
    expect(() => resourceCreateSchema.parse({
      subject_id: "00000000-0000-0000-0000-000000000000",
      title: "Practical",
      kind: "executable",
    })).toThrow();
  });
});
