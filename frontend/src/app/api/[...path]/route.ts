import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.INTERNAL_API_URL || "http://localhost:8000";

async function proxyRequest(
  request: NextRequest,
  params: { path: string[] }
) {
  const pathStr = params.path.join("/");
  const { search } = new URL(request.url);
  const targetUrl = `${BACKEND_URL}/api/${pathStr}${search}`;

  // Forward headers
  const headers: Record<string, string> = {};
  const auth = request.headers.get("authorization");
  if (auth) headers["authorization"] = auth;

  let body: BodyInit | undefined;
  const contentType = request.headers.get("content-type") || "";

  if (request.method !== "GET" && request.method !== "DELETE") {
    if (contentType.includes("multipart/form-data")) {
      const formData = await request.formData();
      // For multipart, let fetch set the boundary automatically
      const plain = new FormData();
      for (const [key, value] of formData.entries()) {
        plain.append(key, value);
      }
      body = plain;
    } else {
      headers["content-type"] = contentType || "application/json";
      body = await request.text();
    }
  }

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers,
      body,
    });

    const data = await response.arrayBuffer();
    const resContentType =
      response.headers.get("content-type") || "application/json";

    // Ensure UTF-8 charset for JSON responses
    const ct = resContentType.includes("application/json") && !resContentType.includes("charset")
      ? resContentType + "; charset=utf-8"
      : resContentType;

    return new NextResponse(data, {
      status: response.status,
      headers: { "content-type": ct },
    });
  } catch {
    return NextResponse.json(
      { detail: "Backend không phản hồi" },
      { status: 503 }
    );
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params);
}

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  return proxyRequest(request, params);
}
