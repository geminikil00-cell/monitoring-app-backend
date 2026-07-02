#!/bin/sh
set -e

DB_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:6543/postgres}"
DB_HOST=$(echo "$DB_URL" | sed -n 's/.*@\([^/:]*\).*/\1/p')
DB_PORT=$(echo "$DB_URL" | sed -n 's/.*@[^:]*:\([0-9]*\)\/.*/\1/p')

if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ] && [ "$DB_HOST" != "127.0.0.1" ]; then
    echo "Target database: $DB_HOST:${DB_PORT:-5432}"

    if echo "$DB_HOST" | grep -q "\.supabase\.co$" && [ "$DB_PORT" = "5432" ]; then
        echo ""
        echo "*** WARNING: You are connecting to Supabase on port 5432 (direct connection)."
        echo "*** Many Docker hosting platforms cannot reach Supabase over IPv6 port 5432."
        echo "*** Go to Supabase Dashboard → Project Settings → Database → Connection Pooling"
        echo "*** Copy the pooler URL (port 6543) and set it as DATABASE_URL in Coolify."
        echo "*** Format: postgresql://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres"
        echo ""
    fi

    echo "Resolving $DB_HOST to IPv4..."
    IPV4=""
    IPV4=$(getent ahostsv4 "$DB_HOST" 2>/dev/null | awk 'NR==1{print $1}')
    if [ -z "$IPV4" ]; then
        IPV4=$(python3 -c "import socket; print(socket.getaddrinfo('$DB_HOST', 0, socket.AF_INET)[0][4][0])" 2>/dev/null)
    fi
    if [ -z "$IPV4" ]; then
        IPV4=$(curl -s --connect-timeout 3 "https://dns.google/resolve?name=$DB_HOST&type=A" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['Answer'][0]['data'])" 2>/dev/null)
    fi
    if [ -n "$IPV4" ]; then
        echo "$IPV4 $DB_HOST" >> /etc/hosts
        echo "Added /etc/hosts entry: $IPV4 $DB_HOST"
    else
        echo "WARNING: Could not resolve $DB_HOST to IPv4."
        echo "If connection fails, use the Supabase pooler URL (port 6543) instead."
    fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
