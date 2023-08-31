#!/usr/bin/env zsh

source ~/.zprofile

# date
datetime=$(date +%Y-%m-%d)

# source
#src="/Users/ageach/Dev/work/pysystemtrade-fsb/data/mongo_dump"
src="/Users/devuser/pysystemtrade-fsb/data/mongo_dump"

# destination
#dest="/Users/ageach/Documents/backup/pysystemtrade-fsb/mongo"
dest="/Users/devuser/Documents/backup"

# full path to compression tool
zip=/usr/bin/zip
#zip=/usr/bin/zip

# base filename
base="pst-fsb-mongo-dump"

# result file
zipfile="${dest}/${base}-${datetime}.zip"

echo -n "Backing up $dest into $zipfile..."

# create zip
${zip} -r -9 $zipfile $src -x "*.DS_Store" && echo "Done!" || echo ""

exit 0
