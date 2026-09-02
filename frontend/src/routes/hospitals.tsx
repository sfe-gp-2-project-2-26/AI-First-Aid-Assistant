import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowLeft, Loader2, MapPin, RefreshCw } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import type { Map as LeafletMap } from "leaflet";

import logo from "@/assets/logo.png";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/hospitals")({
  head: () => ({
    meta: [
      { title: "Nearest Hospitals — MedAid Clinical Assistant" },
      {
        name: "description",
        content:
          "Locate the five nearest hospitals and medical facilities to your current position, with driving routes, distances, and estimated travel times.",
      },
      { property: "og:title", content: "Nearest Hospitals — MedAid Clinical Assistant" },
      {
        property: "og:description",
        content: "Find the closest hospitals to your location with routes and travel times.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: HospitalsPage,
});

interface Facility {
  id: number;
  name: string;
  lat: number;
  lon: number;
  kind: string;
}

interface RouteInfo {
  distanceKm: number;
  durationMin: number;
  geometry: [number, number][]; // [lat, lon] pairs
}

interface FacilityResult extends Facility {
  route: RouteInfo | null;
}

const OSRM_URL = "https://router.project-osrm.org/route/v1/driving";

async function fetchFacilities(lat: number, lon: number): Promise<Facility[]> {
  const response = await fetch("/api/backend/hospitals", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ latitude: lat, longitude: lon }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.upstreamError || err.detail || `Map data service returned ${response.status}.`);
  }

  return response.json();
}

async function fetchRoute(
  from: { lat: number; lon: number },
  to: { lat: number; lon: number },
): Promise<RouteInfo | null> {
  try {
    const url = `${OSRM_URL}/${from.lon},${from.lat};${to.lon},${to.lat}?overview=full&geometries=geojson`;
    const response = await fetch(url);
    if (!response.ok) return null;
    const data: {
      routes?: Array<{
        distance: number;
        duration: number;
        geometry: { coordinates: [number, number][] };
      }>;
    } = await response.json();
    const route = data.routes?.[0];
    if (!route) return null;
    return {
      distanceKm: route.distance / 1000,
      durationMin: route.duration / 60,
      // GeoJSON is [lon, lat]; Leaflet wants [lat, lon].
      geometry: route.geometry.coordinates.map(([lon, lat]) => [lat, lon]),
    };
  } catch {
    return null;
  }
}

function formatDuration(minutes: number): string {
  if (minutes < 60) return `${Math.round(minutes)} min`;
  const h = Math.floor(minutes / 60);
  const m = Math.round(minutes % 60);
  return `${h} h ${m} min`;
}

function HospitalsPage() {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<LeafletMap | null>(null);
  const [status, setStatus] = useState<"locating" | "loading" | "ready" | "error">("locating");
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<FacilityResult[]>([]);
  const [selected, setSelected] = useState<number | null>(null);

  const locate = useCallback(async () => {
    setStatus("locating");
    setError(null);
    setResults([]);
    setSelected(null);

    const position = await new Promise<GeolocationPosition | null>((resolve) => {
      if (!navigator.geolocation) {
        resolve(null);
        return;
      }
      navigator.geolocation.getCurrentPosition(resolve, () => resolve(null), {
        enableHighAccuracy: true,
        timeout: 15000,
      });
    });

    if (!position) {
      setStatus("error");
      setError(
        "Location access is unavailable or was denied. Allow location permission and try again.",
      );
      return;
    }

    const origin = { lat: position.coords.latitude, lon: position.coords.longitude };
    setStatus("loading");

    try {
      const facilities = await fetchFacilities(origin.lat, origin.lon);
      if (facilities.length === 0) {
        setStatus("error");
        setError("No hospitals or clinics found within 8 km of your location.");
        return;
      }

      const routed = await Promise.all(
        facilities.map(async (f) => ({ ...f, route: await fetchRoute(origin, f) })),
      );
      // Order by actual driving time when routes exist.
      routed.sort(
        (a, b) =>
          (a.route?.durationMin ?? Number.POSITIVE_INFINITY) -
          (b.route?.durationMin ?? Number.POSITIVE_INFINITY),
      );

      setResults(routed);
      setStatus("ready");
      renderMap(origin, routed);
    } catch (e) {
      setStatus("error");
      setError(e instanceof Error ? e.message : "Could not load nearby medical facilities.");
    }
  }, []);

  const renderMap = useCallback(
    async (origin: { lat: number; lon: number }, facilities: FacilityResult[]) => {
      if (!mapContainerRef.current) return;
      const L = await import("leaflet");
      await import("leaflet/dist/leaflet.css");

      mapRef.current?.remove();
      const map = L.map(mapContainerRef.current).setView([origin.lat, origin.lon], 14);
      mapRef.current = map;

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
      }).addTo(map);

      // User position marker.
      L.circleMarker([origin.lat, origin.lon], {
        radius: 9,
        color: "hsl(217 91% 60%)",
        weight: 3,
        fillColor: "hsl(217 91% 60%)",
        fillOpacity: 0.9,
      })
        .addTo(map)
        .bindTooltip("You are here", { direction: "top" });

      const bounds = L.latLngBounds([[origin.lat, origin.lon]]);

      facilities.forEach((facility, index) => {
        const isNearest = index === 0;
        const route = facility.route;

        L.marker([facility.lat, facility.lon])
          .addTo(map)
          .bindPopup(
            `<strong>${facility.name}</strong><br/>${facility.kind}${route ? `<br/>${route.distanceKm.toFixed(1)} km · ~${formatDuration(route.durationMin)}` : ""}`,
          );
        bounds.extend([facility.lat, facility.lon]);

        if (route && route.geometry.length > 1) {
          const color = isNearest ? "#16a34a" : "#dc2626";
          L.polyline(route.geometry, {
            color,
            weight: isNearest ? 5 : 3,
            opacity: isNearest ? 0.9 : 0.6,
          }).addTo(map);

          // Distance/time label at the route midpoint.
          const mid = route.geometry[Math.floor(route.geometry.length / 2)];
          if (mid) {
            L.tooltip({
              permanent: true,
              direction: "top",
              className: "route-label",
            })
              .setLatLng(mid)
              .setContent(
                `${route.distanceKm.toFixed(1)} km · ${formatDuration(route.durationMin)}`,
              )
              .addTo(map);
          }
        }
      });

      map.fitBounds(bounds.pad(0.15));
    },
    [],
  );

  useEffect(() => {
    void locate();
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [locate]);

  return (
    <div className="flex min-h-dvh flex-col bg-background">
      <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur">
        <div className="mx-auto flex h-14 w-full max-w-4xl items-center gap-3 px-4 sm:px-6">
          <Button asChild variant="ghost" size="icon" aria-label="Back to chat">
            <Link to="/">
              <ArrowLeft className="size-4" />
            </Link>
          </Button>
          <img src={logo} alt="MedAid logo" width={24} height={24} className="size-6" />
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold tracking-tight text-foreground">
              Nearest Hospitals
            </p>
            <p className="truncate text-[11px] text-muted-foreground">
              Closest medical facilities to your current location
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="ml-auto text-muted-foreground"
            disabled={status === "locating" || status === "loading"}
            onClick={() => void locate()}
          >
            <RefreshCw
              className={cn("size-4", (status === "locating" || status === "loading") && "animate-spin")}
            />
            <span className="hidden sm:inline">Refresh</span>
          </Button>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-4 px-4 py-4 sm:px-6">
        {(status === "locating" || status === "loading") && (
          <div className="flex flex-1 items-center justify-center gap-3 py-24 text-sm text-muted-foreground">
            <Loader2 className="size-5 animate-spin" />
            {status === "locating" ? "Locating you…" : "Finding nearby hospitals and routes…"}
          </div>
        )}

        {status === "error" && (
          <div className="flex flex-1 flex-col items-center justify-center gap-4 py-24 text-center">
            <MapPin className="size-8 text-muted-foreground" />
            <p className="max-w-sm text-sm text-muted-foreground">{error}</p>
            <Button variant="outline" size="sm" onClick={() => void locate()}>
              Try again
            </Button>
          </div>
        )}

        <div
          ref={mapContainerRef}
          aria-label="Map showing your location and nearby hospitals"
          className={cn(
            "h-[55vh] w-full rounded-2xl border border-border shadow-[var(--shadow-card)] sm:h-[60vh]",
            status !== "ready" && "hidden",
          )}
        />

        {status === "ready" && (
          <ol className="space-y-2 pb-6">
            {results.map((facility, index) => (
              <li key={facility.id}>
                <button
                  type="button"
                  onClick={() => {
                    setSelected(facility.id);
                    mapRef.current?.setView([facility.lat, facility.lon], 16);
                  }}
                  className={cn(
                    "flex w-full items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 text-left shadow-[var(--shadow-soft)] transition-colors",
                    selected === facility.id && "border-primary",
                  )}
                >
                  <span
                    className={cn(
                      "flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white",
                      index === 0 ? "bg-green-600" : "bg-red-600",
                    )}
                  >
                    {index + 1}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-sm font-medium text-foreground">
                      {facility.name}
                    </span>
                    <span className="block text-xs capitalize text-muted-foreground">
                      {facility.kind}
                    </span>
                  </span>
                  <span className="shrink-0 text-right text-xs text-muted-foreground">
                    {facility.route ? (
                      <>
                        <span className="block font-medium text-foreground">
                          {facility.route.distanceKm.toFixed(1)} km
                        </span>
                        <span>~{formatDuration(facility.route.durationMin)}</span>
                      </>
                    ) : (
                      "No route"
                    )}
                  </span>
                </button>
              </li>
            ))}
          </ol>
        )}
      </main>
    </div>
  );
}
