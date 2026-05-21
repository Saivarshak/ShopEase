param(
    [Parameter(Mandatory = $true)]
    [string]$PostgresPassword,

    [string]$DatabaseName = "shopdb",
    [string]$SchemaName = "public",
    [string]$PostgresHost = "localhost",
    [int]$PostgresPort = 5432,
    [string]$PostgresUser = "postgres",
    [string]$FixturePath = "data/backup_fixture.json",
    [switch]$UseExistingDatabase
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not (Test-Path $FixturePath)) {
    throw "Fixture file not found: $FixturePath"
}

$pgInstall = Get-ChildItem "C:\Program Files\PostgreSQL" -Directory |
    Sort-Object { [version]$_.Name } -Descending |
    Select-Object -First 1

if (-not $pgInstall) {
    throw "PostgreSQL installation was not found under C:\Program Files\PostgreSQL"
}

$pgBin = Join-Path $pgInstall.FullName "bin"
$psql = Join-Path $pgBin "psql.exe"
$createdb = Join-Path $pgBin "createdb.exe"

if (-not (Test-Path $psql) -or -not (Test-Path $createdb)) {
    throw "PostgreSQL client tools were not found in $pgBin"
}

$env:PGPASSWORD = $PostgresPassword

$dbExists = & $psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DatabaseName';"
if ($LASTEXITCODE -ne 0) {
    throw "Could not connect to PostgreSQL server at ${PostgresHost}:${PostgresPort} as ${PostgresUser}."
}

if (-not $dbExists.Trim()) {
    if ($UseExistingDatabase) {
        throw "Database $DatabaseName does not exist, but -UseExistingDatabase was specified."
    }

    & $createdb -h $PostgresHost -p $PostgresPort -U $PostgresUser $DatabaseName
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create database $DatabaseName."
    }
}
elseif (-not $UseExistingDatabase) {
    $tableCount = & $psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d $DatabaseName -tAc "SELECT count(*) FROM information_schema.tables WHERE table_schema = '$SchemaName';"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not inspect database $DatabaseName."
    }

    if ([int]$tableCount.Trim() -gt 0) {
        throw "Database $DatabaseName already contains tables in schema $SchemaName. Use a fresh database name or pass -UseExistingDatabase only if you are sure the target schema is empty."
    }
}

& $psql -h $PostgresHost -p $PostgresPort -U $PostgresUser -d $DatabaseName -v ON_ERROR_STOP=1 -c "CREATE SCHEMA IF NOT EXISTS ""$SchemaName"";"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create or verify schema $SchemaName."
}

$env:DATABASE_URL = ""
$env:DB_ENGINE = "django.db.backends.postgresql"
$env:DB_NAME = $DatabaseName
$env:DB_USER = $PostgresUser
$env:DB_PASSWORD = $PostgresPassword
$env:DB_HOST = $PostgresHost
$env:DB_PORT = [string]$PostgresPort
$env:PGOPTIONS = "-c search_path=$SchemaName,public"

python manage.py migrate --noinput
if ($LASTEXITCODE -ne 0) {
    throw "Django migrations failed."
}

python manage.py loaddata $FixturePath
if ($LASTEXITCODE -ne 0) {
    throw "Loading fixture data failed."
}

@'
from django.apps import apps
from django.core.management.color import no_style
from django.db import connection

app_labels = {"auth", "store"}
models = [model for model in apps.get_models() if model._meta.app_label in app_labels]

with connection.cursor() as cursor:
    for statement in connection.ops.sequence_reset_sql(no_style(), models):
        cursor.execute(statement)

print("PostgreSQL import completed successfully.")
'@ | python manage.py shell

if ($LASTEXITCODE -ne 0) {
    throw "Sequence reset failed after loading data."
}
