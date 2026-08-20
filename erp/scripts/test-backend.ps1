# Runs the full VERP backend test suite (CRM + IAM) with coverage gates.
$ErrorActionPreference = "Stop"

Write-Host "== CRM suite (coverage gate: 75%) ==" -ForegroundColor Cyan
uv run pytest --cov=CRM/src --cov-report=term-missing --cov-fail-under=75
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "== IAM suite (coverage gate: 70%) ==" -ForegroundColor Cyan
uv run pytest IAM/tests --cov=IAM/src --cov-report=term-missing --cov-fail-under=70
exit $LASTEXITCODE
