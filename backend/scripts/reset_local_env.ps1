Write-Host "Resetting Local Environment for Shadow AI Sentinel..." -ForegroundColor Cyan

# Bring down docker and remove volumes
docker-compose down -v

# Remove sqlite fallback if they exist (from old version)
Remove-Item -Path "backend\*.db", "backend\*.sqlite3" -ErrorAction SilentlyContinue

Write-Host "===========================================================" -ForegroundColor Yellow
Write-Host "WARNING: JWT IDs changed to Supabase UUID format." -ForegroundColor Yellow
Write-Host "If you have an old JWT in your browser, authentication will fail." -ForegroundColor Yellow
Write-Host "Please clear your browser's localStorage for localhost:5173" -ForegroundColor Yellow
Write-Host "Or use developer tools -> Application -> Local Storage -> Clear All" -ForegroundColor Yellow
Write-Host "===========================================================" -ForegroundColor Yellow
Write-Host "Done." -ForegroundColor Cyan
