# Sistema ERP Primotex - Forros e Divisórias Eirelli

Sistema de gerenciamento empresarial integrado desenvolvido em Python para controle completo de operações comerciais.

## 📋 Sobre o Projeto

O **Primotex ERP** é um sistema completo de gestão empresarial desenvolvido especificamente para a empresa Primotex - Forros e Divisórias Eirelli. O sistema oferece controle total sobre todas as operações da empresa, desde o cadastro de clientes até a finalização de serviços, incluindo controle financeiro, estoque e comunicação automática.

## 🏗️ Arquitetura

### Backend
- **Python 3.13.7** 
- **FastAPI** - API REST moderna e rápida
- **SQLAlchemy 1.4.48** - ORM para banco de dados
- **SQLite** - Banco de dados local
- **Alembic** - Controle de migrações
- **JWT** - Autenticação segura
- **Requests** - Comunicação HTTP

### Frontend Desktop
- **tkinter** - Interface gráfica nativa Python
- **Threading** - Operações não-blocking
- **ReportLab** - Geração de PDFs (futuro)

### Integrações (Planejadas)
- **WhatsApp Business API** - Comunicação automática
- **python-barcode** - Geração de códigos de barras
- **python-pptx/docx** - Documentos Office

## 🗂️ Módulos do Sistema

### 1. 👥 Administração
- Configurações gerais do sistema
- Gestão de usuários e permissões
- Backup e segurança
- Templates de comunicação

### 2. 📝 Cadastros
- **Clientes** (3 abas: Dados básicos, Complementares, Observações)
- **Fornecedores** (Gestão completa)
- **Colaboradores** (4 abas + controle de documentos)
- **Produtos e Serviços** (com códigos de barras)

### 3. ⚙️ Fluxo Operacional
Sistema completo de **Ordem de Serviço (OS)** com 7 fases:
1. Abertura da OS
2. Ficha de Visita Técnica
3. Orçamento
4. Envio e Acompanhamento
5. Execução
6. Finalização
7. Arquivo

### 4. 📦 Estoque
- Controle de entrada/saída
- Inventário
- Códigos de barras
- Alertas de estoque mínimo

### 5. 💰 Financeiro
- Contas a receber/pagar
- Controle de caixa
- Fluxo de caixa
- Documentos financeiros

### 6. 🛒 Vendas e Compras
- Pedidos de venda
- Pedidos de compra
- Relatórios

### 7. 📅 Agendamento
- Agenda integrada
- Sincronização com OS
- Alertas automáticos

### 8. 📱 Comunicação
- Email automático
- WhatsApp Business
- Templates personalizáveis

### 9. 📊 Relatórios
- Dashboards interativos
- Estatísticas detalhadas
- KPIs empresariais

### 10. ⚙️ Configurações
- Personalização da interface
- Utilitários diversos
- Backup automático

## 🚀 Funcionalidades Principais

- ✅ **Multiplataforma** (Windows, Web, Mobile)
- ✅ **Funciona offline e online**
- ✅ **Backup automático**
- ✅ **Interface moderna e intuitiva**
- ✅ **Códigos de barras integrados**
- ✅ **Comunicação automática**
- ✅ **Relatórios completos**
- ✅ **Controle de permissões**
- ✅ **Portável** (roda de pendrive/HD externo)
- ✅ **Rede local e remota**

## 📁 Estrutura do Projeto

```
primotex_erp/
├── backend/                 # Backend FastAPI
│   ├── api/                # Endpoints da API
│   ├── models/             # Modelos SQLAlchemy
│   ├── services/           # Lógica de negócio
│   └── database/           # Configuração do banco
├── frontend/               # Interfaces do usuário
│   ├── desktop/           # App PyQt6
│   ├── web/               # Interface web
│   └── mobile/            # App mobile
├── shared/                # Código compartilhado
├── tests/                 # Testes automatizados
├── docs/                  # Documentação
└── README.md              # Este arquivo
```

## 🛠️ Instalação

### Requisitos
- Python 3.10 ou superior
- PostgreSQL 12+
- Redis (para tarefas assíncronas)

### Setup Inicial
```bash
# Clone o repositório
git clone [url-do-repositorio]
cd primotex_erp

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados
alembic upgrade head

# Executar aplicação
python main.py
```

## 📋 Status do Desenvolvimento

### ✅ FASE 1 - FUNDAÇÃO (CONCLUÍDA)
- [x] Estrutura do projeto criada
- [x] Configuração inicial do ambiente
- [x] Modelo de banco de dados SQLite
- [x] Sistema de autenticação JWT
- [x] API REST FastAPI completa
- [x] Validação de todos os modelos

### ✅ FASE 2 - INTERFACE DESKTOP (33% CONCLUÍDA)
- [x] Sistema de login desktop (tkinter)
- [x] Dashboard principal com navegação
- [x] Interface de clientes completa (CRUD)
- [ ] Módulo de produtos (em andamento)
- [ ] Sistema de estoque
- [ ] Geração de códigos de barras
- [ ] Relatórios básicos em PDF
- [ ] Sistema de navegação avançada
- [ ] Testes de integração

### 🔄 Próximas Fases
- **FASE 3** - Fluxo Operacional (OS completa, orçamentos)
- **FASE 4** - Sistema Financeiro e colaboradores
- **FASE 5** - Comunicação automática e relatórios avançados
- **FASE 6** - Web e mobile

## 🚨 Pontos Críticos

### Servidor Backend
- **Porta:** 8002 (obrigatória)
- **Comando:** `python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002`
- **Status:** Deve estar rodando antes da aplicação desktop

### Credenciais de Sistema
- **Admin:** admin / admin123
- ⚠️ **IMPORTANTE:** Alterar senha em produção

### Compatibilidade
- **Python:** 3.13.7 (ambiente atual)
- **SQLAlchemy:** 1.4.48 (NÃO atualizar para 2.x)
- **GUI Framework:** tkinter (PyQt6 tem problemas DLL)
- **Banco:** SQLite local (primotex_erp.db)

## 🏃‍♂️ Inicio Rápido

### 1. Clonar e configurar ambiente
```bash
git clone [url-do-repositorio]
cd GIES
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Inicializar sistema
```bash
python scripts/init_system.py
```

### 3. Executar sistema completo

**Terminal 1 - Backend:**
```bash
.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
```

**Terminal 2 - Frontend:**
```bash
cd frontend\desktop
..\..\venv\Scripts\python.exe test_complete.py
```

### 4. Acessar sistema
- **Desktop:** Executar aplicação frontend
- **API Docs:** http://127.0.0.1:8002/docs
- **Health Check:** http://127.0.0.1:8002/health
- **Login:** admin / admin123

## 👨‍💻 Desenvolvedor

Sistema desenvolvido para **Primotex - Forros e Divisórias Eirelli**

---

**Data de Início:** 29 de outubro de 2025
**Status Atual:** Fase 1 - Fundação em desenvolvimento