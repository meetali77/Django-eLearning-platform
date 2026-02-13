# eLearning Platform


## Features
Authentication & Roles

Custom user model with role-based access (Student / Teacher)
Separate registration flows for students and teachers
Profile photo upload during registration
Secure login/logout with Django's built-in authentication

## For Teachers

Create courses with title, description, and uploadable materials
Manage enrollments — view enrolled students, remove or block/unblock students
Receive notifications when a student enrolls in their course
Search users — filter by role, name, or email with pagination and optional blocked-user exclusion
Mark all notifications as read in one click

## For Students

Browse available courses and enroll with a single click
View enrolled courses and access course details and materials
Leave feedback on courses they are enrolled in
Blocked student handling — students blocked from a course cannot re-enroll

## Real-Time Course Chat

WebSocket-powered group chat per course using Django Channels
Only the course teacher and enrolled students can access the chat room
Join/leave system messages broadcast to the group
Backed by Redis as the channel layer for message brokering

## Additional

Flash message notifications with Bootstrap styling

## Tech Stack

LayerTechnologyBackendPython, Django 4+Real-TimeDjango Channels, Daphne, WebSocketsMessage BrokerRedisDatabaseSQLite (development)FrontendHTML, Bootstrap 5, JavaScriptAPI (future)Django REST FrameworkFile HandlingPillow (image uploads)
Status update system (24-hour rolling window, one active status per user)
Django REST Framework installed for future API expansion
Responsive UI built with Bootstrap 5 and Bootstrap Icons

## Installation
Clone the repository
git clone https://github.com/YOUR_USERNAME/elearning-platform.git
cd elearning-platform/elearning_platform

## Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

## Install dependencies
pip install -r requirements.txt

## Apply database migrations
python manage.py migrate

## Create a superuser (optional, for admin access)
python manage.py createsuperuser

## Terminal 1 — Start Redis
redis-server

## Terminal 2 — Start the Django development server
python manage.py runserver

With daphne in INSTALLED_APPS, Django automatically uses the ASGI server, enabling WebSocket support for the chat feature.
Open your browser and navigate to http://127.0.0.1:8000/.

## Key Design Decisions

Custom User Model — extends Django's AbstractUser with an is_teacher flag and optional photo field, enabling clean role-based access control throughout the app.
Course Blocking — a separate CourseBlock model ensures blocked students cannot re-enroll, with teachers able to block/unblock at the course level.
WebSocket Authentication — the chat consumer uses AuthMiddlewareStack to verify the user's session, and checks enrollment status before allowing access to the chat room.
24-Hour Status Window — status updates auto-expire after 24 hours, keeping the dashboard clean without requiring manual cleanup.
