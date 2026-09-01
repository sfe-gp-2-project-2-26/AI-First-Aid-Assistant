import { createFileRoute } from "@tanstack/react-router";

const DEFAULT_BASE_URL = "http://localhost:3000";
const MAX_PDF_BYTES = 50 * 1024 * 1024;

/** Server-side default backend URL (e.g. an ngrok tunnel or the compose service). */
function envBaseUrl(): string | null {
  const value = process.env["BACKEND_URL"]?.trim();
  return value ? value.replace(/\/+$/, "") : null;
}

/**
 * Forwards an uploaded clinical PDF to the backend's ingestion pipeline
 * (POST /api/v1/ingestion/upload). The backend then delegates parsing and
 * embedding to the remote Colab service and stores the vectors in Qdrant.
 */
export const Route = createFileRoute("/api/backend/ingest")({
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
          return Response.json({ detail: "No PDF file provided." }, { status: 422 });
        }
        if (!file.name.toLowerCase().endsWith(".pdf")) {
          return Response.json({ detail: "Only PDF files can be ingested." }, { status: 415 });
        }
        if (file.size > MAX_PDF_BYTES) {
          return Response.json({ detail: "PDF is larger than the 50 MB limit." }, { status: 413 });
        }

        const override = incoming.get("baseUrl");
        const base = (
          typeof override === "string" && override.trim() ? override.trim() : (envBaseUrl() ?? DEFAULT_BASE_URL)
        ).replace(/\/+$/, "");

        const upstreamBody = new FormData();
        upstreamBody.append("file", file, file.name);

        let upstream: Response;
        try {
          upstream = await fetch(`${base}/api/v1/ingestion/upload`, {
            method: "POST",
            headers: { "ngrok-skip-browser-warning": "true" },
            body: upstreamBody,
          });
        } catch {
          return Response.json(
            { detail: "Could not reach the backend. Make sure it is running." },
            { status: 502 },
          );
        }

        const text = await upstream.text();
        const contentType = upstream.headers.get("content-type") ?? "";
        if (!contentType.includes("application/json")) {
          return Response.json(
            { detail: `The backend did not return a valid response (status ${upstream.status}).` },
            { status: 502 },
          );
        }

        return new Response(text, {
          status: upstream.status,
          headers: { "Content-Type": "application/json" },
        });
      },
    },
  },
});
