from typing import List
from fastapi import APIRouter, Depends

from map.controllers.hospital_controller import HospitalController
from map.schemas.hospitals import HospitalRequest, FacilityResponse

router = APIRouter(prefix="/api/v1/hospitals", tags=["Hospitals"])

def get_controller() -> HospitalController:
    return HospitalController()

@router.post("/nearest", response_model=List[FacilityResponse])
async def get_nearest_hospitals(
    request: HospitalRequest,
    controller: HospitalController = Depends(get_controller)
):
    """Find the 3 nearest medical facilities/hospitals based on coordinates."""
    return await controller.get_nearest(request)
