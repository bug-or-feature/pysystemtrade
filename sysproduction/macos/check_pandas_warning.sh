#!/bin/zsh

source ~/.zprofile

TRAPZERR() {
  datetime=$(date +%Y-%m-%d\ %H\:%M\:%S)
  echo "Problem running 'check_pandas_warning.sh'" | /usr/bin/mail -s "FUTP Problem running 'check_pandas_warning.sh'" $PYSYS_EMAIL
}

# Search for pattern and capture results
RESULTS=$(grep -rnE 'FutureWarning|DeprecationWarning|ChainedAssignmentError' "$ECHO_PATH" 2>/dev/null)

# Exit silently if nothing found
if [[ -z "$RESULTS" ]]; then
    exit 0
fi

# Compose and send email
SUBJECT="Future/Deprecation Warning instances found"
BODY="$RESULTS"

echo "$BODY" | /usr/bin/mail -s "$SUBJECT" "$PYSYS_EMAIL"
