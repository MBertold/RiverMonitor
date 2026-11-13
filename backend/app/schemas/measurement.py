from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MisurazioneBase(BaseModel):
    timestamp: datetime
    livello_idrometrico: Optional[float] = Field(None, example=2.15, description="Livello in metri")
    portata: Optional[float] = Field(None, example=450.0, description="Portata in m³/s")
    stato_allerta: str = Field("verde", example="verde")
    validato: bool = False


class MisurazioneCreate(MisurazioneBase):
    stazione_id: int


class MisurazioneBatchItem(BaseModel):
    codice_stazione: str
    timestamp: datetime
    livello_idrometrico: Optional[float] = None
    portata: Optional[float] = None
    validato: bool = False


class MisurazioneRead(MisurazioneBase):
    id: int
    stazione_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TimeSeriesDataPoint(BaseModel):
    timestamp: datetime
    livello: Optional[float] = None
    portata: Optional[float] = None
    stato_allerta: str = "verde"


class TimeSeriesThresholds(BaseModel):
    gialla: Optional[float] = None
    arancione: Optional[float] = None
    rossa: Optional[float] = None
    zero_idrometrico: Optional[float] = None


class TimeSeriesStats(BaseModel):
    min_livello: Optional[float] = None
    max_livello: Optional[float] = None
    avg_livello: Optional[float] = None
    current_livello: Optional[float] = None
    delta_livello_24h: Optional[float] = None
    trend: str = "stazionario"  # "in_aumento", "in_calo", "stazionario"


class StationTimeSeriesResponse(BaseModel):
    stazione_id: int
    codice_stazione: str
    nome: str
    fiume: Optional[str] = None
    regione: Optional[str] = None
    soglie: TimeSeriesThresholds
    stats: TimeSeriesStats
    serie_storica: List[TimeSeriesDataPoint]
