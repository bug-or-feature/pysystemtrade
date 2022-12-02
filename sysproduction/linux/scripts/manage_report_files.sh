#!/bin/bash

REPORTS_DIR = /home/caleb/harbor-macro/harbor-macro.gitlab.io/public/reports
TODAY = `date "+%Y-%m-%d"`

echo ""
echo "`date "+%Y-%m-%d %H:%M:%S"` Starting archive of today's ($TODAY) report files..."

cp -v $REPORTS_DIR/Status_report.txt $REPORTS_DIR/older/Status_report_$TODAY.txt
cp -v $REPORTS_DIR/Trade_report.txt $REPORTS_DIR/older/Trade_report_$TODAY.txt
cp -v $REPORTS_DIR/Roll_report.txt $REPORTS_DIR/older/Roll_report_$TODAY.txt
cp -v $REPORTS_DIR/Reconcile_report.txt $REPORTS_DIR/older/Reconcile_report_$TODAY.txt
cp -v $REPORTS_DIR/Strategy_report.txt $REPORTS_DIR/older/Strategy_report_$TODAY.txt

#cp -v $REPORTS_DIR/'P&L_report.txt' $REPORTS_DIR/older/'P&L_report'_$TODAY.txt
#cp -v $REPORTS_DIR/'Trading_Rule_P&L.txt.pdf' $REPORTS_DIR/older/'Trading_Rule_P&L_'$TODAY.pdf
#cp -v $REPORTS_DIR/Costs_report.txt $REPORTS_DIR/older/Costs_report_$TODAY.txt
#cp -v $REPORTS_DIR/Account_curve_report.txt.pdf $REPORTS_DIR/older/Account_curve_report_$TODAY.pdf
#cp -v $REPORTS_DIR/Duplicate_markets_report.txt $REPORTS_DIR/older/Duplicate_markets_report_$TODAY.txt
#cp -v $REPORTS_DIR/Instrument_risk_report.txt $REPORTS_DIR/older/Instrument_risk_report_$TODAY.txt
#cp -v $REPORTS_DIR/Liquidity_report.txt $REPORTS_DIR/older/Liquidity_report_$TODAY.txt
#cp -v $REPORTS_DIR/Market_monitor_report.txt $REPORTS_DIR/older/Market_monitor_report_$TODAY.txt
#cp -v $REPORTS_DIR/Minimum_capital_report.txt $REPORTS_DIR/older/Minimum_capital_report_$TODAY.txt
#cp -v $REPORTS_DIR/Remove_markets_report.txt $REPORTS_DIR/older/Remove_markets_report_$TODAY.txt
#cp -v $REPORTS_DIR/Risk_report.txt $REPORTS_DIR/older/Risk_report_$TODAY.txt
#cp -v $REPORTS_DIR/Slippage_report.txt $REPORTS_DIR/older/Slippage_report_$TODAY.txt

echo "`date "+%Y-%m-%d %H:%M:%S"` Finished archive of old report files"
echo ""

echo "`date "+%Y-%m-%d %H:%M:%S"` Starting cleanup of temp report PDF files..."
rm -vf $REPORTS_DIR/_tempfile_*.pdf
echo "`date "+%Y-%m-%d %H:%M:%S"` Finished cleanup of temp report PDF files"
echo ""

exit 0
