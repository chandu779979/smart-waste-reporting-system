"""
Brevo Email Notification Test Script
=====================================
Loads BREVO_API_KEY, MAIL_FROM, MAIL_FROM_NAME from .env and
tests all four notification functions without touching the Flask app.

Run with:  python test_brevo.py
"""

import os
import sys
import datetime
from dotenv import load_dotenv

# Load .env so notifications.py can read the real API key
load_dotenv()

# Verify the key is present before even importing the module
api_key = os.environ.get("BREVO_API_KEY", "").strip()
mail_from = os.environ.get("MAIL_FROM", "").strip()
mail_from_name = os.environ.get("MAIL_FROM_NAME", "Smart Waste Management System").strip()

print("=" * 60)
print("  BREVO EMAIL NOTIFICATION TEST")
print("=" * 60)
print(f"  BREVO_API_KEY : {'*' * 8 + api_key[-6:] if len(api_key) > 6 else '(NOT SET)'}")
print(f"  MAIL_FROM     : {mail_from or '(NOT SET)'}")
print(f"  MAIL_FROM_NAME: {mail_from_name}")
print("=" * 60)

if not api_key or api_key == "PASTE_NEW_API_KEY_HERE":
    print("\n[ERROR] BREVO_API_KEY is not set in .env. Aborting tests.")
    sys.exit(1)

if not mail_from:
    print("\n[ERROR] MAIL_FROM is not set in .env. Aborting tests.")
    sys.exit(1)

# Now import the notification module (it reads env vars at call time)
from utilities.notifications import (
    send_welcome_email,
    send_complaint_submitted_email,
    send_complaint_updated_email,
    send_complaint_resolved_email,
)

# Use the verified sender email as the test recipient so the mail is deliverable
TEST_RECIPIENT_EMAIL = mail_from
TEST_RECIPIENT_NAME  = "SWM Test User"
NOW_UTC = datetime.datetime(2026, 7, 5, 9, 28, 0)   # fixed UTC time for reproducible output

PASS = "[PASS]"
FAIL = "[FAIL]"

results = {}

# ------------------------------------------------------------------
# Test 1 – Welcome Email (Citizen Registration)
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("  TEST 1 — Welcome Email (Citizen Registration)")
print("-" * 60)
ok = send_welcome_email(TEST_RECIPIENT_NAME, TEST_RECIPIENT_EMAIL)
results["Welcome Email"] = ok
print(f"  Result : {PASS if ok else FAIL}")

# ------------------------------------------------------------------
# Test 2 – Complaint Submitted Email
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("  TEST 2 — Complaint Submitted Email")
print("-" * 60)
ok = send_complaint_submitted_email(
    citizen_name      = TEST_RECIPIENT_NAME,
    citizen_email     = TEST_RECIPIENT_EMAIL,
    complaint_id      = 101,
    municipality_name = "Anantapur Municipality",
    waste_category    = "Overflowing Bin",
    created_at        = NOW_UTC,
)
results["Complaint Submitted"] = ok
print(f"  Result : {PASS if ok else FAIL}")

# ------------------------------------------------------------------
# Test 3 – Complaint Status Updated Email
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("  TEST 3 — Complaint Status Updated Email")
print("-" * 60)
ok = send_complaint_updated_email(
    citizen_name    = TEST_RECIPIENT_NAME,
    citizen_email   = TEST_RECIPIENT_EMAIL,
    complaint_id    = 101,
    previous_status = "Pending",
    new_status      = "In Progress",
    updated_at      = NOW_UTC,
    admin_remarks   = "Team dispatched to the location.",
)
results["Status Updated"] = ok
print(f"  Result : {PASS if ok else FAIL}")

# ------------------------------------------------------------------
# Test 4 – Complaint Resolved Email
# ------------------------------------------------------------------
print("\n" + "-" * 60)
print("  TEST 4 — Complaint Resolved Email")
print("-" * 60)
ok = send_complaint_resolved_email(
    citizen_name  = TEST_RECIPIENT_NAME,
    citizen_email = TEST_RECIPIENT_EMAIL,
    complaint_id  = 101,
    resolved_at   = NOW_UTC,
)
results["Complaint Resolved"] = ok
print(f"  Result : {PASS if ok else FAIL}")

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
print("\n" + "=" * 60)
print("  TEST SUMMARY")
print("=" * 60)
all_passed = True
for name, passed in results.items():
    status = PASS if passed else FAIL
    print(f"  {status}  {name}")
    if not passed:
        all_passed = False

print("=" * 60)
if all_passed:
    print("  All 4 emails sent successfully via Brevo!")
    print(f"  Check inbox: {TEST_RECIPIENT_EMAIL}")
else:
    print("  Some emails failed. Check the error messages above.")
print("=" * 60)
