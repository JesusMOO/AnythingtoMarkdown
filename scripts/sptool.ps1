param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ArgsList
)

$PythonExe = Join-Path $PSScriptRoot "..\.venv\Scripts\python.exe"

if ($ArgsList.Count -ge 2 -and $ArgsList[0] -eq "ultra" -and $ArgsList[1] -eq "start") {
    $env:TOOL_MODE = "ultra"
    Write-Output "ultra mode enabled"
    exit 0
}

if ($ArgsList.Count -ge 2 -and $ArgsList[0] -eq "ultra" -and $ArgsList[1] -eq "exit") {
    Remove-Item Env:TOOL_MODE -ErrorAction SilentlyContinue
    Write-Output "ultra mode disabled"
    exit 0
}

& $PythonExe -m sptool.cli @ArgsList
exit $LASTEXITCODE
