#!/bin/bash

function wait_postgres {
    echo "Waiting postgres to run on postgres 5432..."

    while ! psql -h postgres -p 5432 -U my_user -d my_db -c "SELECT datname FROM pg_database LIMIT 1">&/dev/null;
    do
      sleep 0.1
    done

    echo "Postgres launched"
}

wait_postgres

echo "[TRY] CREATE EXTENSION citext"
psql -h postgres -p 5432 -U my_user -d my_db -c "CREATE EXTENSION citext;" > /dev/null;
echo "[COMPLETE] CREATE EXTENSION citext"

echo "[TRY] connect to another container and fill database from *.psql files"
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/users.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/vote.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/forums.psql;

