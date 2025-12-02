@echo off
REM =====================================================
REM ERP PRIMOTEX - LAUNCHER DESKTOP
REM =====================================================
REM
REM Inicia o sistema ERP Primotex completo
REM
REM Uso: Clique duplo neste arquivo
REM =====================================================

REM Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Solicitando permissoes de administrador...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo.
echo ========================================
echo  ERP PRIMOTEX - SISTEMA DESKTOP
echo ========================================
echo.

REM Verificar se .venv existe
if not exist ".venv\Scripts\python.exe" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo.
    echo Execute primeiro: python -m venv .venv
    echo.
    pause
    exit /b 1
)

REM Iniciar sistema
REM =====================================================
REM MIGRADO: 17/11/2025 - Backend Robusto v2.0
REM Auto-inicia backend se não estiver rodando
REM =====================================================

echo Verificando backend...
echo.

REM Tentar conectar na porta 8002
curl http://127.0.0.1:8002/health 2>nul >nul

if errorlevel 1 (
    echo Backend nao detectado - iniciando Backend Robusto v2.0...
    echo.
    
    REM Iniciar backend robusto em janela separada
    start "Backend ERP Primotex - ROBUSTO v2.0" INICIAR_BACKEND_ROBUSTO.bat
    
    echo Aguardando 5 segundos para backend inicializar...
    timeout /t 5 /nobreak >nul
    echo.
) else (
    echo Backend ja esta rodando!
    echo.
)

echo Iniciando sistema desktop...
echo.

.venv\Scripts\python.exe INICIAR_SISTEMA.py

echo.
echo Sistema encerrado.
echo.
pause
