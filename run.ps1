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
    throw 'Python 3.12 is required. Install Python and add it to PATH.'
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
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to install project dependencies. Remove the .venv folder and run again.'
    }
    New-Item -ItemType File -Force -Path $marker | Out-Null
}

# Create .env from the template if missing, so the app starts with a clear message.
$envFile = Join-Path $root '.env'
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $root '.env.example') $envFile
    Write-Host ''
    Write-Host 'Created .env from .env.example. Edit it and set LSEG_APP_KEY, and make sure LSEG Workspace Desktop is open.'
    Write-Host ''
}

& $venvPython -m financial_engineering.app
