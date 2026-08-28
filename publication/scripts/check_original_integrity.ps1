param(
    [string]$Baseline = "publication/original_tracked_hashes.sha256",
    [switch]$Capture
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$baselinePath = Join-Path $projectRoot $Baseline

if ($Capture) {
    $lines = @()
    Push-Location $projectRoot
    try {
        $tracked = git ls-files
        foreach ($relative in $tracked) {
            if ($relative -notlike "publication/*") {
                $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $projectRoot $relative)).Hash.ToLower()
                $lines += "$hash *$relative"
            }
        }
    }
    finally {
        Pop-Location
    }
    [System.IO.File]::WriteAllLines($baselinePath, $lines, [System.Text.UTF8Encoding]::new($false))
    Write-Output "Captured SHA-256 baselines for $($lines.Count) original tracked files."
    exit 0
}

if (-not (Test-Path -LiteralPath $baselinePath)) {
    throw "Baseline hash file not found: $baselinePath"
}

$failures = @()
Get-Content -LiteralPath $baselinePath | ForEach-Object {
    if ($_ -match '^([0-9a-f]{64})\s+\*(.+)$') {
        $expected = $Matches[1]
        $relative = $Matches[2]
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $projectRoot $relative)).Hash.ToLower()
        if ($actual -ne $expected) { $failures += $relative }
    }
}

if ($failures.Count -gt 0) {
    Write-Error ("Original file integrity failure: " + ($failures -join ", "))
}

Write-Output "All original tracked files match the recorded SHA-256 baseline."
