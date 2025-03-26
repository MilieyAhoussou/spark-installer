# Optimisation de Windows Defender
# Nécessite des droits administrateur

# Définir des exclusions pour les dossiers fréquemment utilisés
Add-MpPreference -ExclusionPath "$env:USERPROFILE\Downloads" -ErrorAction SilentlyContinue
Add-MpPreference -ExclusionPath "$env:USERPROFILE\Documents" -ErrorAction SilentlyContinue

# Réduire la priorité du processus d'analyse en arrière-plan
Set-MpPreference -ScanAvgCPULoadFactor 50

# Planifier les analyses pendant les heures creuses
Set-MpPreference -ScanScheduleDay 1 # Dimanche
Set-MpPreference -ScanScheduleTime 02:00:00 # 2h du matin

# Désactiver l'analyse en temps réel temporairement (à utiliser avec précaution)
# Set-MpPreference -DisableRealtimeMonitoring $true

Write-Host "Paramètres de Windows Defender optimisés." 