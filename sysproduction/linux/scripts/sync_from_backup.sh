#!/bin/bash

SOURCE="/home/caleb/pysystemtrade/data/backups_csv";
DEST="/home/caleb/pysystemtrade/data/futures_cj";

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing backup files, source: '$SOURCE', dest: '$DEST'"

echo "`date "+%Y-%m-%d %H:%M:%S"` Backing up adjusted prices"
rsync -av $SOURCE/adjusted_prices/*.csv $DEST/adjusted_prices_csv

echo "`date "+%Y-%m-%d %H:%M:%S"` Backing up multiple prices"
rsync -av $SOURCE/multiple_prices/*.csv $DEST/multiple_prices_csv

echo "`date "+%Y-%m-%d %H:%M:%S"` Backing up fx prices"
rsync -av $SOURCE/fx_prices/*.csv $DEST/fx_prices_csv

echo "`date "+%Y-%m-%d %H:%M:%S"` Committing to repo"
cd $PYSYS_CODE
git pull
git add --verbose $DEST
git commit -m "Syncing data files to repo"
git push origin

echo "`date "+%Y-%m-%d %H:%M:%S"` Finished sync of backup files to data"

exit 0
