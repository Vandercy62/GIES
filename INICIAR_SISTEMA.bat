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
echo Iniciando sistema...
echo.

.venv\Scripts\python.exe INICIAR_SISTEMA.py

echo.
echo Sistema encerrado.
echo.
pause
