# ==============================================================================
# SnapAssist — Automated Setup Script for Windows & Snapdragon Copilot+ PCs
# ==============================================================================

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "SnapAssist: Setting up On-Device AI Workspace Environment" -ForegroundColor Red
Write-Host "Target Architecture: Qualcomm Snapdragon® X Elite / Windows ARM64" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Check Python version
Write-Host "`n[1/4] Verifying Python installation..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.10+."
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Gray

# 2. Check Node & npm
Write-Host "`n[2/4] Verifying Node.js and npm..." -ForegroundColor Green
$nodeVersion = node -v 2>&1
$npmVersion = npm -v 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Node.js is not installed or not in PATH. Please install Node.js 18+."
    exit 1
}
Write-Host "Found Node: $nodeVersion | npm: $npmVersion" -ForegroundColor Gray

# 3. Install Python dependencies
Write-Host "`n[3/4] Installing backend Python dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install Python dependencies."
    exit 1
}

# 4. Install Frontend dependencies
Write-Host "`n[4/4] Installing frontend npm dependencies..." -ForegroundColor Green
Set-Location -Path "frontend"
npm install
Set-Location -Path ".."

# 5. Generate sample benchmark and test dataset
Write-Host "`nGenerating sample data & running benchmark..." -ForegroundColor Green
python scripts/generate_sample_data.py
python scripts/benchmark.py

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "SnapAssist setup completed successfully!" -ForegroundColor Green
Write-Host "Run .\run.ps1 to launch both the backend and frontend servers." -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Cyan
