import { createFileRoute } from "@tanstack/react-router";

const DEFAULT_BASE_URL = "http://localhost:5000";

function envBaseUrl(): string | null {
  const value = process.env["MAP_BACKEND_URL"]?.trim() || process.env["BACKEND_URL"]?.trim();
  return value ? value.replace(/\/+$/, "") : null;
}

type ProxyBody = { latitude?: number; longitude?: number; baseUrl?: string };

export const Route = createFileRoute("/api/backend/hospitals")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        let body: ProxyBody;
        try {
          body = (await request.json()) as ProxyBody;
        } catch {
          return Response.json({ detail: "Invalid request body." }, { status: 400 });
        }

        if (typeof body.latitude !== "number" || typeof body.longitude !== "number") {
          return Response.json(
            { detail: "latitude and longitude must be numbers." },
            { status: 422 },
          );
        }

        const rawBase = typeof body.baseUrl === "string" && body.baseUrl.trim()
          ? body.baseUrl.trim()
          : (envBaseUrl() ?? DEFAULT_BASE_URL);
        const base = rawBase.replace(/\/+$/, "");

        let upstream: Response;
        try {
          upstream = await fetch(`${base}/api/v1/hospitals/nearest`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Accept: "application/json",
              "ngrok-skip-browser-warning": "true",
            },
            body: JSON.stringify({
              latitude: body.latitude,
              longitude: body.longitude,
            }),
          });
        } catch {
          return Response.json({
            upstreamError:
              "Could not reach the clinical backend. Make sure the backend URL is running and correct.",
          });
        }

        const text = await upstream.text();
        const contentType = upstream.headers.get("content-type") ?? "";

        if (!contentType.includes("application/json")) {
          return Response.json({
            upstreamError: `The backend URL did not return a valid API response (status ${upstream.status}). Check the base URL.`,
          });
        }

        if (upstream.status >= 500) {
          return Response.json({
            upstreamError:
              "The hospital locator service is temporarily unavailable. Please try again.",
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

