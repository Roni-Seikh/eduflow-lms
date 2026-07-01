<div align="center">

<img src="./screenshots/logo.png" alt="EduFlow LMS Logo" width="120" height="120"/>

# 🎓 EduFlow LMS

### A Production-Ready Learning Management System

**Built with Flask · MySQL · Tailwind CSS · Cloudinary · ReportLab**

<br/>

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-EduFlow_LMS-4f46e5?style=for-the-badge)](https://eduflow-lms-7ew2.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Roni--Seikh-181717?style=for-the-badge&logo=github)](https://github.com/Roni-Seikh)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Roni_Seikh-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/roniseikh)
[![YouTube](https://img.shields.io/badge/YouTube-Coming_Soon-FF0000?style=for-the-badge&logo=youtube)](https://youtube.com/@roniscreation3672)

<br/>

> 🚀 **Live at:** [https://eduflow-lms-7ew2.onrender.com](https://eduflow-lms-7ew2.onrender.com)
> 📂 **Source Code:** [github.com/Roni-Seikh/eduflow-lms](https://github.com/Roni-Seikh/eduflow-lms)

</div>

---

## 📺 Video Walkthrough

> 🎥 **A full YouTube walkthrough is coming soon!**
> Subscribe to get notified when it drops 👉 [youtube.com/@roniscreation3672](https://youtube.com/@roniscreation3672)

---

## 📸 Screenshots

### 🔐 Login & Registration
| Select Portal | Admin Login | Student Register |
|---|---|---|
| ![Select Login](./screenshots/logo.png) | ![Admin Login](./screenshots/admin-login.png) | ![Student Register](./screenshots/student-register.png) |

### 🛡️ Admin Portal
| Dashboard | Manage Students | Manage Faculty |
|---|---|---|
| ![Admin Dashboard](./screenshots/admin-dashboard.png) | ![Students](./screenshots/admin-students.png) | ![Faculty](./screenshots/admin-faculty.png) |

| Manage Courses | Notifications | Password Requests |
|---|---|---|
| ![Courses](./screenshots/admin-courses.png) | ![Notifications](./screenshots/admin-notifications.png) | ![Password Requests](./screenshots/admin-password-requests.png) |

### 👩‍🏫 Faculty Portal
| Dashboard | My Courses | Create Exam |
|---|---|---|
| ![Faculty Dashboard](./screenshots/faculty-dashboard.png) | ![My Courses](./screenshots/faculty-courses.png) | ![Create Exam](./screenshots/faculty-exams.png) |

| Add Questions | Recorded Lectures | Live Classes |
|---|---|---|
| ![Exam Questions](./screenshots/faculty-exam-questions.png) | ![Lectures](./screenshots/faculty-lectures.png) | ![Live Classes](./screenshots/faculty-live-classes.png) |

| Mark Attendance | My Students | Notifications |
|---|---|---|
| ![Attendance](./screenshots/faculty-attendance.png) | ![Students](./screenshots/faculty-students.png) | ![Notifications](./screenshots/faculty-notifications.png) |

### 👨‍🎓 Student Portal
| Dashboard | My Courses | Exam Interface |
|---|---|---|
| ![Student Dashboard](./screenshots/student-dashboard.png) | ![My Courses](./screenshots/student-courses.png) | ![Exam](./screenshots/student-exam.png) |

| Exam Result | Course Certificate | Exam Certificate |
|---|---|---|
| ![Result](./screenshots/student-exam-result.png) | ![Course Cert](./screenshots/certificate-course.png) | ![Exam Cert](./screenshots/certificate-exam.png) |

---

## ✨ Features

### 🔐 Three Role-Based Portals

EduFlow LMS supports **three completely separate portals** — Admin, Faculty, and Student — each with their own login page, dashboard, sidebar, and access control. Every route is protected by both `@login_required` and a role-specific decorator that blocks cross-role access at the server level.

**Admin Portal**
- Full control over all users, courses, exams, and data
- Add/edit/delete students and faculty with profile photos
- View all enrolled students and exam results system-wide
- Approve or reject password reset requests with one click
- Send notifications to everyone, a specific role, or one individual by LMS ID
- View full activity logs of every login, action, and event
- Dark/light mode toggle persisted in local storage

**Faculty Portal**
- Create and manage courses with thumbnails, categories, and levels
- Schedule live classes with meeting links and duration
- Upload recorded lectures with optional video file or YouTube/Vimeo URL, plus PDF notes
- Build MCQ exams with configurable duration and pass threshold
- Add/delete questions, randomise question order per exam session
- Mark daily attendance course-by-course with Present/Absent/Late status
- View enrolled students grouped by course with live progress bars
- Close or reopen courses; enrolled students are notified automatically
- Send targeted notifications to admin, all students, a specific course's students, or one student by ID

**Student Portal**
- Browse all active courses and self-enroll
- Watch recorded lectures and mark them complete — progress auto-updates
- Join live classes via provided meeting links
- Take timed exams with fullscreen enforcement and anti-cheat monitoring
- View detailed exam results with question-by-question answer review
- Track attendance percentage per course
- Download or view course completion and exam certificates as PDFs
- Verify any certificate via a public QR code — no login required
- Send queries to admin or faculty directly from the portal

---

### 📝 Exam Engine

The exam system is built for fairness and security:

- **Randomised question order** — every student sees questions in a different sequence
- **Countdown timer** — auto-submits when time expires, logged as "auto-submit"
- **Anti-cheat system** — detects and logs:
  - Tab switching or window blur
  - Copy/paste attempts
  - Exiting fullscreen
  - Paste events on option fields
- **Instant scoring** — percentage calculated immediately on submission
- **Pass/fail threshold** — configurable per exam (default 60%)
- **One attempt per exam** — students cannot retake (prevents gaming the system)
- **Cheat log visible to faculty** — faculty can see every violation per student per exam

---

### 🏆 Certificate System

**Course Completion Certificates**
- Premium gold double-border design on landscape A4
- Dark blue header bar with institution name
- Student name with underline signature treatment
- Faculty signature + Admin/Director signature
- Light watermark background
- Issue date and unique Certificate ID
- **Scannable QR code** — links to a public `/verify/<cert_id>` page that anyone (employers, institutions) can use to confirm the certificate is authentic, with no login required

**Exam Achievement Certificates**
- Clean professional blue-themed design
- Issued instantly upon passing any exam
- Same unique ID and verification system

**Certificate Privacy**
- If a course is deleted, the student's certificate is preserved (course link is nulled, certificate itself is not deleted)
- Students can retroactively claim certificates with the "Refresh Certificates" button if they passed before the system was set up

---

### 🔔 Private Notification System

Every notification is **strictly private** — a message sent to one person is never visible to any other user, including other admins. This is enforced at the SQL query level, not just at the template level.

| Sender | Can Send To |
|---|---|
| **Admin** | Everyone · All Students · All Faculty · Individual (by LMS ID) |
| **Faculty** | Admin · All Students · Students in a specific course · One student (by ID) |
| **Student** | Admin only · A specific faculty member (by ID) · All faculty of enrolled courses |

Students **cannot** message other students — enforced by hiding that option entirely and by the backend query never returning student-to-student messages.

---

### 📊 Progress Tracking

Course progress is calculated dynamically from two components:

- **60% weight** — lecture completion (marking recorded lectures as watched)
- **40% weight** — exam performance (passing exams in the course)

A course with no lectures defaults to 100% lecture score; a course with no exams defaults to 100% exam score. This means even a lectures-only or exams-only course tracks correctly. When progress hits 100%, the course certificate is automatically issued and the enrollment is marked complete.

---

### 🔒 Security Features

| Feature | Implementation |
|---|---|
| Password hashing | bcrypt with salt rounds |
| CSRF protection | Flask-WTF on every POST form |
| Math CAPTCHA | On all 3 login pages + registration |
| Role guards | Custom decorators on every route (`@admin_required`, `@faculty_required`, `@student_required`) |
| Session security | `HTTPOnly`, `SameSite=Lax`, 2-hour expiry |
| SQL injection protection | SQLAlchemy ORM (no raw SQL in application code) |
| Password policy | Min 8 chars, uppercase, lowercase, digit, and special character enforced |
| File upload filtering | Extension whitelist for images, videos, and PDFs |
| Notification privacy | Recipient role + ID required for individual messages; query-level filtering |
| Anti-cheat logging | Tab-switch, copy/paste, fullscreen-exit all logged with timestamps |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Backend** | Python 3.11, Flask 3.0 | Lightweight, flexible, production-ready |
| **Database** | MySQL 8.0 (Clever Cloud) | Robust, relational, cloud-hosted free tier |
| **ORM** | SQLAlchemy 2.0 + PyMySQL | Safe queries, no raw SQL |
| **Auth** | Flask-Login, bcrypt | Session-based auth with secure password hashing |
| **Forms** | Flask-WTF, WTForms | CSRF protection on every form |
| **Email** | Flask-Mail (Gmail SMTP) | Password reset & notification emails |
| **Frontend** | Tailwind CSS, JavaScript | Utility-first, responsive, no build step |
| **Icons** | Font Awesome 6 | Consistent icon language |
| **Charts** | Chart.js | Dashboard statistics |
| **PDFs** | ReportLab | Certificate generation with custom design |
| **QR Codes** | qrcode[pil] | Scannable certificate verification |
| **File Storage** | Cloudinary (free 25GB) | Permanent cloud storage for uploads |
| **Hosting** | Render (free Web Service) | Always-on free tier |
| **WSGI** | Gunicorn | Production-grade server |

---

## 📁 Project Structure

```
eduflow-lms/
├── app.py                          # Application factory, Flask-Mail setup
├── requirements.txt
├── Procfile                        # Render deployment start command
├── .python-version                 # Pins Python 3.11.9 for Render
├── .gitignore
├── .env.example
├── database_full_setup.sql         # Complete MySQL schema (run once)
│
├── config/
│   └── config.py                   # MySQL + Clever Cloud + Mail config
│
├── models/
│   └── models.py                   # All SQLAlchemy ORM models
│
├── routes/
│   ├── auth.py                     # Login, register, logout, CAPTCHA
│   ├── admin.py                    # Admin blueprint (16 routes)
│   ├── faculty.py                  # Faculty blueprint (17 routes)
│   ├── student.py                  # Student blueprint (14 routes)
│   └── api.py                      # AJAX/JSON endpoints
│
├── utils/
│   ├── helpers.py                  # Decorators, certificate PDF, validators, CAPTCHA
│   ├── notification_helper.py      # Privacy-safe notification query functions
│   └── email_helper.py             # Flask-Mail HTML email templates
│
├── templates/
│   ├── shared/                     # base.html, 404, 500, verify_certificate
│   ├── auth/                       # Login, register, forgot password pages
│   ├── admin/                      # 10 admin pages
│   ├── faculty/                    # 11 faculty pages
│   └── student/                    # 11 student pages
│
└── static/
    ├── css/                        # Custom styles
    ├── js/                         # Custom scripts
    └── uploads/                    # Local upload fallback (dev only)
        ├── profiles/
        ├── thumbnails/
        ├── videos/
        ├── pdfs/
        └── certificates/
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.11+
- MySQL 8.0+ (local) or a free Clever Cloud MySQL account
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Roni-Seikh/eduflow-lms.git
cd eduflow-lms
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

Open your MySQL client (phpMyAdmin, MySQL Workbench, or CLI) and run:

```bash
mysql -u root -p lms_db < database_full_setup.sql
```

Or paste the contents of `database_full_setup.sql` into phpMyAdmin's SQL tab and run.

### 5. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-random-32-char-string
FLASK_ENV=development

# Local MySQL
DB_HOST=localhost
DB_PORT=3306
DB_NAME=lms_db
DB_USER=root
DB_PASSWORD=your_password

# Optional — Cloudinary for file uploads
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Optional — Gmail for real emails
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-app-password
```

### 6. Run the application

```bash
python app.py
```

Visit: **http://127.0.0.1:5000**

> ⚠️ If using a cloud MySQL with a 5-connection limit (like Clever Cloud's free tier), add `use_reloader=False` to the `app.run()` call to prevent the auto-reloader from opening extra connections.

---

## 🔐 Default Login Credentials

> ⚠️ **Change these immediately after first login.**

| Role | Login | Password |
|---|---|---|
| **Admin** | `admin@lms.com` | `Admin@123` |
| **Faculty** | Created by Admin | Set on creation |
| **Student** | Self-register at `/auth/student/register` | Set on registration |

### Login Portals

| Portal | URL |
|---|---|
| Select Role | `/` |
| Admin Login | `/auth/admin/login` |
| Faculty Login | `/auth/faculty/login` |
| Student Login | `/auth/student/login` |
| Student Register | `/auth/student/register` |

---

## 🪪 ID System

| Role | Format | Example |
|---|---|---|
| Student | `LMS/S/YY/NN` | `LMS/S/26/01` |
| Faculty | `LMS/F/YY/NN` | `LMS/F/26/01` |

IDs are auto-generated in sequence when a user is created. Faculty can look up students and vice versa using these IDs in the notification system.

---

## 🔑 Password Policy

Every password must satisfy all of these:

- ✅ Minimum **8 characters**
- ✅ At least **1 uppercase** letter (A–Z)
- ✅ At least **1 lowercase** letter (a–z)
- ✅ At least **1 digit** (0–9)
- ✅ At least **1 special character** (`@`, `#`, `!`, `$`, `%`, `^`, `&`, `*`, etc.)

Enforced on registration, admin-side creation, and password change — both client-side (immediate feedback) and server-side (cannot be bypassed).

---

## ☁️ Production Deployment

### Hosting Stack

| Service | What it hosts | Cost |
|---|---|---|
| **Render** | Web application (Flask + Gunicorn) | Free forever |
| **Clever Cloud** | MySQL 8.0 database | Free DEV tier |
| **Cloudinary** | File uploads (photos, PDFs, certificates, videos) | Free (25GB) |

### Environment Variables on Render

| Key | Value |
|---|---|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate random 32+ char string |
| `DATABASE_URL` | `mysql+pymysql://USER:PASS@HOST:3306/DBNAME` |
| `APP_BASE_URL` | `https://eduflow-lms-7ew2.onrender.com` |
| `MAIL_USERNAME` | Your Gmail address |
| `MAIL_PASSWORD` | Your Gmail App Password |

### Deploy from GitHub

```bash
git add .
git commit -m "deploy"
git push
```

Render auto-deploys on every push to `main`.

---

## 📧 Email Setup (Gmail)

For real email notifications (password resets, new message alerts):

1. Go to your Google Account → Security → **2-Step Verification** (enable it)
2. Then go to → **App Passwords**
3. Create a new App Password for "Mail" + "Windows Computer"
4. Copy the 16-character password and set it as `MAIL_PASSWORD` in your `.env` or Render environment variables
5. Set `MAIL_USERNAME` to your full Gmail address

> **Never use your real Gmail password** — App Passwords are separate and can be revoked anytime.

---

## 🧰 Troubleshooting

| Error | Fix |
|---|---|
| `No module named 'MySQLdb'` | Change your `DATABASE_URL` to use `mysql+pymysql://` instead of `mysql://` |
| `max_user_connections exceeded` | Click "Kill all connections" on Clever Cloud, then restart your app with `use_reloader=False` |
| `Unknown column 'is_closed'` | Run `add_missing_columns.sql` in phpMyAdmin |
| `unable to open database file` | Only applies to SQLite config; ensure `instance/` directory exists |
| `BuildError: could not build url for endpoint` | A template references a route name that doesn't match `routes/faculty.py` — check function names |
| App sleeps on first visit | Normal Render free tier behaviour — takes ~30 sec to wake from idle |
| Certificate QR code wrong URL | Set `APP_BASE_URL` environment variable to your real Render URL |
| CSRF error on form | Clear browser cookies and try again |
| CAPTCHA always wrong | Ensure browser cookies/sessions are enabled |

---

## 🗺️ Roadmap

- [ ] Real-time notifications via WebSocket (Flask-SocketIO)
- [ ] Email digest — daily summary of new notifications
- [ ] Bulk import students/faculty via CSV upload
- [ ] Course ratings and student feedback
- [ ] Assignment submission with file upload
- [ ] Discussion forum per course
- [ ] Mobile app (React Native) using the same backend API
- [ ] Payment gateway for paid course enrollment
- [ ] Multi-language support (i18n)
- [ ] Admin analytics dashboard with charts for engagement trends

---

## 🤝 Connect With Me

<div align="center">

Built with ❤️ by **Roni Seikh**

| Platform | Link |
|---|---|
| 💼 **LinkedIn** | [linkedin.com/in/roniseikh](https://www.linkedin.com/in/roniseikh) |
| 💻 **GitHub** | [github.com/roniseikh](https://github.com/Roni-Seikh) |
| 📺 **YouTube** | [youtube.com/@roniseikh](https://youtube.com/@roniscreation3672) *(video coming soon)* |
| 🌐 **Live Project** | [eduflow-lms-7ew2.onrender.com](https://eduflow-lms-7ew2.onrender.com) |

If this project helped you or inspired you, consider giving it a ⭐ on GitHub — it means a lot!

</div>

---

## 📜 License

This project is open source and available for educational and personal use.
Feel free to fork, learn from, and build upon it.

---

<div align="center">

**EduFlow LMS** — *Empowering Education, One Course at a Time* 🎓

</div>
