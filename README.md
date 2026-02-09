# BudgetWise - Phase 1: Authentication System

Production-grade authentication system built with Django and PostgreSQL.

## Features

- User registration with validation
- Secure login/logout
- Password hashing (Django default)
- CSRF protection
- Email validation
- Strong password enforcement
- Clean, modern, responsive UI
- PostgreSQL database

## Tech Stack

- **Backend**: Django 5.0
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, Vanilla JS
- **Authentication**: Django built-in auth system

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- pip

## Setup Instructions

### 1. Create PostgreSQL Database

```sql
CREATE DATABASE budgetwise_db;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE budgetwise_db TO postgres;
```

### 2. Clone and Setup Project

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DB_NAME=budgetwise_db
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Testing the Application

### Test Signup Flow

1. Navigate to http://127.0.0.1:8000/accounts/signup/
2. Fill in the form:
   - Username (min 3 characters)
   - Email (valid format)
   - Password (min 8 characters, not too common)
   - Confirm password
3. Submit form
4. Verify redirect to login page with success message

### Test Login Flow

1. Navigate to http://127.0.0.1:8000/accounts/login/
2. Enter credentials
3. Verify redirect to dashboard
4. Check user info displayed correctly

### Test Logout

1. Click "Logout" button on dashboard
2. Verify redirect to login page
3. Verify cannot access dashboard without login

### Verify Database

```bash
# Access PostgreSQL
psql -U postgres -d budgetwise_db

# Check users table
SELECT id, username, email, is_active, date_joined FROM auth_user;

# Verify password is hashed
SELECT username, password FROM auth_user;
```

The password should be a long hashed string starting with `pbkdf2_sha256$`.

### Test Admin Panel

1. Navigate to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. View registered users

## Project Structure

```
budgetwise/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── budgetwise/
│   ├── __init__.py
│   ├── settings.py      # Django configuration
│   ├── urls.py          # Main URL routing
│   ├── wsgi.py          # WSGI config
│   └── asgi.py          # ASGI config
├── accounts/
│   ├── __init__.py
│   ├── models.py        # Uses Django User model
│   ├── views.py         # Authentication views
│   ├── urls.py          # App URL routing
│   ├── forms.py         # Custom signup form
│   ├── admin.py         # Admin configuration
│   └── templates/accounts/
│       ├── login.html
│       ├── signup.html
│       └── dashboard.html
└── static/
    └── css/
        └── style.css    # Modern UI styling
```

## Security Features

- Passwords hashed using PBKDF2 algorithm
- CSRF tokens on all forms
- SQL injection protection (Django ORM)
- XSS protection
- Secure session management
- Password validation rules:
  - Minimum 8 characters
  - Not too similar to username
  - Not a common password
  - Not entirely numeric

## API Endpoints

- `/` - Redirects to login
- `/accounts/signup/` - User registration
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/dashboard/` - Protected dashboard (requires login)
- `/admin/` - Django admin panel

## Future Phases

Phase 1 (Current): Authentication system ✅
- Phase 2: Expense tracking CRUD
- Phase 3: Dashboard analytics
- Phase 4: AI-based forecasting

## Troubleshooting

### Database Connection Error

- Verify PostgreSQL is running
- Check `.env` credentials
- Ensure database exists

### Module Not Found

```bash
pip install -r requirements.txt
```

### Static Files Not Loading

```bash
python manage.py collectstatic
```

### Port Already in Use

```bash
python manage.py runserver 8001
```

## License

MIT License
