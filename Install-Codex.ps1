param([switch]$Static)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskAssetDir = if (Test-Path -LiteralPath (Join-Path $taskRoot 'assets')) { Join-Path $taskRoot 'assets' } else { $taskRoot }
$taskFile = if ($Static -and (Test-Path -LiteralPath (Join-Path $taskAssetDir 'static-spritesheet.webp'))) { 'static-spritesheet.webp' } else { 'spritesheet.webp' }
$taskSource = Join-Path $taskAssetDir $taskFile
if (!(Test-Path -LiteralPath $taskSource)) { throw "Missing pet asset: $taskSource" }
$taskCodexDir = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$taskPetDir = Join-Path $taskCodexDir 'pets\miku-mini'
$taskBackup = Join-Path $taskRoot ('backups\native-' + (Get-Date -Format 'yyyyMMdd-HHmmssfff'))
New-Item -ItemType Directory -Path $taskBackup -Force | Out-Null
foreach ($taskName in @('pet.json','spritesheet.webp')) {
    $taskOldFile = Join-Path $taskPetDir $taskName
    if (Test-Path -LiteralPath $taskOldFile) { Copy-Item -LiteralPath $taskOldFile -Destination $taskBackup }
}
New-Item -ItemType Directory -Path $taskPetDir -Force | Out-Null
$taskMeta = Get-Content -LiteralPath (Join-Path $taskRoot 'pet.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$taskMeta.spritesheetPath = 'spritesheet.webp'
$taskTemp = Join-Path $taskPetDir 'spritesheet.webp.new'
Copy-Item -LiteralPath $taskSource -Destination $taskTemp -Force
Move-Item -LiteralPath $taskTemp -Destination (Join-Path $taskPetDir 'spritesheet.webp') -Force
$taskJson = $taskMeta | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText((Join-Path $taskPetDir 'pet.json'), $taskJson + "`n", [System.Text.UTF8Encoding]::new($false))
Write-Host "Installed Codex pet: $taskPetDir"
Write-Host "Backup: $taskBackup"
Write-Host 'Restart Codex and select Miku Mini in the pet picker to reload the updated image.'
