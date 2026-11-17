
import time
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

from app.database import SessionLocal
from app.models import Ride


API_URL = "http://127.0.0.1:8000/rides"
TOTAL_RIDES = 100
MAX_WORKERS = 20
TIMEOUT_SECONDS = 180


def book_ride(rider_id):
    payload = {
        "rider_id": rider_id,
        "pickup": f"Pickup Location {rider_id}",
        "drop": f"Drop Location {rider_id}"
    }

    response = requests.post(API_URL, json=payload, timeout=30)
    response.raise_for_status()

    return response.json()["rideId"]


def create_100_rides():
    ride_ids = []
    errors = []

    print(f"Creating {TOTAL_RIDES} rides concurrently...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(book_ride, 1000 + i)
            for i in range(TOTAL_RIDES)
        ]

        for future in as_completed(futures):
            try:
                ride_ids.append(future.result())
            except Exception as error:
                errors.append(str(error))

    print(f"Successfully created: {len(ride_ids)}")
    print(f"Booking errors: {len(errors)}")

    if errors:
        for error in errors:
            print("Error:", error)

    return ride_ids


def wait_for_processing(ride_ids):
    print("\nWaiting for rides to finish processing...")

    deadline = time.time() + TIMEOUT_SECONDS

    while time.time() < deadline:
        db = SessionLocal()

        try:
            rides = (
                db.query(Ride)
                .filter(Ride.id.in_(ride_ids))
                .all()
            )

            completed = sum(
                ride.status in ("ASSIGNED", "NO_DRIVER_FOUND")
                for ride in rides
            )

            print(
                f"Processed: {completed}/{len(ride_ids)}",
                end="\r"
            )

            if len(rides) == len(ride_ids) and completed == len(ride_ids):
                print("\nAll rides processed!")
                return True

        finally:
            db.close()

        time.sleep(1)

    print("\nTimeout: Some rides are still pending.")
    return False


def generate_report(ride_ids):
    db = SessionLocal()

    try:
        rides = (
            db.query(Ride)
            .filter(Ride.id.in_(ride_ids))
            .all()
        )

        assigned = [
            ride for ride in rides
            if ride.status == "ASSIGNED"
        ]

        no_driver = [
            ride for ride in rides
            if ride.status == "NO_DRIVER_FOUND"
        ]

        stuck = [
            ride for ride in rides
            if ride.status not in ("ASSIGNED", "NO_DRIVER_FOUND")
        ]

        # An assigned ride must have exactly one driver ID.
        invalid_assignments = [
            ride for ride in rides
            if (
                ride.status == "ASSIGNED"
                and ride.assigned_driver_id is None
            )
            or (
                ride.status != "ASSIGNED"
                and ride.assigned_driver_id is not None
            )
        ]

        total = len(ride_ids)
        created = len(rides)
        final_status_count = len(assigned) + len(no_driver)

        print("\n========== TASK 3 REPORT ==========")
        print(f"Total rides requested:          {total}")
        print(f"Total rides created:             {created}")
        print(f"ASSIGNED:                        {len(assigned)}")
        print(f"NO_DRIVER_FOUND:                 {len(no_driver)}")
        print(f"Rides with final status:         {final_status_count}")
        print(f"Rides stuck without final status:{len(stuck)}")
        print(f"Invalid driver assignments:     {len(invalid_assignments)}")

        print("\n========== FINAL RESULT ==========")

        passed = (
            created == TOTAL_RIDES
            and final_status_count == TOTAL_RIDES
            and len(stuck) == 0
            and len(invalid_assignments) == 0
        )

        if passed:
            print("TASK 3: PASSED")
        else:
            print("TASK 3: FAILED")

    finally:
        db.close()


if __name__ == "__main__":
    ride_ids = create_100_rides()

    if ride_ids:
        wait_for_processing(ride_ids)
        generate_report(ride_ids)
