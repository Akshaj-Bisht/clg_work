import { NextResponse } from "next/server";
import { requireUser } from "../../../../server/auth";
import { routeErrorResponse } from "../../../../server/http";
import { parseJson, resourceUpdateSchema } from "../../../../server/validation";

type Context = { params: Promise<{ resourceId: string }> };

export async function GET(_request: Request, { params }: Context) {
  try {
    const { supabase } = await requireUser();
    const { resourceId } = await params;
    const { data, error } = await supabase.from("resources").select("*, files(*), subjects(id, name), resource_tags(tags(id, name))").eq("id", resourceId).single();
    if (error) throw error;
    return NextResponse.json({ resource: data });
  } catch (error) {
    return routeErrorResponse(error);
  }
}

export async function PATCH(request: Request, { params }: Context) {
  try {
    const { supabase } = await requireUser();
    const { resourceId } = await params;
    const input = await parseJson(request, resourceUpdateSchema);
    const { data, error } = await supabase.from("resources").update(input).eq("id", resourceId).select().single();
    if (error) throw error;
    return NextResponse.json({ resource: data });
  } catch (error) {
    return routeErrorResponse(error);
  }
}
