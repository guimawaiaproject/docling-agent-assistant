# Docker Dev — Docling (lance docker compose pour environnement complet)
# Usage: .\scripts\docker-dev.ps1 [up|down|logs]
# Prérequis: .env configuré (DATABASE_URL, etc.)

param([string]$Action = "up")

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
Set-Location $root

if (-not (Test-Path ".env")) {
    Write-Host "[WARN] .env absent. Copier .env.example vers .env" -ForegroundColor Yellow
}

switch ($Action.ToLower()) {
    "up" {
        Write-Host "`n=== DOCLING — DOCKER COMPOSE UP ===" -ForegroundColor Cyan
        docker compose up -d
        Write-Host "`nServices:"
        Write-Host "  API  : http://localhost:8000"
        Write-Host "  PWA  : http://localhost:5173"
        Write-Host "  Postgres : localhost:5432"
        Write-Host ""
    }
    "down" {
        Write-Host "`n=== DOCLING — DOCKER COMPOSE DOWN ===" -ForegroundColor Cyan
        docker compose down
        Write-Host ""
    }
    "logs" {
        docker compose logs -f
    }
    default {
        Write-Host "Usage: .\scripts\docker-dev.ps1 [up|down|logs]" -ForegroundColor Gray
        exit 1
    }
}
