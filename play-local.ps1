$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$gameUrl = 'http://127.0.0.1:5055/'
$running = $false
try {
    $health = Invoke-RestMethod ($gameUrl + 'health') -TimeoutSec 2
    $running = $health.status -eq 'ok'
} catch {}
if (-not $running) {
    $server = Join-Path $PSScriptRoot 'build\dist\armywars\armywars.exe'
    if (-not (Test-Path -LiteralPath $server)) {
        throw 'Build missing. Run build-local.ps1 first.'
    }
    Start-Process -FilePath $server -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput 'build\server.log' -RedirectStandardError 'build\server-error.log'
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Seconds 1
        try {
            $health = Invoke-RestMethod ($gameUrl + 'health') -TimeoutSec 2
            if ($health.status -eq 'ok') { $running = $true; break }
        } catch {}
    }
    if (-not $running) { throw 'Server failed to start. See build\server-error.log.' }
}
$browser = Join-Path $PSScriptRoot 'build\runtime\flashbrowser\app\FlashBrowser.exe'
if (Test-Path -LiteralPath $browser) {
    Start-Process -FilePath $browser -ArgumentList $gameUrl
} else {
    Write-Host "Server ready at $gameUrl Open this address in a Flash-compatible browser."
}
