@echo off
REM ===================================================================
REM ERP PRIMOTEX - CONFIGURADOR DE REDE
REM Configuração automática para uso em rede
REM ===================================================================

title ERP PRIMOTEX - Configurador de Rede

echo.
echo ================================================================
echo                   ERP PRIMOTEX - CONFIGURADOR
echo                  Configuração Automática de Rede
echo ================================================================
echo.
echo 🌐 Configurando sistema para uso em rede...
echo 📱 Múltiplos dispositivos e terminais
echo 🔧 Configuração automática de IP e portas
echo.

cd /d "C:\GIES"

python configurador_rede.py

echo.
echo ================================================================
echo Sistema configurado! Use os outros ícones para iniciar.
echo ================================================================
pause