import { NextResponse } from "next/server";
import { getEnv } from "../../../../server/env";
import { requireUser } from "../../../../server/auth";
import { routeErrorResponse } from "../../../../server/http";

type Context = { params: Promise<{ fileId: string }> };

export async function GET(_request: Request, { params }: Context) {
  try {
    const { supabase } = await requireUser();
    const { fileId } = await params;
    const { data: file, error: fileError } = await supabase.from("files").select("storage_path, filename").eq("id", fileId).single();
    if (fileError) throw fileError;
    const { data: download, error: downloadError } = await supabase.storage
      .from(getEnv().SUPABASE_RESOURCE_BUCKET)
      .createSignedUrl(file.storage_path, 60 * 10);
    if (downloadError) throw downloadError;
    return NextResponse.json({ download: { ...download, filename: file.filename } });
  } catch (error) {
    return routeErrorResponse(error);
  }
}