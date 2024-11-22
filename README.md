# Google Calendar Appointment Scheduler

A Django-based appointment scheduling system that integrates with Google Calendar. This application allows users to book appointments based on available time slots while preventing double bookings and conflicts.

## Features

- Integration with Google Calendar API
- Dynamic time slot selection
- Customizable appointment durations (30min, 45min, 1hr, 1.5hrs)
- Automatic conflict detection
- Responsive booking interface
- Real-time availability updates

## Prerequisites

Before running this project, make sure you have:

- Python 3.x installed
- pip (Python package manager)
- A Google Cloud Project with Calendar API enabled
- A service account with appropriate permissions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Oyshik-ICT/QuickBooker.git
cd QuickBooker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# OR
venv\Scripts\activate  # For Windows
```

3. Install required packages using requirements.txt:
```bash
pip install -r requirements.txt
```

For reference, here are the packages in requirements.txt:
```
django
google-auth
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
pytz
python-dotenv
```

4. Create a `.env` file in the project root with the following content:
```
SERVICE_ACCOUNT_FILE=<path-to-your-service-account-key.json>
CALENDAR_ID=<your-google-calendar-email>
SCOPES=https://www.googleapis.com/auth/calendar
LOCAL_TIMEZONE=Asia/Dhaka  # Change to your timezone
```

5. Set up Google Calendar API:
   - Go to Google Cloud Console
   - Create a new project or select existing one
   - Enable Google Calendar API
   - Create a service account and download the JSON key file
   - Share your Google Calendar with the service account email

6. Migrate the database:
```bash
python manage.py migrate
```

7. Run the development server:
```bash
python manage.py runserver
```

## Configuration

### Available Time Slots
The application is configured to show appointments between 8:00 AM and 5:00 PM on weekdays. You can modify these settings in `views.py`:

```python
AVAILABILITY = {
    "Monday": [(8, 0), (17, 30)],
    "Tuesday": [(8, 0), (17, 30)],
    "Wednesday": [(8, 0), (17, 30)],
    "Thursday": [(8, 0), (17, 30)],
    "Friday": [(8, 0), (17, 30)],
    "Saturday": [],
    "Sunday": [],
}
```

### Session Durations
Available appointment durations can be modified in `views.py`:

```python
SESSION_DURATIONS = [
    {"value": 30, "display": "30 minutes"},
    {"value": 45, "display": "45 minutes"},
    {"value": 60, "display": "1 hour"},
    {"value": 90, "display": "1.5 hours"},
]
```

## Routes

| URL | View Function | Description |
|-----|--------------|-------------|
| `/` | `google_calendar_events` | Main booking page showing available slots |
| `/book-appointment/` | `book_appointment` | Endpoint for processing appointment bookings |
| `/admin/` | Django Admin | Administrative interface |

## Usage

1. Visit the homepage (`/`)
2. Select appointment duration
3. Choose an available date
4. Select a time slot
5. Fill in your details
6. Submit the booking

The appointment will be automatically added to the specified Google Calendar.

## Error Handling

The application includes various error checks:
- Double booking prevention
- Conflict detection
- Required field validation
- API error handling

## Common Issues

1. **Calendar API Error**: Make sure your service account has the correct permissions and the calendar is shared with the service account email.

2. **Time Zone Issues**: Verify that the `LOCAL_TIMEZONE` in your `.env` file matches your desired timezone.

3. **Service Account File**: Ensure the path to your service account JSON file in `.env` is correct and absolute.

4. **Package Installation Issues**: If you encounter any package installation issues, try installing packages individually:
```bash
pip install django
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install google-api-python-client
pip install pytz
pip install python-dotenv
```