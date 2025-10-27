#!/usr/bin/env zsh

source ~/.zprofile

TRAPZERR() {
  datetime=$(date +%Y-%m-%d\ %H\:%M\:%S)
  echo "Problem running 'archive_mongo_dump.sh'" | /usr/bin/mail -s "FUTP Problem running 'archive_mongo_dump.sh'" $PYSYS_EMAIL
}

# date
datetime=$(date +%Y-%m-%d)

# source
src="$PYSYS_CODE/data/mongo_dump"

# destination
dest=$BACKUP_DIR

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
