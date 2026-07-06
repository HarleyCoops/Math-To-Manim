$ErrorActionPreference = 'SilentlyContinue'

Write-Host "=== Drives ==="
Get-PSDrive -PSProvider FileSystem | ForEach-Object {
  $t = $_.Used + $_.Free
  "{0,-4} Free={1,8:N2} GB  Used={2,8:N2} GB  Total={3,8:N2} GB" -f ($_.Name + ':'), ($_.Free/1GB), ($_.Used/1GB), ($t/1GB)
}

Write-Host "`n=== VHDX (WSL / Store) ==="
Get-ChildItem "$env:LOCALAPPDATA\Packages" -Recurse -Filter '*.vhdx' -ErrorAction SilentlyContinue |
  Sort-Object Length -Descending | Select-Object -First 25 |
  ForEach-Object { "{0,8:N2} GB  {1}" -f ($_.Length/1GB), $_.FullName }

function FolderGB($p) {
  if (-not (Test-Path -LiteralPath $p)) { return }
  $b = (Get-ChildItem -LiteralPath $p -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
  if ($b -gt 200MB) { "{0,8:N2} GB  {1}" -f ($b/1GB), $p }
}

Write-Host "`n=== Heavy paths (slow on huge trees) ==="
@(
  "$env:LOCALAPPDATA\Temp", "$env:TEMP", "$env:WINDIR\Temp",
  "$env:WINDIR\SoftwareDistribution\Download",
  "$env:LOCALAPPDATA\Microsoft\Windows\INetCache",
  "$env:USERPROFILE\.npm", "$env:USERPROFILE\.cache", "$env:USERPROFILE\.nuget\packages",
  "$env:USERPROFILE\.gradle\caches", "$env:USERPROFILE\AppData\Local\pnpm-store",
  "$env:LOCALAPPDATA\pip", "$env:LOCALAPPDATA\Programs",
  "$env:LOCALAPPDATA\Docker", "$env:LOCALAPPDATA\DockerDesktop", "C:\ProgramData\Docker",
  "$env:USERPROFILE\AppData\Local\Android\Sdk"
) | ForEach-Object { FolderGB $_ }

Write-Host "`n=== Top profile subfolders (first level; slower) ==="
Get-ChildItem $env:USERPROFILE -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object {
  $b = (Get-ChildItem $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum
  [PSCustomObject]@{ GB = [math]::Round($b/1GB,2); Path = $_.FullName }
} | Sort-Object GB -Descending | Select-Object -First 15 | Format-Table -AutoSize

Write-Host "`n=== Large installed apps (registry estimate) ==="
Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*,
  HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* -ErrorAction SilentlyContinue |
  Where-Object DisplayName -and EstimatedSize |
  Select @{N='MB';E={[math]::Round($_.EstimatedSize/1024,0)}}, @{N='Name';E={$_.DisplayName}} |
  Sort MB -Descending | Select -First 25 | Format-Table -AutoSize