# EduFlow LMS — Learning Management System

A full-stack Learning Management System built with **Flask**, **MySQL**, **Tailwind CSS**, and **JavaScript**.  
Features three separate portals (Admin, Faculty, Student), live/recorded classes, MCQ exams with anti-cheat, attendance tracking, PDF certificates, and a modern dark/light mode UI.

---

## 🚀 Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Python Flask, Flask-Login, SQLAlchemy |
| Database  | MySQL (via phpMyAdmin)              |
| Frontend  | Tailwind CSS, Chart.js, Font Awesome |
| PDF       | ReportLab                           |
| Auth      | bcrypt, Flask-WTF CSRF              |

---

## 📁 Project Structure

```
lms/
├── app.py                  # App factory & entry point
├── requirements.txt
├── .env.example
├── database.sql            # Complete MySQL schema
├── config/
│   └── config.py           # Flask configuration
├── models/
│   └── models.py           # SQLAlchemy ORM models
├── routes/
│   ├── auth.py             # Login, register, logout
│   ├── admin.py            # Admin blueprint
│   ├── faculty.py          # Faculty blueprint
│   ├── student.py          # Student blueprint
│   └── api.py              # AJAX API endpoints
├── utils/
│   └── helpers.py          # Utilities, cert generator
├── templates/
│   ├── shared/             # base.html, 404.html
│   ├── auth/               # All login/register pages
│   ├── admin/              # Admin dashboard & pages
│   ├── faculty/            # Faculty portal pages
│   └── student/            # Student portal pages
└── static/
    └── uploads/            # Profile pics, thumbnails, videos, PDFs, certs
```

---

## ⚙️ Setup Instructions

### 1. Prerequisites

- Python 3.10+
- MySQL Server (or XAMPP/WAMP with phpMyAdmin)
- pip

### 2. Clone & Install

```bash
# Clone or extract the project
cd lms

# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
SECRET_KEY=your-super-secret-key-min-32-chars
FLASK_ENV=development

DB_HOST=localhost
DB_PORT=3306
DB_NAME=lms_db
DB_USER=root
DB_PASSWORD=your_mysql_password
```

### 4. Set Up MySQL Database (phpMyAdmin)

1. Open phpMyAdmin → `http://localhost/phpmyadmin`
2. Click **New** → Create database named `lms_db`
3. Select `lms_db` → click **Import**
4. Choose `database.sql` → Click **Go**

**Or via MySQL CLI:**
```bash
mysql -u root -p < database.sql
```

### 5. Run the Application

```bash
python app.py
```

Visit: **http://127.0.0.1:5000**

---

## 🔐 Default Admin Login

| Field    | Value            |
|----------|------------------|
| Email    | admin@lms.com    |
| Password | Admin@123        |

> ⚠️ Change the admin password immediately after first login!

---

## 👥 Login Portals

| Portal  | URL                        | Login Method           |
|---------|----------------------------|------------------------|
| Select  | `/`                        | Choose your role       |
| Admin   | `/auth/admin/login`        | Email only             |
| Faculty | `/auth/faculty/login`      | Faculty ID or Email    |
| Student | `/auth/student/login`      | Student ID or Email    |
| Register| `/auth/student/register`   | Students self-register |

---

## 🪪 ID Format

| Role    | Format         | Example        |
|---------|----------------|----------------|
| Student | LMS/S/YY/NN    | LMS/S/26/01    |
| Faculty | LMS/F/YY/NN    | LMS/F/26/01    |

IDs are auto-generated on account creation.

---

## 🔒 Password Policy

Passwords must contain:
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character (e.g. `@#$!`)

---

## 🎓 Features Overview

### Admin Portal
- Dashboard with analytics (Chart.js)
- Student & Faculty management (CRUD + search + pagination)
- Course & Exam monitoring
- Attendance records
- Password reset requests handling
- Broadcast notifications
- Activity logs

### Faculty Portal
- Course creation (with thumbnail upload)
- Schedule live classes (with meeting links)
- Upload recorded lectures (video URL + file + PDF notes)
- Create MCQ exams (dynamic question builder, randomization)
- Mark attendance (Present / Late / Absent)
- View exam results & cheating logs

### Student Portal
- Self-registration with password strength meter
- Browse & enroll in courses
- Watch live & recorded lectures
- Download PDF notes
- Timer-based MCQ exams with anti-cheat
- View results with answer review
- Auto-generated PDF certificates
- Attendance percentage tracker
- Notifications inbox

### Anti-Cheat System
- Full-screen enforcement
- Tab-switch detection
- Right-click disabled
- Copy/paste/cut disabled
- DevTools keyboard shortcut blocking
- Auto-submit on repeated violations
- Cheating log in database

---

## 🎨 UI Features

- **Dark / Light Mode** — toggle button in navbar, saved in `localStorage`
- **Fully responsive** — mobile, tablet, laptop, desktop, 4K
- **Collapsible sidebar** on mobile (hamburger menu)
- **Smooth animations** — cards hover, sidebar transitions, form slide-up
- **Modern design** — rounded cards, gradients, subtle shadows

---

## 📜 Certificate Generation

Certificates are automatically issued as PDFs using **ReportLab** when:
- A student passes an exam (score ≥ passing %)

Certificate contains:
- Student name
- Course name
- Issue date
- Unique certificate ID (e.g. `CERT-20260601-A1B2C3D4`)
- Authorized signature line

---

## 📦 Requirements

See `requirements.txt`. Key packages:

```
Flask==3.0.0
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.1
PyMySQL==1.1.0
bcrypt==4.1.1
reportlab==4.0.7
python-dotenv==1.0.0
Pillow==10.1.0
```

---

## 🛡️ Security

- bcrypt password hashing
- CSRF protection on all forms (Flask-WTF)
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (Jinja2 auto-escaping)
- Session timeout (1 hour)
- Role-based access control decorators
- Secure file upload (extension whitelist + UUID filenames)
- Input validation on all forms

---

## 🐞 Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| DB connection error | Check `.env` DB credentials |
| `OperationalError` | Ensure MySQL is running |
| Static files 404 | Ensure `static/uploads/` directories exist |
| CSRF error | Clear browser cookies and retry |

---

## 📝 License

This project is for educational purposes. Free to use and modify.
