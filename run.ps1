# ==============================================================================
# SnapAssist — One-Command Startup Script for Windows & Snapdragon PCs
# ==============================================================================

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "Launching SnapAssist — Private On-Device AI Workspace" -ForegroundColor Red
Write-Host "Tagline: 'Your files. Your AI. Your device.'" -ForegroundColor White
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in background job or separate process
Write-Host "`n[1/2] Starting local FastAPI backend on http://127.0.0.1:8000..." -ForegroundColor Green
$backendProcess = Start-Process python -ArgumentList "-m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000" -PassThru -NoNewWindow

# Wait 2 seconds for backend initialization
Start-Sleep -Seconds 2

# 2. Start Vite Frontend
Write-Host "[2/2] Starting React Vite frontend on http://localhost:5173..." -ForegroundColor Green
Set-Location -Path "frontend"

Write-Host "`n>>> SnapAssist is live at: http://localhost:5173" -ForegroundColor Yellow
Write-Host ">>> Press Ctrl+C to stop the servers." -ForegroundColor Gray
npm run dev

# Cleanup on exit
Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
