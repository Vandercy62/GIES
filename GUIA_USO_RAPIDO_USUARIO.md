# 📘 GUIA DE USO RÁPIDO - SISTEMA ERP PRIMOTEX
## Manual Simplificado para Usuário Final
**Versão:** 9.0 | **Data:** 16/11/2025 | **Status:** Production-Ready

---

## 🚀 **COMO INICIAR O SISTEMA**

### **Opção 1: Launcher Automático (RECOMENDADO)** ⭐

1. **Localize o arquivo** na pasta do sistema:
   ```
   C:\GIES\INICIAR_SISTEMA_COMPLETO.bat
   ```

2. **Clique 2x** no arquivo `.bat`

3. **Aguarde 10 segundos** - O sistema irá:
   - ✅ Verificar ambiente
   - ✅ Iniciar servidor backend (porta 8002)
   - ✅ Abrir tela de login automaticamente

4. **Faça login:**
   - **Usuário:** `admin`
   - **Senha:** `admin123`

5. **Pronto!** Dashboard principal será exibido.

---

### **Opção 2: Manual (Se houver problemas)**

1. **Abrir terminal (PowerShell):**
   - Pressione `Win + X`
   - Escolha "Windows PowerShell"

2. **Navegar para pasta do projeto:**
   ```powershell
   cd C:\GIES
   ```

3. **Iniciar servidor backend:**
   ```powershell
   .venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
   ```
   - **IMPORTANTE:** Deixe esta janela ABERTA

4. **Abrir NOVO terminal** e iniciar interface:
   ```powershell
   cd C:\GIES
   .venv\Scripts\python.exe frontend\desktop\login_tkinter.py
   ```

---

## 🔐 **CREDENCIAIS DE ACESSO**

| **Tipo** | **Usuário** | **Senha** | **Permissões** |
|:---------|:------------|:----------|:---------------|
| **Administrador** | `admin` | `admin123` | Acesso total ao sistema |

⚠️ **IMPORTANTE:** 
- Altere a senha padrão após primeiro acesso!
- Acesse: **Menu → Configurações → Alterar Senha**

---

## 🖥️ **NAVEGAÇÃO NO SISTEMA**

### **Dashboard Principal**

Ao fazer login, você verá:

```
╔════════════════════════════════════════════════════════╗
║  🏢 SISTEMA ERP PRIMOTEX                               ║
║  👤 Usuário: admin | Perfil: Administrador  [Logout]  ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  📊 WIDGETS PRINCIPAIS:                                ║
║  ┌─────────┐  ┌─────────┐  ┌─────────┐               ║
║  │   OS    │  │ Agenda  │  │Financ.  │               ║
║  └─────────┘  └─────────┘  └─────────┘               ║
║                                                        ║
║  🔘 NAVEGAÇÃO RÁPIDA:                                  ║
║  • Clientes    • Produtos    • Estoque                ║
║  • Relatórios  • OS          • Agendamento            ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

---

## 📋 **MÓDULOS DISPONÍVEIS**

### **1. 👥 GESTÃO DE CLIENTES**

**Como acessar:** Dashboard → Clientes

**Funcionalidades:**
- ✅ **Listar** todos os clientes cadastrados
- ✅ **Criar** novo cliente (botão "Novo Cliente")
- ✅ **Editar** cliente existente (selecionar + botão "Editar")
- ✅ **Buscar** clientes por nome, CPF ou CNPJ
- ✅ **Visualizar** detalhes completos

**Campos do cadastro:**
- Nome completo
- CPF/CNPJ (validação automática)
- Email e telefone
- Endereço completo (com CEP)
- Observações gerais

---

### **2. 📦 GESTÃO DE PRODUTOS**

**Como acessar:** Dashboard → Produtos

**Funcionalidades:**
- ✅ **Listar** produtos com estoque atual
- ✅ **Criar** novo produto
- ✅ **Editar** informações e preços
- ✅ **Controlar** estoque (entradas/saídas)
- ✅ **Gerar** códigos de barras
- ✅ **Alertas** de estoque baixo

**Campos do cadastro:**
- Código do produto
- Nome e descrição
- Categoria
- Preço de custo e venda
- Estoque (atual/mínimo/máximo)
- Código de barras

---

### **3. 📋 ORDENS DE SERVIÇO (OS)**

**Como acessar:** Dashboard → OS Dashboard

**7 Fases do Workflow:**
1. 🔵 **Solicitação** - Cliente solicita serviço
2. 🟠 **Análise Técnica** - Avaliação técnica
3. 🟣 **Orçamento** - Elaboração de orçamento
4. 🟠 **Aprovação** - Cliente aprova/rejeita
5. 🔵 **Execução** - Serviço em andamento
6. 🟢 **Finalização** - Serviço concluído
7. ✅ **Concluído** - OS finalizada

**Funcionalidades:**
- ✅ **Criar** nova OS (botão "Nova OS")
- ✅ **Filtrar** por status e prioridade
- ✅ **Alterar status** da OS
- ✅ **Visualizar** detalhes completos
- ✅ **Editar** OS existente

**Prioridades disponíveis:**
- 🔴 Urgente
- 🟠 Alta
- 🟡 Normal
- 🟢 Baixa

---

### **4. 📅 AGENDAMENTO**

**Como acessar:** Dashboard → Agendamento

**Funcionalidades:**
- ✅ **Visualizar** calendário mensal
- ✅ **Criar** novo agendamento
- ✅ **Vincular** agendamento a OS
- ✅ **Notificações** automáticas
- ✅ **Reagendar** compromissos

---

### **5. 💰 FINANCEIRO**

**Como acessar:** Dashboard → Financeiro

**5 Abas principais:**

**5.1. Contas a Receber**
- Cadastro de valores a receber
- Controle de vencimentos
- Registro de pagamentos

**5.2. Contas a Pagar**
- Cadastro de despesas
- Controle de pagamentos
- Alertas de vencimento

**5.3. Fluxo de Caixa**
- Movimentações diárias
- Entradas e saídas
- Saldo consolidado

**5.4. Relatórios**
- Relatórios financeiros
- Análises de período
- Gráficos e indicadores

**5.5. Configurações**
- Categorias de despesas
- Formas de pagamento
- Contas bancárias

---

### **6. 📦 ESTOQUE**

**Como acessar:** Dashboard → Estoque

**4 Abas especializadas:**

**6.1. Movimentações**
- Registrar entradas
- Registrar saídas
- Histórico completo

**6.2. Inventário**
- Contagem física
- Ajustes de estoque
- Relatórios de divergências

**6.3. Alertas**
- Estoque baixo
- Estoque alto
- Produtos zerados

**6.4. Relatórios**
- Valor do estoque
- Movimentações por período
- Análise ABC

---

### **7. 📊 RELATÓRIOS**

**Como acessar:** Dashboard → Relatórios

**6 Templates disponíveis:**
1. **Executivo** - Resumo geral da empresa
2. **Clientes** - Listagem completa de clientes
3. **Produtos** - Catálogo de produtos
4. **Financeiro** - Demonstrativos financeiros
5. **Estoque** - Inventário atual
6. **Personalizado** - Criar seu próprio modelo

**Formatos de exportação:**
- 📄 PDF (pronto para impressão)
- 📊 Excel (para análise)
- 📧 Email (envio direto)

---

## 🔧 **SOLUÇÃO DE PROBLEMAS COMUNS**

### **❌ Problema: "Servidor não está respondendo"**

**Solução:**
1. Verifique se backend está rodando
2. Acesse no navegador: `http://127.0.0.1:8002/health`
3. Se não carregar, reinicie o servidor:
   ```powershell
   Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
   cd C:\GIES
   .venv\Scripts\python.exe -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
   ```

---

### **❌ Problema: "Login não funciona"**

**Solução:**
1. Confirme credenciais:
   - Usuário: `admin`
   - Senha: `admin123`
2. Verifique se servidor backend está online
3. Verifique erro no terminal do backend

---

### **❌ Problema: "Porta 8002 já está em uso"**

**Solução:**
1. Feche outros processos Python:
   ```powershell
   Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
   ```
2. Aguarde 5 segundos
3. Inicie novamente o launcher

---

### **❌ Problema: "Interface não abre"**

**Solução:**
1. Verifique se Python está instalado: `python --version`
2. Verifique ambiente virtual: 
   ```powershell
   cd C:\GIES
   .venv\Scripts\python.exe --version
   ```
3. Se não funcionar, reinstale dependências:
   ```powershell
   .venv\Scripts\pip install -r requirements.txt
   ```

---

## 📞 **SUPORTE E AJUDA**

### **Documentação Técnica Completa**
- Arquivo: `C:\GIES\DOCUMENTACAO_TECNICA_COMPLETA.md`
- Contém detalhes técnicos de todos os módulos

### **Logs do Sistema**
- Pasta: `C:\GIES\logs\`
- Útil para diagnóstico de problemas

### **API Docs (Desenvolvedores)**
- URL: `http://127.0.0.1:8002/docs`
- Documentação interativa da API

---

## ✅ **CHECKLIST DE USO DIÁRIO**

### **Ao Iniciar o Dia:**
- [ ] Executar `INICIAR_SISTEMA_COMPLETO.bat`
- [ ] Fazer login com suas credenciais
- [ ] Verificar OS pendentes (Dashboard → Widget OS)
- [ ] Verificar agendamentos do dia
- [ ] Verificar contas a vencer

### **Durante o Dia:**
- [ ] Registrar novos clientes conforme necessário
- [ ] Criar/atualizar OS
- [ ] Registrar movimentações de estoque
- [ ] Lançar movimentações financeiras

### **Ao Final do Dia:**
- [ ] Atualizar status das OS
- [ ] Confirmar agendamentos do próximo dia
- [ ] Registrar pagamentos recebidos
- [ ] Fazer backup (opcional)

---

## 💾 **BACKUP E SEGURANÇA**

### **Localização dos Dados:**
- **Banco de dados:** `C:\GIES\primotex_erp.db`
- **Sessões:** `C:\Users\[Usuário]\.primotex_session.json`

### **Como fazer backup manual:**
1. Copiar arquivo `primotex_erp.db`
2. Salvar em local seguro (pen drive, nuvem, etc.)
3. Renomear com data: `primotex_erp_2025-11-16.db`

### **Como restaurar backup:**
1. Fechar sistema completamente
2. Substituir `primotex_erp.db` pelo backup
3. Reiniciar sistema

---

## 🎯 **PRÓXIMOS PASSOS (OPCIONAL)**

Após dominar o básico, você pode:

1. **Personalizar relatórios** - Criar templates customizados
2. **Configurar comunicação** - Integrar WhatsApp Business
3. **Adicionar usuários** - Criar logins para equipe
4. **Explorar API** - Integrar com outros sistemas
5. **App Mobile** - Acessar via smartphone (em desenvolvimento)

---

## 📌 **DICAS IMPORTANTES**

✅ **SEMPRE mantenha o backend rodando** durante uso do sistema  
✅ **NÃO feche o terminal do backend** enquanto usar a interface  
✅ **FAÇA backup semanal** do arquivo de banco de dados  
✅ **ALTERE a senha padrão** na primeira utilização  
✅ **MANTENHA o sistema atualizado** conforme novas versões  

---

## 🏁 **RESUMO RÁPIDO**

### **Para iniciar:**
```
1. Clicar em: INICIAR_SISTEMA_COMPLETO.bat
2. Aguardar 10 segundos
3. Login: admin / admin123
4. Pronto para usar!
```

### **Módulos principais:**
- **Clientes** → Cadastro de clientes
- **OS Dashboard** → Gestão de ordens de serviço
- **Financeiro** → Controle financeiro
- **Estoque** → Gestão de produtos
- **Relatórios** → Gerar relatórios PDF

### **Em caso de problemas:**
1. Verificar se servidor backend está rodando
2. Acessar: `http://127.0.0.1:8002/health`
3. Consultar seção "Solução de Problemas" deste guia

---

**🎉 SISTEMA PRONTO PARA USO PROFISSIONAL! 🎉**

*Manual criado em: 16/11/2025*  
*Versão do Sistema: 9.0 - Consolidação Final*  
*Status: Production-Ready ✅*
