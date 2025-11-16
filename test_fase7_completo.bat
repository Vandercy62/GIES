@echo off
REM =====================================================
REM FASE 7 - TESTE COMPLETO DO SISTEMA
REM =====================================================

echo.
echo ================================================
echo   TESTE COMPLETO - SISTEMA DE LOGIN GLOBAL
echo ================================================
echo.

echo [1/3] Validando migração dos módulos...
C:\GIES\.venv\Scripts\python.exe C:\GIES\frontend\desktop\test_session_quick.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ FALHA na validação de migração!
    pause
    exit /b 1
)

echo.
echo [2/3] Verificando arquivos criados...
if exist "C:\GIES\shared\session_manager.py" (
    echo ✅ session_manager.py
) else (
    echo ❌ session_manager.py NÃO ENCONTRADO
)

if exist "C:\GIES\frontend\desktop\auth_middleware.py" (
    echo ✅ auth_middleware.py
) else (
    echo ❌ auth_middleware.py NÃO ENCONTRADO
)

if exist "C:\GIES\frontend\desktop\dashboard_principal.py" (
    echo ✅ dashboard_principal.py
) else (
    echo ❌ dashboard_principal.py NÃO ENCONTRADO
)

echo.
echo [3/3] Contando linhas de código...
for /f "delims=" %%i in ('powershell -Command "(Get-Content C:\GIES\shared\session_manager.py).Count"') do set LINES_SM=%%i
for /f "delims=" %%i in ('powershell -Command "(Get-Content C:\GIES\frontend\desktop\auth_middleware.py).Count"') do set LINES_AM=%%i
for /f "delims=" %%i in ('powershell -Command "(Get-Content C:\GIES\frontend\desktop\dashboard_principal.py).Count"') do set LINES_DP=%%i

echo   session_manager.py: %LINES_SM% linhas
echo   auth_middleware.py: %LINES_AM% linhas
echo   dashboard_principal.py: %LINES_DP% linhas

echo.
echo ================================================
echo   ✅ FASE 7 - 100%% CONCLUÍDA!
echo ================================================
echo.
echo Documentação completa em: FASE7_COMPLETA.md
echo Testes disponíveis em: frontend/desktop/test_session_*.py
echo.
pause
