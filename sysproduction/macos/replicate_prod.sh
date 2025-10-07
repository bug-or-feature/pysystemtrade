#!/bin/zsh

# replicates mongodb data from production (remote) to development (local)

# fail fast
set -eo pipefail

source ~/.zprofile

# setup source and target paths. the paths below assume:
#   - an ssh config named 'remote'
#   - that the 'run_backups' scheduled process has run on the remote server
#   - 'offsystem_backup_directory' on the remote server is configured as '/home/user/pst_backups'
#   - remote mongo db name is 'production'
#   - local mongo db name is 'development'

MONGO_TARGET=/Users/ageach/Documents/backup/pst-futures

PARQUET_SOURCE=/Users/ageach/Documents/backup/pst-futures/parquet/
PARQUET_TARGET=/Users/ageach/Dev/work/pst-futures/parquet

DB_SOURCE=futures_production_v5
DB_TARGET=futures_development

echo "Starting replication of PROD data to DEV environment..."

echo "Dropping local databases..."
mongo $DB_TARGET --eval "db.dropDatabase()"
echo "Dropping local databases COMPLETE"

echo "Restoring remote data to local database..."
mongorestore --nsInclude="$DB_SOURCE.*" --nsFrom="$DB_SOURCE.*" --nsTo="$DB_TARGET.*" $MONGO_TARGET/mongo_dump
echo "Restoring remote data to local database COMPLETE"

echo "Restoring remote data to local parquet store..."
rsync -chavzP --stats --progress --delete $PARQUET_SOURCE $PARQUET_TARGET
echo "Restoring remote data to local parquet store COMPLETE"

echo "Replication of PROD data to DEV environment COMPLETE"

exit 0
