# Arrêter les processus Docker si présents
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force

# Arrêter les processus Cursor multiples (garder une seule instance)
$cursorProcesses = Get-Process -Name "Cursor" | Sort-Object -Property WorkingSet64 -Descending
if ($cursorProcesses.Count -gt 1) {
    $cursorProcesses | Select-Object -Skip 1 | Stop-Process -Force
}

# Arrêter OneDrive si présent
Get-Process -Name "OneDrive" -ErrorAction SilentlyContinue | Stop-Process -Force

# Arrêter les processus WSL non essentiels
Get-Process -Name "wsl" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "wslhost" -ErrorAction SilentlyContinue | Stop-Process -Force

# Nettoyer la mémoire
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host "Optimisation de la mémoire terminée." 