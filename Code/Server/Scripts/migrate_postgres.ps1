# Define the backup file path
$backupFilePath = "../../../docker/Backup/db_backup.sql"

# Check if the backup file already exists
$counter = 0
while (Test-Path $backupFilePath) {
    $counter++
    $backupFilePath = "../../../docker/Backup/db_backup$counter.sql"
}

try {
    # Dump the database from the 'db' container
    docker exec -it db pg_dump -U postgres -d postgres > $backupFilePath
} catch {
    Write-Host "Error dumping the database: $_"
    exit 1
}

try {
    # Check if the 'postgres' database exists in the 'db1' container
    $dbExists = docker exec -it db1 psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'postgres'"

    # If the 'postgres' database exists, drop it
    if ($dbExists) {
        docker exec -it db1 dropdb -U postgres postgres
    }

    # Create the 'postgres' database
    docker exec -it db1 createdb -U postgres postgres
} catch {
    Write-Host "Error creating the database in db1: $_"
    exit 1
}

try {
    # Restore the dump to the 'db1' container
    Get-Content $backupFilePath | docker exec -i db1 psql -U postgres -d postgres
} catch {
    Write-Host "Error restoring the dump to db1: $_"
    exit 1
}