@echo off
REM ===================================================================
REM ERP PRIMOTEX - SISTEMA COMPLETO PARA REDE
REM Servidor + Cliente em rede
REM ===================================================================

title ERP PRIMOTEX - Sistema em Rede

echo.
echo ================================================================
echo                   ERP PRIMOTEX - SISTEMA REDE
echo                  Servidor + Interface para Rede
echo ================================================================
echo.
echo 🌐 Iniciando sistema completo para rede...
echo 🖥️ Servidor backend + Interface desktop
echo 📱 Disponível para múltiplos dispositivos
echo.

cd /d "C:\GIES"

echo ⚙️ Configurando para rede...
start "ERP Servidor" cmd /c "ERP_Primotex_Servidor.bat"

timeout /t 5 /nobreak > nul

echo 🖥️ Iniciando interface desktop...
.venv\Scripts\python.exe frontend\desktop\login_tkinter.py

pause