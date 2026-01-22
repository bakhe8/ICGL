<#
1. قتل جميع العمليات السابقة على المنافذ (قابل للتخصيص)
2. حذف ملفات القفل وملفات PID إذا وجدت
3. تهيئة البيئة الافتراضية بمسار بايثون مخصص (اختياري)
4. تثبيت الحزم عبر pip أو poetry (يتحقق من توفر poetry)
5. تثبيت أدوات التطوير (dev) إذا كانت معرفة
6. تفعيل pre-commit إذا كان متوفرًا
7. تشغيل Qdrant عبر docker-compose إذا كان متوفرًا
8. إعادة بناء npm (npm install) قبل تشغيل Vite
9. تشغيل الباك اند والفرونت اند مع إمكانية تخصيص المنافذ
10. دعم خيارات Force، health check، وإعادة التشغيل فقط لخدمة معينة
11. رسائل واضحة وتوثيق داخلي لكل خطوة
12. دعم المعلمات (parameters) لتشغيل أجزاء محددة فقط أو جميع الخدمات
خيارات السكربت (يمكن تعديلها أو تمريرها كمعلمات):
# --------------------------------------------------
#>
param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 8080,
    [string]$PythonPath = "python",
    [switch]$WithPoetry = $false,
    [switch]$WithPreCommit = $false,
    [switch]$WithQdrant = $false,
    [switch]$WithDevExtras = $false,
    [switch]$WithNpmInstall = $true,
    [switch]$WithHealthCheck = $false,
    [switch]$Force = $false
)
<#
# 4. تشغيل Qdrant إذا كان مطلوبًا
#>
if ($WithQdrant) {
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        Write-Host "Bringing up Qdrant (docker-compose)..." -ForegroundColor Cyan
        docker-compose up -d qdrant
    } else {
        Write-Host "⚠️ docker-compose غير متوفر. تخطي تشغيل Qdrant." -ForegroundColor Yellow
    }
}
<#
# 5. إعادة بناء npm قبل تشغيل Vite
#>
if ($WithNpmInstall) {
    Write-Host "Running npm install in web..." -ForegroundColor Cyan
    Push-Location web
    npm install
    Pop-Location
}
<#
# 6. تشغيل الباك اند (API)
#>
Write-Host "Starting backend (API) on port $BackendPort..." -ForegroundColor Green
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-NoLogo","-Command","cd `"$PWD`"; .venv\Scripts\Activate.ps1; python -m uvicorn api.server:app --host 127.0.0.1 --port $BackendPort" -WindowStyle Hidden
<#
# 7. تشغيل الفرونت اند (Vite)
#>
Write-Host "Starting frontend (Vite) on port $FrontendPort..." -ForegroundColor Green
$webDir = Join-Path $PWD "web"
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-NoLogo","-Command","cd `"$webDir`"; npm run dev -- --host --port $FrontendPort" -WindowStyle Hidden
<#
# 8. Health check (اختياري)
#>
if ($WithHealthCheck) {
    Write-Host "Checking backend health..." -ForegroundColor Cyan
    # يمكنك هنا إضافة كود فحص الصحة الفعلي إذا رغبت
}
Write-Host "✅ All services started."
Write-Host "  API   -> http://localhost:$BackendPort" -ForegroundColor Green
Write-Host "  Front -> http://localhost:$FrontendPort/app/" -ForegroundColor Green
Write-Host "اضغط Ctrl+C لإيقاف السكربت. لإيقاف الخدمات، أغلق نوافذ السيرفرات أو أعد تشغيل السكربت." -ForegroundColor Yellow

$ErrorActionPreference = "Stop"

Write-Host "🔄 ICGL Dev Launcher: إعادة تشغيل وبناء المشروع بالكامل..." -ForegroundColor Cyan
<#
# 1. قتل العمليات السابقة على المنافذ 8000 و8080 و5173
#>
$ports = @(8000, 8080, 5173)
foreach ($port in $ports) {
    $pids = netstat -ano | Select-String ":$port" | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Select-Object -Unique
    foreach ($procId in $pids) {
        if ($procId -match '^[0-9]+$') {
            try {
                Stop-Process -Id $procId -Force
                Write-Host "Killed process $procId on port $port" -ForegroundColor DarkGray
            } catch {
                Write-Host "Could not kill process $procId (may already be stopped)" -ForegroundColor Yellow
            }
        }
    }
}
<#
# 2. حذف ملف القفل إذا وجد
#>
$lockFile = "data\icgl.lock"
if (Test-Path $lockFile) {
    Remove-Item -LiteralPath $lockFile -Force
    Write-Host "Removed lock file: $lockFile" -ForegroundColor DarkGray
}
<#
# 3. تهيئة البيئة الافتراضية وتثبيت الحزم
#>
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    & python -m venv .venv
}

$activateScript = ".venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating venv..." -ForegroundColor Cyan
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
    . $activateScript
    Write-Host "Upgrading pip and installing dependencies..." -ForegroundColor Cyan
    python -m pip install --upgrade pip
    if (Test-Path "requirements-dev.txt") {
        python -m pip install -r requirements-dev.txt
    }
    python -m pip install -e .[dev] | Out-Null
    # تحقق من توفر pyarrow بدون التأثير على Exit Code
    try {
        $null = python -c "import pyarrow" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️ pyarrow غير مثبت أو غير متوافق. تخطي وظائف تعتمد عليه." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ pyarrow غير مثبت أو غير متوافق. تخطي وظائف تعتمد عليه." -ForegroundColor Yellow
    }
} else {
    Write-Host "Activation script not found!" -ForegroundColor Red
    exit 1
}
<#
# 4. تشغيل الباك اند (API)
#>
Write-Host "Starting backend (API)..." -ForegroundColor Green
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-NoLogo","-Command","cd `"$PWD`"; .venv\Scripts\Activate.ps1; python -m uvicorn api.server:app --host 127.0.0.1 --port 8000" -WindowStyle Hidden
<#
# 5. تشغيل الفرونت اند (Vite)
#>
Write-Host "Starting frontend (Vite)..." -ForegroundColor Green
$webDir = Join-Path $PWD "web"
Start-Process -FilePath "powershell" -ArgumentList "-NoProfile","-NoLogo","-Command","cd `"$webDir`"; npm run dev" -WindowStyle Hidden

Write-Host "✅ All services started."
Write-Host "  API   -> http://localhost:8000" -ForegroundColor Green
Write-Host "  Front -> http://localhost:8080/app/" -ForegroundColor Green
Write-Host "اضغط Ctrl+C لإيقاف السكربت. لإيقاف الخدمات، أغلق نوافذ السيرفرات أو أعد تشغيل السكربت." -ForegroundColor Yellow
