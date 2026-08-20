# Runs the frontend test suite with the coverage gate (see vite.config.ts thresholds).
$ErrorActionPreference = "Stop"

Write-Host "== Frontend tests + coverage ==" -ForegroundColor Cyan
Push-Location frontend
try {
    npm run test:coverage
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
