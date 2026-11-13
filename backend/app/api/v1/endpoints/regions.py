from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter()


class RegioneSummary(BaseModel):
    id: int
    codice_istat: str
    nome: str
    totale_stazioni: int
    stazioni_in_allerta: int


@router.get("", response_model=List[RegioneSummary], summary="Elenco regioni con statistiche stazioni")
async def list_regions(db: AsyncSession = Depends(get_db)):
    """
    Restituisce l'elenco delle regioni con conteggio delle stazioni totali
    e stazioni con superamento soglie.
    """
    sql = """
    SELECT 
        r.id,
        r.codice_istat,
        r.nome,
        COUNT(s.id) AS totale_stazioni,
        COUNT(CASE WHEN m.stato_allerta IN ('giallo', 'arancione', 'rosso') THEN 1 END) AS stazioni_in_allerta
    FROM regioni r
    LEFT JOIN stazioni s ON s.regione_id = r.id AND s.attiva = true
    LEFT JOIN LATERAL (
        SELECT stato_allerta
        FROM misurazioni
        WHERE stazione_id = s.id
        ORDER BY timestamp DESC
        LIMIT 1
    ) m ON true
    GROUP BY r.id, r.codice_istat, r.nome
    ORDER BY r.nome ASC;
    """
    result = await db.execute(text(sql))
    rows = result.mappings().all()

    return [
        RegioneSummary(
            id=r["id"],
            codice_istat=r["codice_istat"],
            nome=r["nome"],
            totale_stazioni=r["totale_stazioni"],
            stazioni_in_allerta=r["stazioni_in_allerta"]
        )
        for r in rows
    ]
