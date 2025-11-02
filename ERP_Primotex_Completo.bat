@echo off
REM ===================================================================
REM ERP PRIMOTEX - SISTEMA COMPLETO LOCAL
REM Sistema ERP completo com todas as funcionalidades
REM ===================================================================

title ERP PRIMOTEX - Sistema Completo Local

echo.
echo ================================================================
echo                   ERP PRIMOTEX - SISTEMA COMPLETO
echo                     Servidor Local + Interface Desktop
echo ================================================================
echo.
echo 🔄 Iniciando servidor local...
echo 🖥️ Sistema completo com todas as funcionalidades
echo 📊 Dashboard, clientes, produtos, estoque, relatórios
echo 🔐 Acesso: admin / admin123
echo.

cd /d "C:\GIES"

echo ⚙️ Configurando servidor local...
python configurador_rede.py

echo.
echo ================================================================
echo Para iniciar o sistema depois, use os arquivos .bat criados
echo Ou execute: cd C:\GIES ^&^& python login_tkinter.py
echo ================================================================
pause