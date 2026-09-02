import { createFileRoute } from "@tanstack/react-router";

const DEFAULT_BASE_URL = "http://localhost:3000";

/** Server-side default backend URL (e.g. an ngrok tunnel or the compose service). */
function envBaseUrl(): string | null {
  const value = process.env["BACKEND_URL"]?.trim();
  return value ? value.replace(/\/+$/, "") : null;
}

/**
 * Forwards a recorded audio file to the backend's POST /transcribe endpoint
 * (multipart/form-data, field name "file"). Proxied server-side to avoid
 * CORS and the ngrok browser-warning interstitial.
 */
export const Route = createFileRoute("/api/backend/transcribe")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        let incoming: FormData;
        try {
          incoming = await request.formData();
        } catch {
          return Response.json({ detail: "Expected multipart/form-data." }, { status: 400 });
        }

        const file = incoming.get("file");
        if (!(file instanceof File) || file.size === 0) {
          return Response.json({ detail: "No audio file provided." }, { status: 422 });
        }
        if (file.size > 25 * 1024 * 1024) {
          return Response.json({ detail: "Recording is too large." }, { status: 413 });
        }

        const override = incoming.get("baseUrl");
        const base = (
          typeof override === "string" && override.trim() ? override.trim() : (envBaseUrl() ?? DEFAULT_BASE_URL)
        ).replace(/\/+$/, "");

        const upstreamBody = new FormData();
        upstreamBody.append("file", file, file.name || "recording.webm");

        let upstream: Response;
        try {
          upstream = await fetch(`${base}/transcribe`, {
            method: "POST",
            headers: { "ngrok-skip-browser-warning": "true" },
            body: upstreamBody,
          });
        } catch {
          return Response.json({
            upstreamError:
              "Could not reach the transcription service. Make sure the backend is running.",
          });
        }

        const text = await upstream.text();
        const contentType = upstream.headers.get("content-type") ?? "";
        if (!contentType.includes("application/json")) {
          return Response.json({
            upstreamError: `The transcription service did not return a valid response (status ${upstream.status}).`,
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
