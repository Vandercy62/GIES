# 📚 Guia de Uso - Grids Especializados para Ordem de Serviço

**Sistema ERP Primotex**  
**Versão:** 1.0  
**Data:** 19/11/2025  

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Acesso aos Grids](#acesso-aos-grids)
3. [Canvas Croqui](#1-canvas-croqui)
4. [Grid Orçamento](#2-grid-orçamento)
5. [Grid Medições](#3-grid-medições)
6. [Grid Materiais](#4-grid-materiais)
7. [Grid Equipe](#5-grid-equipe)
8. [Fluxo Completo de Trabalho](#fluxo-completo-de-trabalho)
9. [Dicas e Atalhos](#dicas-e-atalhos)
10. [Solução de Problemas](#solução-de-problemas)

---

## Visão Geral

### O que são os Grids Especializados?

Os **Grids Especializados** são ferramentas integradas ao sistema de Ordem de Serviço (OS) que permitem gerenciar todos os aspectos técnicos e operacionais de um projeto de instalação:

- 🎨 **Canvas Croqui:** Desenho técnico do projeto
- 💰 **Grid Orçamento:** Criação e gestão de orçamentos detalhados
- 📏 **Grid Medições:** Registro de medidas do local
- 📦 **Grid Materiais:** Controle de aplicação de materiais
- 👥 **Grid Equipe:** Alocação de colaboradores e horas trabalhadas

### Benefícios

✅ **Centralização:** Todos os dados da OS em um só lugar  
✅ **Automação:** Cálculos automáticos de totais, áreas, horas  
✅ **Rastreabilidade:** Histórico completo de todas as operações  
✅ **Profissionalismo:** Geração de PDFs e relatórios  
✅ **Eficiência:** Redução de erros e retrabalho  

---

## Acesso aos Grids

### Pré-requisitos

1. **Login no Sistema**
   - Usuário: `admin`
   - Senha: `admin123`
   - Permissão: Operador ou superior

2. **Backend Rodando**
   - Porta: 8002
   - Status: Verificar em `/health`

### Navegação

**Caminho:** Dashboard Principal → OS Dashboard → [Selecionar Grid]

```
🏠 Dashboard
   └── 📋 OS Dashboard
       ├── 🎨 Croqui
       ├── 💰 Orçamento
       ├── 📏 Medições
       ├── 📦 Materiais
       └── 👥 Equipe
```

---

## 1. Canvas Croqui

### Descrição
Ferramenta de desenho técnico para criar croquis e plantas do projeto.

### Funcionalidades

#### Ferramentas de Desenho
- **✏️ Linha:** Desenhar linhas retas
- **⬜ Retângulo:** Desenhar retângulos
- **⭕ Círculo:** Desenhar círculos
- **📝 Texto:** Adicionar anotações
- **📐 Medida:** Inserir cotas e dimensões

#### Ferramentas de Edição
- **↩️ Desfazer:** Ctrl+Z (últimas 50 ações)
- **↪️ Refazer:** Ctrl+Y
- **🗑️ Limpar Tudo:** Apagar todo o canvas

#### Cores Disponíveis
- ⚫ Preto (padrão)
- 🔴 Vermelho
- 🔵 Azul
- 🟢 Verde
- 🟡 Amarelo

### Como Usar

#### 1. Criar Novo Croqui

```
1. Abrir OS Dashboard
2. Clicar em "🎨 Croqui"
3. Selecionar ferramenta (ex: Linha)
4. Escolher cor
5. Desenhar no canvas (clique + arraste)
6. Adicionar medidas e textos
7. Clicar "💾 Salvar Croqui"
```

#### 2. Carregar Croqui Existente

```
1. Abrir Canvas Croqui
2. Sistema carrega automaticamente se existir
3. Continuar editando normalmente
```

#### 3. Adicionar Medidas

```
1. Selecionar ferramenta "📐 Medida"
2. Clicar no ponto inicial
3. Clicar no ponto final
4. Digite a medida (ex: "2.50m")
5. Pressione Enter
```

### Dicas

💡 **Precisão:** Use zoom para desenhos detalhados  
💡 **Organização:** Use cores diferentes para cada tipo de elemento  
💡 **Anotações:** Adicione textos explicativos importantes  
💡 **Backup:** Salve frequentemente (Ctrl+S)  

---

## 2. Grid Orçamento

### Descrição
Sistema completo de criação e gestão de orçamentos com cálculo automático de valores.

### Estrutura da Tabela

| Coluna | Descrição | Editável |
|--------|-----------|----------|
| Código | Código do produto | ❌ Não |
| Produto | Nome/descrição | ❌ Não |
| Qtd | Quantidade | ✅ Sim (double-click) |
| Unidade | Unidade de medida | ❌ Não |
| Preço Unit. | Preço unitário | ✅ Sim (double-click) |
| Desconto (%) | Desconto aplicado | ✅ Sim (double-click) |
| Total | Valor total calculado | ❌ Não (auto) |

### Funcionalidades

#### Adicionar Item
1. Clicar "➕ Adicionar Item"
2. Selecionar produto no dialog
3. Informar quantidade
4. Aplicar desconto (opcional)
5. Confirmar

#### Editar Item
1. **Double-click** na célula (Qtd, Preço ou Desconto)
2. Digite novo valor
3. Pressione **Enter** para confirmar
4. Ou **Esc** para cancelar

#### Remover Item
1. Selecionar linha na tabela
2. Clicar "🗑️ Remover Item"
3. Confirmar exclusão

#### Salvar Orçamento
1. Revisar todos os itens
2. Verificar totais no rodapé
3. Clicar "💾 Salvar"
4. Sistema salva automaticamente

#### Gerar PDF
1. Clicar "📄 Gerar PDF"
2. Aguardar processamento
3. PDF salvo em: `C:\GIES\relatorios\orcamento_OS{id}.pdf`
4. Visualizar automaticamente

### Cálculos Automáticos

#### Subtotal
```
Subtotal = Σ (Quantidade × Preço Unit. × (1 - Desconto%))
```

#### Impostos (17%)
```
Impostos = Subtotal × 0.17
```

#### Total Geral
```
Total = Subtotal + Impostos
```

### Como Usar

#### Criar Orçamento Completo

```
PASSO 1: Adicionar Produtos
   ├── Clicar "➕ Adicionar Item"
   ├── Buscar produto (ex: "Forro PVC")
   ├── Selecionar da lista
   ├── Definir quantidade (ex: 50 m²)
   ├── Aplicar desconto se houver (ex: 10%)
   └── Confirmar

PASSO 2: Revisar e Ajustar
   ├── Double-click para editar valores
   ├── Verificar totais no rodapé
   └── Adicionar mais produtos se necessário

PASSO 3: Salvar e Gerar PDF
   ├── Clicar "💾 Salvar"
   ├── Aguardar confirmação
   ├── Clicar "📄 Gerar PDF"
   └── Visualizar documento
```

### Dicas

💡 **Desconto por Linha:** Cada item pode ter desconto individual  
💡 **Busca Rápida:** Digite no campo de busca do dialog  
💡 **Impostos Fixos:** 17% aplicados automaticamente  
💡 **PDF Profissional:** Inclui logo, dados da empresa e cliente  

---

## 3. Grid Medições

### Descrição
Registro e controle de todas as medidas do local de instalação.

### Estrutura da Tabela

| Coluna | Descrição |
|--------|-----------|
| Tipo | Tipo de medição (Altura, Largura, etc) |
| Medida | Valor numérico |
| Quantidade | Quantidade de vezes |
| Unidade | Unidade (m, m², m³, un) |
| Observação | Notas adicionais |

### Tipos de Medição Comuns

- 📏 **Altura:** Pé direito, altura de parede
- 📐 **Largura:** Comprimento de paredes
- 📊 **Profundidade:** Profundidade de ambientes
- 📦 **Área:** Área total em m²
- 🔢 **Volume:** Volume em m³
- 📌 **Perímetro:** Perímetro de ambientes

### Funcionalidades

#### Adicionar Medição
1. Clicar "➕ Adicionar Medição"
2. Preencher dialog:
   - Tipo (ex: Altura)
   - Medida (ex: 2.80)
   - Quantidade (ex: 1)
   - Unidade (ex: m)
   - Observação (opcional)
3. Confirmar

#### Editar Medição
1. Selecionar linha
2. Clicar "✏️ Editar"
3. Modificar campos
4. Salvar alterações

#### Remover Medição
1. Selecionar linha
2. Clicar "🗑️ Remover"
3. Confirmar exclusão

#### Cálculo Automático de Área

O sistema detecta automaticamente quando há medições de:
- **Largura** (em metros)
- **Profundidade** (em metros)

E calcula:
```
Área = Largura × Profundidade
```

**Exemplo:**
- Largura: 4.50m
- Profundidade: 6.00m
- → Sistema cria automaticamente: Área = 27.00m²

### Como Usar

#### Medir um Ambiente Completo

```
SEQUÊNCIA RECOMENDADA:

1. Altura (Pé Direito)
   - Tipo: Altura
   - Medida: 2.80
   - Unidade: m
   - Obs: "Pé direito do ambiente"

2. Largura
   - Tipo: Largura
   - Medida: 4.50
   - Unidade: m
   - Obs: "Parede norte-sul"

3. Profundidade
   - Tipo: Profundidade
   - Medida: 6.00
   - Unidade: m
   - Obs: "Parede leste-oeste"

4. Sistema calcula automaticamente:
   ✅ Área = 27.00 m²
```

### Dicas

💡 **Precisão:** Use 2 casas decimais (ex: 2.80 não 2.8)  
💡 **Unidades:** Sempre especifique a unidade correta  
💡 **Observações:** Detalhe onde foi medido  
💡 **Revisão:** Confira valores antes de salvar  

---

## 4. Grid Materiais

### Descrição
Controle completo de aplicação, devolução e perdas de materiais.

### Estrutura da Tabela

| Coluna | Descrição |
|--------|-----------|
| Código | Código do produto |
| Material | Nome do material |
| Qtd Aplicada | Quantidade usada |
| Qtd Devolvida | Quantidade devolvida ao estoque |
| Perdas | Quantidade perdida/danificada |
| Unidade | Unidade de medida |
| Observação | Notas sobre a aplicação |

### Funcionalidades

#### Aplicar Material
1. Clicar "➕ Adicionar Material"
2. Selecionar produto do estoque
3. Informar:
   - Quantidade aplicada
   - Quantidade devolvida (se houver)
   - Perdas (se houver)
   - Observação
4. Confirmar

**Sistema valida automaticamente:**
```
Qtd Aplicada + Qtd Devolvida + Perdas ≤ Estoque Disponível
```

#### Editar Aplicação
1. Selecionar linha
2. Clicar "✏️ Editar"
3. Ajustar quantidades
4. Salvar (sistema re-valida estoque)

#### Devolver Material
1. Editar aplicação existente
2. Aumentar "Qtd Devolvida"
3. Salvar
4. Estoque é atualizado automaticamente

#### Registrar Perdas
1. Editar aplicação
2. Informar "Perdas"
3. Adicionar observação explicativa
4. Salvar

### Integração com Estoque

O Grid Materiais está **100% integrado** com o sistema de estoque:

- ✅ **Validação:** Não permite aplicar mais que o disponível
- ✅ **Atualização:** Estoque é atualizado em tempo real
- ✅ **Rastreabilidade:** Histórico completo de movimentações
- ✅ **Alertas:** Avisa quando estoque está baixo

### Como Usar

#### Aplicar Material em Obra

```
EXEMPLO: Aplicar Forro PVC

1. Clicar "➕ Adicionar Material"

2. Selecionar no dialog:
   - Buscar: "Forro PVC"
   - Selecionar produto

3. Preencher quantidades:
   - Qtd Aplicada: 45 m²
   - Qtd Devolvida: 3 m² (sobrou)
   - Perdas: 2 m² (danificado)
   - Total retirado: 50 m²

4. Observação:
   "Instalação sala principal. 
    Sobra retornada ao estoque.
    Perda por corte inadequado."

5. Confirmar

RESULTADO:
   ✅ Estoque diminui 50 m²
   ✅ 45 m² registrado como aplicado
   ✅ 3 m² volta para estoque
   ✅ 2 m² registrado como perda
```

### Dicas

💡 **Precisão:** Registre valores reais, não estimados  
💡 **Devoluções:** Sempre registre sobras para controle correto  
💡 **Perdas:** Documente o motivo nas observações  
💡 **Conferência:** Valide estoque após grandes aplicações  

---

## 5. Grid Equipe

### Descrição
Alocação de colaboradores e controle de horas trabalhadas.

### Estrutura da Tabela

| Coluna | Descrição |
|--------|-----------|
| Nome | Nome do colaborador |
| Função | Cargo/função na obra |
| Data Início | Data de início do trabalho |
| Data Fim | Data de término |
| Horas Dia | Horas trabalhadas por dia |
| Dias | Total de dias trabalhados |
| Total Horas | Total calculado automaticamente |

### Funcionalidades

#### Alocar Colaborador
1. Clicar "➕ Adicionar Colaborador"
2. Selecionar do cadastro
3. Informar:
   - Função na obra (ex: Instalador, Ajudante)
   - Data início
   - Data fim (ou deixar em aberto)
   - Horas por dia
4. Confirmar

**Cálculo Automático:**
```
Dias Trabalhados = Data Fim - Data Início + 1
Total Horas = Horas/Dia × Dias Trabalhados
```

#### Editar Alocação
1. Selecionar linha
2. Clicar "✏️ Editar"
3. Ajustar datas ou horas
4. Sistema recalcula automaticamente

#### Remover da Equipe
1. Selecionar linha
2. Clicar "🗑️ Remover"
3. Confirmar

### Totalizadores (Rodapé)

O Grid Equipe exibe 4 totalizadores automáticos:

1. **👥 Total Colaboradores:** Quantidade de pessoas
2. **📅 Total Dias:** Soma de todos os dias trabalhados
3. **⏱️ Total Horas:** Soma de todas as horas
4. **💰 Custo Estimado:** (se cadastrado preço/hora)

### Como Usar

#### Montar Equipe Completa

```
EXEMPLO: Instalação de Forro

COLABORADOR 1: Líder da Equipe
   - Nome: João Silva
   - Função: Instalador Líder
   - Data Início: 20/11/2025
   - Data Fim: 27/11/2025
   - Horas/Dia: 8h
   - Sistema calcula: 8 dias × 8h = 64h

COLABORADOR 2: Instalador
   - Nome: Carlos Santos
   - Função: Instalador
   - Data Início: 20/11/2025
   - Data Fim: 27/11/2025
   - Horas/Dia: 8h
   - Sistema calcula: 8 dias × 8h = 64h

COLABORADOR 3: Ajudante
   - Nome: Pedro Costa
   - Função: Ajudante
   - Data Início: 20/11/2025
   - Data Fim: 23/11/2025
   - Horas/Dia: 6h
   - Sistema calcula: 4 dias × 6h = 24h

TOTAIS (Rodapé):
   👥 Colaboradores: 3
   📅 Total Dias: 20 dias
   ⏱️ Total Horas: 152h
   💰 Custo: R$ 4.560,00 (se R$ 30/h)
```

### Dicas

💡 **Planejamento:** Aloque equipe antes do início da obra  
💡 **Flexibilidade:** Deixe data fim em aberto se necessário  
💡 **Funções:** Use funções descritivas (ex: "Instalador Líder")  
💡 **Horas:** Considere horas extras separadamente  

---

## Fluxo Completo de Trabalho

### Sequência Recomendada

```
1️⃣ CROQUI (1º Passo)
   └─> Desenhar planta técnica do projeto
       └─> Definir layout e posicionamento
           └─> Adicionar medidas preliminares

2️⃣ MEDIÇÕES (2º Passo)
   └─> Registrar medidas reais do local
       └─> Calcular áreas e volumes
           └─> Validar com croqui

3️⃣ ORÇAMENTO (3º Passo)
   └─> Criar lista de produtos necessários
       └─> Calcular quantidades baseado nas medições
           └─> Aplicar descontos negociados
               └─> Gerar PDF para aprovação

4️⃣ MATERIAIS (4º Passo - Durante Execução)
   └─> Aplicar materiais conforme orçamento
       └─> Registrar devoluções e perdas
           └─> Manter estoque atualizado

5️⃣ EQUIPE (5º Passo - Durante Execução)
   └─> Alocar colaboradores
       └─> Controlar horas trabalhadas
           └─> Calcular custos de mão de obra
```

### Exemplo Prático Completo

**PROJETO: Instalação de Forro PVC em Escritório**

#### Dia 1: Visita Técnica

**1. Criar Croqui**
- Desenhar planta do escritório
- Marcar posição de colunas e vigas
- Indicar pontos de luz
- Salvar desenho

**2. Fazer Medições**
- Altura: 2.80m
- Largura: 5.00m
- Profundidade: 7.00m
- Área: 35.00m² (auto-calculado)

#### Dia 2: Elaboração do Orçamento

**3. Criar Orçamento**

| Item | Produto | Qtd | Preço Unit. | Desconto | Total |
|------|---------|-----|-------------|----------|-------|
| 1 | Forro PVC Branco | 38 m² | R$ 45,00 | 10% | R$ 1.539,00 |
| 2 | Perfil Alumínio | 24 m | R$ 8,50 | 5% | R$ 193,80 |
| 3 | Parafusos (caixa) | 2 un | R$ 12,00 | 0% | R$ 24,00 |

**Totais:**
- Subtotal: R$ 1.756,80
- Impostos (17%): R$ 298,66
- **Total: R$ 2.055,46**

**4. Gerar PDF e Enviar para Cliente**

#### Dia 3-5: Execução da Obra

**5. Aplicar Materiais**

| Material | Aplicado | Devolvido | Perdas | Obs |
|----------|----------|-----------|--------|-----|
| Forro PVC | 35 m² | 2 m² | 1 m² | Instalação completa |
| Perfil | 22 m | 1 m | 1 m | Cortes normais |

**6. Alocar Equipe**

| Colaborador | Função | Período | Horas/Dia | Total |
|-------------|--------|---------|-----------|-------|
| João Silva | Instalador | 3 dias | 8h | 24h |
| Carlos Santos | Ajudante | 3 dias | 8h | 24h |

**Totais: 2 colaboradores, 48h trabalhadas**

---

## Dicas e Atalhos

### Atalhos de Teclado

| Tecla | Ação | Contexto |
|-------|------|----------|
| **Ctrl+S** | Salvar | Todos os grids |
| **Ctrl+Z** | Desfazer | Canvas Croqui |
| **Ctrl+Y** | Refazer | Canvas Croqui |
| **Delete** | Remover item selecionado | Todos os grids |
| **Enter** | Confirmar edição | Edição de célula |
| **Esc** | Cancelar edição | Edição de célula |
| **F5** | Recarregar dados | Todos os grids |
| **Double-click** | Editar célula | Grid Orçamento |

### Boas Práticas

#### 📝 Documentação
- ✅ Sempre adicione observações relevantes
- ✅ Use nomenclaturas padronizadas
- ✅ Mantenha descrições claras e objetivas

#### 💾 Salvamento
- ✅ Salve frequentemente (Ctrl+S)
- ✅ Aguarde confirmação antes de fechar
- ✅ Verifique se dados foram gravados

#### 🔍 Validação
- ✅ Revise valores antes de salvar
- ✅ Confira cálculos automáticos
- ✅ Valide estoque antes de aplicar materiais

#### 📊 Relatórios
- ✅ Gere PDFs após finalizar orçamento
- ✅ Mantenha cópias dos documentos
- ✅ Envie para cliente antes de executar

---

## Solução de Problemas

### Problema: "Erro ao salvar dados"

**Causas Possíveis:**
- Backend não está rodando
- Sem conexão com banco de dados
- Timeout de autenticação

**Soluções:**
1. Verificar se backend está ativo (porta 8002)
2. Fazer logout e login novamente
3. Verificar logs do sistema
4. Contatar suporte técnico

### Problema: "Produto não encontrado no estoque"

**Causas:**
- Produto não cadastrado
- Estoque zerado
- Filtro de busca muito específico

**Soluções:**
1. Cadastrar produto em Produtos → Cadastro
2. Verificar se há estoque disponível
3. Usar termos de busca mais genéricos

### Problema: "Validação de estoque falhou"

**Causas:**
- Quantidade solicitada > estoque disponível
- Estoque bloqueado
- Produto inativo

**Soluções:**
1. Verificar quantidade disponível em Estoque
2. Reduzir quantidade aplicada
3. Fazer entrada de estoque se necessário

### Problema: "Croqui não carrega"

**Causas:**
- Arquivo corrompido
- Formato inválido
- Tamanho muito grande

**Soluções:**
1. Verificar formato do arquivo (deve ser PNG)
2. Reduzir tamanho da imagem
3. Redesenhar croqui

### Problema: "PDF não é gerado"

**Causas:**
- Orçamento vazio
- Sem permissão de gravação
- Biblioteca ReportLab com erro

**Soluções:**
1. Adicionar pelo menos 1 item ao orçamento
2. Verificar permissões da pasta `relatorios/`
3. Reinstalar dependências: `pip install reportlab`

---

## 📞 Suporte

### Contato
- **Email:** suporte@primotex.com
- **Telefone:** (XX) XXXX-XXXX
- **Horário:** Segunda a Sexta, 8h às 18h

### Documentação Adicional
- [Manual Completo do Sistema](README.md)
- [Guia de Instalação](INSTALACAO.md)
- [FAQ - Perguntas Frequentes](FAQ.md)

### Versão
- **Sistema:** ERP Primotex v9.0
- **Grids OS:** FASE 104 v1.0
- **Última Atualização:** 19/11/2025

---

**© 2025 Primotex - Forros e Divisórias Eirelli**  
**Todos os direitos reservados**
