from typing import List
from pydantic import BaseModel

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

