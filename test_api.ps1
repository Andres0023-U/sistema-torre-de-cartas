$ErrorActionPreference = 'Stop'

Write-Host "=================== 1. VERIFICACIÓN OPENAPI ==================="
$json = Get-Content 'openapi_deployed.json' -Raw | ConvertFrom-Json
$paths = $json.paths.psobject.properties.Name

$hasOpenTournaments = $paths -contains '/tournaments/open'
$hasPasswordChange = $paths -contains '/auth/me/password'

Write-Host "GET /tournaments/open existe:" $hasOpenTournaments
Write-Host "PUT /auth/me/password existe:" $hasPasswordChange

# Schema check for /players/me/history
$historySchemaRef = $json.paths.'/history/my-matches'.get.responses.'200'.content.'application/json'.schema.items.'$ref'
if (-not $historySchemaRef) {
    $historySchemaRef = $json.paths.'/players/me/history'.get.responses.'200'.content.'application/json'.schema.items.'$ref'
}
Write-Host "History schema ref:" $historySchemaRef

$schemas = $json.components.schemas
$schemaName = $historySchemaRef.Split('/')[-1]
$historySchemaProps = $schemas.$schemaName.properties.psobject.properties.Name

Write-Host "Campos en esquema de historial ($schemaName):" ($historySchemaProps -join ', ')
Write-Host " - duration_minutes:" ($historySchemaProps -contains 'duration_minutes')
Write-Host " - final_life:" ($historySchemaProps -contains 'final_life')
Write-Host " - total_rounds:" ($historySchemaProps -contains 'total_rounds')
Write-Host " - won:" ($historySchemaProps -contains 'won')


Write-Host "`n=================== 2. AUTENTICACIÓN CON JUGADOR1 ==================="
$baseUrl = "https://sistema-torre-de-cartas.onrender.com"

# a) POST /auth/login
$loginBody = @{
    email = "jugador1@demo.com"
    password = "Clave123"
} | ConvertTo-Json

try {
    $loginRes = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method Post -ContentType "application/json" -Body $loginBody
    Write-Host "a) POST /auth/login - HTTP 200 OK"
    Write-Host "Campos devueltos:" ($loginRes.psobject.properties.Name -join ', ')
    Write-Host "Respuesta:" ($loginRes | ConvertTo-Json -Compress)
    $token = $loginRes.access_token
} catch {
    Write-Host "a) POST /auth/login FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Cuerpo de error 500/HTTP:" $reader.ReadToEnd()
    }
}

$headers = @{
    Authorization = "Bearer $token"
}

# b) GET /players/me/history (o /history/my-matches)
Write-Host "`n--- b) Historial de Jugador ---"
try {
    # Probar endpoint exacto solicitado
    $historyRes = Invoke-RestMethod -Uri "$baseUrl/history/my-matches" -Headers $headers -Method Get
    Write-Host "b) GET /history/my-matches - HTTP 200 OK"
    Write-Host "Total partidas devueltas:" $historyRes.Count
    if ($historyRes.Count -gt 0) {
        Write-Host "Primera partida devuelta:" ($historyRes[0] | ConvertTo-Json -Depth 3)
    }
} catch {
    Write-Host "b) GET /history/my-matches FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Cuerpo de error:" $reader.ReadToEnd()
    }
}

# Probar tambien si existe /players/me/history
try {
    $historyRes2 = Invoke-RestMethod -Uri "$baseUrl/players/me/history" -Headers $headers -Method Get
    Write-Host "b) GET /players/me/history - HTTP 200 OK"
    Write-Host "Total partidas devueltas:" $historyRes2.Count
    if ($historyRes2.Count -gt 0) {
        Write-Host "Primera partida devuelta:" ($historyRes2[0] | ConvertTo-Json -Depth 3)
    }
} catch {
    Write-Host "b) GET /players/me/history status/detail:" $_.Exception.Message
}

# c) GET /ranking/me
Write-Host "`n--- c) Ranking Mi Perfil ---"
try {
    $rankingMe = Invoke-RestMethod -Uri "$baseUrl/ranking/me" -Headers $headers -Method Get
    Write-Host "c) GET /ranking/me - HTTP 200 OK"
    Write-Host "Campos devueltos:" ($rankingMe.psobject.properties.Name -join ', ')
    Write-Host "Respuesta:" ($rankingMe | ConvertTo-Json -Compress)
} catch {
    Write-Host "c) GET /ranking/me FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Cuerpo de error:" $reader.ReadToEnd()
    }
}

# d) GET /ranking/
Write-Host "`n--- d) Ranking Global ---"
try {
    $rankingGlobal = Invoke-RestMethod -Uri "$baseUrl/ranking/" -Headers $headers -Method Get
    Write-Host "d) GET /ranking/ - HTTP 200 OK"
    Write-Host "Total jugadores devueltos:" $rankingGlobal.Count
    if ($rankingGlobal.Count -gt 0) {
        Write-Host "Campos de primer jugador:" ($rankingGlobal[0].psobject.properties.Name -join ', ')
        Write-Host "Primer elemento:" ($rankingGlobal[0] | ConvertTo-Json -Compress)
    }
} catch {
    Write-Host "d) GET /ranking/ FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Cuerpo de error:" $reader.ReadToEnd()
    }
}

# e) GET /tournaments/open
Write-Host "`n--- e) Torneos Abiertos ---"
try {
    $openTournaments = Invoke-RestMethod -Uri "$baseUrl/tournaments/open" -Headers $headers -Method Get
    Write-Host "e) GET /tournaments/open - HTTP 200 OK"
    Write-Host "Total torneos abiertos:" $openTournaments.Count
    Write-Host "Respuesta completa:" ($openTournaments | ConvertTo-Json -Depth 4)
} catch {
    Write-Host "e) GET /tournaments/open FALLÓ:" $_.Exception.Message
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Cuerpo de error:" $reader.ReadToEnd()
    }
}

Write-Host "`n=================== 3. PRUEBA DE AUTO-INSCRIPCIÓN ==================="
$aficionadosTournament = $openTournaments | Where-Object { $_.name -like "*Aficionados*" }
if ($aficionadosTournament) {
    $tId = $aficionadosTournament.tournament_id
    Write-Host "Encontrado 'Torneo de Aficionados' con ID:" $tId

    # Inscribir
    try {
        Write-Host "Ejecutando POST /tournaments/$tId/registrations..."
        $regRes = Invoke-RestMethod -Uri "$baseUrl/tournaments/$tId/registrations" -Headers $headers -Method Post
        Write-Host "Inscripción exitosa (HTTP 200/201):" ($regRes | ConvertTo-Json -Compress)
    } catch {
        Write-Host "Inscripción falló:" $_.Exception.Message
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            Write-Host "Cuerpo de error:" $reader.ReadToEnd()
        }
    }

    # Dar de baja para dejarlo como estaba
    try {
        Write-Host "Ejecutando DELETE /tournaments/$tId/registrations..."
        $unregRes = Invoke-RestMethod -Uri "$baseUrl/tournaments/$tId/registrations" -Headers $headers -Method Delete
        Write-Host "Baja exitosa (HTTP 200/204):" ($unregRes | ConvertTo-Json -Compress)
    } catch {
        Write-Host "Baja por /tournaments/$tId/registrations falló, probando con /player_id..."
        try {
            # Probar DELETE /tournaments/{id}/registrations/{player_id}
            # Obtener player_id de jugador1
            $myProfile = Invoke-RestMethod -Uri "$baseUrl/auth/me" -Headers $headers -Method Get
            $pId = 1 # O buscar player_id
            $unregRes2 = Invoke-RestMethod -Uri "$baseUrl/tournaments/$tId/registrations/$pId" -Headers $headers -Method Delete
            Write-Host "Baja con player_id exitosa:" ($unregRes2 | ConvertTo-Json -Compress)
        } catch {
            Write-Host "Baja falló:" $_.Exception.Message
            if ($_.Exception.Response) {
                $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                Write-Host "Cuerpo de error:" $reader.ReadToEnd()
            }
        }
    }
} else {
    Write-Host "No se encontró 'Torneo de Aficionados' en GET /tournaments/open"
}
