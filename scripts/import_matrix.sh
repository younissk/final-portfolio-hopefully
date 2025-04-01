#!/bin/bash

# This script runs the obsidian_import.py script to import the Matrix.md file

# Set paths (with spaces correctly handled)
SCRIPT_DIR="$(dirname "$0")"
OBSIDIAN_FILE="/Users/youniss/Documents/GitHub/Ai-stuidum/Notes/AI/Mathematics/Matrix.md"
VAULT_PATH="/Users/youniss/Documents/GitHub/Ai-stuidum"
IMAGE_FOLDER="/Users/youniss/Documents/GitHub/Ai-stuidum/2 Attatchments"

# Install dependencies
pip install -r "$SCRIPT_DIR/requirements.txt"

# Run the Python command directly with properly quoted arguments
python "$SCRIPT_DIR/obsidian_import.py" "$OBSIDIAN_FILE" --vault "$VAULT_PATH" --image-folder "$IMAGE_FOLDER"

echo "Import complete. Check content/articles/matrix/ directory for the imported file." 