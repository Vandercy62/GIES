# 🚀 FASE 104 - OS DESKTOP COMPLETA + INTEGRAÇÕES

**Data Início:** 17/11/2025  
**Status:** 🎯 EM EXECUÇÃO  
**Prioridade:** 🔴 CRÍTICA  
**Estimativa:** 5-7 dias  

---

## 🎯 OBJETIVOS PRINCIPAIS

Completar o sistema de **Ordem de Serviço (OS)** desktop com todas as 7 fases do workflow operacional, integrando com módulos já existentes e criando interfaces faltantes críticas.

### Escopo da Fase 104:

1. **OS Desktop - 7 Fases Completas** ⭐⭐⭐
2. **Canvas Croqui Visual** ⭐⭐⭐
3. **Grid Orçamento Interativo** ⭐⭐⭐
4. **Baixa Automática de Estoque** ⭐⭐
5. **Assinatura Digital** ⭐
6. **Integração Financeiro** ⭐⭐
7. **Testes de Integração** ⭐

---

## 📊 STATUS ATUAL DO SISTEMA

### ✅ Módulos 100% Completos:
- ✅ **FASE 102B:** Cleanup (78% redução de erros)
- ✅ **FASE 103:** Colaboradores Desktop (2.400 linhas, 7 componentes)
- ✅ **FASE 10:** Produtos Desktop Completo (933 linhas)
- ✅ **Backend OS:** 6 endpoints funcionais
- ✅ **Backend Financeiro:** 5 abas (contas, lançamentos, caixa, docs, relatórios)
- ✅ **Backend Fornecedores:** Wizard completo
- ✅ **Backend Clientes:** CRUD completo

### ⚠️ Gaps Críticos Identificados:

#### 1. **OS Desktop - Gaps por Fase:**

| Fase | Backend | Desktop | Gap | Prioridade |
|------|---------|---------|-----|------------|
| **FASE 1 - Abertura** | ✅ 100% | ⚠️ 50% | Canvas croqui, seletor produtos | 🔴 ALTA |
| **FASE 2 - Visita Técnica** | ✅ 100% | ⚠️ 40% | Upload fotos múltiplas, medições | 🔴 ALTA |
| **FASE 3 - Orçamento** ⭐⭐⭐ | ✅ 100% | ❌ 0% | Grid interativo, cálculo auto | 🔴 CRÍTICA |
| **FASE 4 - Envio/Acompanhamento** | ✅ 100% | ⚠️ 40% | Timeline eventos, status visual | 🟡 MÉDIA |
| **FASE 5 - Execução** ⭐⭐ | ✅ 100% | ❌ 0% | Checklist tarefas, baixa estoque | 🔴 CRÍTICA |
| **FASE 6 - Finalização** ⭐⭐⭐ | ✅ 100% | ❌ 0% | Assinatura digital, NF, fotos antes/depois | 🔴 CRÍTICA |
| **FASE 7 - Arquivo Morto** | ✅ 100% | ⚠️ 70% | Compactação PDFs, histórico completo | 🟢 BAIXA |

#### 2. **Integrações Faltantes:**
- ❌ **Estoque ↔ OS:** Baixa automática ao finalizar OS (FASE 5)
- ❌ **Financeiro ↔ OS:** Geração automática de contas a receber (FASE 6)
- ❌ **Produtos ↔ OS:** Seletor com busca e preview (FASE 1/3)
- ❌ **Comunicação ↔ OS:** Envio automático de orçamento/aprovação (FASE 4)

---

## 📋 TAREFAS DA FASE 104

### **TAREFA 1: Canvas Croqui Visual** ⭐⭐⭐ (FASE 1 OS)
**Prioridade:** CRÍTICA  
**Estimativa:** 1.5 dias  

**Objetivo:** Interface de desenho técnico para croquis de ambientes.

**Requisitos:**
- Canvas tkinter com ferramentas de desenho
- Retângulo, linha, texto, medidas
- Upload de imagem de fundo (planta existente)
- Zoom in/out
- Export para PNG/PDF
- Salvar coordenadas em JSON

**Arquivo:** `frontend/desktop/canvas_croqui.py` (~600 linhas)

**Integração:** 
- Chamado de `ordem_servico_window.py` (FASE 1)
- Dados salvos em `ordem_servico.dados_croqui_json`

**Validação:**
- [ ] Canvas renderiza corretamente
- [ ] Ferramentas funcionam (retângulo, linha, texto)
- [ ] Upload de fundo funciona
- [ ] Export PNG/PDF funciona
- [ ] Dados salvam em JSON

---

### **TAREFA 2: Grid Orçamento Interativo** ⭐⭐⭐ (FASE 3 OS)
**Prioridade:** CRÍTICA  
**Estimativa:** 2 dias  

**Objetivo:** Grid editável para criação de orçamentos com cálculos automáticos.

**Requisitos:**
- TreeView editável (double-click)
- Colunas: Produto/Serviço, Quantidade, Unidade, Preço Unit., Desconto, Total
- Busca de produtos (autocomplete)
- Cálculo automático de totais
- Adicionar/Remover linhas
- Seção de impostos (ICMS, ISS, PIS, COFINS)
- Seção de totais (Subtotal, Descontos, Impostos, Total Geral)
- Export para PDF profissional

**Componentes:**
1. `grid_orcamento.py` (~800 linhas)
2. `dialog_produto_selector.py` (~400 linhas)
3. `orcamento_pdf_generator.py` (~500 lininas)

**Integração:**
- Chamado de `ordem_servico_window.py` (FASE 3)
- Usa endpoint `GET /api/v1/produtos/`
- Salva em `ordem_servico.orcamento_itens_json`

**Validação:**
- [ ] Grid exibe corretamente
- [ ] Células editáveis funcionam
- [ ] Busca de produtos funciona
- [ ] Cálculos automáticos corretos
- [ ] PDF gerado profissionalmente
- [ ] Dados salvam em JSON

---

### **TAREFA 3: Baixa Automática de Estoque** ⭐⭐ (FASE 5 OS)
**Prioridade:** ALTA  
**Estimativa:** 1 dia  

**Objetivo:** Integração OS → Estoque para baixa automática de materiais.

**Requisitos:**
- Ao finalizar OS (FASE 6), system verifica orçamento aprovado
- Para cada item do orçamento:
  - Busca produto no estoque
  - Calcula quantidade necessária
  - Cria movimentação de saída
  - Atualiza estoque atual
- Log de todas movimentações
- Reversão em caso de cancelamento

**Arquivos Modificados:**
1. `backend/services/ordem_servico_service.py` (adicionar `_baixar_estoque_automatico()`)
2. `backend/services/estoque_service.py` (adicionar `baixar_por_os()`)

**Novo Endpoint:**
- `POST /api/v1/os/{id}/executar` → Muda status + baixa estoque

**Validação:**
- [ ] Baixa automática funciona
- [ ] Quantidades corretas
- [ ] Movimentações registradas
- [ ] Alertas de estoque insuficiente
- [ ] Reversão funciona

---

### **TAREFA 4: Assinatura Digital** ⭐ (FASE 6 OS)
**Prioridade:** MÉDIA  
**Estimativa:** 1 dia  

**Objetivo:** Coletar assinatura digital do cliente na finalização.

**Requisitos:**
- Canvas de assinatura (mouse ou touch)
- Botão "Limpar" e "Confirmar"
- Preview da assinatura
- Salvar como imagem PNG
- Embedding no PDF final

**Arquivo:** `frontend/desktop/assinatura_digital.py` (~300 linhas)

**Integração:**
- Chamado de `ordem_servico_window.py` (FASE 6)
- Salva em `ordem_servico.assinatura_cliente_path`

**Validação:**
- [ ] Canvas permite desenhar
- [ ] Limpar funciona
- [ ] PNG salvo corretamente
- [ ] Assinatura aparece no PDF

---

### **TAREFA 5: FASE 3 Desktop - Grid Orçamento** ⭐⭐⭐
**Prioridade:** CRÍTICA  
**Estimativa:** Incluída na TAREFA 2  

**Objetivo:** Interface completa da FASE 3 (Orçamento) no wizard OS.

**Componentes:**
- Grid interativo (TAREFA 2)
- Seção de observações
- Botões: Salvar Rascunho, Gerar PDF, Enviar Cliente, Aprovar
- Status visual (Rascunho/Enviado/Aprovado/Rejeitado)

**Arquivo:** Seção de `ordem_servico_window.py` (FASE 3)

---

### **TAREFA 6: FASE 5 Desktop - Execução** ⭐⭐
**Prioridade:** ALTA  
**Estimativa:** 1 dia  

**Objetivo:** Interface de execução com checklist e controle de progresso.

**Requisitos:**
- Checklist de tarefas (customizável)
- Barra de progresso (% concluído)
- Upload de fotos do progresso
- Anotações por tarefa
- Botão "Finalizar Execução" → baixa estoque (TAREFA 3)

**Arquivo:** Seção de `ordem_servico_window.py` (FASE 5)

**Integração:** Trigger para baixa de estoque

---

### **TAREFA 7: FASE 6 Desktop - Finalização** ⭐⭐⭐
**Prioridade:** CRÍTICA  
**Estimativa:** 1 dia  

**Objetivo:** Interface de finalização com assinatura e documentos.

**Requisitos:**
- Upload de fotos ANTES/DEPOIS
- Assinatura digital (TAREFA 4)
- Dados de NF (número, data, valor)
- Checklist de documentos entregues
- Botão "Gerar Conta a Receber" → integra financeiro
- Botão "Arquivar OS" → move para FASE 7

**Arquivo:** Seção de `ordem_servico_window.py` (FASE 6)

**Integração:**
- Assinatura digital
- Baixa estoque (já feita na FASE 5)
- Gera conta a receber no financeiro

---

### **TAREFA 8: Integração Financeiro ↔ OS** ⭐⭐
**Prioridade:** ALTA  
**Estimativa:** 1 dia  

**Objetivo:** Ao finalizar OS, criar automaticamente conta a receber.

**Requisitos:**
- Ao clicar "Gerar Conta a Receber" (FASE 6):
  - Cria registro em `contas_receber`
  - Dados: cliente_id, valor_total, data_vencimento, descrição
  - Vincula: `ordem_servico_id`
  - Status: "PENDENTE"
- Permite parcelamento (opcional)

**Arquivos Modificados:**
1. `backend/services/ordem_servico_service.py` (adicionar `_gerar_conta_receber()`)
2. `backend/services/financeiro_service.py` (adicionar `criar_de_os()`)

**Novo Endpoint:**
- `POST /api/v1/os/{id}/gerar-conta-receber`

**Validação:**
- [ ] Conta criada corretamente
- [ ] Valores corretos
- [ ] Vínculo OS ↔ Financeiro funciona
- [ ] Parcelamento opcional funciona

---

### **TAREFA 9: Melhorias FASE 1/2 Desktop** ⚠️
**Prioridade:** MÉDIA  
**Estimativa:** 0.5 dia  

**Melhorias FASE 1:**
- Integrar Canvas Croqui (TAREFA 1)
- Seletor de produtos visual (autocomplete)

**Melhorias FASE 2:**
- Upload múltiplo de fotos (dialog)
- Preview de fotos em grid

**Arquivos:** `ordem_servico_window.py` (seções FASE 1 e 2)

---

### **TAREFA 10: Testes de Integração** ⭐
**Prioridade:** ALTA  
**Estimativa:** 1 dia  

**Objetivo:** Suite de testes para validar integrações.

**Categorias:**
1. **Testes Canvas Croqui (5):**
   - Desenho, upload fundo, export, salvar JSON
   
2. **Testes Grid Orçamento (8):**
   - Adicionar linha, editar célula, cálculos, PDF
   
3. **Testes Baixa Estoque (6):**
   - Baixa automática, reversão, alertas
   
4. **Testes Assinatura (3):**
   - Desenhar, salvar, embedding PDF
   
5. **Testes Integração Financeiro (5):**
   - Gerar conta, parcelamento, vínculo OS

**Arquivo:** `test_fase104_integracao.py` (~400 linhas)

**Execução:**
```bash
.venv\Scripts\python.exe -m pytest test_fase104_integracao.py -v
```

**Meta:** >85% de aprovação

---

## 📅 CRONOGRAMA ESTIMADO

| Dia | Tarefas | Horas | Status |
|-----|---------|-------|--------|
| **Dia 1** | TAREFA 1 (Canvas Croqui) | 8h | ⏳ |
| **Dia 2** | TAREFA 1 (cont.) + TAREFA 9 (FASE 1/2) | 8h | ⏳ |
| **Dia 3** | TAREFA 2 (Grid Orçamento) | 8h | ⏳ |
| **Dia 4** | TAREFA 2 (cont.) + TAREFA 5 (FASE 3) | 8h | ⏳ |
| **Dia 5** | TAREFA 3 (Baixa Estoque) + TAREFA 6 (FASE 5) | 8h | ⏳ |
| **Dia 6** | TAREFA 4 (Assinatura) + TAREFA 7 (FASE 6) | 8h | ⏳ |
| **Dia 7** | TAREFA 8 (Integração Financeiro) + TAREFA 10 (Testes) | 8h | ⏳ |

**Total:** 7 dias úteis (~56 horas)

---

## 🎯 CRITÉRIOS DE SUCESSO

### Funcionalidades Obrigatórias:
- [x] Backend OS 100% funcional (JÁ COMPLETO)
- [ ] Canvas Croqui funcionando (TAREFA 1)
- [ ] Grid Orçamento com cálculos automáticos (TAREFA 2)
- [ ] Baixa automática de estoque (TAREFA 3)
- [ ] Assinatura digital (TAREFA 4)
- [ ] FASE 3 desktop completa (TAREFA 5)
- [ ] FASE 5 desktop completa (TAREFA 6)
- [ ] FASE 6 desktop completa (TAREFA 7)
- [ ] Integração Financeiro ↔ OS (TAREFA 8)
- [ ] Testes >85% aprovação (TAREFA 10)

### Métricas de Qualidade:
- **Código:** <30 lint errors por arquivo
- **Performance:** Requests <2s
- **UX:** Wizard navegável sem travamentos
- **Integração:** Dados fluem corretamente entre módulos

---

## 🔗 INTEGRAÇÕES MAPEADAS

### 1. **OS → Estoque (TAREFA 3)**
```
Finalizar OS (FASE 6)
    ↓
Ler orçamento_itens_json
    ↓
Para cada produto:
    → GET /api/v1/produtos/{id}
    → POST /api/v1/estoque/movimentacoes/
        {tipo: "SAIDA", produto_id, quantidade, motivo: "OS #123"}
    → Atualiza estoque_atual
    ↓
Log completo salvo
```

### 2. **OS → Financeiro (TAREFA 8)**
```
Clicar "Gerar Conta a Receber" (FASE 6)
    ↓
POST /api/v1/os/{id}/gerar-conta-receber
    {
        cliente_id: OS.cliente_id,
        valor: OS.valor_total,
        vencimento: data + 30 dias,
        parcelas: 1 (ou N),
        descricao: "OS #123 - Serviço XYZ"
    }
    ↓
Cria registro em contas_receber
    com ordem_servico_id vinculado
    ↓
Retorna ID da conta criada
```

### 3. **OS → Produtos (TAREFA 2/9)**
```
Grid Orçamento - Adicionar Linha
    ↓
Dialog "Buscar Produto"
    → GET /api/v1/produtos/?search=termo
    → Exibe: Código, Nome, Preço, Estoque Atual
    ↓
Usuário seleciona produto
    ↓
Grid preenche: codigo, nome, preco_unitario
    ↓
Usuário edita: quantidade, desconto
    ↓
Cálculo automático: total = (preco * qtd) - desconto
```

---

## 📦 ARQUIVOS A CRIAR/MODIFICAR

### Novos Arquivos (7):
1. `frontend/desktop/canvas_croqui.py` (~600 linhas)
2. `frontend/desktop/grid_orcamento.py` (~800 linhas)
3. `frontend/desktop/dialog_produto_selector.py` (~400 linhas)
4. `frontend/desktop/orcamento_pdf_generator.py` (~500 linhas)
5. `frontend/desktop/assinatura_digital.py` (~300 linhas)
6. `test_fase104_integracao.py` (~400 linhas)
7. `FASE_104_CONCLUSAO.md` (documentação final)

**Total Estimado:** ~3.000 linhas novas

### Arquivos Modificados (4):
1. `frontend/desktop/ordem_servico_window.py` (adicionar seções FASE 3/5/6)
2. `backend/services/ordem_servico_service.py` (adicionar integrações)
3. `backend/services/estoque_service.py` (adicionar baixa por OS)
4. `backend/services/financeiro_service.py` (adicionar criação de OS)

**Total Estimado:** ~1.500 linhas modificadas/adicionadas

---

## 🚨 RISCOS E MITIGAÇÕES

### Risco 1: Complexidade do Canvas Croqui
**Probabilidade:** MÉDIA  
**Impacto:** ALTO  

**Mitigação:**
- Usar biblioteca `tkinter.Canvas` nativa (sem deps externas)
- Features incrementais (MVP primeiro: retângulo + texto)
- Se falhar: Permitir upload de imagem estática apenas

---

### Risco 2: Performance do Grid Orçamento
**Probabilidade:** BAIXA  
**Impacto:** MÉDIO  

**Mitigação:**
- Limitar a 100 linhas no grid
- Threading para buscas de produtos
- Debounce em cálculos automáticos

---

### Risco 3: Integração Estoque ↔ OS
**Probabilidade:** MÉDIA  
**Impacto:** ALTO  

**Mitigação:**
- Transações atômicas no backend
- Rollback automático em caso de erro
- Log detalhado de todas movimentações
- Endpoint de teste separado

---

## 📈 MÉTRICAS DE PROGRESSO

### Critérios de Conclusão:

**TAREFA 1 (Canvas Croqui):**
- [ ] Canvas renderiza (weight: 10%)
- [ ] Ferramentas funcionam (weight: 40%)
- [ ] Export PNG/PDF (weight: 30%)
- [ ] Integração OS (weight: 20%)

**TAREFA 2 (Grid Orçamento):**
- [ ] Grid editável (weight: 20%)
- [ ] Busca produtos (weight: 20%)
- [ ] Cálculos automáticos (weight: 30%)
- [ ] PDF profissional (weight: 30%)

**TAREFA 3 (Baixa Estoque):**
- [ ] Endpoint funcional (weight: 30%)
- [ ] Baixa automática (weight: 40%)
- [ ] Reversão (weight: 20%)
- [ ] Log completo (weight: 10%)

**TAREFA 4 (Assinatura):**
- [ ] Canvas assinatura (weight: 50%)
- [ ] Salvar PNG (weight: 30%)
- [ ] Embedding PDF (weight: 20%)

**TAREFAS 5/6/7 (FASE 3/5/6):**
- [ ] Interface completa (weight: 50%)
- [ ] Integração backend (weight: 30%)
- [ ] Validações (weight: 20%)

**TAREFA 8 (Financeiro):**
- [ ] Endpoint funcional (weight: 40%)
- [ ] Criação automática (weight: 40%)
- [ ] Parcelamento (weight: 20%)

**TAREFA 10 (Testes):**
- [ ] Suite criada (weight: 20%)
- [ ] >85% aprovação (weight: 80%)

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

### Hoje (Dia 1):
1. ✅ Criar este plano (FASE_104_PLANO_EXECUCAO.md)
2. ⏳ Iniciar TAREFA 1: Canvas Croqui
   - Criar estrutura básica do arquivo
   - Implementar ferramentas de desenho
   - Testar rendering

### Amanhã (Dia 2):
1. Completar Canvas Croqui
2. Integrar com OS window (FASE 1)
3. Melhorias FASE 1/2 (upload fotos, seletor produtos)

---

## 📚 REFERÊNCIAS

**Documentos Relacionados:**
- `FASE_103_ANALISE_GAP_COMPLETA.md` - Gap analysis original
- `FASE_103_COLABORADORES_CONCLUIDA.md` - Padrão de wizard implementado
- `ordem_servico_window.py` - OS window atual (base para modificações)
- `backend/api/routers/ordem_servico.py` - Backend endpoints
- `GUIA_PRODUTOS_DESKTOP.md` - Padrão de produtos para reusar

**Endpoints Backend Existentes:**
- `GET /api/v1/os/` - Listar OS
- `POST /api/v1/os/` - Criar OS
- `GET /api/v1/os/{id}` - Buscar OS
- `PUT /api/v1/os/{id}` - Atualizar OS
- `DELETE /api/v1/os/{id}` - Excluir OS
- `POST /api/v1/os/{id}/avancar-fase` - Mudar fase

**Novos Endpoints Necessários:**
- `POST /api/v1/os/{id}/executar` - Finalizar execução + baixa estoque
- `POST /api/v1/os/{id}/gerar-conta-receber` - Integração financeiro

---

## ✅ CHECKLIST DE VALIDAÇÃO FINAL

**Antes de marcar FASE 104 como CONCLUÍDA:**

### Funcionalidades Core:
- [ ] Canvas Croqui funciona em todas ferramentas
- [ ] Grid Orçamento calcula corretamente
- [ ] Baixa de estoque automática funciona
- [ ] Assinatura digital salva e exibe
- [ ] FASE 3 desktop completa e funcional
- [ ] FASE 5 desktop completa e funcional
- [ ] FASE 6 desktop completa e funcional
- [ ] Conta a receber gerada automaticamente

### Integrações:
- [ ] OS → Estoque: Dados fluem corretamente
- [ ] OS → Financeiro: Vínculo funciona
- [ ] OS → Produtos: Busca e seleção ok
- [ ] Reversões funcionam (estoque/financeiro)

### Qualidade:
- [ ] <30 lint errors por arquivo novo
- [ ] Testes >85% aprovação
- [ ] Sem crashes reportados
- [ ] Performance <2s em requests

### Documentação:
- [ ] `FASE_104_CONCLUSAO.md` criado
- [ ] README atualizado
- [ ] Endpoints documentados
- [ ] Guia de uso criado

---

**Autor:** GitHub Copilot  
**Versão:** 1.0  
**Última Atualização:** 17/11/2025
