#!/bin/bash

# replicates mongodb data from production v4 to development v4

# fail fast
set -eo pipefail
#shopt -s inherit_errexit

source ~/.profile

if [ -d "/Volumes/devuser" ]
then
    mongo arctic_development_v5 --eval "db.dropDatabase()"
    mongo development_v5 --eval "db.dropDatabase()"

    mongorestore --nsInclude="arctic_production_v5.*" --nsFrom='arctic_production_v5.*' --nsTo='arctic_development_v5.*' /Volumes/devuser/pysystemtrade-fsb/data/mongo_dump
    mongorestore --nsInclude="production_v5.*" --nsFrom='production_v5.*' --nsTo='development_v5.*' /Volumes/devuser/pysystemtrade-fsb/data/mongo_dump

    exit 0
else
    echo "devuser not mounted"
    exit 1
fi
