#!/bin/bash

# replicates mongodb data from production v4 to development v4

# fail fast
set -eo pipefail
#shopt -s inherit_errexit

source ~/.profile

if [ -d "/Volumes/devuser" ]
then
    mongo arctic_development_v4 --eval "db.dropDatabase()"
    mongo development_v4 --eval "db.dropDatabase()"

    mongorestore --nsInclude="arctic_production_v4.*" --nsFrom='arctic_production_v4.*' --nsTo='arctic_development_v4.*' /Volumes/devuser/Documents/pst_backup/mongo/mongo_dump
    mongorestore --nsInclude="production_v4.*" --nsFrom='production_v4.*' --nsTo='development_v4.*' /Volumes/devuser/Documents/pst_backup/mongo/mongo_dump

    exit 0
else
    echo "devuser not mounted"
    exit 1
fi