import { createFileRoute } from "@tanstack/react-router";

const AUTH_URL = process.env['AUTH_BACKEND_URL'] || "http://localhost:4000";

export const Route = createFileRoute("/api/auth/logout")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        try {
          const cookieHeader = request.headers.get("cookie");
          const response = await fetch(`${AUTH_URL}/api/auth/logout`, {
            method: "POST",
            headers: {
              ...(cookieHeader ? { Cookie: cookieHeader } : {}),
            },
          });
          const data = await response.json();
          
          const headers = new Headers();
          headers.set("Content-Type", "application/json");
          const setCookie = response.headers.get("set-cookie");
          if (setCookie) {
            headers.set("Set-Cookie", setCookie);
          }

          return new Response(JSON.stringify(data), {
            status: response.status,
            headers,
          });
        } catch (error) {
          return new Response(JSON.stringify({ error: "Auth service unavailable" }), { status: 503, headers: { "Content-Type": "application/json" } });
        }
      },
    },
  },
});

