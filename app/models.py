
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Ride(Base):
    __tablename__ = "rides"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    rider_id = Column(Integer, nullable=False)

    pickup = Column(String(255), nullable=False)

    drop_location = Column(String(255), nullable=False)

    status = Column(
        String(30),
        nullable=False,
        default="REQUESTED",
        index=True
    )

    assigned_driver_id = Column(Integer, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

class RideEvent(Base):
    __tablename__ = "ride_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ride_id = Column(Integer, ForeignKey("rides.id"), nullable=False, index=True)
    status = Column(String(30), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class ConsumerOffset(Base):
    __tablename__ = "consumer_offsets"

    consumer_name = Column(String(50), primary_key=True)
    last_event_id = Column(Integer, nullable=False, default=0)