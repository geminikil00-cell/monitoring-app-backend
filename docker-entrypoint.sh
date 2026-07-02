#!/bin/sh
set -e

DB_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:6543/postgres}"
DB_HOST=$(echo "$DB_URL" | sed -n 's/.*@\([^/:]*\).*/\1/p')
DB_PORT=$(echo "$DB_URL" | sed -n 's/.*@[^:]*:\([0-9]*\)\/.*/\1/p')

if echo "$DB_HOST" | grep -q "supabase\.co$"; then
    if [ "$DB_PORT" = "5432" ] || [ -z "$DB_PORT" ]; then
        echo "Detected Supabase host with port ${DB_PORT:-5432}. Switching to pooler port 6543..."
        NEW_URL=$(echo "$DB_URL" | sed "s/@$DB_HOST:[0-9]*\//@$DB_HOST:6543\//")
        if echo "$NEW_URL" | grep -q ":6543/"; then
            export DATABASE_URL="$NEW_URL"
            echo "DATABASE_URL rewritten to use pooler port 6543"
        fi
    fi
    echo "Resolving $DB_HOST to IPv4 via multiple methods..."
    IPV4=""
    IPV4=$(getent ahostsv4 "$DB_HOST" 2>/dev/null | awk 'NR==1{print $1}') || true
    if [ -z "$IPV4" ]; then
        IPV4=$(python3 -c "import socket; print(socket.getaddrinfo('$DB_HOST', 6543, socket.AF_INET)[0][4][0])" 2>/dev/null) || true
    fi
    if [ -z "$IPV4" ]; then
        IPV4=$(curl -s --ipv4 "https://dns.google/resolve?name=$DB_HOST&type=A" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['Answer'][0]['data'])" 2>/dev/null) || true
    fi
    if [ -n "$IPV4" ]; then
        echo "$IPV4 $DB_HOST" >> /etc/hosts
        echo "Added /etc/hosts entry: $IPV4 $DB_HOST"
    else
        echo "WARNING: Could not resolve $DB_HOST to IPv4 — trying pooler alternative..."
        POOLER_HOST=$(echo "$DB_HOST" | sed 's/^db\./aws-0-us-east-1.pooler./')
        if echo "$DATABASE_URL" | grep -q "supabase\.co"; then
            export DATABASE_URL=$(echo "$DATABASE_URL" | sed "s/@[^/]*\//@$POOLER_HOST:6543\//")
            echo "DATABASE_URL rewritten to pooler: $POOLER_HOST:6543"
        fi
    fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
