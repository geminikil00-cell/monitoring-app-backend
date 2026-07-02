#!/bin/sh
set -e

DB_HOST=$(echo "${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/postgres}" | sed -n 's/.*@\([^/:]*\).*/\1/p')

if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ] && [ "$DB_HOST" != "127.0.0.1" ]; then
    echo "Resolving $DB_HOST to IPv4..."
    IPV4=$(getent ahostsv4 "$DB_HOST" 2>/dev/null | awk 'NR==1{print $1}') || true
    if [ -n "$IPV4" ]; then
        echo "$IPV4 $DB_HOST" >> /etc/hosts
        echo "Added /etc/hosts entry: $IPV4 $DB_HOST"
    else
        echo "WARNING: Could not resolve $DB_HOST to IPv4, falling back to system DNS"
    fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
