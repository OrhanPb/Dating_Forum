# Dating Forum

A modern, feature-rich dating platform built with Django. Connect, chat, and find your perfect match with advanced matching algorithms, real-time messaging, and a secure environment.

## Features

- **User Registration & Profiles:** Create detailed profiles with photos and personal information.
- **Smart Matching:** Advanced algorithm to suggest compatible matches based on interests and preferences.
- **Instant Messaging:** Real-time chat system for seamless communication.
- **Blog Platform:** Share thoughts and experiences with the community.
- **Map Integration:** View user locations (Google Maps API integrated).
- **Secure Authentication:** Password validation and user privacy prioritized.
- **Responsive Design:** Modern, mobile-friendly UI.

## Getting Started

### Prerequisites
- Python 3.8+
- Django 5.x

### Installation
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd dating_forum
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```
4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
5. **Access the app:**
   Open the URL shown in the terminal (usually http://127.0.0.1:8000/).

### Demo Accounts

#### Superuser
- **Username:** Orhan
- **Password:** Kursun@23

#### Other Users
| Username  | Password    |
|-----------|-------------|
| Try       | trytry11    |
| Barbara   | palvin11    |
| Scarlett  | blackvidow  |
| Takir     | Malatya44   |

## Technologies Used
- Django (Python Web Framework)
- SQLite (Default development database)
- Bootstrap (Frontend styling)
- Google Maps API (Location features)

## Folder Structure
- `users/` - User management, profiles, authentication
- `chat/` - Real-time messaging
- `static/` - Static files (CSS, JS, images)
- `media/` - Uploaded media (profile pictures)

## Contribution
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is for educational purposes. 