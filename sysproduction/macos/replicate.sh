#!/bin/bash

# replicates mongodb data from production to development

# fail fast
set -eo pipefail
#shopt -s inherit_errexit

source ~/.profile

if [ -d "/Volumes/devuser" ]
then
    mongo arctic_development --eval "db.dropDatabase()"
    mongo development --eval "db.dropDatabase()"

    mongorestore --nsInclude="arctic_production.*" --nsFrom='arctic_production.*' --nsTo='arctic_development.*' /Volumes/devuser/Documents/pst_backup/mongo/mongo_dump
    mongorestore --nsInclude="production.*" --nsFrom='production.*' --nsTo='development.*' /Volumes/devuser/Documents/pst_backup/mongo/mongo_dump

    exit 0
else
    echo "devuser not mounted"
    exit 1
fi