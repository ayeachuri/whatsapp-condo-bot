#!/bin/bash

# Default to current directory if no argument provided
TARGET_DIR="${1:-.}"

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: '$TARGET_DIR' is not a directory"
  exit 1
fi

echo "Directory structure of: $(cd "$TARGET_DIR" && pwd)"
echo

find "$TARGET_DIR" -type d -o -type f | sort | sed -e "s|$TARGET_DIR/||" -e "s|[^/]*/|  |g" -e "s|  |  ├── |g"