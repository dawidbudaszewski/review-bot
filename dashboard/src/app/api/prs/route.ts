import { NextResponse } from "next/server";
import { listPRs } from "@/lib/github";

export async function GET() {
  try {
    const prs = await listPRs();
    return NextResponse.json(prs);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
