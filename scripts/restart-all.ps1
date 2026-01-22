# سكربت إعادة تشغيل شامل لسيرفرات ICGL (Vite + FastAPI)
# يقتل أي عملية على المنافذ 8080 و5173، ثم يشغل كل السيرفرات نظيفاً

$ErrorActionPreference = 'Stop'

Write-Host "🔴 Killing any process on ports 8080 and 5173..."
$ports = @(8080, 5173)
foreach ($port in $ports) {
    $pids = netstat -ano | Select-String ":$port" | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Select-Object -Unique
    foreach ($pid in $pids) {
        if ($pid -match '^[0-9]+$') {
            try {
                Stop-Process -Id $pid -Force
                Write-Host "Killed process $pid on port $port"
            } catch {
                Write-Host "Could not kill process $pid (may already be stopped)"
            }
        }
    }
}

Write-Host "🟢 Rebuilding and starting Vite frontend on port 8080..."
Push-Location web
npm install
Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c npm run dev"
Pop-Location

Start-Sleep -Seconds 2

Write-Host "🟢 Starting FastAPI backend on port 5173..."
Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c python -m uvicorn api.server:app --host 127.0.0.1 --port 5173 --reload"

Write-Host "✅ All servers restarted cleanly."
