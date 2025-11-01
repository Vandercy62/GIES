/**
 * Teste Básico de Validação - App Mobile Primotex
 * 
 * Este teste valida a estrutura básica do app mobile sem depender
 * do servidor Expo, contornando problemas de dependências Metro.
 */

const fs = require('fs');
const path = require('path');

// Cores para output no terminal
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    reset: '\x1b[0m'
};

class MobileAppValidator {
    constructor() {
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    log(message, color = 'reset') {
        console.log(`${colors[color]}${message}${colors.reset}`);
    }

    test(name, testFn) {
        try {
            testFn();
            this.tests.push({ name, status: 'PASS' });
            this.passed++;
            this.log(`✅ ${name}`, 'green');
        } catch (error) {
            this.tests.push({ name, status: 'FAIL', error: error.message });
            this.failed++;
            this.log(`❌ ${name}: ${error.message}`, 'red');
        }
    }

    fileExists(filePath) {
        if (!fs.existsSync(filePath)) {
            throw new Error(`Arquivo não encontrado: ${filePath}`);
        }
        return true;
    }

    validateJsonStructure(filePath, requiredFields) {
        const content = fs.readFileSync(filePath, 'utf8');
        const json = JSON.parse(content);
        
        for (const field of requiredFields) {
            if (!(field in json)) {
                throw new Error(`Campo obrigatório '${field}' não encontrado`);
            }
        }
        return json;
    }

    validateReactComponent(filePath) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Verificações básicas de componente React
        if (!content.includes('import React') && !content.includes('from \'react\'')) {
            throw new Error('Importação do React não encontrada');
        }

        if (!content.includes('export default') && !content.includes('module.exports')) {
            throw new Error('Export default não encontrado');
        }

        return true;
    }

    validateReduxStructure(filePath) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        if (!content.includes('@reduxjs/toolkit')) {
            throw new Error('Redux Toolkit não encontrado');
        }

        if (!content.includes('configureStore') && !content.includes('createSlice')) {
            throw new Error('Configuração Redux não encontrada');
        }

        return true;
    }

    run() {
        this.log('\n🚀 INICIANDO VALIDAÇÃO MOBILE APP PRIMOTEX', 'blue');
        this.log('='.repeat(50), 'blue');

        // Teste 1: Estrutura de arquivos principais
        this.test('Estrutura de arquivos principais', () => {
            this.fileExists('package.json');
            this.fileExists('App.js');
            this.fileExists('app.json');
            this.fileExists('babel.config.js');
        });

        // Teste 2: Configuração package.json
        this.test('Configuração package.json', () => {
            const pkg = this.validateJsonStructure('package.json', [
                'name', 'version', 'scripts', 'dependencies'
            ]);
            
            if (!pkg.scripts.start) {
                throw new Error('Script start não definido');
            }
            
            const requiredDeps = [
                'react', 'react-native', 'expo', '@reduxjs/toolkit',
                'react-redux', '@react-navigation/native'
            ];
            
            for (const dep of requiredDeps) {
                if (!(dep in pkg.dependencies)) {
                    throw new Error(`Dependência ${dep} não encontrada`);
                }
            }
        });

        // Teste 3: Configuração Expo
        this.test('Configuração Expo (app.json)', () => {
            const appConfig = this.validateJsonStructure('app.json', [
                'expo'
            ]);
            
            const expo = appConfig.expo;
            if (!expo.name || !expo.slug || !expo.version) {
                throw new Error('Configurações básicas do Expo incompletas');
            }
        });

        // Teste 4: Babel Configuration
        this.test('Configuração Babel', () => {
            const content = fs.readFileSync('babel.config.js', 'utf8');
            
            if (!content.includes('babel-preset-expo')) {
                throw new Error('babel-preset-expo não configurado');
            }
        });

        // Teste 5: App.js Principal
        this.test('Componente App.js', () => {
            this.validateReactComponent('App.js');
            
            const content = fs.readFileSync('App.js', 'utf8');
            
            // Verificar imports específicos do mobile
            const requiredImports = [
                'react-redux',
                '@react-navigation',
                'redux-persist'
            ];
            
            for (const imp of requiredImports) {
                if (!content.includes(imp)) {
                    throw new Error(`Import ${imp} não encontrado`);
                }
            }
        });

        // Teste 6: Redux Store
        this.test('Redux Store Configuration', () => {
            this.fileExists('src/store/store.js');
            this.validateReduxStructure('src/store/store.js');
        });

        // Teste 7: Navigation System
        this.test('Sistema de Navegação', () => {
            this.fileExists('src/navigation/AppNavigator.js');
            this.validateReactComponent('src/navigation/AppNavigator.js');
        });

        // Teste 8: Screens Principais
        this.test('Screens Principais', () => {
            const screens = [
                'src/screens/auth/LoginScreen.js',
                'src/screens/dashboard/DashboardScreen.js',
                'src/screens/os/OSListScreen.js'
            ];
            
            for (const screen of screens) {
                this.fileExists(screen);
                this.validateReactComponent(screen);
            }
        });

        // Teste 9: Services
        this.test('Serviços Mobile', () => {
            const services = [
                'src/services/apiService.js',
                'src/services/offlineDatabaseService.js',
                'src/services/syncService.js'
            ];
            
            for (const service of services) {
                this.fileExists(service);
            }
        });

        // Teste 10: Node Modules
        this.test('Dependências Instaladas', () => {
            this.fileExists('node_modules');
            
            // Verificar algumas dependências críticas
            const criticalDeps = [
                'node_modules/react',
                'node_modules/react-native',
                'node_modules/expo',
                'node_modules/@reduxjs/toolkit'
            ];
            
            for (const dep of criticalDeps) {
                this.fileExists(dep);
            }
        });

        // Resultado final
        this.log('\n📊 RESULTADO DA VALIDAÇÃO', 'blue');
        this.log('='.repeat(50), 'blue');
        this.log(`Total de testes: ${this.tests.length}`, 'yellow');
        this.log(`✅ Passou: ${this.passed}`, 'green');
        this.log(`❌ Falhou: ${this.failed}`, 'red');
        
        const successRate = ((this.passed / this.tests.length) * 100).toFixed(1);
        this.log(`📈 Taxa de sucesso: ${successRate}%`, 'yellow');

        if (this.failed === 0) {
            this.log('\n🎉 TODOS OS TESTES PASSARAM! App mobile estruturalmente válido.', 'green');
            this.log('✨ Pronto para desenvolvimento e testes avançados.', 'green');
        } else {
            this.log('\n⚠️ Alguns testes falharam. Verificar estrutura do projeto.', 'yellow');
        }

        // Relatório detalhado
        this.log('\n📋 RELATÓRIO DETALHADO:', 'blue');
        this.tests.forEach((test, index) => {
            const status = test.status === 'PASS' ? '✅' : '❌';
            this.log(`${index + 1}. ${status} ${test.name}`);
            if (test.error) {
                this.log(`   → ${test.error}`, 'red');
            }
        });

        return this.failed === 0;
    }
}

// Executar validação
if (require.main === module) {
    const validator = new MobileAppValidator();
    const success = validator.run();
    process.exit(success ? 0 : 1);
}

module.exports = MobileAppValidator;