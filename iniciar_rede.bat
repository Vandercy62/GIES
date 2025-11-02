@echo off
echo ========================================
echo   INICIANDO ERP PRIMOTEX - REDE
echo ========================================
echo Servidor: http://192.168.0.249:8003
echo Acesso local: http://127.0.0.1:8003
echo Data/Hora: %date% %time%
echo.
echo IMPORTANTE: Configure o firewall para permitir porta 8003
echo.

cd /d C:\GIES
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8003

pause
