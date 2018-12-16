web: gunicorn config.wsgi --timeout 3000 --keep-alive 200 --log-file - 
worker: celery -A flight worker -l info
beat: celery -A flight  beat -l info