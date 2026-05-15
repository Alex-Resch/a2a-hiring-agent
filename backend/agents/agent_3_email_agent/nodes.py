from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta, timezone
import os
import base64
from email.mime.text import MIMEText

from agents.agent_3_email_agent.state import AgentState, FreeSlot, EmailSent, BusySlot


SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
]

# The user needs to set this in the frontend later
WORK_START_HOUR = 9
WORK_END_HOUR = 18
SLOT_DURATION = timedelta(minutes=60)


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds


def get_calendar_service():
    return build("calendar", "v3", credentials=get_credentials())


def get_gmail_service():
    return build("gmail", "v1", credentials=get_credentials())


def check_busy_slots(state: AgentState):
    service = get_calendar_service()

    now = datetime.now(timezone.utc)
    time_max = (now + timedelta(days=7)).isoformat()

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = events_result.get("items", [])

    busy_slots = [
        BusySlot(
            start=datetime.fromisoformat(event["start"].get("dateTime")),
            end=datetime.fromisoformat(event["end"].get("dateTime")),
        )
        for event in events
        if "dateTime" in event["start"]
    ]

    return state.model_copy(update={"busy_slots": busy_slots})


def get_free_slots(state: AgentState):
    busy_slots = sorted(state.busy_slots, key=lambda s: s.start)

    free_slots = []
    now = datetime.now(timezone.utc)

    for day_offset in range(7):
        day = (now + timedelta(days=day_offset)).date()

        work_start = datetime(
            day.year, day.month, day.day, WORK_START_HOUR, tzinfo=timezone.utc
        )
        work_end = datetime(
            day.year, day.month, day.day, WORK_END_HOUR, tzinfo=timezone.utc
        )

        busy_slots_day = [s for s in busy_slots if s.start.date() == day]

        for busy_slot in busy_slots_day:
            while work_start + SLOT_DURATION <= busy_slot.start:
                free_slots.append(
                    FreeSlot(
                        start=work_start,
                        end=work_start + SLOT_DURATION,
                    )
                )
                work_start += SLOT_DURATION
            work_start = max(work_start, busy_slot.end)

        while work_start + SLOT_DURATION <= work_end:
            free_slots.append(
                FreeSlot(
                    start=work_start,
                    end=work_start + SLOT_DURATION,
                )
            )
            work_start += SLOT_DURATION

    return state.model_copy(update={"free_slots": free_slots})


def create_appointment(state: AgentState):
    service = get_calendar_service()

    if state.selected_slot is None:
        raise ValueError("No Free Slot was selected.")

    events = []
    for profile in state.selected_profiles:
        event = {
            "summary": f"Interview with {profile.username}",
            "start": {
                "dateTime": state.selected_slot.start.isoformat(),
                "timeZone": "UTC",
            },
            "end": {"dateTime": state.selected_slot.end.isoformat(), "timeZone": "UTC"},
            "attendees": [{"email": profile.email}],
        }
        created = (
            service.events()
            .insert(calendarId="primary", body=event, sendUpdates="all")
            .execute()
        )
        events.append(created)

    return state.model_copy(update={"created_events": events})


def build_email_message(username: str, slot: FreeSlot) -> MIMEText:
    return MIMEText(
        f"""
      <html>
         <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Interview Invitation</h2>
            <p>Hi {username},</p>
            <p>We would like to invite you to an interview.</p>
            <div style="background: #f0f0f0; padding: 16px; border-radius: 8px;">
               <strong>Date:</strong> {slot.start.strftime("%B %d, %Y at %I:%M %p")} UTC
            </div>
            <p>Please confirm the appointment.</p>
            <p>Best regards</p>
         </body>
      </html>
      """,
        "html",
    )


def send_interview_invitations(state: AgentState):
    service = get_gmail_service()

    emails_sent = []
    for profile in state.selected_profiles:
        if not state.selected_slot:
            raise ValueError("No Free Slot was selected.")

        try:
            message = build_email_message(profile.username, state.selected_slot)
            message["to"] = profile.email
            message["subject"] = "Invitation to Interview"

            encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(
                userId="me", body={"raw": encoded}
            ).execute()
            emails_sent.append(
                EmailSent(
                    profile=profile.username,
                    status="sent",
                )
            )
        except Exception as e:
            emails_sent.append(
                EmailSent(
                    profile=profile.username, status="failed", error_message=str(e)
                )
            )

    return state.model_copy(update={"emails_sent": emails_sent})
