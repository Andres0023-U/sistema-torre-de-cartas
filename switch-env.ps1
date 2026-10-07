param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("local", "cloud")]
    [string]$target
)

$ErrorActionPreference = "Stop"

$backend = "C:\Users\santi\Documents\desarrollo_orientado_plataformas\torre-de-cartas\backend"
$source = Join-Path $backend ".env.$target"
$dest = Join-Path $backend ".env"

if (-not (Test-Path $source)) { throw "No existe $source" }

$text = [System.IO.File]::ReadAllText($source).TrimStart([char]0xFEFF)

if ($text -notmatch "(?m)^\s*DATABASE_URL\s*=") { throw "$source no tiene DATABASE_URL" }
if ($text -notmatch "(?m)^\s*SECRET_KEY\s*=") { throw "$source no tiene SECRET_KEY" }

[System.IO.File]::WriteAllText($dest, $text, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "Backend apuntando a $target. El .env pesa $((Get-Item $dest).Length) bytes."