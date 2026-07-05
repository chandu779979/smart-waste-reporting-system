"""
Email notification module using Brevo Transactional Email API.
All SMTP code has been replaced with Brevo REST API calls.
If BREVO_API_KEY is not set or an error occurs, the error is logged
and the application continues normally without crashing.
"""
import os
import json
import datetime

try:
    import requests as _requests
    _requests_available = True
except ImportError:
    _requests_available = False

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

BREVO_SEND_URL = "https://api.brevo.com/v3/smtp/email"

def _get_ist_str(dt):
    """Convert a naive UTC datetime to IST (+05:30) and format it."""
    if not dt:
        return ""
    ist_dt = dt + datetime.timedelta(hours=5, minutes=30)
    return ist_dt.strftime('%d %b %Y, %I:%M %p')


def _send_via_brevo(to_email: str, to_name: str, subject: str, text_content: str) -> bool:
    """
    Send a transactional email through the Brevo API.
    Returns True on success, False on any failure (never raises).
    """
    if not _requests_available:
        print("Brevo email skipped: 'requests' package is not installed. Run: pip install requests")
        return False

    api_key = os.environ.get("BREVO_API_KEY", "").strip()
    mail_from = os.environ.get("MAIL_FROM", "").strip()
    mail_from_name = os.environ.get("MAIL_FROM_NAME", "Smart Waste Management System").strip()

    if not api_key or api_key == "PASTE_NEW_API_KEY_HERE":
        print("Brevo email skipped: BREVO_API_KEY is not configured in .env")
        return False

    if not mail_from:
        print("Brevo email skipped: MAIL_FROM is not configured in .env")
        return False

    payload = {
        "sender": {
            "name": mail_from_name,
            "email": mail_from,
        },
        "to": [
            {
                "email": to_email,
                "name": to_name,
            }
        ],
        "subject": subject,
        "textContent": text_content,
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key,
    }

    try:
        response = _requests.post(
            BREVO_SEND_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=10,
        )
        if response.status_code in (200, 201):
            print(f"[Brevo] Email sent successfully to {to_email} | Subject: '{subject}'")
            return True
        else:
            print(
                f"[Brevo] Failed to send email to {to_email} | "
                f"HTTP {response.status_code}: {response.text}"
            )
            return False
    except Exception as exc:
        # Never crash the application
        print(f"[Brevo] Exception while sending email to {to_email}: {exc}")
        return False


# ---------------------------------------------------------------------------
# Public notification functions (called from routes)
# ---------------------------------------------------------------------------

def send_welcome_email(citizen_name: str, citizen_email: str) -> bool:
    """Email 1 – Sent immediately after citizen registration."""
    subject = "Welcome to Smart Waste Reporting & Management System"
    body = (
        f"Hello {citizen_name},\n\n"
        f"Your account has been created successfully.\n\n"
        f"You can now log in and report waste issues.\n\n"
        f"Thank you,\n"
        f"Smart Waste Reporting & Management System"
    )
    return _send_via_brevo(citizen_email, citizen_name, subject, body)


def send_complaint_submitted_email(
    citizen_name: str,
    citizen_email: str,
    complaint_id: int,
    municipality_name: str,
    waste_category: str,
    created_at,
) -> bool:
    """Email 2 – Sent after a complaint is submitted successfully."""
    subject = "Complaint Submitted Successfully"
    date_str = _get_ist_str(created_at)
    body = (
        f"Hello {citizen_name},\n\n"
        f"Your complaint has been submitted successfully.\n\n"
        f"Complaint ID   : {complaint_id}\n"
        f"Municipality   : {municipality_name}\n"
        f"Category       : {waste_category}\n"
        f"Status         : Pending\n"
        f"Submitted On   : {date_str}\n\n"
        f"You can track your complaint by logging into your account.\n\n"
        f"Thank you."
    )
    return _send_via_brevo(citizen_email, citizen_name, subject, body)


def send_complaint_updated_email(
    citizen_name: str,
    citizen_email: str,
    complaint_id: int,
    previous_status: str,
    new_status: str,
    updated_at,
    admin_remarks: str = "",
) -> bool:
    """Email 3 – Sent whenever the admin changes a complaint's status."""
    subject = "Complaint Status Updated"
    date_str = _get_ist_str(updated_at)
    remarks_line = f"Admin Remarks  : {admin_remarks}\n" if admin_remarks else ""
    body = (
        f"Hello {citizen_name},\n\n"
        f"Your complaint has been updated.\n\n"
        f"Complaint ID     : {complaint_id}\n"
        f"Previous Status  : {previous_status}\n"
        f"Current Status   : {new_status}\n"
        f"Updated On       : {date_str}\n"
        f"{remarks_line}\n"
        f"Please log in to view the latest status.\n\n"
        f"Thank you."
    )
    return _send_via_brevo(citizen_email, citizen_name, subject, body)


def send_complaint_resolved_email(
    citizen_name: str,
    citizen_email: str,
    complaint_id: int,
    resolved_at,
) -> bool:
    """Email 4 – Sent when a complaint is marked as Resolved."""
    subject = "Complaint Successfully Resolved"
    date_str = _get_ist_str(resolved_at)
    body = (
        f"Hello {citizen_name},\n\n"
        f"Good news!\n\n"
        f"Your complaint has been resolved successfully.\n\n"
        f"Complaint ID : {complaint_id}\n"
        f"Resolved On  : {date_str}\n\n"
        f"If the issue is still not resolved, please contact your municipality "
        f"using the contact details available in the application.\n\n"
        f"Thank you for helping keep the city clean."
    )
    return _send_via_brevo(citizen_email, citizen_name, subject, body)
