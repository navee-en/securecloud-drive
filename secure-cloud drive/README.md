# Secure Cloud Drive using Flask and AWS S3

## Project Description

Secure Cloud Drive is a web-based cloud storage application inspired by Google Drive. The application allows users to securely upload, manage, preview, share, and download files stored in Amazon S3.

The project was developed using Python Flask and AWS S3 with secure authentication and file versioning features.

---

# Features

## Authentication

* User Registration
* User Login
* Google OAuth 2.0 Login
* Session Management

## Cloud Storage

* AWS S3 Integration
* Secure File Upload
* File Download
* File Deletion

## File Management

* File Versioning
* Search Files
* File Preview
* Public Sharing Links

## Security Features

* File Encryption
* Secure Authentication
* Activity Logging

## Admin Features

* Admin Dashboard
* User Management
* File Management
* Storage Analytics

---

# Technologies Used

## Frontend

* HTML5
* CSS3
* JavaScript
* Bootstrap Icons
* Chart.js

## Backend

* Python
* Flask
* Flask-Login
* Flask-SQLAlchemy
* Flask-Dance

## Database

* SQLite

## Cloud Platform

* Amazon Web Services (AWS S3)

## Security

* OAuth 2.0
* Cryptography (Fernet)

---

# System Architecture

User
↓
Flask Web Application
↓
Authentication System
↓
AWS S3 Storage
↓
SQLite Database

---

# Modules

1. Authentication Module
2. File Upload Module
3. File Download Module
4. File Versioning Module
5. Public Sharing Module
6. File Preview Module
7. Activity Log Module
8. Admin Dashboard Module

---

# Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/secure-cloud-drive.git
```

Move into the project directory:

```bash
cd secure-cloud-drive
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

---

# Project Structure

secure-cloud-drive/

├── app.py

├── models.py

├── config.py

├── s3_service.py

├── encryption.py

├── requirements.txt

├── README.md

├── Procfile

├── templates/

├── static/

└── screenshots/

---

# Screenshots

* Home Page
* Login Page
* User Dashboard
* Upload File
* File Preview
* Share File
* Admin Dashboard
* AWS S3 Bucket

---

# Future Enhancements

* Two Factor Authentication
* Malware Scanning
* Multi-file Upload
* Email Notifications
* Mobile Application
* Docker Deployment
* PostgreSQL Integration

---

# Conclusion

The Secure Cloud Drive project successfully implements a secure cloud storage system similar to Google Drive using AWS S3 and Flask. The application supports OAuth authentication, file versioning, sharing capabilities, and several advanced security features.

---

# Author

Navee

B.Sc Computer Science (Cybersecurity)
