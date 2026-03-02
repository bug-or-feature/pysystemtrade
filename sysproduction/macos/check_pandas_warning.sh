#!/bin/zsh

# Search for pattern and capture results
RESULTS=$(/usr/bin/find "$ECHO_PATH" -type f -name "*.log" -exec /usr/bin/grep -E 'FutureWarning|DeprecationWarning|ChainedAssignmentError' /dev/null {} +)

#echo "RESULTS=[$RESULTS]" >&2

# Exit silently if nothing found
if [[ -z "$RESULTS" ]]; then
    exit 0
fi

SUBJECT="Future/Deprecation/ChainedAssignment Warning instances found"

#echo "$ECHO_PATH=[$ECHO_PATH] SUBJECT=[$SUBJECT] PYSYS_EMAIL=[$PYSYS_EMAIL]" >&2
#echo "HOME=[$HOME] USER=[$USER] LOGNAME=[$LOGNAME]" >&2

echo "$RESULTS" | /usr/bin/mail -v -s $SUBJECT $PYSYS_EMAIL
#echo "mail exit code: $?" >&2
