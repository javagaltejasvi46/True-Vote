# Deployment Guide

This guide covers two popular methods to deploy your Django project: **PythonAnywhere** (Recommended for SQLite) and **Render**.

## Option 1: PythonAnywhere (Recommended)
PythonAnywhere is excellent for Django projects using SQLite because it supports persistent filesystem storage natively.

### Steps:
1.  **Sign Up**: Create a free account at [pythonanywhere.com](https://www.pythonanywhere.com/).
2.  **Open Dashboard**: Go to the "Consoles" tab and start a "Bash" console.
3.  **Clone Repository**:
    ```bash
    git clone https://github.com/javagaltejasvi46/True-Vote.git
    cd True-Vote
    ```
4.  **Create Virtual Environment**:
    ```bash
    mkvirtualenv --python=/usr/bin/python3.10 myenv
    pip install -r requirements.txt
    ```
5.  **Configure Web App**:
    -   Go to the "Web" tab.
    -   Click "Add a new web app" -> "Manual configuration" -> Select Python 3.10.
6.  **Set Paths**:
    -   **Source code**: `/home/yourusername/True-Vote`
    -   **Working directory**: `/home/yourusername/True-Vote`
7.  **Configure WSGI File**:
    -   Click the link next to "WSGI configuration file".
    -   Update it to serve your Django app:
        ```python
        import os
        import sys

        path = '/home/yourusername/True-Vote'
        if path not in sys.path:
            sys.path.append(path)

        os.environ['DJANGO_SETTINGS_MODULE'] = 'voting_system.settings'

        from django.core.wsgi import get_wsgi_application
        application = get_wsgi_application()
        ```
8.  **Static Files**:
    -   In the "Web" tab, under "Static files":
    -   **URL**: `/static/`
    -   **Directory**: `/home/yourusername/True-Vote/staticfiles`
    -   Run `python manage.py collectstatic` in your Bash console.
9.  **Reload**: Click the "Reload" button at the top of the Web tab. Your site should be live!

---

## Option 2: Render.com
Render is a modern cloud provider. Note that SQLite database gets reset on every deployment unless you use a persistent disk (paid). For free tier, use an external PostgreSQL database (e.g., from Neon.tech or Render's generic Postgres).

### Preparation:
1.  Create a `build.sh` file in your repository:
    ```bash
    #!/usr/bin/env bash
    # exit on error
    set -o errexit

    pip install -r requirements.txt
    python manage.py collectstatic --no-input
    python manage.py migrate
    ```
2.  Make sure `requirements.txt` includes `gunicorn`. (Add `gunicorn` to it).
3.  Push these changes to GitHub.

### Steps:
1.  **Sign Up**: Go to [render.com](https://render.com/).
2.  **New Web Service**: Connect your GitHub repository.
3.  **Settings**:
    -   **Runtime**: Python 3
    -   **Build Command**: `./build.sh`
    -   **Start Command**: `gunicorn voting_system.wsgi:application`
4.  **Environment Variables**:
    -   Add `PYTHON_VERSION`: `3.10.0` (or similar)
    -   Add `SECRET_KEY`: (Your random secret key)
    -   Add `DEBUG`: `False`
5.  **Deploy**: Click "Create Web Service".

> [!IMPORTANT]
> For Render, you must ensure `ALLOWED_HOSTS` in `settings.py` includes your Render URL (e.g., `['onrender.com']` or `['*']`).

## Production Readiness Checklist
Before deploying for real usage:
- [ ] Set `DEBUG = False` in `settings.py`.
- [ ] Set a strong, random `SECRET_KEY` via environment variables.
- [ ] Update `ALLOWED_HOSTS` to your specific domain.
- [ ] Use a production database like PostgreSQL instead of SQLite.
- [ ] Use `Whitenoise` for serving static files efficiently.
