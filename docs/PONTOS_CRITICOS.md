🚨 PONTOS CRÍTICOS - SISTEMA ERP PRIMOTEX
==========================================

📅 Atualizado: 29/10/2025 - Módulo de Produtos Concluído
👤 Sistema: ERP Primotex - Forros e Divisórias Eireli

## 🔥 CRÍTICO - CONFIGURAÇÃO DE AMBIENTE

### 1. SERVIDOR BACKEND (OBRIGATÓRIO)
┌─────────────────────────────────────────────────┐
│ ⚠️  SEMPRE VERIFICAR ANTES DE USAR O SISTEMA    │
└─────────────────────────────────────────────────┘

Porta: 8002 (NÃO 8001 - gera conflito)
Comando: 
```bash
cd C:\Users\Vanderci\GIES
.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
```

Status Check: GET http://127.0.0.1:8002/health

### 2. CREDENCIAIS DO SISTEMA
┌─────────────────────────────────────────────────┐
│ 🔐 ACESSO ADMINISTRATIVO                        │
└─────────────────────────────────────────────────┘

Username: admin
Password: admin123
Token: JWT válido por 30 dias

⚠️ ALTERAR SENHA EM PRODUÇÃO!

### 3. DEPENDÊNCIAS CRÍTICAS
┌─────────────────────────────────────────────────┐
│ 🐍 VERSÕES ESPECÍFICAS - NÃO ALTERAR           │
└─────────────────────────────────────────────────┘

Python: 3.13.7
SQLAlchemy: 1.4.48 (❌ NÃO usar 2.x)
GUI: tkinter (❌ PyQt6 tem problemas DLL)
Banco: SQLite (primotex_erp.db)

## 📱 APLICAÇÃO DESKTOP

### ARQUIVOS PRINCIPAIS:
- login_tkinter.py      → Sistema de autenticação ✅
- dashboard.py          → Interface principal ✅  
- clientes_window.py    → CRUD de clientes ✅
- produtos_window.py    → CRUD de produtos ✅
- estoque_window.py     → Controle de estoque ✅
- app.py               → Aplicação integrada
- test_complete.py     → Teste completo

### EXECUÇÃO:
```bash
cd C:\Users\Vanderci\GIES\frontend\desktop
..\..\venv\Scripts\python.exe test_complete.py
```

## 🌐 ENDPOINTS DE API

Base URL: http://127.0.0.1:8002

Principais:
- GET  /health                    → Status do sistema
- POST /api/v1/auth/login        → Autenticação
- GET  /api/v1/clientes          → Listar clientes
- POST /api/v1/clientes          → Criar cliente
- PUT  /api/v1/clientes/{id}     → Atualizar cliente
- DEL  /api/v1/clientes/{id}     → Excluir cliente
- GET  /docs                     → Documentação Swagger

## 🛡️ SEGURANÇA E PERMISSÕES

### NÍVEIS DE ACESSO:
- Administrador → Acesso total ao sistema
- Gerente       → Gestão operacional
- Operador      → Operações diárias
- Consulta      → Apenas visualização

### VALIDAÇÕES IMPLEMENTADAS:
✅ CPF/CNPJ com formatação automática
✅ Email com validação regex
✅ Telefone com máscara (XX) XXXXX-XXXX
✅ CEP formato XXXXX-XXX
✅ Campos obrigatórios
✅ Threading para UI não-blocking

## 📊 STATUS DO PROJETO

### ✅ COMPLETADO (FASE 1 + FASE 2 PARCIAL):
- Estrutura backend completa
- Banco de dados SQLite
- Sistema de autenticação JWT
- Modelos de dados validados
- API REST funcional
- Interface de login desktop
- Dashboard principal
- CRUD de clientes completo

### 🔄 EM ANDAMENTO (FASE 2):
- Módulo de produtos (próximo)
- Sistema de estoque
- Geração de códigos de barras
- Relatórios em PDF

### ⏳ PLANEJADO (FASES 3-5):
- Fluxo operacional (OS completa)
- Sistema financeiro
- Comunicação automática
- Relatórios avançados

## 🚀 COMANDOS RÁPIDOS

### Iniciar Sistema Completo:
```bash
# Terminal 1 - Backend
cd C:\Users\Vanderci\GIES
.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002

# Terminal 2 - Frontend  
cd C:\Users\Vanderci\GIES\frontend\desktop
..\..\venv\Scripts\python.exe test_complete.py
```

### Verificações:
```bash
# API Health Check
curl http://127.0.0.1:8002/health

# Teste de Login
curl -X POST http://127.0.0.1:8002/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 📞 TROUBLESHOOTING

### Problema: Servidor não inicia
Solução: Verificar se porta 8002 está livre

### Problema: PyQt6 DLL Error
Solução: Usar tkinter (já implementado)

### Problema: SQLAlchemy 2.x
Solução: Downgrade para 1.4.48

### Problema: Login falha
Solução: Verificar servidor backend rodando

## 📝 NOTAS IMPORTANTES

⚠️ Sempre usar ambiente virtual (.venv)
⚠️ Servidor backend deve estar rodando antes do frontend
⚠️ Backup do banco SQLite antes de modificações
⚠️ Testes em ambiente separado antes de produção
⚠️ Logs disponíveis no terminal do servidor

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 Primotex - Forros e Divisórias Eireli
📧 Suporte: GitHub Copilot
📅 Última atualização: 29/10/2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━