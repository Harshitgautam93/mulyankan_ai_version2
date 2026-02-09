<#
Set TESSERACT_CMD user environment variable for this machine (no admin required).
It will try a few common local locations, then prompt you for the full path to tesseract.exe.
Usage (normal PowerShell):
  pwsh -File .\scripts\set_tesseract_cmd.ps1
or
  powershell -ExecutionPolicy Bypass -File .\scripts\set_tesseract_cmd.ps1
#>

Write-Host "Attempting to locate common local Tesseract installations..."
$candidates = @(
  "$PSScriptRoot\..\backend\tools\tesseract\tesseract.exe",
  "$PSScriptRoot\..\tools\tesseract\tesseract.exe",
  "$env:USERPROFILE\scoop\apps\tesseract\current\tesseract.exe",
  "C:\Program Files\Tesseract-OCR\tesseract.exe",
  "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
)

$found = $null
foreach ($p in $candidates) {
  $pp = Resolve-Path -LiteralPath $p -ErrorAction SilentlyContinue
  if ($pp) { $found = $pp; break }
}

if ($found) {
  $exe = $found.Path
  Write-Host "Found tesseract executable at: $exe"
} else {
  Write-Host "No common executable found. Please enter the full path to tesseract.exe (or drag it here), then press Enter."
  $exe = Read-Host "Full path to tesseract.exe"
  if (-not (Test-Path $exe)) {
    Write-Host "Path not found: $exe" -ForegroundColor Red
    exit 2
  }
}

Write-Host "Setting user environment variable TESSERACT_CMD to: $exe"
[Environment]::SetEnvironmentVariable('TESSERACT_CMD', $exe, 'User')

# Try to refresh env in this session if refreshenv is available
if (Get-Command refreshenv -ErrorAction SilentlyContinue) {
  try { refreshenv } catch { }
}

Write-Host "Done. To verify, run: tesseract --version"
Write-Host "If 'tesseract' is not on PATH you can still use OCR because pytesseract will read TESSERACT_CMD." 