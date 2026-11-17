
from app.consumers.consumer_utils import consume_events


def process_billing_event(event):
    print(
        f"[BILLING] charging rider for ride {event.ride_id}"
    )


if __name__ == "__main__":
    consume_events("billing", process_billing_event)
