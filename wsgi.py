"""Production entry point:  gunicorn wsgi:app   (Linux hosts)   or   waitress-serve --listen=0.0.0.0:8000 wsgi:app   (Windows)"""
from app import app  # noqa: F401
