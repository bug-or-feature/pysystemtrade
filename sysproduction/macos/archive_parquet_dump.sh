#!/usr/bin/env zsh

source ~/.zprofile

TRAPZERR() {
  datetime=$(date +%Y-%m-%d\ %H\:%M\:%S)
  echo "Problem running 'archive_parquet_dump.sh'" | /usr/bin/mail -s "FUTP Problem running 'archive_parquet_dump.sh'" $PYSYS_EMAIL
}

# date
datetime=$(date +%Y-%m-%d)

# source
src="/Users/devuser/data/parquet"

# destination
dest=$BACKUP_DIR

# full path to compression tool
zip=/usr/bin/zip
#zip=/usr/bin/zip

# base filename
base="pst-futures-parquet-dump"

# result file
zipfile="${dest}/${base}-${datetime}.zip"

echo -n "Backing up $dest into $zipfile..."

# create zip
${zip} -r -9 $zipfile $src -x "*.DS_Store" && echo "Done!" || echo ""

exit 0
