$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $true
Set-Location (Join-Path $PSScriptRoot '..')
python -c "import platform, sys; assert platform.system() == 'Windows' and platform.machine() == 'AMD64' and sys.version_info[:2] == (3, 11)"
python -m pip install --only-binary=:all: -r requirements-windows.txt
python -m pip check

$env:QT_QPA_PLATFORM = 'offscreen'
python -m unittest discover -s tests -v
python tests/smoke_gui.py
Remove-Item Env:QT_QPA_PLATFORM

python scripts/make_icon.py
python -m PyInstaller --clean --noconfirm Velqora-Windows.spec
$reports = New-Item -ItemType Directory -Force 'dist/reports'
$archive = Join-Path (Resolve-Path 'dist') 'Velqora-PDF-10.3-Windows-x64.zip'
Compress-Archive -Path 'dist/Velqora PDF' -DestinationPath $archive -Force
$testRoot = Join-Path $env:RUNNER_TEMP 'velqora-windows-zip-test'
Expand-Archive -LiteralPath $archive -DestinationPath $testRoot -Force
$portable = Join-Path $testRoot 'Velqora PDF'
python scripts/verify_windows.py $portable (Join-Path $reports.FullName 'windows-binary-audit.json')

$exe = Join-Path $portable 'Velqora PDF.exe'
$report = Join-Path $reports.FullName 'windows-app-selftest.json'
$process = Start-Process -FilePath $exe -ArgumentList "--self-test --report `"$report`"" -WorkingDirectory $testRoot -PassThru
if (-not $process.WaitForExit(180000)) {
    $process.Kill()
    throw 'Packaged Windows app self-test timed out.'
}
if ($process.ExitCode -ne 0 -or -not (Test-Path $report)) {
    if (Test-Path $report) { Get-Content $report }
    throw "Packaged Windows app self-test failed with exit code $($process.ExitCode)."
}
$result = Get-Content $report -Raw | ConvertFrom-Json
if ($result.status -ne 'passed' -or -not $result.frozen -or $result.machine -ne 'AMD64') {
    throw 'The packaged app did not report a successful native Windows test.'
}
Get-Content $report
$hash = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant()
"$hash  Velqora-PDF-10.3-Windows-x64.zip" | Set-Content 'dist/SHA256SUMS' -Encoding ascii
