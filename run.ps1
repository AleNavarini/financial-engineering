$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root

$pythonCommand = Get-Command py -ErrorAction SilentlyContinue
$pythonArguments = @('-3.12')
if ($null -eq $pythonCommand) {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    $pythonArguments = @()
}
if ($null -eq $pythonCommand) {
    throw 'Python 3.12 is required. Install Python or the Python Launcher for Windows.'
}

$venv = Join-Path $root '.venv'
$venvPython = Join-Path $venv 'Scripts\python.exe'
$marker = Join-Path $venv '.installed'
$needsInstall = -not (Test-Path $venvPython) -or -not (Test-Path $marker)

if (-not $needsInstall) {
    $needsInstall = (Get-Item (Join-Path $root 'pyproject.toml')).LastWriteTimeUtc -gt (Get-Item $marker).LastWriteTimeUtc
}

if ($needsInstall) {
    & $pythonCommand.Source @pythonArguments -m venv $venv
    & $venvPython -m pip install -e $root
    New-Item -ItemType File -Force -Path $marker | Out-Null
}

& $venvPython -m financial_engineering.api
