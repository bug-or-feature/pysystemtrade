#!/usr/bin/env zsh

source ~/.zprofile


# Search for pattern and capture results
RESULTS=$(grep -rnE 'FutureWarning|DeprecationWarning' "$ECHO_PATH" 2>/dev/null)

# Exit silently if nothing found
if [[ -z "$RESULTS" ]]; then
    exit 0
fi

# Compose and send email
SUBJECT="Future/Deprecation Warning instances found"
BODY="$RESULTS"

echo "$BODY" | /usr/bin/mail -s "$SUBJECT" "$PYSYS_EMAIL"

