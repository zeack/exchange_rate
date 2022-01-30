echo "migrate"
python3 manage.py migrate
echo "collectstatic"
python3 manage.py collectstatic --noinput
echo "run"
gunicorn exchange_rate.wsgi -w 3 -b :3000 --reload --error-logfile error.log --log-level=debug --timeout 3600 --capture-output
