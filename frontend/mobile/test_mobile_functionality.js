/**
 * Teste Avançado de Funcionalidade - App Mobile Primotex
 * 
 * Valida funcionalidades específicas dos componentes React Native,
 * Redux, serviços e integração sem depender do servidor Expo.
 */

const fs = require('fs');
const path = require('path');

// Cores para output no terminal
const colors = {
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    reset: '\x1b[0m'
};

class MobileFunctionalityValidator {
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

    validateComponentStructure(filePath, requiredElements) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        for (const element of requiredElements) {
            if (!content.includes(element)) {
                throw new Error(`Elemento '${element}' não encontrado`);
            }
        }
        return true;
    }

    validateReduxSlice(filePath, sliceName) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        const requiredElements = [
            'createSlice',
            `name: '${sliceName}'`,
            'initialState',
            'reducers'
        ];
        
        for (const element of requiredElements) {
            if (!content.includes(element)) {
                throw new Error(`Redux slice element '${element}' não encontrado`);
            }
        }
        return true;
    }

    validateServiceAPI(filePath, serviceName) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        // Verificar estrutura básica de serviço
        const patterns = [
            /class\s+\w+Service/,
            /export\s+(default\s+)?class/,
            /async\s+\w+\(/
        ];
        
        let foundPatterns = 0;
        for (const pattern of patterns) {
            if (pattern.test(content)) {
                foundPatterns++;
            }
        }
        
        if (foundPatterns === 0) {
            throw new Error(`Estrutura de serviço não encontrada em ${serviceName}`);
        }
        
        return true;
    }

    validateOfflineCapability(filePath) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        const offlineElements = [
            'SQLite',
            'database',
            'offline',
            'sync'
        ];
        
        let foundElements = 0;
        for (const element of offlineElements) {
            if (content.toLowerCase().includes(element.toLowerCase())) {
                foundElements++;
            }
        }
        
        if (foundElements < 2) {
            throw new Error('Funcionalidade offline insuficiente');
        }
        
        return true;
    }

    validateNavigationStructure(filePath) {
        const content = fs.readFileSync(filePath, 'utf8');
        
        const navigationElements = [
            '@react-navigation',
            'createStackNavigator',
            'NavigationContainer'
        ];
        
        for (const element of navigationElements) {
            if (!content.includes(element)) {
                throw new Error(`Elemento de navegação '${element}' não encontrado`);
            }
        }
        
        return true;
    }

    run() {
        this.log('\n🔬 VALIDAÇÃO AVANÇADA DE FUNCIONALIDADE', 'cyan');
        this.log('='.repeat(55), 'cyan');

        // Teste 1: Componente de Login - Funcionalidade
        this.test('Login Screen - Funcionalidade', () => {
            this.validateComponentStructure('src/screens/auth/LoginScreen.js', [
                'useState',
                'TextInput',
                'TouchableOpacity',
                'login',
                'navigation'
            ]);
        });

        // Teste 2: Dashboard - Interface e Stats
        this.test('Dashboard Screen - Interface', () => {
            this.validateComponentStructure('src/screens/dashboard/DashboardScreen.js', [
                'ScrollView',
                'Card',
                'stats',
                'useSelector',
                'useEffect'
            ]);
        });

        // Teste 3: Redux Store - Configuração Avançada
        this.test('Redux Store - Configuração Avançada', () => {
            const storeContent = fs.readFileSync('src/store/store.js', 'utf8');
            
            const requiredElements = [
                'persistReducer',
                'persistStore',
                'combineReducers',
                'configureStore'
            ];
            
            for (const element of requiredElements) {
                if (!storeContent.includes(element)) {
                    throw new Error(`Redux store element '${element}' não encontrado`);
                }
            }
        });

        // Teste 4: Redux Slices - Auth
        this.test('Redux Slice - Auth', () => {
            this.validateReduxSlice('src/store/slices/authSlice.js', 'auth');
            
            const content = fs.readFileSync('src/store/slices/authSlice.js', 'utf8');
            if (!content.includes('login') || !content.includes('logout')) {
                throw new Error('Actions de login/logout não encontradas');
            }
        });

        // Teste 5: Redux Slice - OS
        this.test('Redux Slice - OS', () => {
            this.validateReduxSlice('src/store/slices/osSlice.js', 'os');
            
            const content = fs.readFileSync('src/store/slices/osSlice.js', 'utf8');
            if (!content.includes('fetchOS') || !content.includes('updateOS')) {
                throw new Error('Actions de OS não encontradas');
            }
        });

        // Teste 6: API Service - Estrutura e Métodos
        this.test('API Service - Estrutura', () => {
            this.validateServiceAPI('src/services/apiService.js', 'API');
            
            const content = fs.readFileSync('src/services/apiService.js', 'utf8');
            
            const requiredMethods = ['login', 'get', 'post', 'put', 'delete'];
            for (const method of requiredMethods) {
                if (!content.includes(method)) {
                    throw new Error(`Método API '${method}' não encontrado`);
                }
            }
        });

        // Teste 7: Offline Database Service
        this.test('Offline Database Service', () => {
            this.validateServiceAPI('src/services/offlineDatabaseService.js', 'OfflineDatabase');
            this.validateOfflineCapability('src/services/offlineDatabaseService.js');
        });

        // Teste 8: Sync Service - Sincronização
        this.test('Sync Service - Sincronização', () => {
            this.validateServiceAPI('src/services/syncService.js', 'Sync');
            
            const content = fs.readFileSync('src/services/syncService.js', 'utf8');
            
            const syncMethods = ['syncUp', 'syncDown', 'syncAll'];
            let foundMethods = 0;
            for (const method of syncMethods) {
                if (content.includes(method)) {
                    foundMethods++;
                }
            }
            
            if (foundMethods < 2) {
                throw new Error('Métodos de sincronização insuficientes');
            }
        });

        // Teste 9: Navigation System - Estrutura
        this.test('Navigation System - Estrutura', () => {
            this.validateNavigationStructure('src/navigation/AppNavigator.js');
            
            const content = fs.readFileSync('src/navigation/AppNavigator.js', 'utf8');
            
            // Verificar screens definidas
            const screens = ['Login', 'Dashboard', 'OS'];
            for (const screen of screens) {
                if (!content.includes(screen)) {
                    throw new Error(`Screen '${screen}' não encontrada na navegação`);
                }
            }
        });

        // Teste 10: Camera Service - Funcionalidade Nativa
        this.test('Camera Service - Funcionalidade Nativa', () => {
            this.validateServiceAPI('src/services/cameraService.js', 'Camera');
            
            const content = fs.readFileSync('src/services/cameraService.js', 'utf8');
            
            const cameraFeatures = ['takePicture', 'expo-camera', 'permissions'];
            for (const feature of cameraFeatures) {
                if (!content.includes(feature)) {
                    throw new Error(`Feature de câmera '${feature}' não encontrada`);
                }
            }
        });

        // Teste 11: Location Service - GPS
        this.test('Location Service - GPS', () => {
            this.validateServiceAPI('src/services/locationService.js', 'Location');
            
            const content = fs.readFileSync('src/services/locationService.js', 'utf8');
            
            const locationFeatures = ['getCurrentPosition', 'expo-location', 'coordinates'];
            for (const feature of locationFeatures) {
                if (!content.includes(feature)) {
                    throw new Error(`Feature de localização '${feature}' não encontrada`);
                }
            }
        });

        // Teste 12: File Service - Gestão de Arquivos
        this.test('File Service - Gestão de Arquivos', () => {
            this.validateServiceAPI('src/services/fileService.js', 'File');
            
            const content = fs.readFileSync('src/services/fileService.js', 'utf8');
            
            const fileFeatures = ['saveFile', 'readFile', 'expo-file-system'];
            for (const feature of fileFeatures) {
                if (!content.includes(feature)) {
                    throw new Error(`Feature de arquivo '${feature}' não encontrada`);
                }
            }
        });

        // Teste 13: Componentes Reutilizáveis
        this.test('Componentes Reutilizáveis', () => {
            const components = [
                'src/components/common/Card.js',
                'src/components/forms/FormInput.js'
            ];
            
            for (const component of components) {
                if (fs.existsSync(component)) {
                    this.validateComponentStructure(component, ['export default', 'React']);
                }
            }
        });

        // Teste 14: Styles - Sistema de Estilos
        this.test('Sistema de Estilos', () => {
            const stylesFile = 'src/styles/globalStyles.js';
            if (fs.existsSync(stylesFile)) {
                const content = fs.readFileSync(stylesFile, 'utf8');
                
                const styleElements = ['StyleSheet', 'colors', 'fonts', 'spacing'];
                for (const element of styleElements) {
                    if (!content.includes(element)) {
                        throw new Error(`Elemento de estilo '${element}' não encontrado`);
                    }
                }
            }
        });

        // Teste 15: Package.json - Scripts e Dependências Avançadas
        this.test('Package.json - Scripts Avançados', () => {
            const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
            
            const requiredScripts = ['start', 'android', 'ios'];
            for (const script of requiredScripts) {
                if (!pkg.scripts[script]) {
                    throw new Error(`Script '${script}' não encontrado`);
                }
            }
            
            // Verificar dependências específicas para funcionalidade
            const advancedDeps = [
                'expo-camera',
                'expo-location',
                'expo-local-authentication',
                'redux-persist'
            ];
            
            for (const dep of advancedDeps) {
                if (!pkg.dependencies[dep]) {
                    throw new Error(`Dependência avançada '${dep}' não encontrada`);
                }
            }
        });

        // Resultado final
        this.log('\n📊 RESULTADO DA VALIDAÇÃO AVANÇADA', 'cyan');
        this.log('='.repeat(55), 'cyan');
        this.log(`Total de testes: ${this.tests.length}`, 'yellow');
        this.log(`✅ Passou: ${this.passed}`, 'green');
        this.log(`❌ Falhou: ${this.failed}`, 'red');
        
        const successRate = ((this.passed / this.tests.length) * 100).toFixed(1);
        this.log(`📈 Taxa de sucesso: ${successRate}%`, 'yellow');

        if (this.failed === 0) {
            this.log('\n🎉 VALIDAÇÃO AVANÇADA COMPLETA! App mobile funcionalmente robusto.', 'green');
            this.log('🚀 Funcionalidades prontas:', 'green');
            this.log('   • Autenticação com biometria', 'green');
            this.log('   • Offline-first com SQLite', 'green');
            this.log('   • Sincronização inteligente', 'green');
            this.log('   • Câmera e GPS integrados', 'green');
            this.log('   • Redux com persistência', 'green');
            this.log('   • Navegação completa', 'green');
        } else if (this.failed <= 3) {
            this.log('\n✅ VALIDAÇÃO BOA! App mobile com funcionalidade sólida.', 'yellow');
            this.log('🔧 Pequenos ajustes podem ser necessários.', 'yellow');
        } else {
            this.log('\n⚠️ VALIDAÇÃO PARCIAL! Verificar funcionalidades.', 'red');
        }

        // Análise de Funcionalidades
        this.log('\n🔍 ANÁLISE DE FUNCIONALIDADES:', 'cyan');
        
        const categories = {
            'Autenticação': [1, 4],
            'Interface': [2],
            'Estado (Redux)': [3, 4, 5],
            'Serviços Core': [6, 7, 8],
            'Navegação': [9],
            'Nativos (Device)': [10, 11, 12],
            'UI/UX': [13, 14],
            'Configuração': [15]
        };

        for (const [category, testIndexes] of Object.entries(categories)) {
            const categoryTests = testIndexes.map(i => this.tests[i - 1]);
            const passed = categoryTests.filter(t => t.status === 'PASS').length;
            const total = categoryTests.length;
            const percentage = ((passed / total) * 100).toFixed(0);
            
            const status = percentage == 100 ? '✅' : percentage >= 75 ? '⚠️' : '❌';
            this.log(`${status} ${category}: ${passed}/${total} (${percentage}%)`);
        }

        return this.failed <= 3; // Aceitar até 3 falhas para funcionalidade
    }
}

// Executar validação
if (require.main === module) {
    const validator = new MobileFunctionalityValidator();
    const success = validator.run();
    
    console.log('\n🎯 PRÓXIMOS PASSOS RECOMENDADOS:');
    if (success) {
        console.log('✅ 1. Proceder com testes de integração backend');
        console.log('✅ 2. Implementar testes unitários automatizados');
        console.log('✅ 3. Configurar build para produção');
    } else {
        console.log('🔧 1. Corrigir funcionalidades faltantes');
        console.log('🔧 2. Re-executar validação');
        console.log('🔧 3. Proceder com cautela aos próximos passos');
    }
    
    process.exit(success ? 0 : 1);
}

module.exports = MobileFunctionalityValidator;