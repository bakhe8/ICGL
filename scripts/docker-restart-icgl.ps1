Param()

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "Ensuring qdrant is up..."
docker compose -f docker-compose.yml up -d qdrant | Out-Null

$existing = docker ps -a --filter "name=icgl-app" --format "{{.ID}}"
if ($existing) {
    Write-Host "Found existing container icgl-app. Stopping and removing..."
    docker rm -f icgl-app | Out-Null
}

Write-Host "Starting icgl service (compose)..."
docker compose -f docker-compose.yml up -d --build icgl

Write-Host "Done. Run 'docker ps --filter name=icgl-app' to verify."
