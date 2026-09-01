import logging
import math
from typing import List

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/hospitals", tags=["Hospitals"])
logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
SEARCH_RADIUS_KM = 5.0

class HospitalRequest(BaseModel):
    latitude: float
    longitude: float


class FacilityResponse(BaseModel):
    id: int
    name: str
    lat: float
    lon: float
    kind: str
    distanceKm: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    to_rad = lambda d: d * math.pi / 180
    d_lat = to_rad(lat2 - lat1)
    d_lon = to_rad(lon2 - lon1)
    h = (
        math.sin(d_lat / 2) ** 2
        + math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * math.sin(d_lon / 2) ** 2
    )
    return 6371 * 2 * math.asin(math.sqrt(h))


@router.post("/nearest", response_model=List[FacilityResponse])
async def get_nearest_hospitals(request: HospitalRequest):
    lat = request.latitude
    lon = request.longitude

    # Calculate bounding box for Nominatim
    delta_lat = SEARCH_RADIUS_KM / 111.32
    delta_lon = SEARCH_RADIUS_KM / (111.32 * math.cos(math.radians(lat)))
    viewbox = f"{lon - delta_lon},{lat + delta_lat},{lon + delta_lon},{lat - delta_lat}"

    params = {
        "format": "json",
        "amenity": "hospital",
        "lat": lat,
        "lon": lon,
        "viewbox": viewbox,
        "bounded": 1,
        "limit": 10,
    }
    
    # Nominatim requires a valid User-Agent
    headers = {"User-Agent": "MedAid-Clinical-Assistant/2.0"}

    data = None
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(NOMINATIM_URL, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
            else:
                logger.warning(f"Nominatim returned {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Failed to fetch from Nominatim: {e}")

    if data is None:
        raise HTTPException(
            status_code=503,
            detail="Map data service is currently unavailable. Please try again later.",
        )

    facilities = []
    for el in data:
        try:
            f_lat = float(el.get("lat"))
            f_lon = float(el.get("lon"))
        except (TypeError, ValueError):
            continue

        name = el.get("name", "").strip() or "Unnamed medical facility"
        kind = el.get("type", "hospital")
        place_id = el.get("place_id", 0)

        dist = haversine_km(lat, lon, f_lat, f_lon)
        facilities.append(
            FacilityResponse(
                id=place_id,
                name=name,
                lat=f_lat,
                lon=f_lon,
                kind=kind,
                distanceKm=round(dist, 2),
            )
        )

    # Sort by straight-line distance, keep the closest 3
    facilities.sort(key=lambda x: x.distanceKm)
    return facilities[:3]

