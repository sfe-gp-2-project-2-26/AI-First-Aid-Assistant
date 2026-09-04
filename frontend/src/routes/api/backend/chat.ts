import { createFileRoute } from "@tanstack/react-router";

const AUTH_URL = process.env['AUTH_BACKEND_URL'] || "http://localhost:4000";

type ProxyBody = { query?: unknown; conversation_id?: unknown };

export const Route = createFileRoute("/api/backend/chat")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        let body: ProxyBody;
        try {
          body = (await request.json()) as ProxyBody;
        } catch {
          return Response.json({ detail: "Invalid request body." }, { status: 400 });
        }

        const query = typeof body.query === "string" ? body.query.trim() : "";
        if (query.length < 2) {
          return Response.json(
            { detail: "Please describe the situation in at least 2 characters." },
            { status: 422 },
          );
        }

        const cookieHeader = request.headers.get("cookie");

        let upstream: Response;
        try {
          upstream = await fetch(`${AUTH_URL}/api/chat`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Accept: "application/json",
              ...(cookieHeader ? { Cookie: cookieHeader } : {}),
            },
            body: JSON.stringify({ query, conversation_id: body.conversation_id }),
          });
        } catch {
          return Response.json({
            upstreamError: "Could not reach the auth-backend. Make sure the Node.js backend is running.",
          });
        }

        const text = await upstream.text();
        const contentType = upstream.headers.get("content-type") ?? "";

        if (!contentType.includes("application/json")) {
          return Response.json({
            upstreamError: `The backend URL did not return a valid JSON response (status ${upstream.status}).`,
          });
        }

        if (upstream.status >= 500) {
          return Response.json({
            upstreamError: "The clinical assistant is temporarily unavailable. Please try again.",
          });
        }

        return new Response(text, {
          status: upstream.status,
          headers: { "Content-Type": "application/json" },
        });
      },
    },
  },
});

