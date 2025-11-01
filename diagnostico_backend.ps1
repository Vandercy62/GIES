# Script de diagnóstico para backend FastAPI/Uvicorn
# Salve como diagnostico_backend.ps1 e execute no PowerShell na raiz do projeto

Write-Host "Iniciando diagnóstico do backend FastAPI/Uvicorn..." -ForegroundColor Cyan

# 1. Verificar se o ambiente virtual existe
echo "[1/7] Verificando ambiente virtual..."
if (!(Test-Path ".venv/Scripts/activate")) {
    Write-Host "Ambiente virtual não encontrado!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "Ambiente virtual OK." -ForegroundColor Green
}


# 2. Ativar ambiente virtual e checar dependências críticas (com auto-fix para PyJWT)
. .venv/Scripts/activate
$deps = @(
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "pydantic",
    "passlib",
    "bcrypt",
    "PyJWT"
)
$missing = @()
foreach ($dep in $deps) {
    $result = python -c "import $dep" 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missing += $dep
    }
}

# Se PyJWT estiver ausente, reinstala automaticamente
if ($missing -contains "PyJWT") {
    Write-Host "PyJWT ausente. Tentando reinstalar automaticamente..." -ForegroundColor Yellow
    .venv\Scripts\pip.exe uninstall PyJWT -y
    .venv\Scripts\pip.exe install PyJWT
    $result = python -c "import jwt" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Falha ao importar PyJWT mesmo após reinstalação!" -ForegroundColor Red
        exit 2
    } else {
        Write-Host "PyJWT instalado e importado com sucesso." -ForegroundColor Green
        $missing = $missing | Where-Object { $_ -ne "PyJWT" }
    }
}

if ($missing.Count -gt 0) {
    Write-Host "Dependências ausentes: $($missing -join ", ")" -ForegroundColor Red
    exit 2
} else {
    Write-Host "Dependências críticas OK." -ForegroundColor Green
}

# 3. Checar existência do arquivo principal
if (!(Test-Path "backend/api/main.py")) {
    Write-Host "Arquivo backend/api/main.py não encontrado!" -ForegroundColor Red
    exit 3
}

# 4. Testar importação do app FastAPI
Write-Host "[4/7] Testando importação do app FastAPI..."
$importTest = python -c "from backend.api.main import app" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao importar app: $importTest" -ForegroundColor Red
    exit 4
} else {
    Write-Host "Importação do app OK." -ForegroundColor Green
}

# 5. Rodar Uvicorn em modo debug e capturar logs
Write-Host "[5/7] Iniciando backend em modo debug..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", ".venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002 --reload --log-level debug" -WindowStyle Normal
Write-Host "Backend iniciado em nova janela. Observe os logs para mensagens de erro detalhadas." -ForegroundColor Yellow

# 6. Testar health check após 5 segundos
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8002/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "Health check OK! Backend está rodando." -ForegroundColor Green
    } else {
        Write-Host "Health check falhou: $($response.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "Health check não respondeu. Verifique os logs da janela aberta." -ForegroundColor Red
}

Write-Host "Diagnóstico concluído. Se persistir erro, envie o log completo da janela aberta para análise detalhada." -ForegroundColor Cyan
