import { useEffect, useState } from "react";

/**
 * Detects a phone-like device: coarse pointer (touch) + narrow viewport.
 * Uses media queries rather than user-agent sniffing so it stays correct
 * when a window is resized or a device rotates.
 */
export function useIsMobileDevice() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const coarse = window.matchMedia("(pointer: coarse)");
    const narrow = window.matchMedia("(max-width: 768px)");
    const update = () => setIsMobile(coarse.matches && narrow.matches);
    update();
    coarse.addEventListener("change", update);
    narrow.addEventListener("change", update);
    return () => {
      coarse.removeEventListener("change", update);
      narrow.removeEventListener("change", update);
    };
  }, []);

  return isMobile;
}
