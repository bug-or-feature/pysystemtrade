#!/bin/bash

source ~/.profile

SOURCE="$PYSYS_CODE/data/backups_csv";
DEST="$PYSYS_CODE/data/futures_spreadbet";

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing data files to repo, source: '$SOURCE', dest: '$DEST'"

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing epic history"
rsync -av $SOURCE/epic_history/*.csv $DEST/epic_history_csv

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing adjusted prices"
rsync -av $SOURCE/adjusted_prices/*.csv $DEST/adjusted_prices_csv

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing multiple prices"
rsync -av $SOURCE/multiple_prices/*.csv $DEST/multiple_prices_csv

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing fx prices"
rsync -av $SOURCE/fx_prices/*.csv $DEST/fx_prices_csv

echo "`date "+%Y-%m-%d %H:%M:%S"` Committing to repo"
git add $DEST/epic_history_csv/*.csv
git add $DEST/adjusted_prices_csv/*.csv
git add $DEST/multiple_prices_csv/*.csv
git add $DEST/fx_prices_csv/*.csv
git commit -m "Syncing data files to repo"
git push origin

echo "`date "+%Y-%m-%d %H:%M:%S"` Finished sync of data files to repo"

exit 0
