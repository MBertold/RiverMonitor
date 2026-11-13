import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import init_db, get_db
from app.api.v1.router import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("rivermonitor")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager: esegue l'inizializzazione del database e di PostGIS all'avvio.
    Include una logica di retry in caso il database stia completando l'avvio.
    """
    logger.info("Avvio del servizio RiverMonitor Backend...")
    max_retries = 10
    retry_delay = 2
    for attempt in range(1, max_retries + 1):
        try:
            init_db()
            break
        except Exception as e:
            logger.warning(f"Database non ancora pronto (tentativo {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                logger.error("Impossibile connettersi al database dopo molteplici tentativi.")
                raise e
            time.sleep(retry_delay)

    yield
    logger.info("Arresto del servizio RiverMonitor Backend...")


app = FastAPI(
    title="RiverMonitor API",
    description="API RESTful ad alte prestazioni per il monitoraggio idrometrico in tempo reale dei fiumi italiani.",
    version="0.1.0",
    lifespan=lifespan
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrazione router API v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Info"])
async def root():
    return {
        "app": "RiverMonitor API",
        "status": "online",
        "version": "0.1.0",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Verifica lo stato di salute del backend e la connettività verso PostgreSQL + PostGIS.
    """
    try:
        # Verifica connettività database e versione di PostGIS
        result = await db.execute(text("SELECT 1;"))
        db_ok = result.scalar() == 1

        postgis_ver_res = await db.execute(text("SELECT PostGIS_Version();"))
        postgis_version = postgis_ver_res.scalar()

        return {
            "status": "healthy",
            "database": "connected" if db_ok else "unreachable",
            "postgis_version": postgis_version,
            "environment": settings.ENVIRONMENT
        }
    except Exception as exc:
        logger.error(f"Health check fallito: {exc}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Servizio temporaneamente non disponibile: {str(exc)}"
        )
