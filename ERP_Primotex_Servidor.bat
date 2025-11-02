@echo off
REM ===================================================================
REM ERP PRIMOTEX - SERVIDOR BACKEND
REM Apenas o servidor API para uso em rede
REM ===================================================================

title ERP PRIMOTEX - Servidor Backend

echo.
echo ================================================================
echo                   ERP PRIMOTEX - SERVIDOR API
echo                      Backend para uso em rede
echo ================================================================
echo.
echo 🔄 Iniciando servidor backend...
echo 🌐 Disponível para múltiplos clientes
echo 📡 API REST em http://localhost:8002
echo.

cd /d "C:\GIES"

echo ⚙️ Verificando ambiente...
python -c "import sys; print(f'Python: {sys.version}')"

echo.
echo 🚀 Iniciando servidor FastAPI...
.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8002

pause