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

echo "[TRY] create tables from *.psql files"
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/users.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/vote.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/forums.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/threads.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/posts.psql;
echo "[COMPLETE] create tables from *.psql files"

echo "[TRY] create constraints from *.psql files"
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/constraints/posts.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/constraints/vote.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/constraints/forums.psql;
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/constraints/threads.psql;
echo "[COMPLETE] create constraints from *.psql files"

