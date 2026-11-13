from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.spatial import (
    GeoJSONFeatureCollection,
    GeoJSONFeature,
    GeoJSONPoint,
    StazioneProperties,
    UltimaMisurazioneSummary,
)

router = APIRouter()


def calcola_stato_allerta(
    livello: Optional[float],
    gialla: Optional[float],
    arancione: Optional[float],
    rossa: Optional[float],
    stato_registrato: Optional[str] = None
) -> str:
    """Calcola lo stato di allerta in base alle soglie idrometriche ufficiali."""
    if livello is None:
        return stato_registrato or "verde"
    if rossa is not None and livello >= rossa:
        return "rosso"
    if arancione is not None and livello >= arancione:
        return "arancione"
    if gialla is not None and livello >= gialla:
        return "giallo"
    return "verde"


@router.get("", response_model=GeoJSONFeatureCollection, summary="Recupera stazioni in formato GeoJSON")
async def get_stations_geojson(
    regione_id: Optional[int] = Query(None, description="Filtra per ID regione"),
    codice_istat: Optional[str] = Query(None, max_length=2, description="Filtra per codice ISTAT regione (es. '01')"),
    fiume: Optional[str] = Query(None, description="Filtra per nome fiume/corso d'acqua"),
    stato_allerta: Optional[str] = Query(None, description="Filtra per stato allerta: verde, giallo, arancione, rosso"),
    bbox: Optional[str] = Query(
        None,
        description="Bounding Box nel formato: min_lon,min_lat,max_lon,max_lat (es: 7.0,44.0,10.0,46.0)"
    ),
    solo_attive: bool = Query(True, description="Escludi stazioni disattivate"),
    db: AsyncSession = Depends(get_db)
):
    """
    Restituisce l'elenco delle stazioni idrometriche in formato standard **GeoJSON FeatureCollection** (RFC 7946).
    Supporta filtri territoriali (regione/codice ISTAT), per corso d'acqua, stato di allerta
    e Bounding Box per viewport dinamico della mappa Leaflet/MapLibre.
    """
    conditions = []
    params = {}

    if solo_attive:
        conditions.append("s.attiva = true")

    if regione_id is not None:
        conditions.append("s.regione_id = :regione_id")
        params["regione_id"] = regione_id

    if codice_istat is not None:
        conditions.append("r.codice_istat = :codice_istat")
        params["codice_istat"] = codice_istat

    if fiume is not None:
        conditions.append("s.fiume ILIKE :fiume")
        params["fiume"] = f"%{fiume}%"

    # Gestione Bounding Box con PostGIS ST_MakeEnvelope
    if bbox is not None:
        try:
            coords = [float(c.strip()) for c in bbox.split(",")]
            if len(coords) != 4:
                raise ValueError("BBox deve contenere esattamente 4 coordinate: min_lon,min_lat,max_lon,max_lat")
            min_lon, min_lat, max_lon, max_lat = coords
            conditions.append("ST_Intersects(s.posizione, ST_MakeEnvelope(:min_lon, :min_lat, :max_lon, :max_lat, 4326))")
            params.update({
                "min_lon": min_lon,
                "min_lat": min_lat,
                "max_lon": max_lon,
                "max_lat": max_lat,
            })
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato BBox non valido: {str(e)}"
            )

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    sql = f"""
    SELECT 
        s.id,
        s.codice_stazione,
        s.nome,
        s.fiume,
        s.quota_zero_idrometrico,
        s.soglia_allerta_gialla,
        s.soglia_allerta_arancione,
        s.soglia_allerta_rossa,
        s.fonte_dati,
        s.attiva,
        s.webcam_url,
        ST_X(s.posizione) AS lon,
        ST_Y(s.posizione) AS lat,
        r.nome AS regione_nome,
        b.nome AS bacino_nome,
        m.timestamp AS m_timestamp,
        m.livello_idrometrico AS m_livello,
        m.portata AS m_portata,
        m.stato_allerta AS m_stato_allerta
    FROM stazioni s
    LEFT JOIN regioni r ON s.regione_id = r.id
    LEFT JOIN bacini_idrografici b ON s.bacino_id = b.id
    LEFT JOIN LATERAL (
        SELECT timestamp, livello_idrometrico, portata, stato_allerta
        FROM misurazioni
        WHERE stazione_id = s.id
        ORDER BY timestamp DESC
        LIMIT 1
    ) m ON true
    WHERE {where_clause}
    ORDER BY s.nome ASC;
    """

    result = await db.execute(text(sql), params)
    rows = result.mappings().all()

    features = []
    for row in rows:
        stato_allerta_calc = calcola_stato_allerta(
            livello=row["m_livello"],
            gialla=row["soglia_allerta_gialla"],
            arancione=row["soglia_allerta_arancione"],
            rossa=row["soglia_allerta_rossa"],
            stato_registrato=row["m_stato_allerta"]
        )

        # Se è specificato il filtro per stato allerta, filtra in memoria o nel risultato
        if stato_allerta and stato_allerta_calc != stato_allerta.lower():
            continue

        ultima_misurazione = None
        if row["m_timestamp"]:
            ultima_misurazione = UltimaMisurazioneSummary(
                timestamp=row["m_timestamp"].isoformat(),
                livello_idrometrico=row["m_livello"],
                portata=row["m_portata"],
                stato_allerta=stato_allerta_calc
            )

        properties = StazioneProperties(
            id=row["id"],
            codice_stazione=row["codice_stazione"],
            nome=row["nome"],
            fiume=row["fiume"],
            quota_zero_idrometrico=row["quota_zero_idrometrico"],
            soglia_allerta_gialla=row["soglia_allerta_gialla"],
            soglia_allerta_arancione=row["soglia_allerta_arancione"],
            soglia_allerta_rossa=row["soglia_allerta_rossa"],
            fonte_dati=row["fonte_dati"],
            attiva=row["attiva"],
            webcam_url=row["webcam_url"],
            regione_nome=row["regione_nome"],
            bacino_nome=row["bacino_nome"],
            ultima_misurazione=ultima_misurazione
        )

        feature = GeoJSONFeature(
            type="Feature",
            id=row["id"],
            geometry=GeoJSONPoint(
                type="Point",
                coordinates=[row["lon"], row["lat"]]
            ),
            properties=properties
        )
        features.append(feature)

    return GeoJSONFeatureCollection(
        type="FeatureCollection",
        features=features,
        total_count=len(features)
    )


@router.get("/{station_id}", response_model=GeoJSONFeature, summary="Dettaglio singola stazione")
async def get_station_by_id(station_id: int, db: AsyncSession = Depends(get_db)):
    """Recupera le proprietà e l'ultima misurazione di una singola stazione."""
    sql = """
    SELECT 
        s.id,
        s.codice_stazione,
        s.nome,
        s.fiume,
        s.quota_zero_idrometrico,
        s.soglia_allerta_gialla,
        s.soglia_allerta_arancione,
        s.soglia_allerta_rossa,
        s.fonte_dati,
        s.attiva,
        s.webcam_url,
        ST_X(s.posizione) AS lon,
        ST_Y(s.posizione) AS lat,
        r.nome AS regione_nome,
        b.nome AS bacino_nome,
        m.timestamp AS m_timestamp,
        m.livello_idrometrico AS m_livello,
        m.portata AS m_portata,
        m.stato_allerta AS m_stato_allerta
    FROM stazioni s
    LEFT JOIN regioni r ON s.regione_id = r.id
    LEFT JOIN bacini_idrografici b ON s.bacino_id = b.id
    LEFT JOIN LATERAL (
        SELECT timestamp, livello_idrometrico, portata, stato_allerta
        FROM misurazioni
        WHERE stazione_id = s.id
        ORDER BY timestamp DESC
        LIMIT 1
    ) m ON true
    WHERE s.id = :station_id;
    """
    result = await db.execute(text(sql), {"station_id": station_id})
    row = result.mappings().first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stazione con ID {station_id} non trovata"
        )

    stato_allerta_calc = calcola_stato_allerta(
        livello=row["m_livello"],
        gialla=row["soglia_allerta_gialla"],
        arancione=row["soglia_allerta_arancione"],
        rossa=row["soglia_allerta_rossa"],
        stato_registrato=row["m_stato_allerta"]
    )

    ultima_misurazione = None
    if row["m_timestamp"]:
        ultima_misurazione = UltimaMisurazioneSummary(
            timestamp=row["m_timestamp"].isoformat(),
            livello_idrometrico=row["m_livello"],
            portata=row["m_portata"],
            stato_allerta=stato_allerta_calc
        )

    properties = StazioneProperties(
        id=row["id"],
        codice_stazione=row["codice_stazione"],
        nome=row["nome"],
        fiume=row["fiume"],
        quota_zero_idrometrico=row["quota_zero_idrometrico"],
        soglia_allerta_gialla=row["soglia_allerta_gialla"],
        soglia_allerta_arancione=row["soglia_allerta_arancione"],
        soglia_allerta_rossa=row["soglia_allerta_rossa"],
        fonte_dati=row["fonte_dati"],
        attiva=row["attiva"],
        webcam_url=row["webcam_url"],
        regione_nome=row["regione_nome"],
        bacino_nome=row["bacino_nome"],
        ultima_misurazione=ultima_misurazione
    )

    return GeoJSONFeature(
        type="Feature",
        id=row["id"],
        geometry=GeoJSONPoint(
            type="Point",
            coordinates=[row["lon"], row["lat"]]
        ),
        properties=properties
    )
