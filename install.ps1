#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error "uv is required; install uv and run this script again"
    exit 127
}

$installer = Join-Path $PSScriptRoot "install.py"
& uv run --no-project --with "tomlkit==0.15.1" python $installer @args
exit $LASTEXITCODE
