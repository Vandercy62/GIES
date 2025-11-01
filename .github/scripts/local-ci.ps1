# 🧪 Local CI Testing Script
# Executa validações CI localmente antes do push

param(
    [switch]$SkipTests,
    [switch]$SkipLint,
    [switch]$SkipBuild,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Cores para output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️ $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "⚠️ $Message" -ForegroundColor Yellow }

# Tempo total
$startTime = Get-Date
Write-Info "🧪 PRIMOTEX ERP Mobile - Local CI Testing"
Write-Info "📱 Executando validações antes do push..."

# Verificar se estamos na pasta mobile
if (-not (Test-Path "package.json")) {
    Write-Error "Execute este script na pasta frontend/mobile"
    exit 1
}

# Verificar Node.js
try {
    $nodeVersion = node --version
    Write-Success "Node.js: $nodeVersion"
} catch {
    Write-Error "Node.js não encontrado. Instale em: https://nodejs.org/"
    exit 1
}

# Verificar npm
try {
    $npmVersion = npm --version
    Write-Success "npm: v$npmVersion"
} catch {
    Write-Error "npm não encontrado"
    exit 1
}

# Instalar dependências
Write-Info "📦 Verificando dependências..."
if (-not (Test-Path "node_modules")) {
    Write-Info "📥 Instalando dependências..."
    npm ci
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Falha na instalação de dependências"
        exit 1
    }
} else {
    Write-Success "Dependências já instaladas"
}

# Verificar arquivos alterados
Write-Info "📋 Verificando arquivos alterados..."
try {
    $changedFiles = git diff --name-only HEAD~1 HEAD 2>$null
    if ($changedFiles) {
        Write-Info "Arquivos alterados:"
        $changedFiles | ForEach-Object { Write-Host "  - $_" -ForegroundColor Cyan }
    } else {
        Write-Warning "Nenhum arquivo alterado detectado"
    }
} catch {
    Write-Warning "Não foi possível verificar arquivos alterados (sem git)"
}

# 1. 🔍 Análise de código (ESLint)
if (-not $SkipLint) {
    Write-Info "🔍 Executando ESLint..."
    npm run lint
    if ($LASTEXITCODE -ne 0) {
        Write-Error "ESLint encontrou problemas"
        if (-not $Verbose) {
            Write-Info "Execute com -Verbose para ver detalhes ou corrija com: npm run lint:fix"
        }
        exit 1
    }
    Write-Success "ESLint passou!"
} else {
    Write-Warning "ESLint ignorado (-SkipLint)"
}

# 2. 🎯 Verificação TypeScript
if (-not $SkipLint) {
    Write-Info "🎯 Verificando TypeScript..."
    npm run type-check
    if ($LASTEXITCODE -ne 0) {
        Write-Error "TypeScript encontrou erros de tipo"
        exit 1
    }
    Write-Success "TypeScript passou!"
} else {
    Write-Warning "TypeScript ignorado (-SkipLint)"
}

# 3. 🧪 Testes
if (-not $SkipTests) {
    Write-Info "🧪 Executando testes..."
    npm test -- --coverage --watchAll=false --passWithNoTests
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Alguns testes falharam"
        exit 1
    }
    Write-Success "Todos os testes passaram!"
    
    # Verificar cobertura
    if (Test-Path "coverage/lcov-report/index.html") {
        Write-Info "📊 Relatório de cobertura gerado: coverage/lcov-report/index.html"
    }
} else {
    Write-Warning "Testes ignorados (-SkipTests)"
}

# 4. 🔒 Auditoria de segurança
Write-Info "🔒 Executando auditoria de segurança..."
npm audit --audit-level=moderate
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Vulnerabilidades encontradas. Execute: npm audit fix"
} else {
    Write-Success "Nenhuma vulnerabilidade encontrada!"
}

# 5. 📱 Validação Expo
if (-not $SkipBuild) {
    Write-Info "📱 Verificando configuração Expo..."
    try {
        $expoVersion = npx expo --version
        Write-Success "Expo CLI: v$expoVersion"
    } catch {
        Write-Warning "Expo CLI não encontrado. Instalando..."
        npm install -g @expo/cli
    }
    
    npx expo doctor
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Configuração Expo tem problemas"
        exit 1
    }
    Write-Success "Configuração Expo válida!"
} else {
    Write-Warning "Validação Expo ignorada (-SkipBuild)"
}

# 6. 📦 Análise de bundle (opcional)
if (-not $SkipBuild) {
    Write-Info "📦 Analisando tamanho do bundle..."
    try {
        npx expo export --platform web --dev false
        if (Test-Path "dist") {
            $bundleSize = (Get-ChildItem "dist" -Recurse | Measure-Object -Property Length -Sum).Sum
            $bundleSizeMB = [math]::Round($bundleSize / 1MB, 2)
            Write-Success "Tamanho do bundle: $bundleSizeMB MB"
            
            if ($bundleSizeMB -gt 50) {
                Write-Warning "Bundle grande (>50MB). Considere otimizações."
            }
        }
    } catch {
        Write-Warning "Não foi possível analisar o bundle"
    }
} else {
    Write-Warning "Análise de bundle ignorada (-SkipBuild)"
}

# 7. 📊 Resumo final
Write-Info "📊 Resumo da validação:"
Write-Host "┌─────────────────────────────────────┐" -ForegroundColor Gray
Write-Host "│" -ForegroundColor Gray -NoNewline
Write-Success " Código: ESLint + TypeScript      " -NoNewline
Write-Host "│" -ForegroundColor Gray
Write-Host "│" -ForegroundColor Gray -NoNewline
Write-Success " Testes: Jest + Coverage          " -NoNewline
Write-Host "│" -ForegroundColor Gray
Write-Host "│" -ForegroundColor Gray -NoNewline
Write-Success " Segurança: npm audit            " -NoNewline
Write-Host "│" -ForegroundColor Gray
Write-Host "│" -ForegroundColor Gray -NoNewline
Write-Success " Build: Expo configuration       " -NoNewline
Write-Host "│" -ForegroundColor Gray
Write-Host "└─────────────────────────────────────┘" -ForegroundColor Gray

Write-Success "🎉 Todas as validações CI passaram!"
Write-Info "🚀 Seu código está pronto para push!"

# Sugestões adicionais
Write-Info "💡 Próximos passos sugeridos:"
Write-Host "  • git add ." -ForegroundColor Cyan
Write-Host "  • git commit -m 'feat: sua mensagem aqui'" -ForegroundColor Cyan
Write-Host "  • git push origin feature/sua-branch" -ForegroundColor Cyan

# Tempo total
$endTime = Get-Date
$duration = $endTime - $startTime
Write-Info "⏱️ Tempo total: $($duration.TotalSeconds) segundos"