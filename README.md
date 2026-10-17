# msg↗ — Django Chat System

A web-based chat system built with Django, featuring user authentication, JWT-based access control, password reset functionality, and a dynamic user interface using Django Templates, HTML, CSS, and JavaScript.

## Features

- **User Registration:** Create an account with validated user information.
- **User Login:** Authenticate users using their username and password.
- **JWT Authentication:** Generate and validate JSON Web Tokens for protected pages and requests.
- **Secure Token Storage:** Store the access token in an HTTP-only cookie.
- **Password Security:** Hash passwords using Django's password-hashing utilities.
- **Password Reset:** Provide password-reset functionality through email.
- **Chat System:** Dedicated conversations app for chat-related functionality.
- **Dynamic UI:** Server-rendered Django Templates enhanced with JavaScript.
- **Environment Configuration:** Use environment variables to manage sensitive settings.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| Django Templates | Frontend rendering |
| HTML & CSS | User interface |
| JavaScript | Client-side interactions |
| JWT / PyJWT | Token-based authentication |
| MySQL / PostgreSQL / SQLite | Database, depending on configuration |
| SMTP | Email delivery |

## Project Structure

```text
messageup/
├── accounts/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── forgotpassword.html
│   │   └── resetpassword.html
│   ├── ...
├── auth/
│   ├── migrations/
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── conversations/
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── consumers.py
│   ├── routing.py
│   ├── jwt_auth.py
│   └── ...
├── messageup/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── .env.example
├── .gitignore
├── manage.py
└── requirements.txt
```

*Note: The tree is a general overview; some files may differ depending on your current implementation.*

## Requirements

- Python 3.10 or newer (depending on package compatibility)
- pip
- Git (optional)
- A configured database
- Gmail SMTP credentials or another SMTP provider if using email features

## Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd messageup
```

Navigate into the directory containing `manage.py` if necessary.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example`.

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-app-password
```

Use the exact variable names expected by your `settings.py`. Database variables may also be required depending on your configuration.

**Important:** Never commit `.env`, real credentials, Django secret keys, or email app passwords to GitHub.

### 5. Apply database migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open the local development URL:

```text
http://127.0.0.1:8000/
```

## Authentication Flow

1. A user registers with the required account information.
2. The password is hashed before being stored in the database.
3. The user submits their login credentials.
4. The backend validates the credentials.
5. On successful login, the backend generates a JWT.
6. The token is stored in an HTTP-only cookie.
7. Protected views validate the token before granting access.
8. The token expires according to its configured expiration time.

## Security Considerations

- Keep Django's `SECRET_KEY` private.
- Store credentials in environment variables.
- Never store plaintext passwords.
- Use HTTPS in production.
- Configure JWT expiration and token validation correctly.
- Keep CSRF protection enabled for browser-based requests where applicable.
- Set authentication cookies with appropriate `HttpOnly`, `Secure`, and `SameSite` attributes.
- Add rate limiting and login-attempt protections where appropriate.
- Configure `DEBUG=False` and restrict `ALLOWED_HOSTS` in production.
- Rotate any credentials that have accidentally been exposed.

## Development Notes

This project uses Django Templates rather than a separate frontend framework. HTML pages are rendered by Django, while JavaScript provides client-side interactions.

For local development, use Django's development server. A production deployment requires appropriate application-server, database, HTTPS, and static-file configuration.

## Future Improvements

- Real-time messaging with Django Channels and WebSockets.
- Conversation history and message pagination.
- Online status and typing indicators.
- Improved input validation and error handling.
- Automated tests for authentication and conversation features.
- Production deployment with HTTPS and secure cookie settings.

## Author

**Omar Yasser Hassan Zidane**

Software Engineering Student | Backend Development with Python and Django

---

*Built as a learning project to explore Django backend development, authentication, JWT, and web application security.*
