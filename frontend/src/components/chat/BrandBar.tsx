import { Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { MapPin, Settings2 } from "lucide-react";
import type { ReactNode } from "react";

import logo from "@/assets/logo.png";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { DEFAULT_API_BASE_URL, getApiBaseUrl, setApiBaseUrl } from "@/lib/clinical-api";

export function BrandBar({ actions }: { actions?: ReactNode }) {
  const [baseUrl, setBaseUrl] = useState(DEFAULT_API_BASE_URL);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setBaseUrl(getApiBaseUrl());
  }, []);

  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/85 backdrop-blur">
      <div className="mx-auto flex h-14 w-full max-w-4xl items-center gap-2 px-4 sm:gap-3 sm:px-6">
        <img src={logo} alt="MedAid Clinical Assistant logo" width={28} height={28} className="size-7 shrink-0" />
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold tracking-tight text-foreground">
            MedAid Clinical Assistant
          </p>
          <p className="hidden truncate text-[11px] text-muted-foreground sm:block">
            Evidence-based first-aid guidance
          </p>
        </div>

        <div className="ml-auto flex items-center gap-1">
          {actions}
          <Button asChild variant="ghost" size="sm" className="text-muted-foreground">
            <Link to="/hospitals" aria-label="Find nearby hospitals">
              <MapPin className="size-4" />
              <span className="hidden sm:inline">Hospitals</span>
            </Link>
          </Button>
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Backend settings">
                <Settings2 className="size-4 text-muted-foreground" />
              </Button>
            </PopoverTrigger>
            <PopoverContent align="end" className="w-96">
              <div className="space-y-3">
                <div className="space-y-1">
                  <Label htmlFor="base-url" className="text-xs font-semibold">
                    Backend base URL
                  </Label>
                  <p className="text-[11px] text-muted-foreground">
                    Configure the backend base URL (default: http://localhost:3000).
                  </p>
                </div>
                <Input
                  id="base-url"
                  value={baseUrl}
                  onChange={(e) => {
                    setBaseUrl(e.target.value);
                    setSaved(false);
                  }}
                  placeholder={DEFAULT_API_BASE_URL}
                  spellCheck={false}
                />
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    onClick={() => {
                      setApiBaseUrl(baseUrl);
                      setBaseUrl(getApiBaseUrl());
                      setSaved(true);
                    }}
                  >
                    Save
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setApiBaseUrl("");
                      setBaseUrl(DEFAULT_API_BASE_URL);
                      setSaved(true);
                    }}
                  >
                    Reset
                  </Button>
                  {saved && <span className="text-xs text-primary">Saved</span>}
                </div>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </div>
    </header>
  );
}
