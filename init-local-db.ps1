$env:PGPASSWORD = Read-Host "Contraseña de postgres"

$ddl = "C:\Users\santi\Documents\desarrollo_orientado_plataformas\torre-de-cartas\database\ddl"
$seeds = "C:\Users\santi\Documents\desarrollo_orientado_plataformas\torre-de-cartas\database\seeds"

psql -U postgres -h localhost -c "DROP DATABASE IF EXISTS torre_de_cartas;"
psql -U postgres -h localhost -c "CREATE DATABASE torre_de_cartas;"

psql -U postgres -h localhost -d torre_de_cartas -f "$ddl\00_create_schemas.sql"
psql -U postgres -h localhost -d torre_de_cartas -f "$ddl\01_tables.sql"
psql -U postgres -h localhost -d torre_de_cartas -f "$ddl\03_functions.sql"
psql -U postgres -h localhost -d torre_de_cartas -f "$ddl\02_triggers.sql"
psql -U postgres -h localhost -d torre_de_cartas -f "$seeds\00_roles.sql"
psql -U postgres -h localhost -d torre_de_cartas -f "$seeds\01_cards.sql"

Write-Host "Base de datos local creada y lista."