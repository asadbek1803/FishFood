release: python manage.py collectstatic --noinput
web: gunicorn config.wsgi --timeout 300 --workers 2 --threads 4 --worker-class sync --max-requests 1000 --max-requests-jitter 50
