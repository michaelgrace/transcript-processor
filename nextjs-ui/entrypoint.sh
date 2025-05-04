#!/bin/sh
set -e

# Echo environment variables relevant to hot reload
echo "CHOKIDAR_USEPOLLING: $CHOKIDAR_USEPOLLING"
echo "WATCHPACK_POLLING: $WATCHPACK_POLLING"
echo "NODE_ENV: $NODE_ENV"

# Optional: Install any missing dependencies
# This is useful if you mount volumes that might overwrite node_modules
if [ ! -d "node_modules" ] || [ ! "$(ls -A node_modules)" ]; then
  echo "Node modules not found or empty, installing dependencies..."
  npm install
else
  echo "Using existing node_modules"
fi

# Execute the command (likely npm run dev)
exec "$@"