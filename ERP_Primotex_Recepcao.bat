@echo off
REM ===================================================================
REM ERP PRIMOTEX - SISTEMA DE RECEPÇÃO HÍBRIDO
REM Interface gráfica moderna (online/offline automático)
REM ===================================================================

title ERP PRIMOTEX - Sistema de Recepcao Hibrido

echo.
echo ================================================================
echo                   ERP PRIMOTEX - RECEPCAO
echo                  Sistema Hibrido (Online/Offline)
echo ================================================================
echo.
echo 🔄 Iniciando sistema inteligente...
echo 📱 Interface grafica moderna
echo 🌐 Conecta automaticamente ao servidor se disponivel
echo 💾 Funciona offline com dados locais
echo.

cd /d "C:\GIES"

python sistema_recepcao_completo.py

echo.
echo ================================================================
echo Sistema encerrado. Pressione qualquer tecla para fechar...
echo ================================================================
pause