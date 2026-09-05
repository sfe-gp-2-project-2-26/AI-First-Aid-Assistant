import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from map.routes.hospitals import router as hospitals_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Map Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hospitals_router)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "map"}

if __name__ == "__main__":
    uvicorn.run("map.main:app", host="0.0.0.0", port=5000, reload=True)

