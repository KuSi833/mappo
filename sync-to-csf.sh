#!/bin/bash

# Syncs local directory to remote server using rsync, accepting a username as an argument.

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 [username]"
    exit 1
fi

# Variables
SOURCE_DIR="."
USERNAME="$1"
DESTINATION="${USERNAME}@csf3.itservices.manchester.ac.uk:/scratch/${USERNAME}/pymarl/"
EXCLUDE_FILE=".gitignore"

# Rsync Command
rsync -avz --exclude-from="${EXCLUDE_FILE}" "${SOURCE_DIR}" "${DESTINATION}"
