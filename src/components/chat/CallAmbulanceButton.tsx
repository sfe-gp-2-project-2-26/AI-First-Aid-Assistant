import { PhoneCall } from "lucide-react";

import { useIsMobileDevice } from "@/hooks/use-mobile-device";

/**
 * Mobile-only emergency call button. Rendered as a tel: link so the phone
 * OS opens the dialer with the configured number. Hidden entirely on
 * desktop, where placing a call is not possible.
 */
export function CallAmbulanceButton() {
  const isMobile = useIsMobileDevice();
  const number = (import.meta.env["VITE_AMBULANCE_NUMBER"] ?? "").trim();

  if (!isMobile || !number) return null;

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
