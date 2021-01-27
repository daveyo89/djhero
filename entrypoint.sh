#!/bin/sh
echo "Started collecting static files."
python manage.py collectstatic --noinput
echo "Done"