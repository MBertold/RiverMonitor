from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.measurement import (
    StationTimeSeriesResponse,
    TimeSeriesDataPoint,
    TimeSeriesThresholds,
    TimeSeriesStats,
    MisurazioneBatchItem,
)
from app.api.v1.endpoints.stations import calcola_stato_allerta

router = APIRouter()


@router.get(
    "/stations/{station_id}/measurements",
    response_model=StationTimeSeriesResponse,
    summary="Serie storica idrometrica per stazione"
)
async def get_station_timeseries(
    station_id: int,
    hours: int = Query(48, ge=1, le=720, description="Numero di ore passate da visualizzare (default: 48)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Restituisce la serie storica idrometrica cronologica delle ultime N ore per la stazione richiesta.
    Include soglie di allerta (per tracciare le linee guida nei grafici Recharts/Chart.js)
    e statistiche calcolate (min, max, media, variazione 24h, trend).
    """
    # 1. Recupera metadati della stazione
    station_sql = """
    SELECT 
        s.id, s.codice_stazione, s.nome, s.fiume,
        s.quota_zero_idrometrico, s.soglia_allerta_gialla,
        s.soglia_allerta_arancione, s.soglia_allerta_rossa,
        r.nome AS regione_nome
    FROM stazioni s
    LEFT JOIN regioni r ON s.regione_id = r.id
    WHERE s.id = :station_id;
    """
    st_res = await db.execute(text(station_sql), {"station_id": station_id})
    station = st_res.mappings().first()

    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stazione con ID {station_id} non trovata"
        )

    # 2. Recupera le misurazioni nelle ultime N ore
    start_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    measurements_sql = """
    SELECT 
        timestamp,
        livello_idrometrico,
        portata,
        stato_allerta
    FROM misurazioni
    WHERE stazione_id = :station_id AND timestamp >= :start_time
    ORDER BY timestamp ASC;
    """
    meas_res = await db.execute(
        text(measurements_sql),
        {"station_id": station_id, "start_time": start_time}
    )
    rows = meas_res.mappings().all()

    # 3. Costruisci serie e calcola statistiche
    serie_storica: List[TimeSeriesDataPoint] = []
    livelli_validi: List[float] = []

    for r in rows:
        liv = r["livello_idrometrico"]
        if liv is not None:
            livelli_validi.append(liv)

        alert_status = calcola_stato_allerta(
            livello=liv,
            gialla=station["soglia_allerta_gialla"],
            arancione=station["soglia_allerta_arancione"],
            rossa=station["soglia_allerta_rossa"],
            stato_registrato=r["stato_allerta"]
        )

        serie_storica.append(TimeSeriesDataPoint(
            timestamp=r["timestamp"],
            livello=liv,
            portata=r["portata"],
            stato_allerta=alert_status
        ))

    # Statistiche riassuntive
    min_l = min(livelli_validi) if livelli_validi else None
    max_l = max(livelli_validi) if livelli_validi else None
    avg_l = round(sum(livelli_validi) / len(livelli_validi), 2) if livelli_validi else None
    cur_l = livelli_validi[-1] if livelli_validi else None

    # Calcolo variazione 24h e trend
    delta_24h = None
    trend = "stazionario"
    if len(livelli_validi) >= 2:
        diff = livelli_validi[-1] - livelli_validi[0]
        delta_24h = round(diff, 2)
        if diff > 0.05:
            trend = "in_aumento"
        elif diff < -0.05:
            trend = "in_calo"

    stats = TimeSeriesStats(
        min_livello=min_l,
        max_livello=max_l,
        avg_livello=avg_l,
        current_livello=cur_l,
        delta_livello_24h=delta_24h,
        trend=trend
    )

    thresholds = TimeSeriesThresholds(
        gialla=station["soglia_allerta_gialla"],
        arancione=station["soglia_allerta_arancione"],
        rossa=station["soglia_allerta_rossa"],
        zero_idrometrico=station["quota_zero_idrometrico"]
    )

    return StationTimeSeriesResponse(
        stazione_id=station["id"],
        codice_stazione=station["codice_stazione"],
        nome=station["nome"],
        fiume=station["fiume"],
        regione=station["regione_nome"],
        soglie=thresholds,
        stats=stats,
        serie_storica=serie_storica
    )


@router.post(
    "/measurements/batch",
    status_code=status.HTTP_201_CREATED,
    summary="Ingestione dati batch per worker ETL (Upsert)"
)
async def ingest_batch_measurements(
    items: List[MisurazioneBatchItem],
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint utilizzato dai worker ETL per inviare rilevazioni batch.
    Esegue un **UPSERT** basato su `(stazione_id, timestamp)` per garantire l'idempotenza.
    """
    if not items:
        return {"inserted_or_updated": 0}

    # Risoluzione id stazioni dai codici stazione
    codici = list({item.codice_stazione for item in items})
    sql_stazioni = "SELECT id, codice_stazione FROM stazioni WHERE codice_stazione = ANY(:codici);"
    res = await db.execute(text(sql_stazioni), {"codici": codici})
    codice_to_id = {row["codice_stazione"]: row["id"] for row in res.mappings().all()}

    upsert_sql = """
    INSERT INTO misurazioni (stazione_id, timestamp, livello_idrometrico, portata, stato_allerta, validato, created_at)
    VALUES (:stazione_id, :timestamp, :livello, :portata, :stato_allerta, :validato, NOW())
    ON CONFLICT (stazione_id, timestamp)
    DO UPDATE SET
        livello_idrometrico = EXCLUDED.livello_idrometrico,
        portata = EXCLUDED.portata,
        stato_allerta = EXCLUDED.stato_allerta,
        validato = EXCLUDED.validato;
    """

    processed = 0
    for item in items:
        st_id = codice_to_id.get(item.codice_stazione)
        if not st_id:
            continue  # Salta se la stazione non è ancora censita nell'anagrafica

        await db.execute(
            text(upsert_sql),
            {
                "stazione_id": st_id,
                "timestamp": item.timestamp,
                "livello": item.livello_idrometrico,
                "portata": item.portata,
                "stato_allerta": "verde",
                "validato": item.validato
            }
        )
        processed += 1

    await db.commit()
    return {"inserted_or_updated": processed, "total_received": len(items)}
