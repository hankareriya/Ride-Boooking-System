
import time

from app.database import SessionLocal
from app.models import RideEvent, ConsumerOffset


def consume_events(consumer_name, process_event):
    print(f"{consumer_name} consumer started...")

    # Create or load this consumer's independent offset
    db = SessionLocal()

    try:
        offset = db.get(ConsumerOffset, consumer_name)

        if offset is None:
            offset = ConsumerOffset(
                consumer_name=consumer_name,
                last_event_id=0
            )
            db.add(offset)
            db.commit()

    finally:
        db.close()

    # Continuously check for new events
    while True:
        db = SessionLocal()

        try:
            offset = db.get(ConsumerOffset, consumer_name)
            last_id = offset.last_event_id

            events = (
                db.query(RideEvent)
                .filter(RideEvent.id > last_id)
                .order_by(RideEvent.id.asc())
                .limit(100)
                .all()
            )

            for event in events:
                # Process the event
                process_event(event)

                # Save progress independently
                offset.last_event_id = event.id
                db.commit()

        except Exception as e:
            db.rollback()
            print(f"{consumer_name} consumer error: {e}")

        finally:
            db.close()

        time.sleep(1)
