from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, Integer, Float, String, Boolean, DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Misurazione(Base):
    """
    Tabella dei fatti (Fact Table) nello schema a stella.
    Raccoglie le misurazioni temporali (livello idrometrico in metri e portata in m³/s)
    acquisite dalle stazioni dai flussi ETL regionali.
    """
    __tablename__ = "misurazioni"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    stazione_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("stazioni.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # Metriche idrometriche
    livello_idrometrico: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # in metri
    portata: Mapped[Optional[float]] = mapped_column(Float, nullable=True)              # in m³/s

    # Stato idrometrico calcolato/riportato rispetto alle soglie di allerta
    # Valori tipici: "verde" (regolare), "giallo" (attenzione), "arancione" (preallarme), "rosso" (allarme)
    stato_allerta: Mapped[str] = mapped_column(String(20), default="verde", nullable=False)

    # Flag di qualità / validazione del dato
    validato: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Data di inserimento nel DB RiverMonitor
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relazione verso la stazione
    stazione: Mapped["Stazione"] = relationship("Stazione", back_populates="misurazioni")

    __table_args__ = (
        # Vincolo di unicità per consentire upsert idempotenti durante l'ingestione ETL
        UniqueConstraint("stazione_id", "timestamp", name="uq_stazione_timestamp"),
        # Indice composito per velocizzare il recupero delle serie storiche (es. ultime 24/48h)
        Index("ix_misurazioni_stazione_timestamp", "stazione_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<Misurazione(id={self.id}, stazione_id={self.stazione_id}, timestamp='{self.timestamp}', livello={self.livello_idrometrico}m, stato='{self.stato_allerta}')>"
