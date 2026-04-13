Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $RootDir "data"
$RawDir = Join-Path $DataDir "raw"
$YoloDir = Join-Path $DataDir "visdrone"
$TmpDir = Join-Path $DataDir "tmp"

function Ensure-Directory {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Download-File {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    if (Test-Path -LiteralPath $OutputPath) {
        Write-Host "Resuming or validating existing archive: $OutputPath"
    }

    Write-Host "Downloading $Url"
    & curl.exe -L --fail --retry 3 -C - $Url -o $OutputPath
    if ($LASTEXITCODE -ne 0) {
        throw "curl.exe failed while downloading $Url"
    }
}

function Extract-File {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Archive,
        [Parameter(Mandatory = $true)]
        [string]$Target
    )

    if (Test-Path -LiteralPath $Target) {
        Write-Host "Skipping existing extract: $Target"
        return
    }

    Write-Host "Extracting $Archive"
    Expand-Archive -LiteralPath $Archive -DestinationPath $RawDir -Force
}

function Ensure-Split {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [Parameter(Mandatory = $true)]
        [string]$Archive,
        [Parameter(Mandatory = $true)]
        [string]$Target
    )

    if (Test-Path -LiteralPath $Target) {
        Write-Host "Skipping download and extract for existing split: $Target"
        return
    }

    Download-File -Url $Url -OutputPath $Archive
    Extract-File -Archive $Archive -Target $Target
}

function Resolve-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return "python"
    }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return "py"
    }

    throw "Could not find python or py on PATH."
}

Ensure-Directory -Path $RawDir
Ensure-Directory -Path $YoloDir
Ensure-Directory -Path $TmpDir

Ensure-Split `
    -Url "https://github.com/ultralytics/yolov5/releases/download/v1.0/VisDrone2019-DET-train.zip" `
    -Archive (Join-Path $TmpDir "VisDrone2019-DET-train.zip") `
    -Target (Join-Path $RawDir "VisDrone2019-DET-train")
Ensure-Split `
    -Url "https://github.com/ultralytics/yolov5/releases/download/v1.0/VisDrone2019-DET-val.zip" `
    -Archive (Join-Path $TmpDir "VisDrone2019-DET-val.zip") `
    -Target (Join-Path $RawDir "VisDrone2019-DET-val")
Ensure-Split `
    -Url "https://github.com/ultralytics/yolov5/releases/download/v1.0/VisDrone2019-DET-test-dev.zip" `
    -Archive (Join-Path $TmpDir "VisDrone2019-DET-test-dev.zip") `
    -Target (Join-Path $RawDir "VisDrone2019-DET-test-dev")

$pythonCommand = Resolve-PythonCommand
& $pythonCommand (Join-Path $RootDir "scripts\prepare_visdrone.py") --root $RootDir
if ($LASTEXITCODE -ne 0) {
    throw "VisDrone conversion failed."
}

Write-Host "VisDrone download and conversion complete."
