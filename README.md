# Niagara

## Purpose

Niagara is a deliberately simple, locally hosted customer manager. It is the source workload for an Azure migration proof of concept—not an Azure deployment or migration harness.

## Prerequisites

- Windows
- Python 3.12
- SQL Server Express, using the default `localhost\SQLEXPRESS` instance
- Microsoft ODBC Driver 18 for SQL Server

## Setup

Open PowerShell in the repository root and run:

```powershell
cd to project directory
.\scripts\setup.ps1
```
```
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

The script creates and activates `.venv`, installs the Python dependencies, and copies `.env.example` to the ignored `.env` file when needed. Edit `.env` if your SQL Server instance differs.

## Database

At startup, the application connects with Windows Integrated Authentication and attempts to create `NiagaraDb`, creates its `customers` table, and adds five sample rows only when the table is empty.

Your Windows account must have permission to create the database. If it does not, connect to SQL Server as an administrator, run:

```sql
CREATE DATABASE NiagaraDb;
```

Grant your Windows account access to that database if necessary, then restart the application. SQL Server stays local/private.

## Running

```powershell
.\scripts\run.ps1
```

Open <http://localhost:8000>. The app also listens on the PC's network interfaces on TCP port 8000.

## Testing

With the application running, open a second PowerShell window:

```powershell
.\scripts\test.ps1 -BaseUrl "http://localhost:8000"
```

The same script can later test another base URL. Interactive API documentation is available at <http://localhost:8000/docs>.

## Public Access

```text
Public IP :8000
    |
Router Port Forward
    |
Windows PC :8000
```

If public access is required, manually allow inbound TCP 8000 in Windows Firewall and forward external TCP 8000 on the router to TCP 8000 on this PC's reserved local IP. Browse to `http://<PUBLIC-IP>:8000`. Expose only the FastAPI port; keep SQL Server private and do not forward its port. This sample has no authentication or TLS, so limit exposure to controlled proof-of-concept use.

If CGNAT, ISP restrictions, or router limitations prevent direct access, an optional Cloudflare quick tunnel can proxy the web app without becoming an application dependency:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

## Future Migration

```text
BEFORE                    AFTER

Windows PC                Azure App Service
   |                           |
FastAPI                   FastAPI
   |                           |
SQL Server Express        Azure SQL Database
```
