import { NextResponse } from "next/server";
import { requireUser } from "../../../server/auth";
import { routeErrorResponse } from "../../../server/http";
import { parseJson, resourceCreateSchema } from "../../../server/validation";

export async function GET(request: Request) {
  try {
    const { supabase } = await requireUser();
    const url = new URL(request.url);
    let query = supabase.from("resources").select("*, files(*), subjects(id, name), resource_tags(tags(id, name))").order("created_at", { ascending: false });
    const subjectId = url.searchParams.get("subject_id");
    const kind = url.searchParams.get("kind");
    if (subjectId) query = query.eq("subject_id", subjectId);
    if (kind) query = query.eq("kind", kind);
    const { data, error } = await query;
    if (error) throw error;
    return NextResponse.json({ resources: data });
  } catch (error) {
    return routeErrorResponse(error);
  }
}

export async function POST(request: Request) {
  try {
    const { supabase, user } = await requireUser();
    const input = await parseJson(request, resourceCreateSchema);
    const { tags = [], ...resource } = input;
    const { data, error } = await supabase.from("resources").insert({ ...resource, owner_id: user.id }).select().single();
    if (error) throw error;
    if (tags.length) {
      const { data: tagRows, error: tagError } = await supabase.from("tags").upsert(
        tags.map((name) => ({ name, owner_id: user.id })),
        { onConflict: "owner_id,name" },
      ).select("id, name");
      if (tagError) throw tagError;
      const { error: relationError } = await supabase.from("resource_tags").insert(
        tagRows.map((tag) => ({ resource_id: data.id, tag_id: tag.id })),
      );
      if (relationError) throw relationError;
    }
    return NextResponse.json({ resource: data }, { status: 201 });
  } catch (error) {
    return routeErrorResponse(error);
  }
}
