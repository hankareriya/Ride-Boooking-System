
# Ride Booking and Dispatch System

A backend ride-booking and driver-dispatch application built using **Python, FastAPI, MySQL, and SQLAlchemy**.

This project implements ride booking, background driver assignment, event broadcasting to independent consumers, and concurrent load testing with 100 ride requests.

## Features

### Task 1: Ride Booking and Driver Dispatch

- REST API to book a ride.
- Stores ride details in MySQL.
- Uses Python's `queue.Queue` for background processing.
- Background worker selects drivers from a predefined list of 10 drivers.
- Simulates driver acceptance and rejection with a 50% acceptance probability.
- Tries up to 3 drivers for each ride.
- Updates ride status to:
  - `REQUESTED`
  - `ASSIGNED`
  - `NO_DRIVER_FOUND`
- Stores the assigned driver's ID.

### Task 2: Event Broadcasting

- Stores ride status events in a MySQL `ride_events` table.
- Implements two independent consumers:
  - **Billing Consumer:** Prints a billing message for each ride event.
  - **Operations Consumer:** Prints the ride ID and its updated status.
- Uses separate offsets for each consumer in the `consumer_offsets` table.
- Both consumers independently receive events.
- Consumers can resume processing from their last saved event offset.

### Task 3: Load Testing

- Creates 100 rides using concurrent HTTP requests.
- Uses Python's `ThreadPoolExecutor`.
- Waits for background processing to finish.
- Checks final ride statuses.
- Validates driver assignments.
- Checks for rides stuck in `REQUESTED`.
- Generates a final test report.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| MySQL | Database |
| SQLAlchemy | ORM and database operations |
| PyMySQL | MySQL connectivity |
| Python Queue | Background ride processing |
| ThreadPoolExecutor | Concurrent load testing |
| Requests | HTTP requests for testing |

## Project Structure

```text
Ride-Booking-System/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   └── ride_worker.py
│   │
│   └── consumers/
│       ├── __init__.py
│       ├── consumer_utils.py
│       ├── billing.py
│       └── operations.py
│
├── tests/
│   ├── __init__.py
│   └── test_rides.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10 or later
- MySQL Server
- Git

## Database Setup

First, create the MySQL database:

```sql
CREATE DATABASE ride_booking_db;
```

The application automatically creates the required tables when it starts.

### Database Tables

| Table | Purpose |
|---|---|
| `rides` | Stores ride information and current status |
| `ride_events` | Stores ride status change events |
| `consumer_offsets` | Stores individual consumer progress |

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd Ride-Booking-System
```

### 2. Create a Virtual Environment

```powershell
python -m venv venv
```

Activate the virtual environment:

```powershell
.\venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root directory.

Add your MySQL configuration:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=ride_booking_db
```

Replace the example password with your own MySQL password.

**Note:** Do not upload your `.env` file or actual database credentials to GitHub.

### 5. Start the FastAPI Application

```powershell
uvicorn app.main:app
```

The application will run at:

`http://127.0.0.1:8000`

Open the interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/rides` | Book a new ride |
| GET | `/rides` | Retrieve all rides |
| GET | `/rides/{ride_id}` | Retrieve a specific ride |

### Sample Ride Request

**POST `/rides`**

```json
{
  "rider_id": 101,
  "pickup": "Mumbai",
  "drop": "Pune"
}
```

### Sample Response

```json
{
  "rideId": 1,
  "rider_id": 101,
  "pickup": "Mumbai",
  "drop": "Pune",
  "status": "REQUESTED",
  "assigned_driver_id": null
}
```

The ride is initially created with `REQUESTED` status. The background worker processes the ride and updates its final status.

## Running Event Consumers

Run the Billing and Operations consumers in separate terminals while the FastAPI application is running.

### Terminal 1: FastAPI Application

```powershell
uvicorn app.main:app
```

### Terminal 2: Billing Consumer

```powershell
python -m app.consumers.billing
```

### Terminal 3: Operations Consumer

```powershell
python -m app.consumers.operations
```

### Sample Consumer Output

**Billing Consumer**

```text
[BILLING] charging rider for ride 1
```

**Operations Consumer**

```text
[OPS] ride 1 is now in status REQUESTED
[OPS] ride 1 is now in status ASSIGNED
```

Both consumers independently receive ride status events and maintain their own processing offsets.

## Load Testing – 100 Rides

Keep the FastAPI application running.

Open another terminal and execute:

```powershell
python -m tests.test_rides
```

The test sends 100 concurrent ride-booking requests and waits for the background worker to process them.

### Example Test Report

```text
========== TASK 3 REPORT ==========

Total rides requested:          100
Total rides created:            100
ASSIGNED:                        87
NO_DRIVER_FOUND:                 13
Rides with final status:        100
Rides stuck without final status: 0
Invalid driver assignments:      0

========== FINAL RESULT ==========

TASK 3: PASSED
```

The actual number of assigned and rejected rides may vary because driver acceptance is randomized. The above output is an example.

## Implementation Notes

- Driver acceptance is simulated using random selection.
- The application does not currently check real driver availability or GPS-based proximity.
- Ride processing uses an in-memory Python queue.
- Event broadcasting uses MySQL polling and independent consumer offsets.
- Each ride stores a single assigned driver ID.
- Consumers may process an event more than once if they stop before saving their offset. Production implementations should use idempotent event handling.
- The current load test sends concurrent API requests, while the configured background worker processes rides sequentially.

## Future Improvements

- Real-time driver location tracking.
- Persistent queue processing.
- Authentication and authorization.
- Idempotent event handling.
- Automated unit and integration testing.
- Improved concurrent ride dispatch and database locking.
