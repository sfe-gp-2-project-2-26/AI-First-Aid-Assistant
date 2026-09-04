import { createFileRoute } from "@tanstack/react-router";

const AUTH_URL = process.env['AUTH_BACKEND_URL'] || "http://localhost:4000";

export const Route = createFileRoute("/api/backend/conversations/")({
  server: {
    handlers: {
      GET: async ({ request }) => {
        try {
          const cookieHeader = request.headers.get("cookie");
          const response = await fetch(`${AUTH_URL}/api/conversations`, {
            method: "GET",
            headers: {
              ...(cookieHeader ? { Cookie: cookieHeader } : {}),
            },
          });
          const data = await response.json();
          return new Response(JSON.stringify(data), {
            status: response.status,
            headers: { "Content-Type": "application/json" },
          });
        } catch (error) {
          return new Response(JSON.stringify({ error: "Auth service unavailable" }), { status: 503, headers: { "Content-Type": "application/json" } });
        }
      },
    },
  },
});

