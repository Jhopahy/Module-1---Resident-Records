# Module 1 – Resident Records

A web-based **Barangay Resident Record Management System** built with **Flask** and **SQLite**. This application allows barangay personnel to manage resident information through an easy-to-use web interface with secure authentication.

---

## Features

- User Login Authentication
- Dashboard Overview
- Add New Residents
- Edit Resident Information
- Delete Resident Records
- Search Residents
- Resident Reports
- SQLite Database Storage
- REST API Endpoints
- Responsive User Interface

---

## Built With

- Python 3.x
- Flask
- SQLite3
- HTML5
- CSS3
- JavaScript
- Flask-CORS
- Werkzeug Security

---

## Project Structure

```
barangay_resident_records/
│
├── app.py                 # Main Flask application
├── config.py              # Application configuration
├── database.py            # Database initialization
├── users.db               # User authentication database
│
├── routes/
│   ├── dashboard.py
│   ├── residents.py
│   ├── reports.py
│   ├── pages.py
│   └── api.py
│
├── templates/             # HTML templates
├── static/                # CSS, JavaScript, Images
└── instance/              # SQLite database files
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Jhopahy/Module-1---Resident-Records.git
```

### 2. Open the project

```bash
cd Module-1---Resident-Records
```

### 3. Create a virtual environment

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install flask flask-cors werkzeug
```

or

```bash
pip install -r requirements.txt
```

---

## Running the Application

Start the Flask server:

```bash
python app.py
```

The application will be available at:

```
http://127.0.0.1:5000
```

---

## Default Login Credentials

| Username | Password |
|----------|----------|
| admin | adminpass |
| staff | staffpass |

> These accounts are intended for development and demonstration purposes only.

---

## Database

The project uses **SQLite** for data storage.

The application automatically initializes the required database tables when it starts.

---

## Main Modules

- Dashboard
- Resident Management
- Reports
- API Services
- Authentication

---

## Security

The application includes:

- Password hashing using Werkzeug
- Session-based authentication
- Protected routes
- Configurable secret key

---

## Future Improvements

- Role-based access control
- Resident profile photos
- QR Code generation
- Export reports to PDF
- Excel import/export
- Audit logs
- Backup and restore functionality

---

## Academic Project

This project was developed as part of a **Bachelor of Science in Information Technology (BSIT)** coursework for a Barangay Record Management System.

---

## License

This project is intended for educational purposes.
