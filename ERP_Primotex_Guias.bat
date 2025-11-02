@echo off
REM ===================================================================
REM ERP PRIMOTEX - GUIA DE INSTALAÇÃO
REM Instruções completas para uso do sistema
REM ===================================================================

title ERP PRIMOTEX - Guia de Instalação

echo.
echo ================================================================
echo                   ERP PRIMOTEX - GUIA COMPLETO
echo                     Instruções de Instalação
echo ================================================================
echo.
echo 📚 Abrindo guias de instalação...
echo 📖 Instruções para todos os cenários de uso
echo.

cd /d "C:\GIES"

echo 🔍 Verificando documentação disponível...
if exist "guia_completo_implantacao.md" (
    echo ✅ Guia de Implantação encontrado
    echo 📄 Abrindo no navegador...
    start "" "guia_completo_implantacao.md"
) else (
    echo ❌ Guia não encontrado - criando...
    python -c "print('Guia de instalação será criado automaticamente')"
)

if exist "guia_uso_rede.md" (
    echo ✅ Guia de Rede encontrado
    echo 📄 Abrindo no navegador...
    start "" "guia_uso_rede.md"
)

if exist "guia_recepcao_online.md" (
    echo ✅ Guia de Recepção encontrado
    echo 📄 Abrindo no navegador...
    start "" "guia_recepcao_online.md"
)

echo.
echo ================================================================
echo ÍCONES DISPONÍVEIS NA ÁREA DE TRABALHO:
echo.
echo 🏠 ERP_Primotex_Completo.bat    - Sistema completo local
echo 📱 ERP_Primotex_Recepcao.bat    - Terminal de recepção
echo 🌐 ERP_Primotex_Rede.bat        - Sistema em rede
echo 🔧 ERP_Primotex_Configurador.bat - Configuração automática
echo 🖥️ ERP_Primotex_Servidor.bat    - Apenas servidor backend
echo ================================================================
echo.
pause