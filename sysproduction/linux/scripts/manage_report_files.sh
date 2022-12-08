#!/bin/bash

#REPORTS_DIR=/Users/ageach/Dev/work/harbor-macro/harbor-macro.gitlab.io/public/reports
REPORTS_DIR=/home/caleb/harbor-macro/harbor-macro.gitlab.io/public/reports
TODAY=`date "+%Y-%m-%d"`

echo ""
echo "`date "+%Y-%m-%d %H:%M:%S"` Starting archive of today's ($TODAY) report files..."

cp -v $REPORTS_DIR/Trade_report.txt $REPORTS_DIR/older/Trade_report_$TODAY.txt
cp -v $REPORTS_DIR/Strategy_report.txt $REPORTS_DIR/older/Strategy_report_$TODAY.txt

echo "`date "+%Y-%m-%d %H:%M:%S"` Finished archive of old report files"
echo ""

echo ""
echo "`date "+%Y-%m-%d %H:%M:%S"` Building index for older report files..."

OLD_REPORTS=$REPORTS_DIR/older
OUTPUT="$OLD_REPORTS/index.html"

echo "<html lang='en'><head><meta charset="utf-8"><title>Previous reports</title><link rel="stylesheet" href="../../style.css"></head>" > $OUTPUT
echo "<body>" >> $OUTPUT
echo "<a href='../index.html'>Back</a><br/>" >> $OUTPUT
echo "<h1>Directory listing:</h1>" >> $OUTPUT
echo "<ul>" >> $OUTPUT
for i in `find "$OLD_REPORTS" -maxdepth 1 -mindepth 1 -name "*.txt" -type f| sort -r`; do
  file=`basename "$i"`
  echo "    <li><a href=\"./$file\">$file</a></li>" >> $OUTPUT
done
echo "</ul>" >> $OUTPUT
echo "</body></html>" >> $OUTPUT

echo "`date "+%Y-%m-%d %H:%M:%S"` Finished building index for older report files"
echo ""

echo "`date "+%Y-%m-%d %H:%M:%S"` Starting cleanup of temp report PDF files..."
rm -vf $REPORTS_DIR/_tempfile_*.pdf
echo "`date "+%Y-%m-%d %H:%M:%S"` Finished cleanup of temp report PDF files"
echo ""

exit 0
