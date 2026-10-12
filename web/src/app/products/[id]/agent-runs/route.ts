import { NextResponse } from "next/server";
export async function GET(request: Request) { return NextResponse.redirect(new URL("/course-stage", request.url), 303); }
export async function POST(request: Request) { return NextResponse.redirect(new URL("/course-stage", request.url), 303); }
