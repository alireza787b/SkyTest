#!/bin/bash

# Define the path for the initialization marker file
INIT_MARKER="instance/db_initialized.marker"

# Check if the database has already been initialized by looking for the marker file
if [ ! -e "$INIT_MARKER" ]; then
    echo "Database not initialized. Running initialize_db.py..."
    python initialize_db.py

    # After successful initialization, create the marker file
    touch "$INIT_MARKER"
else
    echo "Database already initialized."
fi

# Continue with the startup of the main application
exec python run.py
