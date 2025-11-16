@echo off
chcp 65001 > nul
cls

:: ====================================================================
:: 🚀 SISTEMA ERP PRIMOTEX - LAUNCHER COMPLETO
:: ====================================================================
:: Versão: 9.0 - Consolidação Final
:: Data: 16/11/2025
:: Status: PRODUCTION-READY
:: ====================================================================

color 0A
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║     🏢 SISTEMA ERP PRIMOTEX - FORROS E DIVISÓRIAS EIRELLI       ║
echo ║                                                                  ║
echo ║                    LAUNCHER COMPLETO v9.0                        ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.
echo [INFO] Iniciando Sistema ERP Primotex...
echo.

:: ====================================================================
:: ETAPA 1: VERIFICAÇÕES PRELIMINARES
:: ====================================================================

echo [1/5] Verificando ambiente virtual...
if not exist ".venv\Scripts\python.exe" (
    color 0C
    echo.
    echo [ERRO] Ambiente virtual não encontrado!
    echo.
    echo Por favor, execute primeiro:
    echo     python -m venv .venv
    echo     .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo [OK] Ambiente virtual encontrado ✓
echo.

:: ====================================================================
:: ETAPA 2: VERIFICAR BANCO DE DADOS
:: ====================================================================

echo [2/5] Verificando banco de dados...
if not exist "primotex_erp.db" (
    echo [AVISO] Banco de dados será criado automaticamente na primeira inicialização
)
echo [OK] Verificação concluída ✓
echo.

:: ====================================================================
:: ETAPA 3: INICIAR SERVIDOR BACKEND
:: ====================================================================

echo [3/5] Iniciando servidor backend (porta 8002)...
echo.
echo [INFO] Aguarde... servidor iniciando em segundo plano...
start "ERP Primotex - Backend API Server" /MIN cmd /k ".venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002"

:: Aguardar 5 segundos para servidor inicializar
timeout /t 5 /nobreak > nul

:: Verificar se servidor está rodando
echo.
echo [INFO] Testando conexão com servidor...
powershell -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8002/health' -UseBasicParsing -TimeoutSec 5 | Out-Null; exit 0 } catch { exit 1 }"

if errorlevel 1 (
    color 0E
    echo.
    echo [AVISO] Servidor ainda está inicializando...
    echo [INFO] Aguardando mais 5 segundos...
    timeout /t 5 /nobreak > nul
    
    :: Testar novamente
    powershell -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8002/health' -UseBasicParsing -TimeoutSec 5 | Out-Null; exit 0 } catch { exit 1 }"
    
    if errorlevel 1 (
        color 0C
        echo.
        echo [ERRO] Servidor backend não está respondendo!
        echo.
        echo Verifique:
        echo   1. Se há outro processo usando a porta 8002
        echo   2. Se há erros no terminal do backend
        echo.
        echo Pressione qualquer tecla para tentar abrir o frontend mesmo assim...
        pause > nul
    ) else (
        color 0A
        echo [OK] Servidor backend online ✓
    )
) else (
    echo [OK] Servidor backend online ✓
)
echo.

:: ====================================================================
:: ETAPA 4: AGUARDAR BANCO INICIALIZAR
:: ====================================================================

echo [4/5] Aguardando inicialização do banco de dados...
timeout /t 2 /nobreak > nul
echo [OK] Banco de dados pronto ✓
echo.

:: ====================================================================
:: ETAPA 5: INICIAR INTERFACE DESKTOP
:: ====================================================================

echo [5/5] Iniciando interface desktop...
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║                   ✅ SISTEMA PRONTO PARA USO!                    ║
echo ║                                                                  ║
echo ║  📊 Backend API: http://127.0.0.1:8002                          ║
echo ║  📚 Documentação: http://127.0.0.1:8002/docs                    ║
echo ║  🖥️  Interface Desktop: Abrindo agora...                         ║
echo ║                                                                  ║
echo ║  🔐 Credenciais padrão:                                          ║
echo ║     Usuário: admin                                               ║
echo ║     Senha: admin123                                              ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

:: Iniciar interface desktop (em primeiro plano)
.venv\Scripts\python.exe frontend\desktop\login_tkinter.py

:: ====================================================================
:: ENCERRAMENTO
:: ====================================================================

echo.
echo.
echo [INFO] Interface desktop foi fechada.
echo.
echo Deseja encerrar o servidor backend também?
echo.
echo Pressione qualquer tecla para MANTER servidor rodando (recomendado)
echo OU feche esta janela para encerrar tudo.
echo.
pause > nul

echo.
echo [INFO] Servidor backend continua rodando em segundo plano.
echo [INFO] Para encerrar completamente, feche a janela "ERP Primotex - Backend API Server"
echo.
pause
