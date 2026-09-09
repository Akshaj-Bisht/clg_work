import { NextResponse } from "next/server";
import { requireUser } from "../../../../server/auth";
import { routeErrorResponse } from "../../../../server/http";
import { parseJson, subjectUpdateSchema } from "../../../../server/validation";

type Context = { params: Promise<{ subjectId: string }> };

export async function GET(_request: Request, { params }: Context) {
  try {
    const { supabase } = await requireUser();
    const { subjectId } = await params;
    const { data, error } = await supabase.from("subjects").select("*, resources(*)").eq("id", subjectId).single();
    if (error) throw error;
    return NextResponse.json({ subject: data });
  } catch (error) {
    return routeErrorResponse(error);
  }
}

export async function PATCH(request: Request, { params }: Context) {
  try {
    const { supabase } = await requireUser();
    const { subjectId } = await params;
    const input = await parseJson(request, subjectUpdateSchema);
    const { data, error } = await supabase.from("subjects").update(input).eq("id", subjectId).select().single();
    if (error) throw error;
    return NextResponse.json({ subject: data });
  } catch (error) {
    return routeErrorResponse(error);
  }
}

export async function DELETE(_request: Request, { params }: Context) {
  try {
    const { supabase } = await requireUser();
    const { subjectId } = await params;
    const { error } = await supabase.from("subjects").delete().eq("id", subjectId);
    if (error) throw error;
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    return routeErrorResponse(error);
  }
}
