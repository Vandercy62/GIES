# 📋 FASE 101 - MODERNIZAÇÃO CADASTRO DE FORNECEDORES

**Data:** 16/11/2025  
**Status:** 🎯 EM PLANEJAMENTO  
**Prioridade:** ALTA  
**Estimativa:** 3-5 dias  
**Depende de:** FASE 100 (Clientes) concluída  

---

## 🎯 OBJETIVO

Modernizar completamente o módulo de cadastro de fornecedores seguindo o mesmo padrão da FASE 100, com interface em **4 ABAS** (Wizard) para facilitar o uso por colaboradores de idade avançada.

**Seguir exatamente o mesmo modelo visual e funcional do módulo de Clientes.**

---

## 📊 ANÁLISE DO BANCO DE DADOS ATUAL

**Data da Análise:** 16/11/2025  
**Status:** ⏳ **AGUARDANDO ANÁLISE**  

### ✅ Estrutura Existente (fornecedor_model.py)

O modelo atual possui campos organizados conforme necessidades do negócio:

#### **ABA 1 - Dados Básicos**
- ✅ id (chave primária)
- ✅ cnpj_cpf (CNPJ ou CPF único)
- ✅ razao_social (Razão Social ou Nome Completo)
- ✅ nome_fantasia (Nome Fantasia ou Apelido)
- ✅ tipo_pessoa (Física/Jurídica)
- ✅ inscricao_estadual (Inscrição Estadual)
- ✅ categoria (Categoria principal)
- ✅ subcategoria (Subcategoria)
- ✅ porte_empresa (MEI, Micro, Pequena, etc.)
- ✅ status (Ativo/Inativo/Bloqueado/Em Análise)
- ✅ ativo (boolean)
- ✅ avaliacao (1 a 5 estrelas)

#### **ABA 2 - Dados Complementares**
**Endereço:**
- ✅ cep
- ✅ logradouro
- ✅ numero
- ✅ complemento
- ✅ bairro
- ✅ cidade
- ✅ estado
- ✅ endereco_completo (calculado)

**Contatos:**
- ✅ contato_principal (nome do responsável)
- ✅ telefone (principal)
- ✅ telefone_2 (secundário/WhatsApp)
- ✅ email (principal)
- ✅ email_2 (secundário/financeiro)
- ✅ website (site da empresa)

**Dados Bancários:**
- ✅ banco (nome do banco)
- ✅ agencia
- ✅ conta
- ✅ chave_pix

**Dados Comerciais:**
- ✅ condicoes_pagamento (condições padrão)
- ✅ prazo_entrega_padrao (dias)
- ✅ valor_minimo_pedido (R$)
- ✅ desconto_padrao (%)

#### **ABA 3 - Observações e Controle**
- ✅ observacoes (observações gerais)
- ✅ historico_problemas (registro de ocorrências)
- ✅ tags (JSON - palavras-chave)
- ✅ motivo_inativacao

#### **Controle Sistema**
- ✅ data_cadastro
- ✅ data_atualizacao
- ✅ usuario_cadastro_id
- ✅ usuario_atualizacao_id

### 🎯 **AÇÃO NECESSÁRIA:**
1. ⏳ Verificar schema `fornecedor_schemas.py` (provavelmente incompleto)
2. ⏳ Atualizar schema para match 100% com modelo
3. ⏳ Criar schemas auxiliares (JSON fields)
4. ⏳ Implementar validadores (CNPJ/CPF, avaliação, etc.)

---

## 🎨 NOVA INTERFACE - 4 ABAS (WIZARD)

### **ABA 1: 📋 LISTA DE FORNECEDORES**
- **Objetivo:** Visualização e busca rápida
- **Layout:** Tela cheia com tabela
- **Funcionalidades:**
  - ✅ Tabela com todos os fornecedores
  - ✅ Busca em tempo real (razão social, CNPJ, categoria)
  - ✅ Filtros: Status, Categoria, Porte, Avaliação
  - ✅ Botões grandes: **NOVO FORNECEDOR** | **EDITAR** | **EXCLUIR**
  - ✅ Duplo clique → vai para Aba 2 (edição)
  - ✅ Botão **IMPRIMIR LISTA** (PDF)
  - ✅ Indicador visual de avaliação (estrelas)

### **ABA 2: 🏭 DADOS BÁSICOS DO FORNECEDOR**
- **Objetivo:** Informações principais
- **Layout:** Formulário vertical com scroll
- **Campos:**
  1. Tipo de Pessoa (Física/Jurídica) - Radio grande
  2. CNPJ/CPF ⭐ (com validação)
  3. Razão Social / Nome Completo ⭐
  4. Nome Fantasia / Apelido
  5. Inscrição Estadual
  6. Categoria ⭐ (Dropdown com categorias predefinidas)
  7. Subcategoria
  8. Porte da Empresa (MEI, Micro, Pequena, Média, Grande)
  9. Status (Ativo/Inativo/Bloqueado/Em Análise) - Dropdown
  10. **Avaliação** (1-5 estrelas - widget visual)

**Botões de Navegação:**
- ⬅️ **VOLTAR** (→ Aba 1)
- ➡️ **PRÓXIMO** (→ Aba 3)
- 💾 **SALVAR E CONTINUAR**

### **ABA 3: 🏠 DADOS COMPLEMENTARES**
- **Objetivo:** Endereço, contatos, dados comerciais, bancários
- **Layout:** 4 painéis verticais com scroll

**Painel 1: Endereço**
1. CEP (com busca automática) 🔍
2. Logradouro
3. Número
4. Complemento
5. Bairro
6. Cidade
7. Estado (dropdown UF)

**Painel 2: Contatos**
1. Contato Principal (Nome do responsável)
2. Telefone Principal ⭐
3. Telefone 2 (WhatsApp)
4. Email Principal ⭐
5. Email 2 (Financeiro)
6. Website

**Painel 3: Dados Comerciais**
1. Condições de Pagamento (texto livre)
2. Prazo de Entrega Padrão (dias)
3. Valor Mínimo de Pedido (R$)
4. Desconto Padrão (%)

**Painel 4: Dados Bancários**
1. Banco (nome)
2. Agência
3. Conta
4. Chave PIX

**Botões de Navegação:**
- ⬅️ **ANTERIOR** (→ Aba 2)
- ➡️ **PRÓXIMO** (→ Aba 4)
- 💾 **SALVAR E CONTINUAR**

### **ABA 4: 📝 OBSERVAÇÕES E IMPRESSÃO**
- **Objetivo:** Notas, histórico, impressão
- **Layout:** 2 colunas

**Coluna 1: Observações**
1. Observações Gerais (textarea grande)
2. Histórico de Problemas (textarea com histórico)
3. Tags/Palavras-chave (chips editáveis)
   - Ex: "entrega rápida", "preço baixo", "qualidade", etc.
4. Motivo de Inativação (se inativo)

**Coluna 2: Ações**
1. 📄 **IMPRIMIR FICHA COMPLETA** (PDF)
   - Gera ficha profissional com TODOS os dados
   - Logo da empresa
   - Avaliação em estrelas
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

### **Seguir EXATAMENTE o padrão da FASE 100:**

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
   - Mensagens claras: "CNPJ inválido - Digite corretamente"

6. **Navegação:**
   - Indicador visual de aba ativa (1/4, 2/4, etc.)
   - Breadcrumb: **Lista → Dados Básicos → Complementares → Observações**
   - Atalhos: **F2=Salvar | F3=Próximo | F4=Anterior | ESC=Cancelar**

7. **Widget Especial - Avaliação:**
   - ⭐⭐⭐⭐⭐ (5 estrelas clicáveis)
   - Cor dourada para estrelas marcadas
   - Cor cinza para estrelas vazias
   - Tamanho: 30px cada estrela

---

## 📁 ESTRUTURA DE ARQUIVOS

```
frontend/desktop/
├── fornecedores_wizard.py           # NOVO - Interface principal 4 abas
├── fornecedores_window.py           # ANTIGO - Manter como backup (se existir)
├── fornecedores_components/         # NOVO - Pasta de componentes
│   ├── __init__.py
│   ├── aba_lista.py                 # Aba 1 - Lista
│   ├── aba_dados_basicos.py         # Aba 2 - Dados Básicos
│   ├── aba_complementares.py        # Aba 3 - Complementares
│   ├── aba_observacoes.py           # Aba 4 - Observações
│   ├── avaliacao_widget.py          # Widget de estrelas (1-5)
│   └── impressao_ficha.py           # Gerador PDF ficha completa

backend/schemas/
├── fornecedor_schemas.py            # Atualizar schema completo

shared/
├── validadores.py                   # Adicionar validação CNPJ
├── formatadores.py                  # Máscaras (já existe)
└── busca_cep.py                     # Integração ViaCEP (já existe)
```

---

## 🔧 TECNOLOGIAS E BIBLIOTECAS

### **Já Instaladas (da FASE 100):**
- ✅ tkinter (interface)
- ✅ requests (API)
- ✅ Pillow (imagens)
- ✅ ReportLab (PDF)

### **Novas (se necessário):**
```bash
# Validações brasileiras (se ainda não tiver)
pip install python-validate-br
```

---

## 📝 TAREFAS DETALHADAS

### **TAREFA 0: Preparação e Análise** ⏱️ 2 horas
- [ ] Analisar `fornecedor_model.py` (já feito acima)
- [ ] Analisar `fornecedor_schemas.py`
- [ ] Atualizar schema para match 100% com modelo
- [ ] Criar schemas auxiliares (Tags, etc.)
- [ ] Implementar validadores (CNPJ, avaliação 1-5)
- [ ] Documentar alterações

### **TAREFA 1: Estrutura Base** ⏱️ 3 horas
- [ ] Criar pasta `fornecedores_components/`
- [ ] Criar `fornecedores_wizard.py` (janela principal)
- [ ] Configurar ttk.Notebook com 4 abas
- [ ] Implementar navegação entre abas
- [ ] Criar barra de progresso visual (1/4, 2/4...)
- [ ] **COPIAR estrutura da FASE 100 e adaptar**

### **TAREFA 2: Aba 1 - Lista** ⏱️ 3 horas
- [ ] Criar `aba_lista.py`
- [ ] Implementar Treeview com colunas:
  - Código, Razão Social, CNPJ, Categoria, Avaliação, Status
- [ ] Sistema de busca em tempo real
- [ ] Filtros (Status, Categoria, Porte, Avaliação)
- [ ] Botões grandes (NOVO | EDITAR | EXCLUIR)
- [ ] Duplo clique → abre edição
- [ ] Função de impressão de lista (PDF)
- [ ] **ADAPTAR da FASE 100**

### **TAREFA 3: Aba 2 - Dados Básicos** ⏱️ 4 horas
- [ ] Criar `aba_dados_basicos.py`
- [ ] Formulário com todos os 10 campos
- [ ] Validação CNPJ/CPF em tempo real
- [ ] Toggle Física/Jurídica (altera labels)
- [ ] Dropdown Categoria (com categorias predefinidas)
- [ ] Dropdown Porte Empresa
- [ ] Dropdown Status
- [ ] Widget de Avaliação (5 estrelas clicáveis)
- [ ] Botões VOLTAR | PRÓXIMO | SALVAR
- [ ] **ADAPTAR da FASE 100**

### **TAREFA 4: Aba 3 - Dados Complementares** ⏱️ 5 horas
- [ ] Criar `aba_complementares.py`
- [ ] Painel de endereço com busca CEP (REUSAR código FASE 100)
- [ ] Painel de contatos (validação email)
- [ ] Painel de dados comerciais (4 campos)
- [ ] Painel de dados bancários (4 campos)
- [ ] Máscaras de formatação
- [ ] Botões ANTERIOR | PRÓXIMO | SALVAR
- [ ] **4 PAINÉIS ao invés de 3**

### **TAREFA 5: Aba 4 - Observações** ⏱️ 4 horas
- [ ] Criar `aba_observacoes.py`
- [ ] Textarea para observações gerais
- [ ] Textarea para histórico de problemas
- [ ] Sistema de tags/palavras-chave (chips)
- [ ] Campo motivo inativação (condicional)
- [ ] Botões de ação (Email, WhatsApp)
- [ ] Botões ANTERIOR | SALVAR E FECHAR
- [ ] **ADAPTAR da FASE 100**

### **TAREFA 6: Impressão de Ficha** ⏱️ 4 horas
- [ ] Criar `impressao_ficha.py`
- [ ] Template PDF profissional
- [ ] Header com logo da empresa
- [ ] Avaliação em estrelas (visual)
- [ ] Dados organizados em seções
- [ ] Footer com data/hora/usuário
- [ ] Botão de visualização prévia
- [ ] **REUSAR código da FASE 100**

### **TAREFA 7: Componentes Auxiliares** ⏱️ 3 horas
- [ ] Criar `avaliacao_widget.py` (widget de estrelas)
- [ ] Atualizar `shared/validadores.py` (CNPJ)
- [ ] **REUSAR:** `shared/formatadores.py` (já existe)
- [ ] **REUSAR:** `shared/busca_cep.py` (já existe)

### **TAREFA 8: Integração API** ⏱️ 2 horas
- [ ] Verificar endpoints existentes em `/api/v1/fornecedores`
- [ ] Atualizar se necessário para novos campos
- [ ] Testar CRUD completo
- [ ] Validar respostas da API

### **TAREFA 9: Integração Dashboard** ⏱️ 1 hora
- [ ] Atualizar `dashboard_principal.py`
- [ ] Adicionar botão "🏭 Fornecedores"
- [ ] Abrir `fornecedores_wizard.py`
- [ ] Manter backward compatibility

### **TAREFA 10: Testes** ⏱️ 4 horas
- [ ] Testar navegação entre abas
- [ ] Testar validações de campos (CNPJ, avaliação)
- [ ] Testar busca CEP
- [ ] Testar widget de avaliação
- [ ] Testar impressão de ficha
- [ ] Testar CRUD completo
- [ ] Testar filtros e busca

---

## ⏱️ CRONOGRAMA

| Dia | Tarefas | Horas | Status |
|-----|---------|-------|--------|
| **Dia 1** | Tarefas 0, 1, 2 | 8h | ⏳ Pendente |
| **Dia 2** | Tarefas 3, 7 (parcial) | 7h | ⏳ Pendente |
| **Dia 3** | Tarefa 4 | 5h | ⏳ Pendente |
| **Dia 4** | Tarefas 5, 6 | 8h | ⏳ Pendente |
| **Dia 5** | Tarefas 7, 8, 9, 10 | 7h | ⏳ Pendente |

**Total:** ~35 horas de desenvolvimento

---

## 🎯 CRITÉRIOS DE ACEITAÇÃO

### **Funcionalidade:**
- ✅ Todas as 4 abas funcionando
- ✅ Navegação fluida entre abas
- ✅ Botões PRÓXIMO/ANTERIOR funcionais
- ✅ Validação de campos obrigatórios
- ✅ Busca CEP online funcionando
- ✅ Widget de avaliação (estrelas) funcionando
- ✅ Impressão de ficha gerando PDF
- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Integração com API
- ✅ Filtros por categoria e avaliação

### **Usabilidade:**
- ✅ Fontes grandes (14-16px)
- ✅ Botões grandes (50px altura mínima)
- ✅ Cores contrastantes
- ✅ Mensagens de erro claras
- ✅ Validações visuais (verde/vermelho)
- ✅ Atalhos de teclado funcionando
- ✅ **Idêntico visualmente à FASE 100**

### **Performance:**
- ✅ Lista carrega em < 2 segundos
- ✅ Busca em tempo real < 500ms
- ✅ Geração de PDF < 3 segundos
- ✅ Sem travamentos na interface

---

## 📋 CHECKLIST FINAL

### **Antes de Iniciar:**
- [ ] FASE 100 (Clientes) 100% concluída
- [ ] Backup do banco de dados atual
- [ ] Schema atualizado e documentado
- [ ] Criar branch Git: `feature/fase-101-fornecedores`

### **Durante Desenvolvimento:**
- [ ] Commits frequentes (a cada tarefa)
- [ ] Testar cada aba isoladamente
- [ ] Documentar código
- [ ] Criar logs de debug
- [ ] **REUSAR código da FASE 100 sempre que possível**

### **Antes de Deploy:**
- [ ] Testes com dados reais
- [ ] Testes com colaboradores
- [ ] Validar performance
- [ ] Documentação de uso
- [ ] Guia rápido impresso

---

## 🔄 DIFERENÇAS EM RELAÇÃO À FASE 100

### **Campos Exclusivos de Fornecedores:**
1. **Avaliação** (1-5 estrelas) → Widget especial
2. **Categoria/Subcategoria** → Dropdown predefinido
3. **Porte da Empresa** → MEI, Micro, Pequena, etc.
4. **Dados Comerciais:** Prazo entrega, valor mínimo, desconto
5. **Histórico de Problemas** → Textarea separada
6. **Chave PIX** → Campo adicional em dados bancários

### **Campos que NÃO existem:**
- ❌ Foto do fornecedor (Clientes tem)
- ❌ Data de nascimento/fundação (Clientes tem)
- ❌ Redes sociais (Clientes tem)
- ❌ Contatos adicionais JSON (Clientes tem)
- ❌ Anexos (Clientes tem)
- ❌ Histórico de interações (Clientes tem)

### **Simplificações:**
- ✅ Menos campos no total (mais focado)
- ✅ Sem upload de fotos
- ✅ Sem anexos
- ✅ Mais focus em dados comerciais

---

## 🚀 PRÓXIMOS PASSOS (APÓS FASE 101)

1. **FASE 102:** Cadastro de Colaboradores (5 abas + documentos)
2. **FASE 103:** Cadastro de Produtos (wizard simplificado)
3. **FASE 104:** OS completa (7 fases do documento)
4. **FASE 105:** Sistema financeiro completo

---

## 📞 DECISÕES PENDENTES

1. ❓ Sistema de tags: predefinidas ou livres?
2. ❓ Impressão de ficha deve incluir histórico de compras?
3. ❓ Envio por WhatsApp: já tem API configurada?
4. ❓ Widget de avaliação: permitir meio ponto (4.5 estrelas)?
5. ❓ Categorias: fixas ou permitir customização?

---

## 🔗 DEPENDÊNCIAS

### **Depende de:**
- ✅ FASE 100 (Clientes) → Usar como template

### **Fornece base para:**
- 🔄 FASE 102 (Colaboradores)
- 🔄 FASE 105 (Sistema Financeiro - Contas a Pagar)
- 🔄 Sistema de Compras (futuro)

---

## ✅ APROVAÇÃO PARA INICIAR

- [ ] FASE 100 está 100% concluída e testada
- [ ] Schema foi analisado e atualizado
- [ ] Cliente revisou e aprovou o plano
- [ ] Decisões pendentes foram respondidas
- [ ] Cronograma está aprovado
- [ ] Pode iniciar desenvolvimento

---

**Criado por:** GitHub Copilot  
**Data:** 16/11/2025  
**Versão:** 1.0  
**Status:** 🎯 AGUARDANDO CONCLUSÃO DA FASE 100
