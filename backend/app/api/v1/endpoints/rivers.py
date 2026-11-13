import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.schemas.spatial import (
    RiverFeatureCollection,
    RiverFeature,
    RiverProperties,
    GeoJSONLineString,
)

router = APIRouter()


class RiverSummary(BaseModel):
    id: int
    nome: str
    lunghezza_km: Optional[float] = None
    bacino_nome: Optional[str] = None
    regioni_attraversate: Optional[str] = None
    totale_stazioni: int
    stazioni_in_allerta: int


@router.get("", response_model=List[RiverSummary], summary="Elenco fiumi con statistiche")
async def list_rivers(db: AsyncSession = Depends(get_db)):
    """Restituisce l'elenco dei fiumi censiti con conteggio stazioni e allerte."""
    sql = """
    SELECT 
        tf.id,
        tf.nome,
        tf.lunghezza_km,
        tf.bacino_nome,
        tf.regioni_attraversate,
        COUNT(s.id) AS totale_stazioni,
        COUNT(CASE WHEN m.stato_allerta IN ('giallo', 'arancione', 'rosso') THEN 1 END) AS stazioni_in_allerta
    FROM tracciati_fiumi tf
    LEFT JOIN stazioni s ON s.fiume ILIKE tf.nome AND s.attiva = true
    LEFT JOIN LATERAL (
        SELECT stato_allerta
        FROM misurazioni
        WHERE stazione_id = s.id
        ORDER BY timestamp DESC
        LIMIT 1
    ) m ON true
    GROUP BY tf.id, tf.nome, tf.lunghezza_km, tf.bacino_nome, tf.regioni_attraversate
    ORDER BY tf.lunghezza_km DESC NULLS LAST;
    """
    result = await db.execute(text(sql))
    rows = result.mappings().all()

    return [
        RiverSummary(
            id=r["id"],
            nome=r["nome"],
            lunghezza_km=r["lunghezza_km"],
            bacino_nome=r["bacino_nome"],
            regioni_attraversate=r["regioni_attraversate"],
            totale_stazioni=r["totale_stazioni"],
            stazioni_in_allerta=r["stazioni_in_allerta"]
        )
        for r in rows
    ]


@router.get("/geojson", response_model=RiverFeatureCollection, summary="Tracciati geografici completi dei fiumi (GeoJSON LineString)")
async def get_rivers_geojson(
    nome: Optional[str] = Query(None, description="Filtra per nome fiume (es. 'Po', 'Adige', 'Tevere')"),
    db: AsyncSession = Depends(get_db)
):
    """
    Restituisce i tracciati vettoriali dei corsi d'acqua (LineString EPSG:4326)
    generati tramite PostGIS ST_AsGeoJSON per il rendering ed evidenziazione su Leaflet.
    """
    conditions = []
    params = {}

    if nome:
        conditions.append("tf.nome ILIKE :nome")
        params["nome"] = f"%{nome}%"

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    sql = f"""
    SELECT 
        tf.id,
        tf.nome,
        tf.lunghezza_km,
        tf.bacino_nome,
        tf.regioni_attraversate,
        ST_AsGeoJSON(tf.geometria) AS geojson_geom,
        (SELECT COUNT(*) FROM stazioni WHERE fiume ILIKE tf.nome AND attiva = true) AS stazioni_attive
    FROM tracciati_fiumi tf
    {where_clause}
    ORDER BY tf.lunghezza_km DESC NULLS LAST;
    """

    result = await db.execute(text(sql), params)
    rows = result.mappings().all()

    features = []
    for r in rows:
        geom_dict = json.loads(r["geojson_geom"])
        feature = RiverFeature(
            type="Feature",
            id=r["id"],
            geometry=GeoJSONLineString(
                type="LineString",
                coordinates=geom_dict.get("coordinates", [])
            ),
            properties=RiverProperties(
                id=r["id"],
                nome=r["nome"],
                lunghezza_km=r["lunghezza_km"],
                bacino_nome=r["bacino_nome"],
                regioni_attraversate=r["regioni_attraversate"],
                stazioni_attive=r["stazioni_attive"]
            )
        )
        features.append(feature)

    return RiverFeatureCollection(
        type="FeatureCollection",
        features=features,
        total_count=len(features)
    )
