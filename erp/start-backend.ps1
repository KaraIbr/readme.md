
param(
    [switch]$NoReload,
    [switch]$Frontend
)

$reload = if ($NoReload) { $false } else { $true }
$crmPort = 8000
$iamPort = 8100
$frontendPort = 5173

Write-Host "Starting VERP backend services..." -ForegroundColor Cyan
Write-Host "  CRM -> http://127.0.0.1:$crmPort" -ForegroundColor Green
Write-Host "  IAM -> http://127.0.0.1:$iamPort" -ForegroundColor Green

$reloadArg = if ($reload) { "--reload" } else { "" }

$crmJob = Start-Process -FilePath "uv" -ArgumentList "run uvicorn CRM.main:app --host 127.0.0.1 --port $crmPort $reloadArg" -NoNewWindow -PassThru
$iamJob = Start-Process -FilePath "uv" -ArgumentList "run uvicorn IAM.main:app --host 127.0.0.1 --port $iamPort $reloadArg" -NoNewWindow -PassThru

$frontendJob = $null
if ($Frontend) {
    Write-Host "  Frontend -> http://127.0.0.1:$frontendPort" -ForegroundColor Green
    $frontendJob = Start-Process -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "frontend" -NoNewWindow -PassThru
}

Write-Host "`nPress any key to stop all services." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

foreach ($job in @($crmJob, $iamJob, $frontendJob)) {
    if ($job -and -not $job.HasExited) { $job.Kill() }
}
Write-Host "All services stopped." -ForegroundColor Cyan
