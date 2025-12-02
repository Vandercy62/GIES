@echo off
title ERP Primotex - Iniciador Web Completo
color 0A

echo ===============================================
echo    🔧 ERP PRIMOTEX - INICIADOR WEB COMPLETO
echo ===============================================
echo.

:: Verificar se está na pasta correta
if not exist "backend\api\main.py" (
    echo ❌ ERRO: Execute este arquivo na pasta raiz do projeto GIES
    echo Pasta atual: %CD%
    pause
    exit /b 1
)

:: Matar processos python existentes na porta 8002 e 8003
echo 🔄 Finalizando processos anteriores...
taskkill /F /FI "WINDOWTITLE eq *8002*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *8003*" >nul 2>&1
timeout /t 2 >nul

echo.
echo 📋 Iniciando serviços...
echo.

:: Iniciar backend em uma nova janela
echo 🚀 Iniciando Backend API (Porta 8002)...
start "Backend API - Porta 8002" /MIN cmd /c ".venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002 && pause"

:: Aguardar o backend inicializar
echo ⏳ Aguardando backend inicializar (5 segundos)...
timeout /t 5 >nul

:: Iniciar interface web em uma nova janela  
echo 🌐 Iniciando Interface Web (Porta 8003)...
start "Interface Web - Porta 8003" /MIN cmd /c ".venv\Scripts\python.exe web_interface_ultra_simples.py && pause"

:: Aguardar interface web inicializar
echo ⏳ Aguardando interface web inicializar (3 segundos)...
timeout /t 3 >nul

echo.
echo ===============================================
echo ✅ SISTEMA INICIADO COM SUCESSO!
echo ===============================================
echo.
echo 🌐 Interface Web: http://localhost:8003
echo 📚 API Docs: http://localhost:8002/docs
echo 💓 Health Check: http://localhost:8002/health
echo.
echo 🔑 Credenciais de Login:
echo    Usuário: admin
echo    Senha: admin123
echo.
echo 📌 Dica: Mantenha esta janela aberta para monitorar o sistema
echo.

:: Tentar abrir o navegador automaticamente
echo 🚀 Abrindo navegador automaticamente...
start http://localhost:8003

echo.
echo ⚠️ Para parar o sistema: Feche as janelas do Backend e Interface Web
echo ⚠️ Ou pressione Ctrl+C nas respectivas janelas
echo.
echo Pressione qualquer tecla para sair do iniciador...
pause >nul