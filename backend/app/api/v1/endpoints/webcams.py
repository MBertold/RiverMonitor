from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.spatial import (
    WebcamFeatureCollection,
    WebcamFeature,
    GeoJSONPoint,
    WebcamFluvialeProperties,
)

router = APIRouter()


@router.get("", response_model=WebcamFeatureCollection, summary="Elenco webcam fluviali in formato GeoJSON")
async def get_webcams_geojson(
    regione: Optional[str] = Query(None, description="Filtra per regione"),
    fiume: Optional[str] = Query(None, description="Filtra per corso d'acqua"),
    tipo_feed: Optional[str] = Query(None, description="Filtra per tipo feed (jpeg_stream, iframe, link_esterno)"),
    solo_attive: bool = Query(True, description="Escludi webcam disattivate"),
    db: AsyncSession = Depends(get_db)
):
    """
    Restituisce l'elenco delle webcam fluviali geolocalizzate in formato standard GeoJSON.
    Include telecamere panoramiche su ponti storici, webcam meteo con vista fiumi e punti di monitoraggio indipendenti.
    """
    conditions = []
    params = {}

    if solo_attive:
        conditions.append("attiva = true")

    if regione:
        conditions.append("LOWER(regione) = LOWER(:regione)")
        params["regione"] = regione

    if fiume:
        conditions.append("LOWER(corso_dacqua) = LOWER(:fiume)")
        params["fiume"] = fiume

    if tipo_feed:
        conditions.append("tipo_feed = :tipo_feed")
        params["tipo_feed"] = tipo_feed

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = text(f"""
        SELECT 
            id,
            nome,
            corso_dacqua,
            localita,
            regione,
            tipo_feed,
            url_feed,
            url_web,
            provider,
            descrizione,
            attiva,
            ST_X(posizione) AS lon,
            ST_Y(posizione) AS lat
        FROM webcam_fluviali
        {where_clause}
        ORDER BY nome ASC
    """)

    result = await db.execute(query, params)
    rows = result.fetchall()

    features = []
    for r in rows:
        feature = WebcamFeature(
            type="Feature",
            id=r.id,
            geometry=GeoJSONPoint(
                type="Point",
                coordinates=[round(float(r.lon), 6), round(float(r.lat), 6)]
            ),
            properties=WebcamFluvialeProperties(
                id=r.id,
                nome=r.nome,
                corso_dacqua=r.corso_dacqua,
                localita=r.localita,
                regione=r.regione,
                tipo_feed=r.tipo_feed,
                url_feed=r.url_feed,
                url_web=r.url_web,
                provider=r.provider,
                descrizione=r.descrizione,
                attiva=r.attiva
            )
        )
        features.append(feature)

    return WebcamFeatureCollection(
        type="FeatureCollection",
        features=features,
        total_count=len(features)
    )


@router.get("/{webcam_id}", response_model=WebcamFeature, summary="Dettaglio singola webcam fluviale")
async def get_webcam_by_id(
    webcam_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Restituisce la singola webcam fluviale dato il suo ID univoco."""
    query = text("""
        SELECT 
            id,
            nome,
            corso_dacqua,
            localita,
            regione,
            tipo_feed,
            url_feed,
            url_web,
            provider,
            descrizione,
            attiva,
            ST_X(posizione) AS lon,
            ST_Y(posizione) AS lat
        FROM webcam_fluviali
        WHERE id = :id
    """)

    result = await db.execute(query, {"id": webcam_id})
    r = result.fetchone()

    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Webcam fluviale con ID {webcam_id} non trovata."
        )

    return WebcamFeature(
        type="Feature",
        id=r.id,
        geometry=GeoJSONPoint(
            type="Point",
            coordinates=[round(float(r.lon), 6), round(float(r.lat), 6)]
        ),
        properties=WebcamFluvialeProperties(
            id=r.id,
            nome=r.nome,
            corso_dacqua=r.corso_dacqua,
            localita=r.localita,
            regione=r.regione,
            tipo_feed=r.tipo_feed,
            url_feed=r.url_feed,
            url_web=r.url_web,
            provider=r.provider,
            descrizione=r.descrizione,
            attiva=r.attiva
        )
    )
