import { createFileRoute } from "@tanstack/react-router";

const AUTH_URL = process.env['AUTH_BACKEND_URL'] || "http://localhost:4000";

export const Route = createFileRoute("/api/auth/register")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        try {
          const body = await request.json();
          const response = await fetch(`${AUTH_URL}/api/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
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

