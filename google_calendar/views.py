import datetime
import os

import pytz
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()


SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
SCOPES = [os.getenv("SCOPES")]
LOCAL_TIMEZONE = pytz.timezone(os.getenv("LOCAL_TIMEZONE"))
CALENDAR_ID = os.getenv("CALENDAR_ID")


SESSION_DURATIONS = [
    {"value": 30, "display": "30 minutes"},
    {"value": 45, "display": "45 minutes"},
    {"value": 60, "display": "1 hour"},
    {"value": 90, "display": "1.5 hours"},
]


TIME_SLOTS = [
    (8, 0),
    (8, 5),
    (8, 10),
    (8, 15),
    (8, 20),
    (8, 25),
    (8, 30),
    (8, 35),
    (8, 40),
    (8, 45),
    (8, 50),
    (8, 55),
    (9, 0),
    (9, 5),
    (9, 10),
    (9, 15),
    (9, 20),
    (9, 25),
    (9, 30),
    (9, 35),
    (9, 40),
    (9, 45),
    (9, 50),
    (9, 55),
    (10, 0),
    (10, 5),
    (10, 10),
    (10, 15),
    (10, 20),
    (10, 25),
    (10, 30),
    (10, 35),
    (10, 40),
    (10, 45),
    (10, 50),
    (10, 55),
    (11, 0),
    (11, 5),
    (11, 10),
    (11, 15),
    (11, 20),
    (11, 25),
    (11, 30),
    (11, 35),
    (11, 40),
    (11, 45),
    (11, 50),
    (11, 55),
    (12, 0),
    (12, 5),
    (12, 10),
    (12, 15),
    (12, 20),
    (12, 25),
    (12, 30),
    (12, 35),
    (12, 40),
    (12, 45),
    (12, 50),
    (12, 55),
    (13, 0),
    (13, 5),
    (13, 10),
    (13, 15),
    (13, 20),
    (13, 25),
    (13, 30),
    (13, 35),
    (13, 40),
    (13, 45),
    (13, 50),
    (13, 55),
    (14, 0),
    (14, 5),
    (14, 10),
    (14, 15),
    (14, 20),
    (14, 25),
    (14, 30),
    (14, 35),
    (14, 40),
    (14, 45),
    (14, 50),
    (14, 55),
    (15, 0),
    (15, 5),
    (15, 10),
    (15, 15),
    (15, 20),
    (15, 25),
    (15, 30),
    (15, 35),
    (15, 40),
    (15, 45),
    (15, 50),
    (15, 55),
    (16, 0),
    (16, 5),
    (16, 10),
    (16, 15),
    (16, 20),
    (16, 25),
    (16, 30),
    (16, 35),
    (16, 40),
    (16, 45),
    (16, 50),
    (16, 55),
    (17, 0),
]

AVAILABILITY = {
    "Monday": [(8, 0), (17, 30)],
    "Tuesday": [(8, 0), (17, 30)],
    "Wednesday": [(8, 0), (17, 30)],
    "Thursday": [(8, 0), (17, 30)],
    "Friday": [(8, 0), (17, 30)],
    "Saturday": [],
    "Sunday": [],
}


# Helper functions
def get_calendar_service():
    """Create and return Google Calendar service"""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES,
    )
    return build("calendar", "v3", credentials=creds)


def format_time_slots(time_slots):
    """Format time slots for display"""
    formatted_slots = []
    for hour, minute in time_slots:
        time = datetime.time(hour, minute)
        formatted_slots.append(
            {"value": f"{hour:02d}:{minute:02d}", "display": time.strftime("%I:%M %p")}
        )
    return formatted_slots


def check_event_conflict(current_time, potential_end_time, events):
    """Check if a time slot conflicts with existing events"""
    for event in events:
        event_start = datetime.datetime.fromisoformat(
            event["start"].get("dateTime")
        ).astimezone(current_time.tzinfo)
        event_end = datetime.datetime.fromisoformat(
            event["end"].get("dateTime")
        ).astimezone(current_time.tzinfo)

        if current_time < event_end and potential_end_time > event_start:
            return True
        if current_time < event_start and potential_end_time > event_start:
            return True
    return False


def get_available_times(start_time, end_time, events):
    """Get available time slots within a given time range considering session duration"""
    available_times = []
    current_time = start_time
    session_duration = int(getattr(get_available_times, "current_duration", 30))

    while current_time < end_time:
        hour = current_time.hour
        minute = current_time.minute

        if (hour, minute) in TIME_SLOTS:
            potential_end_time = current_time + datetime.timedelta(
                minutes=session_duration
            )

            is_available = True
            if check_event_conflict(current_time, potential_end_time, events):
                is_available = False

            if potential_end_time > end_time:
                is_available = False

            if is_available:
                available_times.append(
                    {
                        "value": f"{hour:02d}:{minute:02d}",
                        "display": current_time.strftime("%I:%M %p"),
                    }
                )

        current_time += datetime.timedelta(minutes=30)

    return available_times


def find_free_slots(events, availability, local_tz):
    free_slots = []
    now = datetime.datetime.now(local_tz)
    today = now.date()
    slots_by_date = {}

    for day, time_range in availability.items():
        if time_range:
            day_date = today + datetime.timedelta(
                days=(list(availability.keys()).index(day) - today.weekday()) % 7
            )
            start_hour, start_minute = time_range[0]
            end_hour, end_minute = time_range[1]
            start_time = local_tz.localize(
                datetime.datetime.combine(
                    day_date, datetime.time(start_hour, start_minute)
                )
            )
            end_time = local_tz.localize(
                datetime.datetime.combine(day_date, datetime.time(end_hour, end_minute))
            )

            if end_time < now:
                continue

            if start_time < now:
                start_time = now.astimezone(local_tz).replace(
                    minute=(now.minute // 15) * 15, second=0, microsecond=0
                ) + datetime.timedelta(minutes=15)

            day_events = [
                event
                for event in events
                if datetime.datetime.fromisoformat(event["start"].get("dateTime"))
                .astimezone(local_tz)
                .date()
                == day_date
            ]

            day_events.sort(
                key=lambda x: datetime.datetime.fromisoformat(
                    x["start"].get("dateTime")
                )
            )

            date_key = start_time.strftime("%Y-%m-%d")
            if date_key not in slots_by_date:
                slots_by_date[date_key] = {
                    "start": start_time,
                    "end": end_time,
                    "events": day_events,
                }

    for date_key, slot_data in slots_by_date.items():
        free_slots.append((slot_data["start"], slot_data["end"], slot_data["events"]))

    return sorted(free_slots, key=lambda x: x[0])


# View functions
def google_calendar_events(request):
    try:
        service = get_calendar_service()
        now = datetime.datetime.now(LOCAL_TIMEZONE).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        free_slots = find_free_slots(events, AVAILABILITY, LOCAL_TIMEZONE)
        formatted_slots = []

        for start, end, day_events in free_slots:
            duration_minutes = int((end - start).total_seconds() / 60)
            if duration_minutes >= SESSION_DURATIONS[0]["value"]:
                formatted_slots.append(
                    {
                        "start": start.strftime("%Y-%m-%d %H:%M"),
                        "end": end.strftime("%Y-%m-%d %H:%M"),
                        "display": f"{start.strftime('%B %d, %Y')}",
                        "available_times": get_available_times(start, end, day_events),
                        "duration_minutes": duration_minutes,
                    }
                )
        return render(
            request,
            "google_calendar/booking_template.html",
            {
                "free_slots": formatted_slots,
                "session_durations": SESSION_DURATIONS,
                "time_slots": format_time_slots(TIME_SLOTS),
            },
        )

    except Exception as error:
        return HttpResponse(f"An error occurred: {error}")


def book_appointment(request):
    if request.method == "POST":
        try:
            # Extract form data
            start_date = request.POST.get("start_date")
            start_time = request.POST.get("start_time")
            session_duration = int(request.POST.get("session_duration", 30))
            name = request.POST.get("name")
            email = request.POST.get("email")
            description = request.POST.get("description")

            if not all([start_date, start_time, session_duration, name, email]):
                return JsonResponse(
                    {"status": "error", "message": "All fields are required."},
                    status=400,
                )

            service = get_calendar_service()

            try:
                start_dt = datetime.datetime.strptime(
                    f"{start_date} {start_time}", "%Y-%m-%d %H:%M"
                )
                start_dt = LOCAL_TIMEZONE.localize(start_dt)
                end_dt = start_dt + datetime.timedelta(minutes=session_duration)
            except ValueError:
                return JsonResponse(
                    {"status": "error", "message": "Invalid date format provided."},
                    status=400,
                )

            events_result = (
                service.events()
                .list(
                    calendarId=CALENDAR_ID,
                    timeMin=start_dt.isoformat(),
                    timeMax=end_dt.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = events_result.get("items", [])

            if events:
                conflicting_event = events[0]
                conflict_start = datetime.datetime.fromisoformat(
                    conflicting_event["start"].get("dateTime")
                ).astimezone(LOCAL_TIMEZONE)

                available_duration = int(
                    (conflict_start - start_dt).total_seconds() / 60
                )

                if available_duration > 0:
                    message = f"There is an event at {conflict_start.strftime('%I:%M %p')}. Please select a shorter duration (maximum {available_duration} minutes) or choose a different time slot."
                else:
                    message = "This time slot conflicts with an existing event. Please choose a different time."

                return JsonResponse({"status": "error", "message": message}, status=400)

            event = {
                "summary": f"Appointment: {name} ({session_duration} minutes)",
                "description": f"""
Appointment Details:
------------------
Name: {name}
Email: {email}
Duration: {session_duration} minutes
Description: {description}
""".strip(),
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "Asia/Dhaka",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "Asia/Dhaka",
                },
            }

            try:
                event = (
                    service.events()
                    .insert(calendarId=CALENDAR_ID, body=event, sendUpdates="none")
                    .execute()
                )

                formatted_start = start_dt.strftime("%B %d, %Y at %I:%M %p")
                formatted_end = end_dt.strftime("%I:%M %p")
                success_message = f"""Appointment booked successfully! 
Your {session_duration}-minute appointment is scheduled for {formatted_start} - {formatted_end}.
Please add this to your calendar."""

                return JsonResponse(
                    {
                        "status": "success",
                        "message": success_message,
                        "event_id": event.get("id"),
                    }
                )

            except HttpError as error:
                error_message = error.reason if hasattr(error, "reason") else str(error)
                return JsonResponse(
                    {
                        "status": "error",
                        "message": f"Calendar API error: {error_message}",
                    },
                    status=500,
                )

        except Exception as error:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"An unexpected error occurred: {str(error)}",
                },
                status=500,
            )

    return JsonResponse(
        {"status": "error", "message": "Invalid request method"}, status=405
    )
