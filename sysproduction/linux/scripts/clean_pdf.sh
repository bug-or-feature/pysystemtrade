#!/bin/bash

echo "`date "+%Y-%m-%d %H:%M:%S"` Starting cleanup of temp report PDF files..."

rm /home/caleb/harbor-macro/harbor-macro.gitlab.io/public/reports/_tempfile_*.pdf

echo "`date "+%Y-%m-%d %H:%M:%S"` Finished cleanup of temp report PDF files"

exit 0
