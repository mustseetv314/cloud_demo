$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python was not found. Install Python 3.12 and ensure it is on PATH."
}

$PythonVersion = & python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($PythonVersion -ne "3.12") {
    throw "Python 3.12 is required; found Python $PythonVersion."
}

if (-not (Test-Path ".venv")) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example."
}

Write-Host ""
Write-Host "Setup complete. Manual prerequisites:"
Write-Host "- Install and start SQL Server Express (localhost\SQLEXPRESS)."
Write-Host "- Install Microsoft ODBC Driver 18 for SQL Server."
Write-Host "- Ensure your Windows account can create/access NiagaraDb."
Write-Host "- Configure Windows Firewall and router port forwarding manually only if public access is needed."
