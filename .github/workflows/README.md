# 📋 CI/CD Configuration - PRIMOTEX ERP Mobile

Este diretório contém os workflows do GitHub Actions para CI/CD do aplicativo mobile.

## 🔄 **Workflows Disponíveis**

### 1. **🧪 Mobile CI** (`mobile-ci.yml`)
**Trigger**: Push/PR para `main` e `develop`
- ✅ Análise de código (ESLint + TypeScript)
- ✅ Testes unitários com cobertura
- ✅ Segurança (CodeQL + npm audit)
- ✅ Validação de build
- ✅ Performance testing

### 2. **🚀 Mobile CD** (`mobile-cd.yml`)
**Trigger**: Push para `main`, tags `mobile-v*`, manual
- 📱 Build iOS (EAS)
- 🤖 Build Android (EAS)
- 🔄 OTA Updates (desenvolvimento)
- 🏪 Deploy automático para stores (produção)

### 3. **📦 Dependencies Update** (`dependencies-update.yml`)
**Trigger**: Cronometrado (segundas às 9h UTC), manual
- 🔍 Verifica atualizações de dependências
- 🔄 Cria PRs automáticos com updates
- 🔒 Auditoria de segurança semanal
- 📊 Relatório semanal de dependências

### 4. **🏷️ Release** (`release.yml`)
**Trigger**: Manual (workflow_dispatch)
- 📝 Gera changelog automático
- 🔄 Atualiza versões (package.json + app.json)
- 🏷️ Cria tags e releases GitHub
- 🚀 Dispara deployment automático

---

## ⚙️ **Configuração de Secrets**

### **🔑 Secrets Necessários**

```bash
# Expo & EAS
EXPO_TOKEN=your-expo-access-token

# Apple Developer
EXPO_APPLE_ID=your-apple-id@email.com
EXPO_APPLE_PASSWORD=your-app-specific-password

# Android
EXPO_ANDROID_KEYSTORE_PASSWORD=your-keystore-password

# Codecov (opcional)
CODECOV_TOKEN=your-codecov-token
```

### **🛠️ Como Configurar Secrets**

```bash
# Via GitHub CLI
gh secret set EXPO_TOKEN --body "your-token"
gh secret set EXPO_APPLE_ID --body "your-apple-id"

# Via GitHub Web UI
Settings → Secrets and variables → Actions → New repository secret
```

---

## 🎯 **Estratégia de Branches**

### **📊 Branch Flow**

```
main (produção)
├── develop (desenvolvimento)
├── feature/* (features)
├── hotfix/* (correções urgentes)
└── release/* (preparação releases)
```

### **🔄 Triggers por Branch**

| Branch | CI | CD | Deploy |
|--------|----|----|--------|
| `main` | ✅ | ✅ | Preview + Stores |
| `develop` | ✅ | ✅ | Preview apenas |
| `feature/*` | ✅ | ❌ | Nenhum |
| `hotfix/*` | ✅ | ❌ | Nenhum |

---

## 📱 **Estratégia de Deploy**

### **🎯 Ambientes**

1. **🧪 Development**
   - Build: EAS preview
   - OTA: Branch `develop`
   - Distribuição: Internal

2. **🎬 Preview**
   - Build: EAS preview
   - OTA: Branch `preview`
   - Distribuição: Internal + TestFlight/Internal Track

3. **🏭 Production**
   - Build: EAS production
   - OTA: Branch `production`
   - Distribuição: App Store + Google Play

### **📋 Deploy Workflow**

```bash
# 1. Desenvolvimento contínuo
feature → develop → CI ✅ → CD ✅ → OTA Update

# 2. Release para preview
develop → main → CI ✅ → CD ✅ → Preview Build

# 3. Release para produção
main + tag → CI ✅ → CD ✅ → Production Build → Stores
```

---

## 🔧 **Configuração EAS**

### **📄 eas.json**

```json
{
  "cli": { "version": ">= 5.9.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": true }
    },
    "production": {
      "ios": { "resourceClass": "m1-medium" },
      "android": { "buildType": "aab" }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "$EXPO_APPLE_ID",
        "ascAppId": "your-app-store-connect-id"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

---

## 📊 **Monitoramento & Métricas**

### **📈 Métricas Coletadas**

- ✅ Taxa de sucesso dos builds
- ⏱️ Tempo de build (iOS/Android)
- 📊 Cobertura de testes
- 🔒 Vulnerabilidades de segurança
- 📦 Tamanho do bundle
- ⚡ Performance dos testes

### **🔔 Notificações**

- 📧 Email em falhas de produção
- 💬 Comentários automáticos em PRs
- 📊 Relatórios semanais de dependências
- 🎉 Notificações de releases

---

## 🛠️ **Comandos Úteis**

### **🧪 Executar CI Localmente**

```bash
# Simular CI completo
npm run ci:full

# Apenas testes
npm test -- --coverage --watchAll=false

# Validação de build
npx expo doctor
```

### **🚀 Deploy Manual**

```bash
# Preview build
eas build --platform all --profile preview

# Production build
eas build --platform all --profile production

# OTA update
eas update --branch production --message "Critical fix"
```

### **🏷️ Criar Release**

```bash
# Via GitHub CLI
gh workflow run release.yml -f version=1.2.0 -f release_type=minor

# Via GitHub Web UI
Actions → Release → Run workflow
```

---

## 🔍 **Troubleshooting**

### **❌ Problemas Comuns**

#### **Build Falha**
```bash
# Verificar configuração EAS
eas config

# Limpar cache
eas build --clear-cache

# Verificar credentials
eas credentials
```

#### **Testes Falhando**
```bash
# Executar localmente
npm test -- --verbose

# Limpar cache Jest
npm test -- --clearCache

# Verificar dependências
npm audit
```

#### **Deploy Falha**
```bash
# Verificar tokens
echo $EXPO_TOKEN

# Verificar configuração
cat eas.json

# Logs detalhados
eas build --platform ios --profile production --verbose
```

### **📞 Suporte**

- 🐛 **Issues**: [GitHub Issues](https://github.com/Vandercy62/GIES/issues)
- 📧 **Email**: suporte@primotex.com
- 📱 **Expo Discord**: [expo.dev/discord](https://expo.dev/discord)

---

**🔄 Última Atualização**: Novembro 2025  
**🤖 Pipeline**: GitHub Actions + EAS  
**📱 Plataformas**: iOS & Android