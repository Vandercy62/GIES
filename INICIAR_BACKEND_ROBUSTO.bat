@echo off
chcp 65001 >nul
cls

echo ╔════════════════════════════════════════════════════════════════════╗
echo ║         SISTEMA ERP PRIMOTEX - BACKEND ROBUSTO v2.0               ║
echo ║         Primotex - Forros e Divisórias Eireli                      ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.

REM Navegar para pasta do projeto
cd /d %~dp0

echo [1/3] Verificando ambiente virtual...
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Ambiente virtual não encontrado em .venv
    echo.
    echo Soluções:
    echo   1. Crie o ambiente: python -m venv .venv
    echo   2. Instale dependências: .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo ✅ Ambiente virtual encontrado

echo.
echo [2/3] Verificando script de inicialização...
if exist "start_backend_robust.py" (
    echo ✅ Script robusto encontrado - Usando start_backend_robust.py
    set SCRIPT=start_backend_robust.py
) else if exist "start_backend.py" (
    echo ⚠️  Usando start_backend.py padrão
    set SCRIPT=start_backend.py
) else (
    echo ❌ Nenhum script de inicialização encontrado
    pause
    exit /b 1
)

echo.
echo [3/3] Iniciando backend...
echo.
echo ═══════════════════════════════════════════════════════════════════
echo 📍 Script: %SCRIPT%
echo 📍 Python: .venv\Scripts\python.exe
echo 📍 Porta: 8002
echo 📍 Modo: Robusto (com retry automático)
echo ═══════════════════════════════════════════════════════════════════
echo.
echo Pressione Ctrl+C para encerrar
echo.

REM Iniciar backend com retry automático
.venv\Scripts\python.exe %SCRIPT%

REM Capturar código de saída
if errorlevel 1 (
    echo.
    echo ═══════════════════════════════════════════════════════════════════
    echo ❌ BACKEND ENCERROU COM ERRO
    echo ═══════════════════════════════════════════════════════════════════
    echo.
    echo Diagnóstico:
    echo   1. Verifique os logs acima
    echo   2. Confira se a porta 8002 está disponível
    echo   3. Certifique-se que todas dependências estão instaladas
    echo.
    echo Comandos úteis:
    echo   • Reinstalar dependências: .venv\Scripts\pip install -r requirements.txt
    echo   • Ver processos na porta: netstat -ano ^| findstr :8002
    echo   • Testar conexão: curl http://127.0.0.1:8002/health
    echo.
) else (
    echo.
    echo ═══════════════════════════════════════════════════════════════════
    echo ✅ BACKEND ENCERRADO NORMALMENTE
    echo ═══════════════════════════════════════════════════════════════════
)

echo.
pause
