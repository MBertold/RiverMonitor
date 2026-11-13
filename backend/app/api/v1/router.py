from fastapi import APIRouter
from app.api.v1.endpoints import stations, measurements, regions, rivers, webcams

api_router = APIRouter()

api_router.include_router(stations.router, prefix="/stations", tags=["Stazioni Idrometriche"])
api_router.include_router(measurements.router, tags=["Misurazioni & Serie Storiche"])
api_router.include_router(regions.router, prefix="/regions", tags=["Regioni & Territorio"])
api_router.include_router(rivers.router, prefix="/rivers", tags=["Fiumi & Tracciati Idrografici"])
api_router.include_router(webcams.router, prefix="/webcams", tags=["Webcam Fluviali & Ponti"])
