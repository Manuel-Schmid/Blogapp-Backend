#!/bin/bash
set -e

# Check if script was called by CMD, can be sh -c 'CMD' or CMD
if [ "$1" = '/usr/libexec/s2i/run' ] || [ "$3" = '/usr/libexec/s2i/run' ] || [ "$2" = 'runserver' ]; then
    # Wait for the database to be available
    until nc -vzw 2 "$DJANGO_DB_HOST" "$DJANGO_DB_PORT"; do echo "mysql is not available. waiting..." && sleep 2; done

    echo "Apply database migrations"
    python ./manage.py migrate

    echo "Load fixtures"
    python ./manage.py loaddata blog/fixtures/initial_data.json

    echo "Collect static files"
    python ./manage.py collectstatic --noinput
fi

exec "$@"
