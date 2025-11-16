@echo off
REM Iniciar Backend ERP Primotex
REM Mantém terminal aberto
title Backend ERP Primotex - Porta 8002

echo ============================================================
echo      BACKEND ERP PRIMOTEX - INICIANDO
echo ============================================================
echo.
echo Servidor rodando em: http://127.0.0.1:8002
echo Documentacao API: http://127.0.0.1:8002/docs
echo.
echo Pressione Ctrl+C para parar o servidor
echo ============================================================
echo.

cd /d "C:\GIES"
.venv\Scripts\python.exe start_backend.py

pause
