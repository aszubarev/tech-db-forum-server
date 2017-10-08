#!/bin/bash

echo "sleep"
sleep 5
echo "not sleep"

echo "try connect to another container and fill database from *.psql files"
psql -h postgres -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/users.psql

