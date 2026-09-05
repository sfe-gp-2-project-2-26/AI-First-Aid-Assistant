import logging
from fastapi import HTTPException
from typing import Optional

from map.services.hospital_service import HospitalService
from map.schemas.hospitals import HospitalRequest, FacilityResponse
from typing import List

logger = logging.getLogger(__name__)

class HospitalController:
    """Controller for hospital-related endpoints."""
    
    def __init__(self, hospital_service: Optional[HospitalService] = None):
        self.hospital_service = hospital_service or HospitalService()
        
    async def get_nearest(self, request: HospitalRequest) -> List[FacilityResponse]:
        try:
            return await self.hospital_service.get_nearest_hospitals(request)
        except RuntimeError as re:
            logger.error(f"Hospital service error: {re}")
            raise HTTPException(status_code=503, detail=str(re) + " Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected hospital search failure: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error while searching for hospitals.")

