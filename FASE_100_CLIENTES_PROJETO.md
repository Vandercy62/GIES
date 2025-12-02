# 📋 FASE 100 - MODERNIZAÇÃO CADASTRO DE CLIENTES

**Data:** 16/11/2025  
**Status:** 🎯 EM PLANEJAMENTO  
**Prioridade:** ALTA  
**Estimativa:** 3-5 dias  

---

## 🎯 OBJETIVO

Modernizar completamente o módulo de cadastro de clientes seguindo o documento original do sistema, com interface em **4 ABAS** (Wizard) para facilitar o uso por colaboradores de idade avançada.

---

## 📊 ANÁLISE DO BANCO DE DADOS ATUAL

**Data da Análise:** 16/11/2025  
**Status:** ✅ **CONCLUÍDA E ATUALIZADA**  

### ✅ Estrutura Existente (cliente_model.py)

O modelo atual JÁ possui TODOS os campos necessários organizados em 3 seções:

**RESULTADO:** ✅ **MODELO PERFEITO - NÃO PRECISA ALTERAÇÃO!**

#### **ABA 1 - Dados Básicos** ✅
- ✅ id (chave primária)
- ✅ codigo (único, ex: CLI001)
- ✅ tipo_pessoa (Física/Jurídica)
- ✅ nome (Nome completo ou Razão Social)
- ✅ cpf_cnpj (com validação)
- ✅ rg_ie (RG ou Inscrição Estadual)
- ✅ data_nascimento_fundacao
- ✅ foto_path (caminho da foto)
- ✅ status (Ativo/Inativo/Prospect)
- ✅ origem (Google, Indicação, etc.)
- ✅ tipo_cliente (Residencial, Comercial, etc.)

#### **ABA 2 - Dados Complementares** ✅
**Endereço:**
- ✅ endereco_cep
- ✅ endereco_logradouro
- ✅ endereco_numero
- ✅ endereco_complemento
- ✅ endereco_bairro
- ✅ endereco_cidade
- ✅ endereco_estado

**Contatos:**
- ✅ telefone_fixo
- ✅ telefone_celular
- ✅ telefone_whatsapp
- ✅ email_principal
- ✅ email_secundario
- ✅ site
- ✅ redes_sociais (JSON)
- ✅ contatos_adicionais (JSON)

**Dados Bancários:**
- ✅ banco_nome
- ✅ banco_agencia
- ✅ banco_conta

**Dados Comerciais:**
- ✅ limite_credito
- ✅ dia_vencimento_preferencial

#### **ABA 3 - Observações e Anexos** ✅
- ✅ observacoes_gerais
- ✅ historico_interacoes (JSON)
- ✅ anexos_paths (JSON)
- ✅ tags_categorias (JSON)

#### **Controle Sistema** ✅
- ✅ data_criacao
- ✅ data_atualizacao
- ✅ usuario_criacao_id
- ✅ usuario_atualizacao_id

### 🎉 CONCLUSÃO DA ANÁLISE DE BANCO DE DADOS

#### ✅ **MODELO (cliente_model.py):**
- **Status:** 100% PERFEITO
- **Campos:** Todos os 35+ campos presentes
- **Organização:** Estrutura em 3 abas conforme documento
- **Ação:** ✅ **NENHUMA ALTERAÇÃO NECESSÁRIA**

#### ⚠️ **SCHEMA (cliente_schemas.py):**
- **Status Anterior:** ❌ INCOMPLETO (apenas 13 campos)
- **Status Atual:** ✅ **100% ATUALIZADO** (35+ campos)
- **Ação Tomada:** ✅ **SCHEMA COMPLETAMENTE REESCRITO**

#### 📋 **ALTERAÇÕES REALIZADAS:**
1. ✅ Adicionados **22 campos faltantes** ao schema
2. ✅ Corrigido nome: `data_cadastro` → `data_criacao`
3. ✅ Criados **5 schemas auxiliares** para campos JSON
4. ✅ Implementados **4 validadores customizados**
5. ✅ Documentação completa em todos os campos
6. ✅ Organização em 3 seções (ABA 1, 2, 3)

#### 🔗 **DOCUMENTAÇÃO DETALHADA:**
- Ver: `FASE_100_ALTERACOES_SCHEMA.md`
- Arquivo modificado: `backend/schemas/cliente_schemas.py`
- Data: 16/11/2025

#### 🎯 **IMPACTO:**
- ✅ Compatibilidade 100% entre API e Banco de Dados
- ✅ Todos os campos do modelo agora disponíveis na API
- ✅ Validações robustas implementadas
- ✅ Pronto para implementação da interface 4 abas

---

## 🎨 NOVA INTERFACE - 4 ABAS (WIZARD)

### **ABA 1: 📋 LISTA DE CLIENTES**
- **Objetivo:** Visualização e busca rápida
- **Layout:** Tela cheia com tabela
- **Funcionalidades:**
  - ✅ Tabela com todos os clientes
  - ✅ Busca em tempo real (nome, CPF, telefone)
  - ✅ Filtros: Status, Tipo, Origem
  - ✅ Botões grandes: **NOVO CLIENTE** | **EDITAR** | **EXCLUIR**
  - ✅ Duplo clique → vai para Aba 2 (edição)
  - ✅ Botão **IMPRIMIR LISTA** (PDF)

### **ABA 2: 👤 DADOS BÁSICOS DO CLIENTE**
- **Objetivo:** Informações principais
- **Layout:** Formulário vertical com scroll
- **Campos:**
  1. Tipo de Pessoa (Física/Jurídica) - Radio grande
  2. Nome Completo / Razão Social ⭐
  3. CPF/CNPJ ⭐ (com validação)
  4. RG / Inscrição Estadual
  5. Data Nascimento / Fundação
  6. Status (Ativo/Inativo/Prospect) - Dropdown
  7. Origem (Google, Indicação, etc.) - Dropdown
  8. Tipo Cliente (Residencial, Comercial, etc.) - Dropdown
  9. **Foto do Cliente** (botão CAPTURAR/UPLOAD)

**Botões de Navegação:**
- ⬅️ **VOLTAR** (→ Aba 1)
- ➡️ **PRÓXIMO** (→ Aba 3)
- 💾 **SALVAR E CONTINUAR**

### **ABA 3: 🏠 DADOS COMPLEMENTARES**
- **Objetivo:** Endereço, contatos, dados comerciais
- **Layout:** 3 painéis verticais com scroll

**Painel 1: Endereço**
1. CEP (com busca automática) 🔍
2. Logradouro
3. Número
4. Complemento
5. Bairro
6. Cidade
7. Estado (dropdown)

**Painel 2: Contatos**
1. Telefone Fixo
2. Celular ⭐
3. WhatsApp
4. Email Principal ⭐
5. Email Secundário
6. Site
7. **Contatos Adicionais** (botão ADICIONAR)
   - Nome, Cargo, Telefone, Email

**Painel 3: Dados Comerciais**
1. Limite de Crédito (R$)
2. Dia Vencimento Preferencial (1-31)
3. Banco (nome)
4. Agência
5. Conta

**Botões de Navegação:**
- ⬅️ **ANTERIOR** (→ Aba 2)
- ➡️ **PRÓXIMO** (→ Aba 4)
- 💾 **SALVAR E CONTINUAR**

### **ABA 4: 📝 OBSERVAÇÕES E IMPRESSÃO**
- **Objetivo:** Notas, anexos, impressão
- **Layout:** 2 colunas

**Coluna 1: Observações**
1. Observações Gerais (textarea grande)
2. Tags/Categorias (chips editáveis)
3. **Histórico de Interações** (timeline)
4. **Anexos** (lista + botão ADICIONAR)
   - Upload de documentos, plantas, fotos

**Coluna 2: Ações**
1. 📄 **IMPRIMIR FICHA COMPLETA** (PDF)
   - Gera ficha profissional com TODOS os dados
   - Logo da empresa
   - Foto do cliente
   - Dados organizados
2. 📧 **ENVIAR POR EMAIL**
3. 📱 **ENVIAR POR WHATSAPP**
4. 💾 **SALVAR E VOLTAR**
5. ❌ **CANCELAR**

**Botões de Navegação:**
- ⬅️ **ANTERIOR** (→ Aba 3)
- 💾 **SALVAR E FECHAR**

---

## 🎨 DESIGN E USABILIDADE

### **Para Colaboradores de Idade:**

1. **Fontes Grandes:**
   - Labels: **14px bold**
   - Campos: **16px**
   - Botões: **16px bold**

2. **Botões Grandes:**
   - Altura mínima: **50px**
   - Largura mínima: **150px**
   - Cores contrastantes
   - Ícones + Texto

3. **Espaçamento:**
   - Entre campos: **20px**
   - Entre seções: **30px**
   - Padding interno: **15px**

4. **Cores:**
   - Botão Próximo: **Verde #27ae60**
   - Botão Anterior: **Azul #3498db**
   - Botão Salvar: **Verde escuro #16a085**
   - Botão Cancelar: **Vermelho #e74c3c**
   - Campos obrigatórios: **Borda vermelha se vazio**

5. **Validações Visuais:**
   - ✅ Verde se válido
   - ❌ Vermelho se inválido
   - Mensagens claras: "CPF inválido - Digite corretamente"

6. **Navegação:**
   - Indicador visual de aba ativa (1/4, 2/4, etc.)
   - Breadcrumb: **Lista → Dados Básicos → Complementares → Observações**
   - Atalhos: **F2=Salvar | F3=Próximo | F4=Anterior | ESC=Cancelar**

---

## 📁 ESTRUTURA DE ARQUIVOS

```
frontend/desktop/
├── clientes_wizard.py               # NOVO - Interface principal 4 abas
├── clientes_window.py               # ANTIGO - Manter como backup
├── clientes_components/             # NOVO - Pasta de componentes
│   ├── __init__.py
│   ├── aba_lista.py                 # Aba 1 - Lista
│   ├── aba_dados_basicos.py         # Aba 2 - Dados Básicos
│   ├── aba_complementares.py        # Aba 3 - Complementares
│   ├── aba_observacoes.py           # Aba 4 - Observações
│   ├── foto_widget.py               # Widget de captura/upload foto
│   ├── contatos_adicionais.py       # Dialog contatos extras
│   └── impressao_ficha.py           # Gerador PDF ficha completa

backend/api/routes/
├── clientes.py                      # Atualizar endpoints (se necessário)

shared/
├── validadores.py                   # Funções de validação CPF/CNPJ
├── formatadores.py                  # Máscaras de telefone, CEP, etc.
└── busca_cep.py                     # Integração ViaCEP API
```

---

## 🔧 TECNOLOGIAS E BIBLIOTECAS

### **Já Instaladas:**
- ✅ tkinter (interface)
- ✅ requests (API)
- ✅ Pillow (imagens)
- ✅ ReportLab (PDF)

### **Novas (se necessário):**
```bash
# Captura de webcam (se não tiver opencv)
pip install opencv-python

# Validações brasileiras
pip install python-validate-br

# ViaCEP (busca endereço)
pip install pycep-correios
```

---

## 📝 TAREFAS DETALHADAS

### **TAREFA 1: Estrutura Base** ⏱️ 4 horas
- [ ] Criar pasta `clientes_components/`
- [ ] Criar `clientes_wizard.py` (janela principal)
- [ ] Configurar ttk.Notebook com 4 abas
- [ ] Implementar navegação entre abas
- [ ] Criar barra de progresso visual (1/4, 2/4...)

### **TAREFA 2: Aba 1 - Lista** ⏱️ 3 horas
- [ ] Criar `aba_lista.py`
- [ ] Implementar Treeview com colunas otimizadas
- [ ] Sistema de busca em tempo real
- [ ] Filtros (Status, Tipo, Origem)
- [ ] Botões grandes (NOVO | EDITAR | EXCLUIR)
- [ ] Duplo clique → abre edição
- [ ] Função de impressão de lista (PDF)

### **TAREFA 3: Aba 2 - Dados Básicos** ⏱️ 4 horas
- [ ] Criar `aba_dados_basicos.py`
- [ ] Formulário com todos os campos
- [ ] Validação CPF/CNPJ em tempo real
- [ ] Toggle Física/Jurídica (altera labels)
- [ ] Widget de foto (captura/upload)
- [ ] Dropdowns com dados das constantes
- [ ] Botões VOLTAR | PRÓXIMO | SALVAR

### **TAREFA 4: Aba 3 - Dados Complementares** ⏱️ 5 horas
- [ ] Criar `aba_complementares.py`
- [ ] Painel de endereço com busca CEP
- [ ] Painel de contatos (validação email)
- [ ] Dialog de contatos adicionais
- [ ] Painel de dados comerciais
- [ ] Máscaras de formatação
- [ ] Botões ANTERIOR | PRÓXIMO | SALVAR

### **TAREFA 5: Aba 4 - Observações** ⏱️ 4 horas
- [ ] Criar `aba_observacoes.py`
- [ ] Textarea para observações
- [ ] Sistema de tags/categorias
- [ ] Timeline de histórico
- [ ] Upload de anexos
- [ ] Botões de ação (Email, WhatsApp)
- [ ] Botões ANTERIOR | SALVAR E FECHAR

### **TAREFA 6: Impressão de Ficha** ⏱️ 4 horas
- [ ] Criar `impressao_ficha.py`
- [ ] Template PDF profissional
- [ ] Header com logo da empresa
- [ ] Foto do cliente (se tiver)
- [ ] Dados organizados em seções
- [ ] Footer com data/hora/usuário
- [ ] Botão de visualização prévia

### **TAREFA 7: Componentes Auxiliares** ⏱️ 3 horas
- [ ] Criar `foto_widget.py` (captura/upload)
- [ ] Criar `contatos_adicionais.py` (dialog)
- [ ] Criar `shared/validadores.py`
- [ ] Criar `shared/formatadores.py`
- [ ] Criar `shared/busca_cep.py`

### **TAREFA 8: Integração API** ⏱️ 2 horas
- [ ] Verificar endpoints existentes
- [ ] Atualizar se necessário para novos campos
- [ ] Testar CRUD completo
- [ ] Upload de fotos/anexos

### **TAREFA 9: Integração Dashboard** ⏱️ 1 hora
- [ ] Atualizar `dashboard_principal.py`
- [ ] Alterar botão "Clientes" para abrir wizard
- [ ] Manter backward compatibility

### **TAREFA 10: Testes** ⏱️ 4 horas
- [ ] Testar navegação entre abas
- [ ] Testar validações de campos
- [ ] Testar busca CEP
- [ ] Testar captura de foto
- [ ] Testar impressão de ficha
- [ ] Testar CRUD completo
- [ ] Testar com colaboradores reais

---

## ⏱️ CRONOGRAMA

| Dia | Tarefas | Horas | Status |
|-----|---------|-------|--------|
| **Dia 1** | Tarefas 1, 2 | 7h | ⏳ Pendente |
| **Dia 2** | Tarefas 3, 7 (parcial) | 7h | ⏳ Pendente |
| **Dia 3** | Tarefa 4 | 5h | ⏳ Pendente |
| **Dia 4** | Tarefas 5, 6 | 8h | ⏳ Pendente |
| **Dia 5** | Tarefas 7, 8, 9, 10 | 7h | ⏳ Pendente |

**Total:** ~34 horas de desenvolvimento

---

## 🎯 CRITÉRIOS DE ACEITAÇÃO

### **Funcionalidade:**
- ✅ Todas as 4 abas funcionando
- ✅ Navegação fluida entre abas
- ✅ Botões PRÓXIMO/ANTERIOR funcionais
- ✅ Validação de campos obrigatórios
- ✅ Busca CEP online funcionando
- ✅ Captura de foto funcionando
- ✅ Upload de anexos funcionando
- ✅ Impressão de ficha gerando PDF
- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Integração com API

### **Usabilidade:**
- ✅ Fontes grandes (14-16px)
- ✅ Botões grandes (50px altura mínima)
- ✅ Cores contrastantes
- ✅ Mensagens de erro claras
- ✅ Validações visuais (verde/vermelho)
- ✅ Atalhos de teclado funcionando

### **Performance:**
- ✅ Lista carrega em < 2 segundos
- ✅ Busca em tempo real < 500ms
- ✅ Geração de PDF < 3 segundos
- ✅ Sem travamentos na interface

---

## 📋 CHECKLIST FINAL

### **Antes de Iniciar:**
- [ ] Backup do banco de dados atual
- [ ] Backup do `clientes_window.py` atual
- [ ] Criar branch Git: `feature/fase-100-clientes`
- [ ] Instalar dependências novas (se houver)

### **Durante Desenvolvimento:**
- [ ] Commits frequentes (a cada tarefa)
- [ ] Testar cada aba isoladamente
- [ ] Documentar código
- [ ] Criar logs de debug

### **Antes de Deploy:**
- [ ] Testes com dados reais
- [ ] Testes com colaboradores
- [ ] Validar performance
- [ ] Documentação de uso
- [ ] Guia rápido impresso

---

## 🚀 PRÓXIMOS PASSOS (APÓS FASE 100)

1. **FASE 101:** Cadastro de Fornecedores (mesmo modelo 4 abas)
2. **FASE 102:** Cadastro de Colaboradores (5 abas + documentos)
3. **FASE 103:** Cadastro de Produtos (wizard simplificado)
4. **FASE 104:** OS completa (7 fases do documento)
5. **FASE 105:** Sistema financeiro completo

---

## 📞 DECISÕES PENDENTES

1. ❓ Quer captura de foto via webcam ou apenas upload?
2. ❓ Impressão de ficha deve incluir histórico de compras?
3. ❓ Sistema de tags: predefinidas ou livres?
4. ❓ Anexos: onde salvar? (local/servidor/nuvem)
5. ❓ Envio por WhatsApp: já tem API configurada?

---

## ✅ APROVAÇÃO PARA INICIAR

- [ ] Cliente revisou e aprovou o plano
- [ ] Decisões pendentes foram respondidas
- [ ] Cronograma está aprovado
- [ ] Pode iniciar desenvolvimento

---

**Criado por:** GitHub Copilot  
**Data:** 16/11/2025  
**Versão:** 1.0  
**Status:** 🎯 AGUARDANDO APROVAÇÃO
