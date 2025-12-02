@echo off
chcp 65001 >nul
title ERP Primotex - Sistema Completo

echo.
echo ================================================================================
echo   🚀 ERP PRIMOTEX - INICIANDO SISTEMA COMPLETO
echo ================================================================================
echo.
echo   Iniciando backend API e interface web...
echo   Por favor, aguarde...
echo.

cd /d "C:\GIES"

REM Verificar se o Python está disponível
.venv\Scripts\python.exe --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado no ambiente virtual
    echo    Certifique-se de que o ambiente virtual está configurado
    pause
    exit /b 1
)

REM Executar o launcher Python
.venv\Scripts\python.exe INICIAR_SISTEMA_COMPLETO.py

echo.
echo ================================================================================
echo   Sistema encerrado. Pressione qualquer tecla para fechar.
echo ================================================================================
pause >nul