#!/bin/zsh

SOURCE=/Users/devuser/Sites/pst-futures/
TARGET=tacticalgrace::NetBackup/pst_site

echo "`date "+%Y-%m-%d %H:%M:%S"` starting sync of monitor site files to httpd home..."

/usr/local/bin/rsync -av --exclude=.DS_Store -e "ssh -p 2222" $SOURCE $TARGET

echo "`date "+%Y-%m-%d %H:%M:%S"` sync of monitor site files done."

exit 0
