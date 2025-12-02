# ✅ Checklist de Deployment - FASE 104

**Sistema ERP Primotex**  
**Módulo:** Grids Especializados para OS  
**Data:** 19/11/2025  
**Versão:** 1.0

---

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Checklist de Backend](#checklist-de-backend)
3. [Checklist de Frontend](#checklist-de-frontend)
4. [Checklist de Banco de Dados](#checklist-de-banco-de-dados)
5. [Checklist de Segurança](#checklist-de-segurança)
6. [Checklist de Testes](#checklist-de-testes)
7. [Checklist de Documentação](#checklist-de-documentação)
8. [Procedimento de Deploy](#procedimento-de-deploy)
9. [Rollback Plan](#rollback-plan)
10. [Monitoramento Pós-Deploy](#monitoramento-pós-deploy)

---

## Pré-requisitos

### Ambiente de Produção

- [ ] **Servidor:** Windows Server 2019+ ou Windows 10/11
- [ ] **Python:** 3.13.7 instalado
- [ ] **RAM:** Mínimo 4GB disponível
- [ ] **Disco:** Mínimo 10GB disponível
- [ ] **Rede:** Porta 8002 liberada no firewall
- [ ] **Usuário:** Conta com privilégios administrativos

### Softwares Necessários

- [ ] **Python 3.13.7** instalado e no PATH
- [ ] **Git** (opcional, para versionamento)
- [ ] **Editor de Texto** (Notepad++, VSCode)
- [ ] **Navegador** (Chrome/Edge para acessar API docs)
- [ ] **PDF Viewer** (para visualizar orçamentos)

### Credenciais

- [ ] **Senha Admin:** Alterar senha padrão (`admin123`)
- [ ] **JWT Secret:** Configurar secret key único
- [ ] **Banco de Dados:** Backup da versão anterior
- [ ] **Email SMTP:** Configurar (se necessário)

---

## Checklist de Backend

### 1. Dependências

- [ ] Criar ambiente virtual `.venv`
  ```bash
  python -m venv .venv
  ```

- [ ] Ativar ambiente virtual
  ```bash
  .venv\Scripts\activate
  ```

- [ ] Instalar dependências
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verificar versões críticas:
  - [ ] `SQLAlchemy==1.4.48` (NÃO 2.x)
  - [ ] `fastapi>=0.104.0`
  - [ ] `uvicorn>=0.24.0`
  - [ ] `python-jose>=3.3.0`
  - [ ] `reportlab>=4.0.0`

### 2. Configuração

- [ ] Verificar `backend/database/config.py`:
  - [ ] Database URL correta
  - [ ] Pool size adequado
  - [ ] Timeout configurado

- [ ] Verificar `backend/auth/jwt_handler.py`:
  - [ ] Secret key única (não usar padrão!)
  - [ ] Token expiry adequado (30 dias OK)
  - [ ] Algorithm: HS256

- [ ] Verificar `shared/config.py`:
  - [ ] API_BASE_URL correto
  - [ ] LOG_LEVEL adequado (INFO em prod)
  - [ ] BACKUP_ENABLED = True

### 3. Endpoints API

- [ ] Testar todos os 10 novos endpoints:
  - [ ] `POST /api/v1/os/{id}/croqui`
  - [ ] `GET /api/v1/os/{id}/croqui`
  - [ ] `POST /api/v1/os/{id}/medicoes-json`
  - [ ] `GET /api/v1/os/{id}/medicoes-json`
  - [ ] `POST /api/v1/os/{id}/orcamento-json`
  - [ ] `GET /api/v1/os/{id}/orcamento-json`
  - [ ] `POST /api/v1/os/{id}/materiais-json`
  - [ ] `GET /api/v1/os/{id}/materiais-json`
  - [ ] `POST /api/v1/os/{id}/equipe-json`
  - [ ] `GET /api/v1/os/{id}/equipe-json`

- [ ] Verificar `/health` endpoint
  ```bash
  curl http://127.0.0.1:8002/health
  ```

- [ ] Acessar documentação Swagger
  ```
  http://127.0.0.1:8002/docs
  ```

### 4. Inicialização

- [ ] Testar startup do backend
  ```bash
  .venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
  ```

- [ ] Verificar logs de inicialização
  - [ ] Sem erros críticos
  - [ ] Banco conectado
  - [ ] Routers registrados
  - [ ] Servidor ouvindo na porta 8002

- [ ] Testar autenticação
  ```bash
  curl -X POST http://127.0.0.1:8002/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}'
  ```

---

## Checklist de Frontend

### 1. Arquivos Desktop

- [ ] Verificar arquivos principais existem:
  - [ ] `frontend/desktop/login_tkinter.py`
  - [ ] `frontend/desktop/dashboard_principal.py`
  - [ ] `frontend/desktop/os_dashboard.py`
  - [ ] `frontend/desktop/canvas_croqui.py`
  - [ ] `frontend/desktop/grid_orcamento.py`
  - [ ] `frontend/desktop/grid_medicoes.py`
  - [ ] `frontend/desktop/grid_materiais.py`
  - [ ] `frontend/desktop/grid_equipe.py`
  - [ ] `frontend/desktop/dialog_produto_selector.py`
  - [ ] `frontend/desktop/pdf_orcamento.py`

### 2. Autenticação

- [ ] Verificar `shared/session_manager.py`:
  - [ ] Singleton implementado
  - [ ] Thread-safe
  - [ ] Persistência JSON funcionando

- [ ] Verificar `frontend/desktop/auth_middleware.py`:
  - [ ] Decorators @require_login funcionando
  - [ ] Decorators @require_permission funcionando
  - [ ] Redirect para login funcional

### 3. Integração OS Dashboard

- [ ] Verificar botões no OS Dashboard:
  - [ ] 🎨 "Croqui" abre Canvas
  - [ ] 💰 "Criar Orçamento" abre Grid Orçamento
  - [ ] 📏 "Medições" abre Grid Medições
  - [ ] 📦 "Materiais" abre Grid Materiais
  - [ ] 👥 "Equipe" abre Grid Equipe

- [ ] Verificar integração com backend:
  - [ ] Token JWT enviado em headers
  - [ ] Timeout de 10s configurado
  - [ ] Retry logic implementado

### 4. Funcionalidades

- [ ] **Canvas Croqui:**
  - [ ] Desenhar linhas
  - [ ] Desenhar retângulos
  - [ ] Desenhar círculos
  - [ ] Adicionar textos
  - [ ] Adicionar medidas
  - [ ] Desfazer/Refazer (Ctrl+Z/Y)
  - [ ] Salvar PNG no backend
  - [ ] Carregar PNG do backend

- [ ] **Grid Orçamento:**
  - [ ] Adicionar item (dialog seletor)
  - [ ] Editar qtd (double-click)
  - [ ] Editar preço (double-click)
  - [ ] Editar desconto (double-click)
  - [ ] Remover item
  - [ ] Cálculo automático de totais
  - [ ] Salvar JSON no backend
  - [ ] Gerar PDF

- [ ] **Grid Medições:**
  - [ ] Adicionar medição
  - [ ] Editar medição
  - [ ] Remover medição
  - [ ] Cálculo automático de área
  - [ ] Salvar JSON

- [ ] **Grid Materiais:**
  - [ ] Adicionar material (dialog seletor)
  - [ ] Editar aplicação
  - [ ] Validação de estoque
  - [ ] Registrar devoluções
  - [ ] Registrar perdas
  - [ ] Salvar JSON

- [ ] **Grid Equipe:**
  - [ ] Adicionar colaborador (dialog seletor)
  - [ ] Editar alocação
  - [ ] Remover colaborador
  - [ ] Cálculo automático de dias
  - [ ] Cálculo automático de horas
  - [ ] Totalizadores (4 valores)
  - [ ] Salvar JSON

---

## Checklist de Banco de Dados

### 1. Estrutura

- [ ] Verificar tabela `ordens_servico` existe
- [ ] Verificar coluna `dados_croqui` (LargeBinary)
- [ ] Verificar coluna `dados_medicoes_json` (Text)
- [ ] Verificar coluna `dados_orcamento_json` (Text)
- [ ] Verificar coluna `dados_materiais_json` (Text)
- [ ] Verificar coluna `dados_equipe_json` (Text)

### 2. Dados

- [ ] Backup do banco de dados atual
  ```bash
  copy primotex_erp.db primotex_erp.db.backup
  ```

- [ ] Verificar dados essenciais existem:
  - [ ] Pelo menos 1 usuário admin
  - [ ] Pelo menos 1 cliente de teste
  - [ ] Pelo menos 3 produtos cadastrados
  - [ ] Pelo menos 2 colaboradores

### 3. Migrações

- [ ] Executar migrações pendentes (se houver)
  ```bash
  alembic upgrade head
  ```

- [ ] Verificar versão do schema
  ```bash
  alembic current
  ```

### 4. Performance

- [ ] Criar índices recomendados:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_os_cliente ON ordens_servico(cliente_id);
  CREATE INDEX IF NOT EXISTS idx_os_status ON ordens_servico(status);
  CREATE INDEX IF NOT EXISTS idx_os_data ON ordens_servico(data_abertura);
  ```

- [ ] Configurar auto-vacuum
  ```sql
  PRAGMA auto_vacuum = FULL;
  ```

---

## Checklist de Segurança

### 1. Autenticação

- [ ] **CRÍTICO:** Alterar senha padrão do admin
  ```python
  # NÃO usar: admin / admin123 em produção!
  ```

- [ ] Criar usuários com senhas fortes
- [ ] Configurar JWT secret key única
  ```python
  # backend/auth/jwt_handler.py
  SECRET_KEY = "sua-chave-super-secreta-aqui-minimo-32-chars"
  ```

- [ ] Validar token expiry (30 dias OK)

### 2. Permissões

- [ ] Verificar hierarquia de permissões:
  - [ ] Admin → Acesso total
  - [ ] Gerente → Gestão operacional
  - [ ] Operador → Operações diárias
  - [ ] Consulta → Apenas visualização

- [ ] Testar @require_permission em todas as telas

### 3. Dados Sensíveis

- [ ] Não logar senhas ou tokens
- [ ] Não expor secret keys em logs
- [ ] Criptografar dados sensíveis (se aplicável)
- [ ] HTTPS habilitado (se aplicável)

### 4. Validações

- [ ] Validar CPF/CNPJ
- [ ] Validar Email
- [ ] Validar Telefone
- [ ] Sanitizar inputs de usuário
- [ ] Prevenir SQL Injection (usar ORM)
- [ ] Prevenir XSS (usar templates)

---

## Checklist de Testes

### 1. Testes Automatizados

- [ ] Executar suite completa de testes:
  ```bash
  .venv\Scripts\python.exe -m pytest tests/ -v
  ```

- [ ] Verificar taxa de sucesso ≥ 95%
  - [ ] Testes unitários: 54/56 (96.4%)
  - [ ] Testes E2E: 6/6 (100%)
  - [ ] Total: 60/62 (96.8%) ✅

### 2. Testes Manuais

- [ ] **Fluxo Completo de OS:**
  1. [ ] Login no sistema
  2. [ ] Abrir OS Dashboard
  3. [ ] Criar croqui
  4. [ ] Adicionar medições
  5. [ ] Criar orçamento
  6. [ ] Aplicar materiais
  7. [ ] Alocar equipe
  8. [ ] Gerar PDF
  9. [ ] Verificar dados salvos

- [ ] **Testes de Performance:**
  - [ ] Tempo de login < 2s
  - [ ] Tempo de carregamento grid < 500ms
  - [ ] Tempo de geração PDF < 5s
  - [ ] API response < 2s

- [ ] **Testes de UI:**
  - [ ] Todas as telas abrem corretamente
  - [ ] Botões respondem ao clique
  - [ ] Double-click edita células
  - [ ] Scrollbars funcionam
  - [ ] Validações mostram mensagens

### 3. Testes de Integração

- [ ] Backend + Frontend
- [ ] Backend + Banco de Dados
- [ ] Frontend + SessionManager
- [ ] Grids + API Endpoints
- [ ] PDF + ReportLab
- [ ] Croqui + PIL/Pillow

---

## Checklist de Documentação

### 1. Documentação de Usuário

- [ ] `GUIA_USO_GRIDS_OS.md` criado ✅
  - [ ] Instruções de todos os 5 grids
  - [ ] Exemplos práticos
  - [ ] Screenshots (se aplicável)
  - [ ] FAQ de problemas comuns

### 2. Documentação Técnica

- [ ] `RELATORIO_EXECUTIVO_FASE_104.md` criado ✅
  - [ ] Visão geral do projeto
  - [ ] Arquitetura técnica
  - [ ] Métricas de qualidade
  - [ ] ROI e benefícios

- [ ] `STATUS_FASE_104_COMPLETA.md` criado ✅
  - [ ] Status de todas as 10 tarefas
  - [ ] Testes executados
  - [ ] Próximos passos

- [ ] `copilot-instructions.md` atualizado ✅
  - [ ] FASE 104 marcada como completa
  - [ ] Novos arquivos documentados

### 3. Documentação de API

- [ ] Swagger disponível em `/docs`
- [ ] Endpoints documentados
- [ ] Exemplos de request/response
- [ ] Códigos de erro documentados

---

## Procedimento de Deploy

### Fase 1: Preparação (30 minutos)

**1.1. Backup Completo**
```bash
# 1. Parar serviços
taskkill /IM python.exe /F

# 2. Backup do banco
copy primotex_erp.db backups\primotex_erp_pre_fase104_%date:~-4,4%%date:~-7,2%%date:~-10,2%.db

# 3. Backup de arquivos
xcopy frontend\desktop backups\frontend_desktop_%date% /E /I /Y
xcopy backend backups\backend_%date% /E /I /Y
```

**1.2. Verificar Pré-requisitos**
- [ ] Checklist de pré-requisitos 100% completo
- [ ] Todos os testes passando
- [ ] Documentação pronta

### Fase 2: Deploy Backend (15 minutos)

**2.1. Atualizar Código**
```bash
# Se usando Git
git pull origin main

# Ou copiar arquivos manualmente
```

**2.2. Atualizar Dependências**
```bash
.venv\Scripts\activate
pip install -r requirements.txt --upgrade
```

**2.3. Atualizar Banco de Dados**
```bash
# Se houver migrações
alembic upgrade head
```

**2.4. Iniciar Backend**
```bash
.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
```

**2.5. Verificar Health**
```bash
curl http://127.0.0.1:8002/health
# Esperado: {"status": "ok"}
```

### Fase 3: Deploy Frontend (10 minutos)

**3.1. Copiar Arquivos Novos**
- [ ] `canvas_croqui.py`
- [ ] `grid_orcamento.py`
- [ ] `grid_medicoes.py`
- [ ] `grid_materiais.py`
- [ ] `grid_equipe.py`
- [ ] `dialog_produto_selector.py`
- [ ] `pdf_orcamento.py`

**3.2. Atualizar Arquivos Existentes**
- [ ] `os_dashboard.py` (botões dos grids)
- [ ] `dashboard_principal.py` (se necessário)

**3.3. Verificar Integração**
- [ ] Importações corretas
- [ ] SessionManager disponível
- [ ] Auth middleware funcionando

### Fase 4: Testes Pós-Deploy (30 minutos)

**4.1. Smoke Tests**
- [ ] Login funciona
- [ ] Dashboard abre
- [ ] OS Dashboard abre
- [ ] Cada grid abre sem erros

**4.2. Testes de Funcionalidade**
- [ ] Criar orçamento completo
- [ ] Salvar e recuperar dados
- [ ] Gerar PDF
- [ ] Verificar estoque atualizado

**4.3. Testes de Regressão**
- [ ] Funcionalidades antigas funcionam
- [ ] Clientes, Produtos, Estoque OK
- [ ] Relatórios existentes OK

### Fase 5: Validação Final (15 minutos)

**5.1. Checklist de Qualidade**
- [ ] Zero erros críticos
- [ ] Performance aceitável
- [ ] Logs sem warnings graves
- [ ] Documentação acessível

**5.2. Comunicação**
- [ ] Notificar equipe do deploy
- [ ] Enviar guia de uso
- [ ] Agendar treinamento (se necessário)

**5.3. Monitoramento**
- [ ] Ativar logs de produção
- [ ] Configurar alertas
- [ ] Preparar suporte

---

## Rollback Plan

### Quando Fazer Rollback?

Fazer rollback imediatamente se:
- ❌ Erro crítico que impede login
- ❌ Banco de dados corrompido
- ❌ Backend não inicia
- ❌ Perda de dados
- ❌ Performance inaceitável (>10s)

### Procedimento de Rollback (10 minutos)

**1. Parar Serviços**
```bash
taskkill /IM python.exe /F
```

**2. Restaurar Banco de Dados**
```bash
# Renomear banco atual
ren primotex_erp.db primotex_erp_fase104_failed.db

# Restaurar backup
copy backups\primotex_erp_pre_fase104_YYYYMMDD.db primotex_erp.db
```

**3. Restaurar Código**
```bash
# Reverter arquivos
xcopy backups\frontend_desktop_YYYYMMDD frontend\desktop /E /I /Y
xcopy backups\backend_YYYYMMDD backend /E /I /Y
```

**4. Reiniciar Backend Antigo**
```bash
.venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
```

**5. Verificar Funcionamento**
- [ ] Health check OK
- [ ] Login funciona
- [ ] Funcionalidades básicas OK

**6. Comunicar Rollback**
- [ ] Notificar equipe
- [ ] Explicar motivo
- [ ] Planejar novo deploy

---

## Monitoramento Pós-Deploy

### Primeiras 24 Horas

**Métricas a Monitorar:**

- [ ] **Erros Críticos:** 0 esperado
- [ ] **Tempo de Resposta API:** <2s
- [ ] **Uso de Memória:** <500MB
- [ ] **Uso de CPU:** <30% idle
- [ ] **Tamanho do Banco:** Verificar crescimento

**Logs a Revisar:**

- [ ] `logs/primotex_erp.json` (logs gerais)
- [ ] Console do backend (erros HTTP)
- [ ] Logs de sessão (`~/.primotex_session.json`)

**Checklist Diário (Semana 1):**

- [ ] Revisar logs de erro
- [ ] Verificar performance
- [ ] Coletar feedback de usuários
- [ ] Anotar bugs encontrados
- [ ] Planejar hotfixes se necessário

### Primeira Semana

**KPIs a Acompanhar:**

| Métrica | Meta | Frequência |
|---------|------|------------|
| Uptime | >99% | Diário |
| Erros/dia | <5 | Diário |
| Tempo médio resposta | <2s | Diário |
| Usuários ativos | 100% equipe | Diário |
| Satisfação | >8/10 | Fim da semana |

**Ações Preventivas:**

- [ ] Backup automático diário
- [ ] Monitoramento de disco
- [ ] Alertas de erro configurados
- [ ] Suporte técnico disponível
- [ ] Documentação facilmente acessível

### Primeiro Mês

**Revisão Mensal:**

- [ ] Análise de performance
- [ ] Relatório de bugs
- [ ] Feedback consolidado
- [ ] Melhorias identificadas
- [ ] Planejamento de próximas features

---

## 📞 Suporte Pós-Deploy

### Canais de Suporte

- **Email:** suporte@primotex.com
- **Telefone:** (XX) XXXX-XXXX
- **Horário:** Segunda a Sexta, 8h às 18h

### Escalação de Problemas

1. **Nível 1 - Usuário Final:**
   - Consultar `GUIA_USO_GRIDS_OS.md`
   - Consultar FAQ
   - Reiniciar aplicação

2. **Nível 2 - Suporte Técnico:**
   - Verificar logs
   - Revisar configurações
   - Testes básicos

3. **Nível 3 - Desenvolvimento:**
   - Debug avançado
   - Análise de código
   - Hotfix se necessário

---

## ✅ Checklist Final

Antes de considerar o deploy **CONCLUÍDO**:

- [ ] ✅ Todos os checklists acima 100% completos
- [ ] ✅ Testes automatizados passando (≥95%)
- [ ] ✅ Testes manuais completos e aprovados
- [ ] ✅ Backup realizado e verificado
- [ ] ✅ Documentação entregue e acessível
- [ ] ✅ Equipe treinada e confiante
- [ ] ✅ Suporte técnico preparado
- [ ] ✅ Monitoramento ativo
- [ ] ✅ Plano de rollback testado
- [ ] ✅ Stakeholders comunicados

---

## 🎉 Conclusão

Este checklist garante um **deploy seguro, confiável e profissional** da FASE 104.

**Lembre-se:**
- 📋 Siga cada etapa na ordem
- ⏰ Não pule verificações
- 💾 Backup é OBRIGATÓRIO
- 🧪 Teste ANTES e DEPOIS
- 📞 Mantenha suporte disponível

**Boa sorte com o deploy!** 🚀

---

**Versão do Checklist:** 1.0  
**Data:** 19/11/2025  
**Sistema:** ERP Primotex - FASE 104  
**Status:** Production-Ready ✅
