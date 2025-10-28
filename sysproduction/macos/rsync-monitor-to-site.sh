#!/bin/zsh

source ~/.zprofile

TRAPZERR() {
  datetime=$(date +%Y-%m-%d\ %H\:%M\:%S)
  echo "Problem running 'rsync-monitor-to-site.sh'" | /usr/bin/mail -s "FUTP Problem running 'rsync-monitor-to-site.sh'" $PYSYS_EMAIL
}

echo "`date "+%Y-%m-%d %H:%M:%S"` starting sync of monitor site files to httpd home..."
echo "`date "+%Y-%m-%d %H:%M:%S"` source: $PYSYS_SITE_DIR"
echo "`date "+%Y-%m-%d %H:%M:%S"` dest: $PYSYS_HTTPD_DIR"

/usr/local/bin/rsync -av --exclude=.DS_Store -e "ssh -p 2222" $PYSYS_SITE_DIR $PYSYS_HTTPD_DIR

echo "`date "+%Y-%m-%d %H:%M:%S"` sync of monitor site files done."

exit 0
