#!/bin/bash
cd "$(dirname "$0")"

# Detect OS and set browser-open command
if [[ "$OSTYPE" == "darwin"* ]]; then
    OPEN_CMD="open"
else
    OPEN_CMD="xdg-open"
fi

# Wait for server to be ready, then open browser
(
    for i in $(seq 1 60); do
        if curl -s http://127.0.0.1:7860 > /dev/null 2>&1; then
            $OPEN_CMD "http://127.0.0.1:7860"
            break
        fi
        sleep 1
    done
) &

python3 bootstrap.py
