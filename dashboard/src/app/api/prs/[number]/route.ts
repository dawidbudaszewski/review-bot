import { NextResponse } from "next/server";
import { getPRDetail } from "@/lib/github";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ number: string }> }
) {
  try {
    const { number } = await params;
    const prNumber = parseInt(number, 10);
    if (isNaN(prNumber)) {
      return NextResponse.json({ error: "Invalid PR number" }, { status: 400 });
    }
    const pr = await getPRDetail(prNumber);
    return NextResponse.json(pr);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
