@echo off
echo Testando login do ERP Primotex...
curl -X POST "http://127.0.0.1:8002/api/v1/auth/login" -H "Content-Type: application/json" -d "{\"username\": \"admin\", \"password\": \"admin123\"}"
echo.
echo Teste concluido.
pause