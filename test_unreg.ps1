$baseUrl = "https://sistema-torre-de-cartas.onrender.com"
$loginBody = @{ email = "jugador1@demo.com"; password = "Clave123" } | ConvertTo-Json
$loginRes = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
$headers = @{ Authorization = "Bearer $($loginRes.access_token)" }

Write-Host "Realizando baja del torneo 3..."
try {
    # Probar DELETE /tournaments/3/registrations (sin player_id en path)
    $res1 = Invoke-RestMethod -Uri "$baseUrl/tournaments/3/registrations" -Headers $headers -Method Delete
    Write-Host "DELETE /tournaments/3/registrations exito:" ($res1 | ConvertTo-Json -Compress)
} catch {
    Write-Host "DELETE /tournaments/3/registrations falló:" $_.Exception.Message
    try {
        # Probar DELETE /tournaments/3/registrations/1
        $res2 = Invoke-RestMethod -Uri "$baseUrl/tournaments/3/registrations/1" -Headers $headers -Method Delete
        Write-Host "DELETE /tournaments/3/registrations/1 exito:" ($res2 | ConvertTo-Json -Compress)
    } catch {
        Write-Host "DELETE /tournaments/3/registrations/1 falló:" $_.Exception.Message
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            Write-Host "Cuerpo de error:" $reader.ReadToEnd()
        }
    }
}
