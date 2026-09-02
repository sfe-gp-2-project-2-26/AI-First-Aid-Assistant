import { Loader2, Mic, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { getApiBaseUrlOverride } from "@/lib/clinical-api";
import { cn } from "@/lib/utils";

type RecorderState = "idle" | "recording" | "transcribing";

function pickMimeType(): string {
  const candidates = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4"];
  if (typeof MediaRecorder === "undefined") return "";
  return candidates.find((t) => MediaRecorder.isTypeSupported(t)) ?? "";
}

function extensionFor(mimeType: string): string {
  if (mimeType.includes("mp4")) return "mp4";
  if (mimeType.includes("wav")) return "wav";
  return "webm";
}

function formatElapsed(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

/**
 * Microphone button for the chat composer. Click to start recording, click
 * again to stop; the audio is sent to the backend /transcribe endpoint and
 * the returned text is placed into the input for review (never auto-sent).
 */
export function VoiceRecordButton({
  onTranscript,
  onError,
  disabled,
}: {
  onTranscript: (text: string) => void;
  onError: (message: string) => void;
  disabled?: boolean;
}) {
  const [state, setState] = useState<RecorderState>("idle");
  const [elapsed, setElapsed] = useState(0);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      recorderRef.current?.stream.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const startRecording = async () => {
    if (typeof MediaRecorder === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      onError("Voice recording is not supported in this browser.");
      return;
    }

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      onError("Microphone access was denied. Allow microphone permission to use voice input.");
      return;
    }

    const mimeType = pickMimeType();
    const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
    recorderRef.current = recorder;
    chunksRef.current = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };

    recorder.onstop = () => {
      stream.getTracks().forEach((t) => t.stop());
      void sendForTranscription(new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" }), recorder.mimeType);
    };

    recorder.start();
    setElapsed(0);
    timerRef.current = setInterval(() => setElapsed((v) => v + 1), 1000);
    setState("recording");
  };

  const stopRecording = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    recorderRef.current?.stop();
    setState("transcribing");
  };

  const sendForTranscription = async (blob: Blob, mimeType: string) => {
    try {
      if (blob.size < 1024) {
        onError("That recording was too short — please try again.");
        return;
      }

      const body = new FormData();
      body.append("file", blob, `recording.${extensionFor(mimeType)}`);
      const override = getApiBaseUrlOverride();
      if (override) body.append("baseUrl", override);

      let response: Response;
      try {
        response = await fetch("/api/backend/transcribe", { method: "POST", body });
      } catch {
        onError("Could not reach the transcription service. Check your connection.");
        return;
      }

      const payload: unknown = await response.json().catch(() => null);

      if (payload && typeof payload === "object" && "upstreamError" in payload) {
        onError(String((payload as { upstreamError: unknown }).upstreamError));
        return;
      }
      if (!response.ok) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload
            ? String((payload as { detail: unknown }).detail)
            : `Transcription failed (${response.status}).`;
        onError(detail);
        return;
      }
      if (!payload || typeof payload !== "object" || typeof (payload as { text?: unknown }).text !== "string") {
        onError("The transcription service returned an unexpected response.");
        return;
      }

      const text = (payload as { text: string }).text.trim();
      if (!text) {
        onError("Nothing was recognized — please try again or type your question.");
        return;
      }
      onTranscript(text);
    } finally {
      setState("idle");
      setElapsed(0);
    }
  };

  const isRecording = state === "recording";
  const isTranscribing = state === "transcribing";

  return (
    <div className="flex items-center gap-2">
      {isRecording && (
        <span className="flex items-center gap-1.5 text-xs font-medium text-destructive">
          <span className="size-2 animate-pulse rounded-full bg-destructive" />
          {formatElapsed(elapsed)}
        </span>
      )}
      <Button
        type="button"
        variant={isRecording ? "destructive" : "ghost"}
        size="icon"
        disabled={disabled || isTranscribing}
        aria-label={isRecording ? "Stop recording" : isTranscribing ? "Transcribing…" : "Record voice input"}
        title={isRecording ? "Stop recording" : "Record voice input"}
        className={cn(isRecording && "animate-pulse")}
        onClick={() => {
          if (isRecording) {
            stopRecording();
          } else if (state === "idle") {
            void startRecording();
          }
        }}
      >
        {isTranscribing ? (
          <Loader2 className="size-4 animate-spin" />
        ) : isRecording ? (
          <Square className="size-4" />
        ) : (
          <Mic className="size-4" />
        )}
      </Button>
    </div>
  );
}
