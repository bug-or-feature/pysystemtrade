#!/bin/bash

SOURCE="/disk1/caleb/pst_backups/csv/backups_csv";
DEST="s3://pst-caleb-csv-data";

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing price data to AWS S3, source: '$SOURCE', dest: '$DEST'"

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing instrument data"
aws s3 sync $SOURCE/instrument_data s3://pst-caleb-csv-data/instrument_data

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing roll parameters"
aws s3 sync $SOURCE/roll_parameters s3://pst-caleb-csv-data/roll_parameters

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing FX prices"
aws s3 sync $SOURCE/fx_prices s3://pst-caleb-csv-data/fx_prices

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing multiple prices"
aws s3 sync $SOURCE/multiple_prices s3://pst-caleb-csv-data/multiple_prices

echo "`date "+%Y-%m-%d %H:%M:%S"` Syncing adjusted prices"
aws s3 sync $SOURCE/adjusted_prices s3://pst-caleb-csv-data/adjusted_prices

echo "`date "+%Y-%m-%d %H:%M:%S"` Finished syncing of price data to AWS S3"

exit 0
