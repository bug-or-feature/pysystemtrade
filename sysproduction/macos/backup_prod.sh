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

MONGO_SOURCE=injurytime:/Users/devuser/pst-futures/data/mongo_dump
MONGO_TARGET=/Users/ageach/Documents/backup/pst-futures

CSV_SOURCE=injurytime:/Users/devuser/pst-futures/data/backups_csv
CSV_TARGET=/Users/ageach/Documents/backup/pst-futures

PARQUET_SOURCE=injurytime:/Users/devuser/data/parquet
PARQUET_TARGET=/Users/ageach/Documents/backup/pst-futures

echo "Starting backup of PROD data to DEV environment..."

echo "Starting rsync of remote files to local..."
rsync -chavzP --stats --progress $MONGO_SOURCE $MONGO_TARGET
rsync -chavzP --stats --progress $CSV_SOURCE $CSV_TARGET
rsync -chavzP --stats --progress $PARQUET_SOURCE $PARQUET_TARGET
echo "rsync of remote files to local COMPLETE"

echo "Backup of PROD data to DEV environment COMPLETE"

exit 0
