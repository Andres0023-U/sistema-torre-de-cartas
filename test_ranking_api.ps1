$ErrorActionPreference = 'Stop'
$baseUrl = "https://sistema-torre-de-cartas.onrender.com"

# Login
$loginBody = @{ email = "jugador1@demo.com"; password = "Clave123" } | ConvertTo-Json
$loginRes = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
$headers = @{ Authorization = "Bearer $($loginRes.access_token)" }

Write-Host "=================== TEST RANKING ENDPOINTS ==================="

# 1. GET /ranking/
Write-Host "`n--- 1. GET /ranking/ ---"
try {
    $rGlobal = Invoke-RestMethod -Uri "$baseUrl/ranking/" -Headers $headers -Method Get
    Write-Host "GET /ranking/ - HTTP 200 OK"
    Write-Host "Total jugadores:" $rGlobal.Count
    $top5 = $rGlobal | Select-Object -First 5
    Write-Host "Primeras 5 posiciones:" ($top5 | ConvertTo-Json -Depth 5)
} catch {
    Write-Host "GET /ranking/ FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "CUERPO COMPLETO DE ERROR 500/HTTP:" $reader.ReadToEnd()
    }
}

# 2. GET /ranking/me
Write-Host "`n--- 2. GET /ranking/me ---"
try {
    $rMe = Invoke-RestMethod -Uri "$baseUrl/ranking/me" -Headers $headers -Method Get
    Write-Host "GET /ranking/me - HTTP 200 OK"
    Write-Host "Respuesta completa:" ($rMe | ConvertTo-Json -Depth 5)
} catch {
    Write-Host "GET /ranking/me FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "CUERPO COMPLETO DE ERROR 500/HTTP:" $reader.ReadToEnd()
    }
}

# 3. GET /tournaments/2/ranking
Write-Host "`n--- 3. GET /tournaments/2/ranking ---"
try {
    $rTourn2 = Invoke-RestMethod -Uri "$baseUrl/tournaments/2/ranking" -Headers $headers -Method Get
    Write-Host "GET /tournaments/2/ranking - HTTP 200 OK"
    Write-Host "Campos devueltos:" ($rTourn2.psobject.properties.Name -join ', ')
    if ($rTourn2.ranking) {
        $top3 = $rTourn2.ranking | Select-Object -First 3
        Write-Host "Primeras 3 posiciones del Torneo 2:" ($top3 | ConvertTo-Json -Depth 5)
    } else {
        Write-Host "Respuesta completa:" ($rTourn2 | ConvertTo-Json -Depth 5)
    }
} catch {
    Write-Host "GET /tournaments/2/ranking FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "CUERPO COMPLETO DE ERROR 500/HTTP:" $reader.ReadToEnd()
    }
}
