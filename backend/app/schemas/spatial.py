from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


# --- Schemi Regione e Bacino ---

class RegioneBase(BaseModel):
    codice_istat: str = Field(..., max_length=2, example="01")
    nome: str = Field(..., max_length=100, example="Piemonte")


class RegioneRead(RegioneBase):
    id: int

    class Config:
        from_attributes = True


class BacinoBase(BaseModel):
    codice: str = Field(..., example="PO")
    nome: str = Field(..., example="Bacino del Po")
    autorita_distretto: Optional[str] = Field(None, example="Autorità di Bacino Distrettuale del Fiume Po")


class BacinoRead(BacinoBase):
    id: int

    class Config:
        from_attributes = True


# --- Schemi Stazione ---

class StazioneBase(BaseModel):
    codice_stazione: str = Field(..., example="TO01_PO_TORINO")
    nome: str = Field(..., example="Po a Torino - Murazzi")
    fiume: Optional[str] = Field(None, example="Po")
    quota_zero_idrometrico: Optional[float] = Field(None, example=215.4)
    soglia_allerta_gialla: Optional[float] = Field(None, example=3.5)
    soglia_allerta_arancione: Optional[float] = Field(None, example=4.5)
    soglia_allerta_rossa: Optional[float] = Field(None, example=5.5)
    fonte_dati: str = Field(..., example="ARPA Piemonte")
    attiva: bool = True


class StazioneCreate(StazioneBase):
    regione_id: Optional[int] = None
    bacino_id: Optional[int] = None
    longitudine: float = Field(..., ge=-180.0, le=180.0, example=7.692)
    latitudine: float = Field(..., ge=-90.0, le=90.0, example=45.059)


class UltimaMisurazioneSummary(BaseModel):
    timestamp: str
    livello_idrometrico: Optional[float] = None
    portata: Optional[float] = None
    stato_allerta: str = "verde"  # verde, giallo, arancione, rosso
    trend: Optional[str] = None   # "stazionario", "crescente", "decrescente"


class StazioneProperties(StazioneBase):
    id: int
    regione_nome: Optional[str] = None
    bacino_nome: Optional[str] = None
    ultima_misurazione: Optional[UltimaMisurazioneSummary] = None

    class Config:
        from_attributes = True


# --- GeoJSON RFC 7946 Compliant Schemas ---

class GeoJSONPoint(BaseModel):
    type: str = "Point"
    coordinates: List[float] = Field(..., min_length=2, max_length=2, example=[7.692, 45.059])


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    id: int
    geometry: GeoJSONPoint
    properties: StazioneProperties


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
    total_count: int
