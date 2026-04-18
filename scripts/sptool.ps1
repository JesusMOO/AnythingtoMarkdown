param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $ArgsList
)

& "$PSScriptRoot\..\python.exe" -m sptool.cli @ArgsList
exit $LASTEXITCODE
