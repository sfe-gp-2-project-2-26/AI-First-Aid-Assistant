import { useRef, useState } from "react";
import { AlertCircle, CheckCircle2, FileUp, Loader2, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ClinicalApiError, ingestPdf, type IngestionResponse } from "@/lib/clinical-api";

type Status =
  | { kind: "idle" }
  | { kind: "uploading"; name: string }
  | { kind: "done"; result: IngestionResponse }
  | { kind: "error"; message: string };

/**
 * Lets the user add a new clinical PDF to the knowledge base. The file is sent
 * to the backend, which parses and embeds it remotely and stores the vectors.
 */
export function UploadDocumentButton() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  const busy = status.kind === "uploading";

  async function handleFile(file: File | undefined) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setStatus({ kind: "error", message: "Only PDF files can be added to the knowledge base." });
      return;
    }

    setStatus({ kind: "uploading", name: file.name });
    try {
      const result = await ingestPdf(file);
      setStatus({ kind: "done", result });
    } catch (error) {
      setStatus({
        kind: "error",
        message:
          error instanceof ClinicalApiError ? error.message : "Ingestion failed. Please try again.",
      });
    } finally {
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        if (busy) return;
        setOpen(next);
        if (!next) setStatus({ kind: "idle" });
      }}
    >
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="text-muted-foreground" aria-label="Add a clinical document">
          <FileUp className="size-4" />
          <span className="hidden sm:inline">Add document</span>
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add a clinical document</DialogTitle>
          <DialogDescription>
            Upload a PDF guideline. It is parsed and embedded, then indexed so the assistant can cite
            it in future answers.
          </DialogDescription>
        </DialogHeader>

        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="sr-only"
          onChange={(e) => void handleFile(e.target.files?.[0])}
        />

        <Button
          type="button"
          className="w-full"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
        >
          {busy ? <Loader2 className="size-4 animate-spin" /> : <Upload className="size-4" />}
          {busy ? "Processing…" : "Choose PDF"}
        </Button>

        {status.kind === "uploading" && (
          <p className="text-xs text-muted-foreground">
            Parsing and embedding “{status.name}”. Large guidelines can take a few minutes — keep this
            dialog open.
          </p>
        )}

        {status.kind === "done" && (
          <div className="flex items-start gap-2 rounded-md border border-border bg-muted/40 p-3 text-xs">
            <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-primary" />
            <div className="space-y-1">
              <p className="font-medium text-foreground">
                {status.result.status === "already_exists"
                  ? "Already in the knowledge base"
                  : "Document indexed"}
              </p>
              <p className="text-muted-foreground">
                {status.result.filename} — {status.result.chunks_created} chunks,{" "}
                {status.result.vectors_stored} vectors stored.
              </p>
            </div>
          </div>
        )}

        {status.kind === "error" && (
          <div className="flex items-start gap-2 rounded-md border border-destructive/40 bg-destructive/10 p-3 text-xs">
            <AlertCircle className="mt-0.5 size-4 shrink-0 text-destructive" />
            <p className="text-foreground">{status.message}</p>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
