# Real-Time eLearning Platform

Full-stack educational platform with WebSocket-based real-time chat, role-based authentication, and course management system.

## 🎯 Project Overview

Interactive learning management system supporting teachers and students with real-time communication capabilities.

## ✨ Key Features

- **Real-Time Chat**: WebSocket-based course chat using Django Channels + Redis
- **Role-Based Auth**: Separate teacher/student dashboards and permissions
- **Course Management**: Full CRUD operations for courses, enrollment, feedback
- **Auto-Expiring Status Updates**: 24-hour temporary student status posts
- **Responsive UI**: Bootstrap 5 with custom CSS

## 🛠️ Technologies

**Backend:**
- Django 5.2.3
- Django Channels 4.0+
- Redis 5.0+ (message broker)
- SQLite (development) / PostgreSQL-ready

**Frontend:**
- Django Templates
- Bootstrap 5
- JavaScript (WebSocket client)

## 🏗️ Architecture

- **3-Tier Application**: Presentation, Application, Data layers
- **MVT Pattern**: Model-View-Template (Django standard)
- **WebSocket Flow**: Client → Django Channels → Redis → Broadcast to group
- **Database**: 5 normalized tables (User, Course, Enrollment, Feedback, StatusUpdate)

## 📊 Technical Highlights

- Custom User model extending AbstractUser
- ASGI deployment with Daphne server
- Redis pub/sub for horizontal scalability
- CSRF protection and session-based authentication
- Unit tests for core functionality

## 🚀 Setup & Installation

1. **Install dependencies:**
```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```

2. **Start Redis:**
```bash
   redis-server
```

3. **Run migrations:**
```bash
   python manage.py migrate
```

4. **Start server:**
```bash
   daphne -p 8000 elearning_platform.asgi:application
```

5. **Access at:** http://127.0.0.1:8000

## 📁 Project Structure
├── elearning_platform/  # Main Django project
├── core/               # Main application
│   ├── models.py      # Database models
│   ├── views.py       # Business logic
│   ├── consumers.py   # WebSocket consumers
│   ├── routing.py     # WebSocket routing
│   └── templates/     # HTML templates
├── static/            # CSS, JS files
├── requirements.txt   # Dependencies
└── README.md         # This file
## 🎓 Course Context

Developed for Web Development module. Includes comprehensive 18-page technical report analyzing architecture, implementation decisions, and trade-offs.

## 👤 Author

Meetali Mandhare - CS Student specializing in ML/AI
