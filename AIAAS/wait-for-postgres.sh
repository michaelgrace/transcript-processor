#!/bin/sh
set -e

host="$DB_HOST"
port="$DB_PORT"

until pg_isready -h "$host" -p "$port" -U "$DB_USER"; do
  echo "Waiting for Postgres at $host:$port..."
  sleep 1
done

exec "$@"
