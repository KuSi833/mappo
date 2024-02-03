#!/bin/bash

# Syncs only selected remote directories from the server to local directory using rsync, accepting a username as an argument.

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [username]"
    exit 1
fi

# Variables
DESTINATION_DIR="."
USERNAME="$1"
SOURCE="${USERNAME}@csf3.itservices.manchester.ac.uk:/scratch/${USERNAME}/projects/typ/mappo/"
EXCLUDE_FILE=".syncignore"

# Rsync Command
## Logs
rsync -avz --exclude-from="${EXCLUDE_FILE}" "${SOURCE}/logs/" "${DESTINATION_DIR}/logs/"

## Add anything else you might want to sync...
