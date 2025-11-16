Set-StrictMode -Version Latest
# ensure working directory is the script folder (project root)
Set-Location -Path $PSScriptRoot

$buildDir = ".\build"
$distDir = ".\dist"

if (Test-Path $buildDir) {
    Write-Host "Removing build folder: $buildDir"
    Remove-Item $buildDir -Recurse -Force -ErrorAction Stop
} else {
    Write-Host "No build folder to remove."
}

if (Test-Path $distDir) {
    Write-Host "Removing dist folder: $distDir"
    Remove-Item $distDir -Recurse -Force -ErrorAction Stop
} else {
    Write-Host "No dist folder to remove."
}

Write-Host "Running nicegui-pack..."
& nicegui-pack --onefile --windowed --icon favicon.ico --name "BCPrinter" .\BCPrinter.py
$exit = $LASTEXITCODE

if ($exit -ne 0) {
    Write-Error "nicegui-pack failed with exit code $exit"
    exit $exit
} else {
    Write-Host "nicegui-pack completed successfully."
}