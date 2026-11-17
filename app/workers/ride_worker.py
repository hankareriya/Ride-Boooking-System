
import random
from queue import Queue

from app.database import SessionLocal
from app.models import Ride, RideEvent

ride_queue = Queue()

DRIVERS = [
    {"id": 1, "name": "Amit"},
    {"id": 2, "name": "Rahul"},
    {"id": 3, "name": "Priya"},
    {"id": 4, "name": "Sneha"},
    {"id": 5, "name": "Vikram"},
    {"id": 6, "name": "Neha"},
    {"id": 7, "name": "Arjun"},
    {"id": 8, "name": "Karan"},
    {"id": 9, "name": "Pooja"},
    {"id": 10, "name": "Rohan"}
]


def process_ride(ride_id):
    db = SessionLocal()

    try:
        ride = db.query(Ride).filter(Ride.id == ride_id).first()

        if ride is None or ride.status != "REQUESTED":
            return

        print(f"\nProcessing Ride {ride_id}")

        selected_drivers = random.sample(DRIVERS, 3)

        for driver in selected_drivers:
            print(
                f"Offering Ride {ride_id} to "
                f"Driver {driver['id']} ({driver['name']})"
            )

            # Simulate driver acceptance (50%)
            accepted = random.random() < 0.5

            if accepted:
                ride.status = "ASSIGNED"
                ride.assigned_driver_id = driver["id"]

                db.add(
                    RideEvent(
                        ride_id=ride.id,
                        status="ASSIGNED"
                    )
                )

                db.commit()

                print(f"Driver {driver['id']} accepted Ride {ride_id}")
                print("Event published: ASSIGNED")
                return

            print(f"Driver {driver['id']} rejected Ride {ride_id}")

        # All three drivers rejected
        ride.status = "NO_DRIVER_FOUND"
        ride.assigned_driver_id = None

        db.add(
            RideEvent(
                ride_id=ride.id,
                status="NO_DRIVER_FOUND"
            )
        )

        db.commit()

        print(f"Ride {ride_id} status: NO_DRIVER_FOUND")
        print("Event published: NO_DRIVER_FOUND")

    except Exception as e:
        db.rollback()
        print(f"Error processing Ride {ride_id}: {e}")

    finally:
        db.close()


def ride_worker():
    print("Ride background worker started...")

    while True:
        ride_id = ride_queue.get()

        try:
            if ride_id is None:
                return

            process_ride(ride_id)

        finally:
            ride_queue.task_done()
