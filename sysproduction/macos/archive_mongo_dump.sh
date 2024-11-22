#!/usr/bin/env zsh

source ~/.zprofile

# date
datetime=$(date +%Y-%m-%d)

# source
src="/Users/devuser/pst-futures/data/mongo_dump"

# destination
dest="/Users/devuser/Documents/backup"

# full path to compression tool
zip=/usr/bin/zip
#zip=/usr/bin/zip

# base filename
base="pst-futures-mongo-dump"

# result file
zipfile="${dest}/${base}-${datetime}.zip"

echo -n "Backing up $dest into $zipfile..."

# create zip
${zip} -r -9 $zipfile $src -x "*.DS_Store" && echo "Done!" || echo ""

exit 0
