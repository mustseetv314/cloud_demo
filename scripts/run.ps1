$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    throw "Virtual environment not found. Run .\scripts\setup.ps1 first."
}
. .\.venv\Scripts\Activate.ps1

Write-Host @"
MigrationDemo is running.

Local:
http://localhost:8000

Health:
http://localhost:8000/health

API:
http://localhost:8000/api/customers

Swagger:
http://localhost:8000/docs
"@

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
