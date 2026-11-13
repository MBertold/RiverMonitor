from typing import List, Optional
from geoalchemy2 import Geometry
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Regione(Base, TimestampMixin):
    """
    Dimensione spaziale: Regione italiana (es. Piemonte, Lombardia).
    Include il poligono territoriale (WGS84) derivato da fonti ufficiali (es. ISPRA / ISTAT)
    per consentire filtraggio spaziale e selezione nella mappa.
    """
    __tablename__ = "regioni"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codice_istat: Mapped[str] = mapped_column(String(2), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    
    # Confini regionali multipoligono in WGS84 (SRID 4326)
    geometria: Mapped[Optional[object]] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=True
    )

    # Relazioni
    stazioni: Mapped[List["Stazione"]] = relationship("Stazione", back_populates="regione", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Regione(id={self.id}, codice='{self.codice_istat}', nome='{self.nome}')>"


class BacinoIdrografico(Base, TimestampMixin):
    """
    Dimensione spaziale: Bacino idrografico o Distretto di bacino (es. Bacino del Po, Tevere).
    """
    __tablename__ = "bacini_idrografici"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codice: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    autorita_distretto: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # Poligono del bacino idrografico (opzionale)
    geometria: Mapped[Optional[object]] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=True
    )

    # Relazioni
    stazioni: Mapped[List["Stazione"]] = relationship("Stazione", back_populates="bacino")

    def __repr__(self) -> str:
        return f"<BacinoIdrografico(id={self.id}, codice='{self.codice}', nome='{self.nome}')>"


class Stazione(Base, TimestampMixin):
    """
    Dimensione spaziale: Stazione idrometrica di monitoraggio.
    Contiene la posizione puntiforme (WGS84), il corso d'acqua associato,
    le soglie di allerta idrometrica (gialla, arancione, rossa) e la fonte dati.
    """
    __tablename__ = "stazioni"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codice_stazione: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    fiume: Mapped[Optional[str]] = mapped_column(String(150), index=True, nullable=True)

    # Chiavi esterne
    regione_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("regioni.id", ondelete="SET NULL"), nullable=True, index=True
    )
    bacino_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("bacini_idrografici.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Posizione geografica: punto (Longitudine, Latitudine) in EPSG:4326
    posizione: Mapped[object] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=False
    )

    # Quota dello zero idrometrico in m s.l.m.
    quota_zero_idrometrico: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Soglie di allerta idrometrica (in metri di altezza idrometrica)
    soglia_allerta_gialla: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soglia_allerta_arancione: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soglia_allerta_rossa: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Provenienza del dato (es. ARPA Piemonte, ARPA Lombardia, PDND, Protezione Civile)
    fonte_dati: Mapped[str] = mapped_column(String(100), nullable=False, default="ARPA")
    attiva: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)

    # URL feed webcam live (video stream HLS/m3u8, snapshot JPEG o embed player)
    webcam_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relazioni
    regione: Mapped[Optional["Regione"]] = relationship("Regione", back_populates="stazioni")
    bacino: Mapped[Optional["BacinoIdrografico"]] = relationship("BacinoIdrografico", back_populates="stazioni")
    misurazioni: Mapped[List["Misurazione"]] = relationship(
        "Misurazione",
        back_populates="stazione",
        cascade="all, delete-orphan",
        order_by="desc(Misurazione.timestamp)"
    )

    def __repr__(self) -> str:
        return f"<Stazione(id={self.id}, codice='{self.codice_stazione}', nome='{self.nome}', fiume='{self.fiume}')>"


class TracciatoFiume(Base, TimestampMixin):
    """
    Dimensione spaziale: Geometria vettoriale del tracciato fluviale (LineString in EPSG:4326).
    Consente di visualizzare ed evidenziare l'intero corso del fiume dalla sorgente alla foce sulla mappa.
    """
    __tablename__ = "tracciati_fiumi"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    lunghezza_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    bacino_nome: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    regioni_attraversate: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)

    # LineString con le coordinate del corso d'acqua
    geometria: Mapped[object] = mapped_column(
        Geometry(geometry_type="LINESTRING", srid=4326, spatial_index=True),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<TracciatoFiume(id={self.id}, nome='{self.nome}', km={self.lunghezza_km})>"

