#!/bin/bash

echo "try connect to another container and fill database from *.psql files"
psql -h localhost -p 5432 -U my_user -d my_db < /tmp/database/postgres/tables/users.psql

