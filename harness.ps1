# Convenience wrapper: .\harness.ps1 run --models my-model
& "$PSScriptRoot\.venv\Scripts\python.exe" -m harness @args
exit $LASTEXITCODE
