#!/bin/bash
# 📋 GitHub Actions Secrets Configuration
# Execute este script para configurar todos os secrets necessários

# Verificar se GitHub CLI está instalado
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI não encontrado. Instale em: https://cli.github.com/"
    exit 1
fi

# Verificar se está logado
if ! gh auth status &> /dev/null; then
    echo "🔐 Fazendo login no GitHub..."
    gh auth login
fi

echo "🔧 Configurando secrets para PRIMOTEX ERP Mobile CI/CD..."

# Função para configurar secret
set_secret() {
    local secret_name=$1
    local description=$2
    
    echo "📝 Configurando $secret_name..."
    echo "💡 $description"
    read -s -p "Digite o valor para $secret_name: " secret_value
    echo
    
    if [[ -n "$secret_value" ]]; then
        gh secret set "$secret_name" --body "$secret_value"
        echo "✅ $secret_name configurado com sucesso!"
    else
        echo "⚠️ $secret_name ignorado (valor vazio)"
    fi
    echo
}

# Secrets obrigatórios
echo "🎯 === SECRETS OBRIGATÓRIOS ==="

set_secret "EXPO_TOKEN" "Token de acesso do Expo (obtido em: https://expo.dev/accounts/settings)"

set_secret "EXPO_APPLE_ID" "Apple ID usado para desenvolvimento iOS (ex: dev@primotex.com)"

set_secret "EXPO_APPLE_PASSWORD" "App-specific password do Apple ID (gerado em: https://appleid.apple.com/)"

# Secrets opcionais
echo "📋 === SECRETS OPCIONAIS ==="

set_secret "EXPO_ANDROID_KEYSTORE_PASSWORD" "Senha do keystore Android (deixe vazio para gerar automaticamente)"

set_secret "CODECOV_TOKEN" "Token do Codecov para relatórios de cobertura (opcional)"

set_secret "SLACK_WEBHOOK" "Webhook do Slack para notificações (opcional)"

# Verificar secrets configurados
echo "📊 Verificando secrets configurados..."
gh secret list

echo "✅ Configuração de secrets concluída!"
echo ""
echo "🚀 Próximos passos:"
echo "1. Configurar certificados iOS no Expo: eas credentials"
echo "2. Configurar keystore Android: eas credentials --platform android"
echo "3. Testar pipeline: git push origin main"
echo ""
echo "📚 Documentação completa: .github/workflows/README.md"