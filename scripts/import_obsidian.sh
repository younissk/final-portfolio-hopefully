#!/bin/bash

# This script imports any Obsidian markdown file into the Eleventy site
# Usage: ./import_obsidian.sh /path/to/obsidian/note.md

# Set default paths
SCRIPT_DIR="$(dirname "$0")"
VAULT_PATH="/Users/youniss/Documents/GitHub/Ai-stuidum"
IMAGE_FOLDER="/Users/youniss/Documents/GitHub/Ai-stuidum/2 Attatchments"

# Function to display usage
function show_usage {
  echo "Usage: $(basename $0) [options] <path-to-obsidian-file>"
  echo ""
  echo "Options:"
  echo "  -v, --vault PATH       Set the Obsidian vault path (default: $VAULT_PATH)"
  echo "  -i, --images PATH      Set the Obsidian images folder path (default: $IMAGE_FOLDER)"
  echo "  -h, --help             Show this help message and exit"
  echo ""
  echo "Example:"
  echo "  $(basename $0) /Users/youniss/Documents/GitHub/Ai-stuidum/Notes/AI/Mathematics/Matrix.md"
  echo "  $(basename $0) --vault /path/to/vault --images /path/to/images /path/to/note.md"
}

# Parse command line arguments
OBSIDIAN_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -v|--vault)
      VAULT_PATH="$2"
      shift 2
      ;;
    -i|--images)
      IMAGE_FOLDER="$2"
      shift 2
      ;;
    -h|--help)
      show_usage
      exit 0
      ;;
    *)
      if [[ "$1" == -* ]]; then
        echo "Unknown option: $1"
        show_usage
        exit 1
      else
        OBSIDIAN_FILE="$1"
        shift
      fi
      ;;
  esac
done

# Check if OBSIDIAN_FILE is provided
if [ -z "$OBSIDIAN_FILE" ]; then
  echo "Error: No Obsidian file specified"
  show_usage
  exit 1
fi

# Check if file exists
if [ ! -f "$OBSIDIAN_FILE" ]; then
  echo "Error: File does not exist: $OBSIDIAN_FILE"
  exit 1
fi

# Install dependencies
pip install -r "$SCRIPT_DIR/requirements.txt"

# Run the Python command directly with properly quoted arguments
python "$SCRIPT_DIR/obsidian_import.py" "$OBSIDIAN_FILE" --vault "$VAULT_PATH" --image-folder "$IMAGE_FOLDER"

echo "Import complete. Check content/articles/ directory for the imported file." 