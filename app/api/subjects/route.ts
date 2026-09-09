import { NextResponse } from "next/server";
import { requireUser } from "../../../server/auth";
import { routeErrorResponse } from "../../../server/http";
import { parseJson, subjectCreateSchema } from "../../../server/validation";

export async function GET() {
  try {
    const { supabase } = await requireUser();
    const { data, error } = await supabase.from("subjects").select("*").order("name");
    if (error) throw error;
    return NextResponse.json({ subjects: data });
  } catch (error) {
    return routeErrorResponse(error);
  }
}

export async function POST(request: Request) {
  try {
    const { supabase, user } = await requireUser();
    const input = await parseJson(request, subjectCreateSchema);
    const { data, error } = await supabase.from("subjects").insert({ ...input, owner_id: user.id }).select().single();
    if (error) throw error;
    return NextResponse.json({ subject: data }, { status: 201 });
  } catch (error) {
    return routeErrorResponse(error);
  }
}
