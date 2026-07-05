# Smart Waste Reporting & Management System

> A full-stack, role-based web application that enables citizens to report waste issues to their municipality and allows admins to track, update, and resolve complaints in real time.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Screenshots](#screenshots)
- [Project Workflow](#project-workflow)
- [Folder Structure](#folder-structure)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Email Notifications](#email-notifications)
- [Future Enhancements](#future-enhancements)
- [Troubleshooting](#troubleshooting)

---

## Project Overview

The **Smart Waste Reporting & Management System** is a production-ready web application built with Python (Flask) and PostgreSQL. It provides separate portals for citizens and municipality administrators.

Citizens can submit geo-tagged waste complaints with photos. The system automatically routes each complaint to the correct municipality admin, who can track progress, update status, and add remarks. All status changes are recorded in a full audit trail, and automatic email notifications are sent at every step via the **Brevo Transactional Email API**.

---

## Features

### Citizen Portal
- Secure registration and login
- Interactive Google Maps location picker to geo-tag the complaint location
- Upload complaint photos (validated, UUID-named, max 5 MB)
- Choose waste category (Overflowing Bin, Illegal Dumping, etc.)
- Real-time complaint tracking with full status history timeline
- View municipality contact details per complaint
- Receive automatic email notifications at every step

### Municipality Admin Portal
- Secure admin registration linked to a specific municipality
- Dashboard with Chart.js analytics (status breakdown, category trends, monthly timeline)
- Paginated complaint list with filters
- Update complaint status (Pending → In Progress → Resolved) with remarks
- Complete audit trail for every status change
- Municipality Profile page to manage public contact information

### System Features
- Role-based authentication (Citizen vs. Admin)
- CSRF protection on all forms
- IST (Indian Standard Time) timestamps throughout
- Automatic email notifications via Brevo (Welcome, Complaint Submitted, Status Updated, Resolved)
- Auto-migration of new database columns on startup (no manual ALTER TABLE needed)
- Fail-safe email sending (errors are logged, application never crashes)

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.13, Flask 3.0 |
| **Database** | PostgreSQL 15+, SQLAlchemy ORM |
| **Authentication** | Flask-Login, Werkzeug password hashing |
| **Forms & Validation** | Flask-WTF, WTForms, CSRF protection |
| **Frontend** | HTML5, CSS3, Bootstrap 5, Jinja2 templates |
| **Maps** | Google Maps JavaScript API + Geocoding API |
| **Charts** | Chart.js |
| **Email** | Brevo Transactional Email REST API |
| **Environment** | python-dotenv |
| **Migrations** | Flask-Migrate (Alembic) |

---

## Screenshots

> Screenshots from the live application:

### Landing Page
![Landing Page](docs/screenshots/landing_page.png)

### Citizen Dashboard
![Citizen Dashboard](docs/screenshots/citizen_dashboard.png)

### Submit Complaint (with Google Maps)
![Complaint Form](docs/screenshots/complaint_form.png)

### Admin Complaint Details
![Admin Complaint Details](docs/screenshots/admin_complaint_details.png)

---

## Project Workflow

```
Citizen Registers
      │
      ▼
Brevo sends Welcome Email
      │
      ▼
Citizen submits complaint
(selects location on Google Maps, uploads photo, picks category)
      │
      ▼
Complaint routed to correct Municipality Admin
Brevo sends Complaint Submitted confirmation email
      │
      ▼
Admin reviews complaint on dashboard
      │
      ├──► Admin updates status to "In Progress"
      │         │
      │         ▼
      │    Brevo sends Status Updated email to citizen
      │
      └──► Admin marks complaint as "Resolved"
                │
                ▼
           Brevo sends Complaint Resolved email to citizen
```

---

## Folder Structure

```
swm/
├── app.py                    # Application factory + auto-migration logic
├── config.py                 # Configuration classes (Dev/Prod)
├── extensions.py             # Flask extensions (DB, Migrate, LoginManager, CSRF)
├── seed.py                   # Database seeder (creates tables + 20 municipalities)
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variable template (safe to commit)
├── .gitignore                # Git ignore rules
│
├── models/                   # SQLAlchemy ORM models
│   ├── municipality.py       # Municipality + contact info fields
│   ├── citizen.py            # Citizen user model
│   ├── admin.py              # Admin user model
│   ├── complaint.py          # Complaint model with geo fields
│   └── status_history.py     # Audit trail model
│
├── routes/                   # Flask Blueprint routes
│   ├── main.py               # Landing page, 404 handler
│   ├── auth.py               # Citizen/Admin registration & login
│   ├── citizen.py            # Citizen dashboard, complaint submit & view
│   └── admin.py              # Admin dashboard, status updates, profile
│
├── utilities/
│   ├── helpers.py            # Image upload helper, admin-required decorator
│   └── notifications.py      # Brevo email notification functions
│
├── static/
│   ├── css/style.css         # Custom theme, gradients, animations
│   ├── js/charts.js          # Chart.js dashboard logic
│   ├── js/maps.js            # Google Maps API integration
│   └── uploads/              # User-uploaded images (git-ignored)
│
└── templates/
    ├── base.html             # Base layout (navbar, footer)
    ├── main/                 # Landing page & 404
    ├── auth/                 # Login & registration pages
    ├── citizen/              # Citizen dashboard, form, complaint details
    └── admin/                # Admin dashboard, complaint details, profile
```

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 13 or higher
- A Google Maps API key (Maps JavaScript API + Geocoding API enabled)
- A Brevo account for email notifications (free tier: 300 emails/day)

### Step 1 — Clone the Repository

```bash
git clone https://github.com/chandu779979/smart-waste-reporting-system.git
cd smart-waste-reporting-system
```

### Step 2 — Create & Activate Virtual Environment

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS/Linux
```

Open `.env` and fill in your values (see [Environment Variables](#environment-variables) below).

---

## Environment Variables

Copy `.env.example` to `.env` and fill in all values. **Never commit `.env`.**

```env
# Flask
SECRET_KEY=replace_with_a_secure_random_string_in_production
FLASK_APP=app.py
FLASK_ENV=development

# PostgreSQL Database
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/swm_db

# Google Maps API
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_MAPS_API_KEY_HERE

# Upload Settings
MAX_CONTENT_LENGTH=5242880

# Brevo Transactional Email API
BREVO_API_KEY=
MAIL_FROM=your_verified_sender@example.com
MAIL_FROM_NAME=Smart Waste Management System
```

### How to get your keys

| Key | Where to get it |
|---|---|
| `SECRET_KEY` | Run `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | Your local PostgreSQL credentials |
| `GOOGLE_MAPS_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services |
| `BREVO_API_KEY` | [app.brevo.com](https://app.brevo.com) → Transactional → Settings → API Keys |
| `MAIL_FROM` | A verified sender address in your Brevo account |

---

## Database Setup

1. Start PostgreSQL and create the database:

```sql
CREATE DATABASE swm_db;
```

2. Run the seed script to create all tables and load 20 municipalities:

```bash
python seed.py
```

---

## Running the Application

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

### Sample Test Accounts (register them via the web UI)

| Role | Name | Email | Password |
|---|---|---|---|
| Citizen | Jane Doe | jane@gmail.com | password123 |
| Admin | Officer John | john@municipality.gov.in | adminpass |

> Admin must select a municipality during registration.

---

## Email Notifications

The system uses **Brevo Transactional Email API** to send automatic emails.

| Trigger | Email Subject |
|---|---|
| Citizen registers | Welcome to Smart Waste Reporting & Management System |
| Complaint submitted | Complaint Submitted Successfully |
| Admin updates status | Complaint Status Updated |
| Admin marks Resolved | Complaint Successfully Resolved |

- If `BREVO_API_KEY` is blank, emails are silently skipped (logged only).
- The application **never crashes** due to email failures.

---

## Future Enhancements

- [ ] Push notifications (Web Push / Firebase Cloud Messaging)
- [ ] Citizen complaint rating & feedback after resolution
- [ ] Admin bulk status update
- [ ] SMS notifications via Twilio
- [ ] Multi-language support (Telugu, Hindi)
- [ ] Mobile-responsive PWA (Progressive Web App)
- [ ] Heatmap of complaint hotspots on the admin map view
- [ ] Auto-escalation if complaint is not addressed within SLA (e.g., 48 hours)
- [ ] Public-facing complaint tracker (without login)
- [ ] Docker + deployment guide for cloud hosting (Render / Railway / AWS)

---

## Troubleshooting

### `pg_config executable not found` (pip install failure)
Use `psycopg2-binary==2.9.12` or newer — it contains pre-compiled binaries for Python 3.13 on Windows x64.

### `Connection refused (10061)` on port 5432
PostgreSQL is not running. On Windows: `Win + R` → `services.msc` → Start `postgresql-x64-xx`.

### Google Map shows "For development purposes only"
Billing is not enabled on your Google Cloud project, or the API key is not set in `.env`.

### Emails not sending
- Check `BREVO_API_KEY` is set in `.env`.
- Ensure `MAIL_FROM` is a verified sender in your Brevo account.
- Check the Flask terminal for `[Brevo]` log lines.

---

## License

This project is for educational and demonstration purposes.

---

*Built with Flask, PostgreSQL, and Brevo · Designed for Smart City Waste Management*
