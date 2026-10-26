$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3.10 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.10 is required to create the build environment.' }
}
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $python -m pip install -r requirements.txt pyinstaller
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $python -m PyInstaller --onedir --console --noupx --noconfirm `
    --add-data "$PSScriptRoot\assets;assets" `
    --add-data "$PSScriptRoot\config;config" `
    --add-data "$PSScriptRoot\stub;stub" `
    --add-data "$PSScriptRoot\templates;templates" `
    --add-data "$PSScriptRoot\villages;villages" `
    --distpath build/dist --workpath build/work --specpath build/bundle `
    --icon "$PSScriptRoot\build\icon.ico" --name armywars server.py
if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
