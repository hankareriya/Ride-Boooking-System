
from app.consumers.consumer_utils import consume_events


def process_operations_event(event):
    print(
        f"[OPS] ride {event.ride_id} "
        f"is now in status {event.status}"
    )


if __name__ == "__main__":
    consume_events("operations", process_operations_event)
