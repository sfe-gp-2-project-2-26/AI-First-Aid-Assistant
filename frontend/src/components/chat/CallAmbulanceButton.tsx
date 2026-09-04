import { PhoneCall } from "lucide-react";

/**
 * Emergency call button. Rendered as a tel: link so the OS opens the
 * appropriate app:
 *  - Mobile  → opens the phone dialer directly.
 *  - Windows → triggers the system "Open with" prompt (e.g. Phone Link).
 *  - Other desktops → browser / OS handles the tel: protocol as configured.
 */
export function CallAmbulanceButton() {
  const number = (import.meta.env["VITE_AMBULANCE_NUMBER"] ?? "").trim();

  if (!number) return null;

  return (
    <a
      href={`tel:${number}`}
      aria-label={`Call an ambulance now at ${number}`}
      className="inline-flex items-center gap-2 rounded-full bg-destructive px-4 py-2 text-sm font-semibold text-destructive-foreground shadow-[var(--shadow-soft)] transition-transform active:scale-95"
    >
      <PhoneCall className="size-4 animate-pulse" />
      Call Ambulance
    </a>
  );
}
