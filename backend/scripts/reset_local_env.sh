#!/bin/bash
echo "Resetting Local Environment for Shadow AI Sentinel..."

# Bring down docker and remove volumes
docker-compose down -v

# Remove sqlite fallback if they exist (from old version)
rm -f backend/*.db backend/*.sqlite3

echo "==========================================================="
echo "WARNING: JWT IDs changed to Supabase UUID format."
echo "If you have an old JWT in your browser, authentication will fail."
echo "Please clear your browser's localStorage for localhost:5173"
echo "Or use developer tools -> Application -> Local Storage -> Clear All"
echo "==========================================================="
echo "Done."
