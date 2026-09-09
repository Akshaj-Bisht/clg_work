import { randomUUID } from "node:crypto";
import { NextResponse } from "next/server";
import { getEnv } from "../../../../../server/env";
import { requireUser } from "../../../../../server/auth";
import { routeErrorResponse } from "../../../../../server/http";
import { parseJson, fileMetadataSchema } from "../../../../../server/validation";

type Context = { params: Promise<{ resourceId: string }> };

export async function POST(request: Request, { params }: Context) {
  try {
    const { supabase, user } = await requireUser();
    const { resourceId } = await params;
    const input = await parseJson(request, fileMetadataSchema);
    if (input.resource_id !== resourceId) {
      return NextResponse.json({ error: "Resource mismatch" }, { status: 400 });
    }
    const safeFilename = input.filename.replace(/[^a-zA-Z0-9._-]/g, "_");
    const storagePath = `${user.id}/${resourceId}/${randomUUID()}-${safeFilename}`;
    const { data: file, error: fileError } = await supabase.from("files").insert({
      ...input,
      owner_id: user.id,
      storage_path: storagePath,
    }).select().single();
    if (fileError) throw fileError;
    const { data: upload, error: uploadError } = await supabase.storage.from(getEnv().SUPABASE_RESOURCE_BUCKET).createSignedUploadUrl(storagePath);
    if (uploadError) throw uploadError;
    return NextResponse.json({ file, upload }, { status: 201 });
  } catch (error) {
    return routeErrorResponse(error);
  }
}
