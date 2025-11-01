# 🚀 Guia de Deploy - PRIMOTEX ERP Mobile

> **Plataformas**: iOS & Android  
> **Framework**: React Native + Expo  
> **Status**: Pronto para produção

---

## 📋 **ÍNDICE**

1. [Pré-requisitos](#-pré-requisitos)
2. [Configuração Inicial](#-configuração-inicial)
3. [Build de Desenvolvimento](#-build-de-desenvolvimento)
4. [Build de Produção](#-build-de-produção)
5. [Deploy App Stores](#-deploy-app-stores)
6. [CI/CD Pipeline](#-cicd-pipeline)
7. [Monitoramento](#-monitoramento)
8. [Troubleshooting](#-troubleshooting)

---

## 📋 **PRÉ-REQUISITOS**

### **🔧 Ferramentas Necessárias**

| Ferramenta | Versão | Plataforma | Status |
|------------|--------|------------|--------|
| **Node.js** | 18+ | Todas | ✅ Obrigatório |
| **Expo CLI** | 6+ | Todas | ✅ Obrigatório |
| **EAS CLI** | Latest | Todas | ✅ Obrigatório |
| **Xcode** | 15+ | iOS | 🍎 iOS Only |
| **Android Studio** | 2023+ | Android | 🤖 Android Only |
| **JDK** | 17+ | Android | 🤖 Android Only |

### **📱 Requisitos de Sistema**

#### **iOS Development**
```bash
# Verificar Xcode
xcode-select --print-path

# Verificar simuladores disponíveis
xcrun simctl list devices

# Instalar Command Line Tools
xcode-select --install
```

#### **Android Development**
```bash
# Verificar Java JDK
java -version

# Verificar Android SDK
$ANDROID_HOME/tools/bin/sdkmanager --list

# Verificar emuladores
$ANDROID_HOME/emulator/emulator -list-avds
```

### **🔑 Credenciais Necessárias**

```bash
# Apple Developer Account
# - Team ID
# - Distribution Certificate  
# - Provisioning Profile

# Google Play Console
# - Service Account Key
# - Upload Key Certificate
# - App Bundle Key

# Expo Account
expo login
```

---

## ⚙️ **CONFIGURAÇÃO INICIAL**

### **📦 Instalação EAS CLI**

```bash
# Instalar EAS CLI globalmente
npm install -g @expo/eas-cli

# Verificar instalação
eas --version

# Login no Expo
eas login

# Configurar projeto
eas build:configure
```

### **🔧 Configuração app.json**

```json
{
  "expo": {
    "name": "PRIMOTEX ERP",
    "slug": "primotex-erp",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.primotex.erp",
      "buildNumber": "1",
      "infoPlist": {
        "NSCameraUsageDescription": "Este app precisa acessar a câmera para capturar fotos de serviços.",
        "NSLocationWhenInUseUsageDescription": "Este app precisa acessar sua localização para registrar endereços de serviços.",
        "NSLocationAlwaysAndWhenInUseUsageDescription": "Este app precisa acessar sua localização para funcionalidades de mapeamento."
      }
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#FFFFFF"
      },
      "package": "com.primotex.erp",
      "versionCode": 1,
      "permissions": [
        "android.permission.CAMERA",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.INTERNET",
        "android.permission.ACCESS_NETWORK_STATE"
      ]
    },
    "web": {
      "favicon": "./assets/favicon.png"
    },
    "extra": {
      "eas": {
        "projectId": "your-project-id"
      }
    },
    "owner": "primotex",
    "runtimeVersion": {
      "policy": "sdkVersion"
    },
    "updates": {
      "url": "https://u.expo.dev/your-project-id"
    }
  }
}
```

### **🏗️ Configuração eas.json**

```json
{
  "cli": {
    "version": ">= 5.9.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "resourceClass": "m1-medium"
      },
      "android": {
        "buildType": "apk"
      }
    },
    "preview": {
      "distribution": "internal",
      "ios": {
        "simulator": true,
        "resourceClass": "m1-medium"
      },
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "ios": {
        "resourceClass": "m1-medium"
      },
      "android": {
        "buildType": "aab"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@email.com",
        "ascAppId": "your-app-store-connect-id",
        "appleTeamId": "your-team-id"
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

## 🛠️ **BUILD DE DESENVOLVIMENTO**

### **📱 Build Local para Desenvolvimento**

```bash
# Instalar Expo Development Build
npx create-expo-app --template

# Instalar dependências
npm install

# Executar em desenvolvimento
npx expo start --dev-client

# Executar no iOS Simulator
npx expo run:ios

# Executar no Android Emulator
npx expo run:android

# Executar com clear cache
npx expo start --clear
```

### **☁️ Build na Nuvem (EAS)**

```bash
# Build de desenvolvimento iOS
eas build --platform ios --profile development

# Build de desenvolvimento Android
eas build --platform android --profile development

# Build simultâneo ambas plataformas
eas build --platform all --profile development

# Build com cache clear
eas build --platform all --profile development --clear-cache
```

### **🔧 Debugging em Desenvolvimento**

```bash
# Flipper integration (React Native debugging)
npx react-native doctor

# Verificar dependências
npx expo doctor

# Logs detalhados
npx expo start --verbose

# Reset Metro cache
npx expo start --reset-cache

# Debug com Reactotron
npm install --save-dev reactotron-react-native
```

---

## 🏭 **BUILD DE PRODUÇÃO**

### **📋 Pré-Deploy Checklist**

- [ ] **✅ Testes**: 91 testes passando (100%)
- [ ] **📊 Performance**: Lighthouse score > 90
- [ ] **🔒 Segurança**: Tokens e credenciais configurados
- [ ] **🖼️ Assets**: Ícones e splash screens otimizados
- [ ] **📝 Versioning**: Version e build number atualizados
- [ ] **🌐 API**: Endpoints de produção configurados
- [ ] **📜 Permissions**: Todas as permissões necessárias
- [ ] **🔐 Certificates**: Certificados iOS/Android válidos

### **🍎 Build iOS Produção**

```bash
# Build produção iOS
eas build --platform ios --profile production

# Build específico para App Store
eas build --platform ios --profile production --auto-submit

# Verificar certificados
eas credentials

# Update provisioning profile
eas credentials --platform ios
```

### **🤖 Build Android Produção**

```bash
# Build produção Android (AAB)
eas build --platform android --profile production

# Build APK para testes
eas build --platform android --profile preview

# Verificar keystore
eas credentials --platform android

# Build com upload automático
eas build --platform android --profile production --auto-submit
```

### **⚡ Build Otimizações**

```bash
# Build com otimizações máximas
eas build --platform all --profile production --clear-cache

# Build apenas incrementais
eas build --platform all --profile production --local

# Verificar tamanho do bundle
npx expo export --platform all

# Analisar bundle size
npx @expo/bundle-analyzer@latest dist/bundles/*
```

---

## 🏪 **DEPLOY APP STORES**

### **🍎 Apple App Store**

#### **1. Preparação**
```bash
# Gerar build de produção
eas build --platform ios --profile production

# Verificar App Store Connect
open https://appstoreconnect.apple.com

# Submeter para review
eas submit --platform ios --profile production
```

#### **2. App Store Connect Setup**

```json
{
  "appStoreInfo": {
    "bundleId": "com.primotex.erp",
    "version": "1.0.0",
    "buildNumber": "1",
    "category": "Business",
    "contentRating": "4+",
    "keywords": "ERP, Primotex, Business, Management",
    "description": "Sistema ERP completo para gestão de negócios Primotex",
    "privacyPolicyUrl": "https://primotex.com/privacy",
    "supportUrl": "https://primotex.com/support"
  }
}
```

#### **3. Submissão Automática**
```bash
# Submit com EAS
eas submit --platform ios

# Submit com metadata customizada
eas submit --platform ios --apple-id your-apple-id --asc-app-id your-app-id
```

### **🤖 Google Play Store**

#### **1. Preparação**
```bash
# Gerar AAB de produção
eas build --platform android --profile production

# Submit para Play Console
eas submit --platform android --profile production
```

#### **2. Play Console Setup**

```json
{
  "playStoreInfo": {
    "packageName": "com.primotex.erp",
    "versionCode": 1,
    "versionName": "1.0.0",
    "category": "Business",
    "contentRating": "Everyone",
    "shortDescription": "Sistema ERP Primotex - Gestão Completa",
    "fullDescription": "Sistema ERP completo para gestão empresarial da Primotex...",
    "privacyPolicyUrl": "https://primotex.com/privacy",
    "websiteUrl": "https://primotex.com"
  }
}
```

#### **3. Configuração Track Release**
```bash
# Release para internal testing
eas submit --platform android --track internal

# Release para alpha
eas submit --platform android --track alpha

# Release para beta
eas submit --platform android --track beta

# Release para produção
eas submit --platform android --track production
```

### **📈 Release Management**

```bash
# Verificar status de submissão
eas submit:list

# Cancelar submissão
eas submit:cancel --submission-id <id>

# Baixar builds
eas build:list
eas build:view <build-id>

# Update over-the-air (OTA)
eas update --branch production --message "Critical bug fix"
```

---

## 🔄 **CI/CD PIPELINE**

### **⚙️ GitHub Actions Workflow**

```yaml
# .github/workflows/build.yml
name: Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Run linting
        run: npm run lint
      
      - name: Check TypeScript
        run: npm run type-check

  build-preview:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Setup Expo
        uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build preview
        run: eas build --platform all --profile preview --non-interactive

  build-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Setup Expo
        uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build production
        run: eas build --platform all --profile production --non-interactive
      
      - name: Submit to stores
        run: eas submit --platform all --profile production --non-interactive
        env:
          EXPO_APPLE_PASSWORD: ${{ secrets.EXPO_APPLE_PASSWORD }}
          EXPO_ANDROID_KEYSTORE_PASSWORD: ${{ secrets.EXPO_ANDROID_KEYSTORE_PASSWORD }}
```

### **🔐 Secrets Configuration**

```bash
# GitHub Secrets necessários
EXPO_TOKEN=your-expo-access-token
EXPO_APPLE_ID=your-apple-id
EXPO_APPLE_PASSWORD=your-app-specific-password
EXPO_APPLE_TEAM_ID=your-team-id
EXPO_ANDROID_KEYSTORE_PASSWORD=your-keystore-password
EXPO_ANDROID_SERVICE_ACCOUNT_KEY=your-service-account-json

# Configurar secrets
gh secret set EXPO_TOKEN --body "your-token"
gh secret set EXPO_APPLE_PASSWORD --body "your-password"
```

### **📊 Pipeline Monitoring**

```yaml
# .github/workflows/monitoring.yml
name: App Monitoring

on:
  schedule:
    - cron: '0 */6 * * *' # A cada 6 horas

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check App Store Status
        run: |
          curl -s "https://itunes.apple.com/lookup?bundleId=com.primotex.erp"
      
      - name: Check Play Store Status
        run: |
          curl -s "https://play.google.com/store/apps/details?id=com.primotex.erp"
      
      - name: Check Update Server
        run: |
          curl -s "https://u.expo.dev/your-project-id"
      
      - name: Notify if issues
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 📊 **MONITORAMENTO**

### **📈 Analytics & Crash Reporting**

```javascript
// services/analyticsService.js
import * as Analytics from 'expo-analytics-amplitude';
import * as Sentry from '@sentry/react-native';

class AnalyticsService {
  initialize() {
    // Amplitude Analytics
    Analytics.initialize('your-amplitude-api-key');
    
    // Sentry Crash Reporting
    Sentry.init({
      dsn: 'your-sentry-dsn',
      environment: __DEV__ ? 'development' : 'production',
    });
  }

  trackEvent(eventName, properties = {}) {
    Analytics.logEvent(eventName, properties);
  }

  trackScreen(screenName) {
    Analytics.logEvent('Screen View', { screen: screenName });
  }

  trackError(error, context = {}) {
    Sentry.captureException(error, { extra: context });
  }

  setUser(userId, userProperties) {
    Analytics.setUserId(userId);
    Analytics.setUserProperties(userProperties);
    
    Sentry.setUser({ id: userId, ...userProperties });
  }
}

export default new AnalyticsService();
```

### **🔔 Error Monitoring Setup**

```bash
# Instalar Sentry
npm install @sentry/react-native

# Configurar Sentry
npx @sentry/wizard -p reactnative -i expo

# Instalar Amplitude
expo install expo-analytics-amplitude

# Configurar Flipper (development)
npm install --save-dev react-native-flipper
```

### **📱 Performance Monitoring**

```javascript
// hooks/usePerformanceMonitoring.js
import { useEffect } from 'react';
import { Performance } from 'react-native-performance';

export const usePerformanceMonitoring = (screenName) => {
  useEffect(() => {
    const startTime = Performance.now();
    
    return () => {
      const loadTime = Performance.now() - startTime;
      
      analyticsService.trackEvent('Screen Performance', {
        screen: screenName,
        loadTime: Math.round(loadTime),
      });
    };
  }, [screenName]);
};
```

### **📊 Real User Monitoring (RUM)**

```javascript
// services/rumService.js
class RUMService {
  constructor() {
    this.metrics = {
      screenLoadTimes: {},
      apiResponseTimes: {},
      crashCount: 0,
      errorCount: 0,
    };
  }

  measureScreenLoad(screenName, callback) {
    const startTime = Performance.now();
    
    return (...args) => {
      const result = callback(...args);
      const loadTime = Performance.now() - startTime;
      
      this.metrics.screenLoadTimes[screenName] = loadTime;
      this.reportMetric('screen_load_time', loadTime, { screen: screenName });
      
      return result;
    };
  }

  measureApiCall(endpoint, promise) {
    const startTime = Performance.now();
    
    return promise.finally(() => {
      const responseTime = Performance.now() - startTime;
      this.metrics.apiResponseTimes[endpoint] = responseTime;
      this.reportMetric('api_response_time', responseTime, { endpoint });
    });
  }

  reportMetric(name, value, tags = {}) {
    analyticsService.trackEvent('Performance Metric', {
      metric: name,
      value,
      ...tags,
    });
  }
}

export default new RUMService();
```

---

## 🔧 **TROUBLESHOOTING**

### **❌ Problemas Comuns de Build**

#### **iOS Build Issues**

```bash
# Erro: Certificate/Provisioning Profile
eas credentials --platform ios
eas credentials:configure --platform ios

# Erro: Xcode version
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer

# Erro: Simulator não encontrado
xcrun simctl list devices

# Cache issues
eas build --platform ios --clear-cache
```

#### **Android Build Issues**

```bash
# Erro: Java version
java -version
export JAVA_HOME=/path/to/java

# Erro: Android SDK
export ANDROID_HOME=/path/to/android-sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools

# Erro: Keystore
eas credentials --platform android

# Gradle issues
cd android && ./gradlew clean
```

#### **Expo/EAS Issues**

```bash
# Login issues
eas logout
eas login

# Project ID issues
eas init

# Build stuck
eas build:cancel

# Quota exceeded
eas account:view
```

### **🔍 Debug de Deploy**

```bash
# Verificar configuração
eas config

# Verificar credenciais
eas credentials

# Verificar status do projeto
eas project:info

# Logs detalhados
eas build --platform all --profile production --verbose

# Verificar submissão
eas submit:list
```

### **📊 Monitoramento de Problemas**

```javascript
// services/deploymentHealthService.js
class DeploymentHealthService {
  async checkAppStoreStatus() {
    try {
      const response = await fetch(
        'https://itunes.apple.com/lookup?bundleId=com.primotex.erp'
      );
      const data = await response.json();
      return data.resultCount > 0;
    } catch (error) {
      console.error('App Store check failed:', error);
      return false;
    }
  }

  async checkPlayStoreStatus() {
    try {
      const response = await fetch(
        'https://play.google.com/store/apps/details?id=com.primotex.erp',
        { method: 'HEAD' }
      );
      return response.ok;
    } catch (error) {
      console.error('Play Store check failed:', error);
      return false;
    }
  }

  async checkUpdateServerStatus() {
    try {
      const response = await fetch('https://u.expo.dev/your-project-id');
      return response.ok;
    } catch (error) {
      console.error('Update server check failed:', error);
      return false;
    }
  }
}
```

---

## 📞 **SUPORTE & RECURSOS**

### **📚 Documentação Oficial**
- [Expo Documentation](https://docs.expo.dev/)
- [EAS Build](https://docs.expo.dev/build/introduction/)
- [EAS Submit](https://docs.expo.dev/submit/introduction/)
- [App Store Connect](https://developer.apple.com/app-store-connect/)
- [Google Play Console](https://play.google.com/console/)

### **🛠️ Ferramentas Úteis**
- [App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi)
- [Google Play Developer API](https://developers.google.com/android-publisher)
- [Expo Application Services](https://expo.dev/eas)

### **🆘 Suporte Técnico**
- **Expo Discord**: [expo.dev/discord](https://expo.dev/discord)
- **GitHub Issues**: Para problemas específicos do projeto
- **Stack Overflow**: Tag `expo` ou `react-native`

---

**🚀 Última Atualização**: Novembro 2025  
**📱 Plataformas**: iOS & Android  
**✅ Status**: Pronto para produção