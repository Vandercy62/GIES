/**
 * Build Script para Produção
 * Automatização de build, testes e deploy
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class ProductionBuilder {
  constructor() {
    this.projectRoot = process.cwd();
    this.buildConfig = {
      android: {
        profile: 'production',
        type: 'app-bundle'
      },
      ios: {
        profile: 'production',
        type: 'archive'
      }
    };
  }

  // Pre-build checks
  async preBuildChecks() {
    console.log('🔍 Executando verificações pré-build...');
    
    // Verificar dependências críticas
    const requiredDeps = [
      'react-native',
      'expo',
      '@react-navigation/native',
      '@reduxjs/toolkit',
      'react-redux'
    ];
    
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep]);
    
    if (missingDeps.length > 0) {
      throw new Error(`❌ Dependências faltando: ${missingDeps.join(', ')}`);
    }
    
    console.log('✅ Dependências verificadas');
    
    // Verificar configuração do app.json
    const appJson = JSON.parse(fs.readFileSync('app.json', 'utf8'));
    if (!appJson.expo.ios.bundleIdentifier || !appJson.expo.android.package) {
      throw new Error('❌ Bundle identifiers não configurados');
    }
    
    console.log('✅ Configuração do app verificada');
    
    // Verificar EAS configuração
    if (!fs.existsSync('eas.json')) {
      throw new Error('❌ Arquivo eas.json não encontrado');
    }
    
    console.log('✅ Configuração EAS verificada');
  }

  // Executar testes
  async runTests() {
    console.log('🧪 Executando testes...');
    
    try {
      execSync('npm test -- --watchAll=false', { stdio: 'inherit' });
      console.log('✅ Todos os testes passaram');
    } catch (error) {
      throw new Error('❌ Testes falharam');
    }
  }

  // Lint e formatação
  async runLinting() {
    console.log('📝 Executando lint...');
    
    try {
      execSync('npm run lint', { stdio: 'inherit' });
      console.log('✅ Lint passou sem erros');
    } catch (error) {
      console.warn('⚠️ Lint encontrou problemas, tentando correção automática...');
      try {
        execSync('npm run lint:fix', { stdio: 'inherit' });
        console.log('✅ Problemas de lint corrigidos automaticamente');
      } catch (fixError) {
        throw new Error('❌ Não foi possível corrigir problemas de lint');
      }
    }
  }

  // Type checking
  async runTypeCheck() {
    console.log('🔍 Verificando tipos...');
    
    try {
      execSync('npm run type-check', { stdio: 'inherit' });
      console.log('✅ Verificação de tipos passou');
    } catch (error) {
      throw new Error('❌ Erros de tipo encontrados');
    }
  }

  // Otimização de assets
  async optimizeAssets() {
    console.log('🖼️ Otimizando assets...');
    
    const assetsDir = path.join(this.projectRoot, 'assets');
    if (fs.existsSync(assetsDir)) {
      // Listar arquivos de imagem grandes
      const imageFiles = fs.readdirSync(assetsDir)
        .filter(file => /\.(png|jpg|jpeg)$/i.test(file))
        .map(file => {
          const filePath = path.join(assetsDir, file);
          const stats = fs.statSync(filePath);
          return { file, size: stats.size };
        })
        .filter(item => item.size > 1024 * 1024); // > 1MB
      
      if (imageFiles.length > 0) {
        console.warn('⚠️ Imagens grandes encontradas:');
        imageFiles.forEach(item => {
          console.log(`   ${item.file}: ${(item.size / 1024 / 1024).toFixed(1)}MB`);
        });
        console.log('   Considere otimizar essas imagens antes do build');
      }
    }
    
    console.log('✅ Assets verificados');
  }

  // Build Android
  async buildAndroid() {
    console.log('🤖 Iniciando build Android...');
    
    try {
      execSync(`eas build --platform android --profile ${this.buildConfig.android.profile}`, { 
        stdio: 'inherit' 
      });
      console.log('✅ Build Android concluído');
      return true;
    } catch (error) {
      console.error('❌ Falha no build Android:', error.message);
      return false;
    }
  }

  // Build iOS
  async buildIOS() {
    console.log('🍎 Iniciando build iOS...');
    
    try {
      execSync(`eas build --platform ios --profile ${this.buildConfig.ios.profile}`, { 
        stdio: 'inherit' 
      });
      console.log('✅ Build iOS concluído');
      return true;
    } catch (error) {
      console.error('❌ Falha no build iOS:', error.message);
      return false;
    }
  }

  // Build completo
  async buildAll() {
    console.log('🚀 Iniciando build completo...');
    
    try {
      execSync('eas build --platform all --profile production', { 
        stdio: 'inherit' 
      });
      console.log('✅ Build completo concluído');
      return true;
    } catch (error) {
      console.error('❌ Falha no build completo:', error.message);
      return false;
    }
  }

  // Análise de bundle
  async analyzeBundle() {
    console.log('📊 Analisando bundle...');
    
    try {
      execSync('npm run analyze:bundle', { stdio: 'inherit' });
      console.log('✅ Análise de bundle concluída');
    } catch (error) {
      console.warn('⚠️ Análise de bundle não disponível');
    }
  }

  // Gerar release notes
  generateReleaseNotes() {
    const version = JSON.parse(fs.readFileSync('package.json', 'utf8')).version;
    const date = new Date().toLocaleDateString('pt-BR');
    
    const releaseNotes = `
# Primotex Técnico v${version}

## 📅 Data de Release: ${date}

## ✨ Funcionalidades Principais
- ✅ Sistema completo de Ordens de Serviço
- ✅ Agendamento integrado com calendário
- ✅ Sistema de notificações push
- ✅ Analytics e relatórios avançados
- ✅ Autenticação biométrica
- ✅ Funcionamento offline
- ✅ Sincronização automática

## 🔧 Melhorias de Performance
- Bundle otimizado para produção
- Lazy loading de componentes
- Cache inteligente de dados
- Monitoramento de performance

## 🔒 Segurança
- Criptografia de dados sensíveis
- Validação rigorosa de entrada
- Controle de tentativas de login
- Logs de auditoria

## 📱 Compatibilidade
- Android 7.0+ (API 24+)
- iOS 12.0+
- Suporte a tablets (Android)

## 🎯 Próximos Passos
- Integração com ERP desktop
- Módulos financeiros
- Relatórios customizáveis
- Integração WhatsApp

---
*Build gerado automaticamente pelo sistema de CI/CD*
`;
    
    fs.writeFileSync('RELEASE_NOTES.md', releaseNotes);
    console.log('✅ Release notes geradas');
  }

  // Executar todo o pipeline
  async runFullPipeline(platform = 'all') {
    const startTime = Date.now();
    
    try {
      console.log('🚀 INICIANDO PIPELINE DE PRODUÇÃO');
      console.log('=' .repeat(50));
      
      await this.preBuildChecks();
      await this.runTests();
      await this.runLinting();
      await this.runTypeCheck();
      await this.optimizeAssets();
      
      // Build baseado na plataforma
      let buildSuccess = false;
      switch (platform) {
        case 'android':
          buildSuccess = await this.buildAndroid();
          break;
        case 'ios':
          buildSuccess = await this.buildIOS();
          break;
        case 'all':
        default:
          buildSuccess = await this.buildAll();
          break;
      }
      
      if (!buildSuccess) {
        throw new Error('Build falhou');
      }
      
      await this.analyzeBundle();
      this.generateReleaseNotes();
      
      const duration = ((Date.now() - startTime) / 1000 / 60).toFixed(1);
      
      console.log('\n' + '=' .repeat(50));
      console.log('🎉 PIPELINE CONCLUÍDO COM SUCESSO!');
      console.log(`⏱️ Tempo total: ${duration} minutos`);
      console.log('=' .repeat(50));
      
      return true;
      
    } catch (error) {
      const duration = ((Date.now() - startTime) / 1000 / 60).toFixed(1);
      
      console.log('\n' + '=' .repeat(50));
      console.error('💥 PIPELINE FALHOU!');
      console.error(`❌ Erro: ${error.message}`);
      console.log(`⏱️ Tempo até falha: ${duration} minutos`);
      console.log('=' .repeat(50));
      
      return false;
    }
  }
}

// CLI Interface
if (require.main === module) {
  const platform = process.argv[2] || 'all';
  const builder = new ProductionBuilder();
  
  builder.runFullPipeline(platform)
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('Erro fatal:', error);
      process.exit(1);
    });
}

module.exports = ProductionBuilder;