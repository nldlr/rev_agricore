#! /usr/bin/env bash

#this file handles seeding our app data in the database or rds in the correct order
#(schema first, then business data, then user accounts)
#To run this file, we have 2 commands:
# bash bin/seed.sh local (this is the default if no argument is given)
# bash bin/seed.sh rds


# $1 is the first argument typed after the script name
# $2 is option --reset
TARGET="${1:-local}"
ACTION="$2"

if [ "$TARGET" != "local" ] && [ "$TARGET" != "rds" ]; then
    echo "Usage: bin/seed.sh [local|rds] [--reset]"
    exit 1
fi

# Handle reset prompt
if [ "$ACTION" == "--reset" ]; then
    echo "Resetting all seed data on $TARGET..."
    read -p "Proceed? (y/N): " yn
    case "$yn" in
        [yY]* )
            echo "Proceeding with database reset...";;
        [nN]* )
            echo "Database reset canceled."
            exit 0;;
        * )
            echo "Database reset canceled."
            exit 0;;
    esac
fi

if [ "$TARGET" == "local" ]; then

    ##TODO: Replace the details in the db url below with YOUR details
    export DATABASE_URL="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/agricore_db"
    # database_url should be handled in .env
    PSQL_HOST="127.0.0.1"
    PSQL_DB="agricore_db"
elif [ "$TARGET" == "rds" ]; then

    ##TODO: Replace the details in the db url with YOUR REMOTE RDS details
    export DATABASE_URL="postgresql+asyncpg://<user>:<password>@<your-rds-endpoint>:5432/agricore"
    PSQL_HOST="<your-rds-endpoint>"
    PSQL_DB="agricore"
fi

echo "Seeding target: $TARGET"

cd backend
source .venv/Scripts/activate

#step 1: WIPES the DB FIRST, THEN CREATES the db tables
python -m scripts.create_tables

#step 2: load the core business data
psql -h "$PSQL_HOST" -U postgres -d "$PSQL_DB" -f ../db/sql/seed.sql

#step 3: load the RBAC demo users
python -m scripts.seed_users

echo "Seed complete for $TARGET"