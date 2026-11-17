
from contextlib import asynccontextmanager
from threading import Thread

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Ride, RideEvent
from app.database import Base, engine, get_db
from app.models import Ride
from app.schemas import RideCreate, RideResponse
from app.workers.ride_worker import ride_queue, ride_worker


# Start database and background worker
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Start worker in a separate thread
    worker_thread = Thread(
        target=ride_worker,
        daemon=True
    )

    worker_thread.start()

    print("Database connected successfully")
    print("Ride booking application started")

    yield

    # Stop worker gracefully after pending tasks
    ride_queue.put(None)
    worker_thread.join(timeout=10)


app = FastAPI(
    title="Ride Booking System",
    description="Simple ride booking and driver assignment",
    version="1.0.0",
    lifespan=lifespan
)


# API 1: Book a ride

@app.post("/rides", response_model=RideResponse, status_code=202)
def book_ride(request: RideCreate, db: Session = Depends(get_db)):

    new_ride = Ride(
        rider_id=request.rider_id,
        pickup=request.pickup,
        drop_location=request.drop_location,
        status="REQUESTED"
    )

    db.add(new_ride)
    db.flush()

    # Publish REQUESTED event
    event = RideEvent(
        ride_id=new_ride.id,
        status="REQUESTED"
    )

    db.add(event)

    # Save ride and event together
    db.commit()
    db.refresh(new_ride)

    # Add ride to background queue
    ride_queue.put(new_ride.id)

    print(f"Ride {new_ride.id} added to queue")
    print(f"Event published: Ride {new_ride.id} - REQUESTED")

    return RideResponse(
        ride_id=new_ride.id,
        rider_id=new_ride.rider_id,
        pickup=new_ride.pickup,
        drop_location=new_ride.drop_location,
        status="REQUESTED",
        assigned_driver_id=None
    )



# API 2: Get ride details
@app.get(
    "/rides/{ride_id}",
    response_model=RideResponse
)
def get_ride(
    ride_id: int,
    db: Session = Depends(get_db)
):

    ride = db.query(Ride).filter(
        Ride.id == ride_id
    ).first()

    if ride is None:
        raise HTTPException(
            status_code=404,
            detail="Ride not found"
        )

    return RideResponse(
        ride_id=ride.id,
        rider_id=ride.rider_id,
        pickup=ride.pickup,
        drop_location=ride.drop_location,
        status=ride.status,
        assigned_driver_id=ride.assigned_driver_id
    )


# API 3: Get all rides
@app.get("/rides")
def get_all_rides(
    db: Session = Depends(get_db)
):

    rides = db.query(Ride).order_by(
        Ride.id.desc()
    ).all()

    return [
        {
            "rideId": ride.id,
            "rider_id": ride.rider_id,
            "pickup": ride.pickup,
            "drop": ride.drop_location,
            "status": ride.status,
            "assigned_driver_id": ride.assigned_driver_id
        }
        for ride in rides
    ]
