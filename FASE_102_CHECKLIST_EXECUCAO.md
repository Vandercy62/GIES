# ✅ FASE 102 - CHECKLIST DE EXECUÇÃO

**Data:** 16/11/2025  
**Versão:** 1.0  
**Estimativa Total:** 72 horas (~2 semanas)

---

## 📋 COMO USAR ESTE CHECKLIST

1. Marque cada tarefa com ✅ quando concluída
2. Use ⏳ para tarefas em progresso
3. Use ❌ para problemas/bloqueios
4. Atualize a data de conclusão de cada tarefa

---

## 🎯 PARTE 1: COLABORADORES (40 horas)

### 🔧 TAREFA 1: Revisão Backend (4h) - Estimativa: 0.5 dia
**Status:** ⏳ Não iniciado

- [ ] **1.1** Revisar `backend/models/colaborador_model.py`
  - [ ] Comparar com documento original
  - [ ] Adicionar campos faltantes (se houver)
  - [ ] Validar relacionamentos (FK Cargo, Departamento)
  - [ ] Adicionar campo `foto_path` (String, nullable)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **1.2** Revisar `backend/schemas/colaborador_schemas.py`
  - [ ] Comparar com documento original
  - [ ] Adicionar campos faltantes
  - [ ] Validações: CPF (regex), email, datas
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **1.3** Criar/Validar Endpoints API
  - [ ] `GET /api/v1/colaboradores` - Listar todos
  - [ ] `GET /api/v1/colaboradores/{id}` - Buscar por ID
  - [ ] `POST /api/v1/colaboradores` - Criar novo
  - [ ] `PUT /api/v1/colaboradores/{id}` - Atualizar
  - [ ] `DELETE /api/v1/colaboradores/{id}` - Deletar
  - [ ] `GET /api/v1/colaboradores/{id}/documentos` - Listar documentos
  - [ ] `POST /api/v1/colaboradores/{id}/documentos` - Adicionar documento
  - [ ] `GET /api/v1/colaboradores/alertas-expiracao` - Docs vencidos/próximos
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **1.4** Tabelas Auxiliares
  - [ ] Validar tabela `cargos` (ou criar se não existir)
  - [ ] Validar tabela `departamentos` (ou criar se não existir)
  - [ ] Enum/tabela `tipo_contrato` (CLT, PJ, Temporário, Estágio)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **1.5** Testes Backend
  - [ ] Testes unitários endpoints (pytest)
  - [ ] Testar CRUD completo
  - [ ] Testar validações (CPF, email, etc)
  - [ ] **Taxa de sucesso esperada:** > 95%
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 1 COMPLETA:** [ ] Data: _____/_____/2025

---

### 🖥️ TAREFA 2: Desktop Wizard - Estrutura (8h) - Estimativa: 1 dia
**Status:** ⏳ Não iniciado

- [ ] **2.1** Criar arquivo `frontend/desktop/colaboradores_wizard.py`
  - [ ] Classe principal `ColaboradoresWizard(tk.Toplevel)` ou `QDialog`
  - [ ] Import de dependências (tkinter, requests, threading, etc)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **2.2** Implementar estrutura 4 abas
  - [ ] `QTabWidget` ou `ttk.Notebook`
  - [ ] Aba 1: Dados Pessoais
  - [ ] Aba 2: Dados Profissionais
  - [ ] Aba 3: Documentos
  - [ ] Aba 4: Observações
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **2.3** Layout Responsivo
  - [ ] Grid system (QGridLayout ou grid())
  - [ ] Tamanho mínimo 1024x768
  - [ ] Scrollbars quando necessário
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **2.4** Navegação
  - [ ] Botões: Anterior | Próximo | Salvar | Cancelar
  - [ ] Lógica de navegação entre abas
  - [ ] Confirmação ao cancelar (MessageBox)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **2.5** Validação em Tempo Real
  - [ ] Campos obrigatórios com *
  - [ ] Highlight de erros (borda vermelha)
  - [ ] Mensagens de erro inline
  - [ ] Bloquear navegação se aba inválida
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **2.6** Integração Auth Middleware
  - [ ] Import `auth_middleware.py`
  - [ ] Decorator `@require_login()`
  - [ ] `get_token_for_api()` para headers
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 2 COMPLETA:** [ ] Data: _____/_____/2025

---

### 👤 TAREFA 3: Aba 1 - Dados Pessoais (6h) - Estimativa: 0.75 dia
**Status:** ⏳ Não iniciado

- [ ] **3.1** Campos Identificação
  - [ ] Nome completo (Entry, obrigatório)
  - [ ] CPF (Entry + validação em tempo real)
  - [ ] RG (Entry)
  - [ ] Data nascimento (DatePicker/Entry com máscara)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **3.2** Campos Pessoais
  - [ ] Estado civil (ComboBox: Solteiro, Casado, Divorciado, Viúvo)
  - [ ] Sexo (RadioButton: Masculino, Feminino, Outro)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **3.3** Endereço
  - [ ] CEP (Entry + máscara XXXXX-XXX)
  - [ ] Botão "Buscar CEP" (ViaCEP API)
  - [ ] Logradouro, Número, Complemento
  - [ ] Bairro, Cidade, Estado
  - [ ] Preenchimento automático após busca CEP
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **3.4** Contatos
  - [ ] Telefone fixo (Entry + máscara (XX) XXXX-XXXX)
  - [ ] Celular (Entry + máscara (XX) XXXXX-XXXX)
  - [ ] Email (Entry + validação regex)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **3.5** Widget Foto 3x4 ⭐
  - [ ] Frame dedicado (200x200px)
  - [ ] Preview circular ou quadrado
  - [ ] Botão "Upload Foto" (FileDialog .jpg/.png)
  - [ ] Botão "Capturar Webcam" (OpenCV ou PIL)
  - [ ] Botão "Remover Foto"
  - [ ] Salvar em `assets/colaboradores/fotos/{id}.jpg`
  - [ ] Placeholder se sem foto
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **3.6** Validações Aba 1
  - [ ] CPF válido (11 dígitos + algoritmo validação)
  - [ ] Email válido (regex)
  - [ ] Data nascimento > 18 anos
  - [ ] Campos obrigatórios preenchidos
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 3 COMPLETA:** [ ] Data: _____/_____/2025

---

### 💼 TAREFA 4: Aba 2 - Dados Profissionais (4h) - Estimativa: 0.5 dia
**Status:** ⏳ Não iniciado

- [ ] **4.1** Campos Funcionais
  - [ ] Cargo (ComboBox populado da API `/api/v1/cargos`)
  - [ ] Departamento (ComboBox populado da API `/api/v1/departamentos`)
  - [ ] Data admissão (DatePicker)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **4.2** Campos Financeiros
  - [ ] Salário (Entry + formatação R$ 0.000,00)
  - [ ] Tipo contrato (ComboBox: CLT, PJ, Temporário, Estágio, Aprendiz)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **4.3** Campos Status
  - [ ] Status (ComboBox: Ativo, Inativo, Férias, Afastado)
  - [ ] Jornada trabalho (Entry - ex: "44h semanais")
  - [ ] Responsável direto (ComboBox populado de colaboradores ativos)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **4.4** Populamento Combos (Threading)
  - [ ] Thread para buscar cargos
  - [ ] Thread para buscar departamentos
  - [ ] Thread para buscar colaboradores (responsável)
  - [ ] Loading indicator durante busca
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **4.5** Validações Aba 2
  - [ ] Cargo selecionado (obrigatório)
  - [ ] Departamento selecionado (obrigatório)
  - [ ] Data admissão < hoje
  - [ ] Salário > 0
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 4 COMPLETA:** [ ] Data: _____/_____/2025

---

### 📄 TAREFA 5: Aba 3 - Documentos ⭐ CRÍTICO (10h) - Estimativa: 1.25 dia
**Status:** ⏳ Não iniciado

- [ ] **5.1** TreeView/TableWidget Documentos
  - [ ] Colunas: Tipo | Número | Emissão | **Validade** | Status | Ações
  - [ ] Ordenação clicável nas colunas
  - [ ] Seleção de linha
  - [ ] Ícone ⚠️ para docs vencidos/próximos
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **5.2** Botões CRUD Documentos
  - [ ] Botão "Adicionar Documento"
  - [ ] Botão "Editar Documento" (linha selecionada)
  - [ ] Botão "Excluir Documento" (confirmação)
  - [ ] Botão "Visualizar Anexo" (abrir PDF/imagem)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **5.3** Dialog "Adicionar/Editar Documento"
  - [ ] Tipo documento (ComboBox: CNH, ASO, Atestado, Certidão, NR10, etc)
  - [ ] Número documento (Entry)
  - [ ] Data emissão (DatePicker)
  - [ ] **Data validade (DatePicker) ⭐ OBRIGATÓRIO**
  - [ ] Upload anexo (FileDialog .pdf/.jpg/.png)
  - [ ] Observações (TextEdit)
  - [ ] Botões: Salvar | Cancelar
  - [ ] Salvar anexo em `assets/colaboradores/documentos/{id}_{tipo}.{ext}`
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **5.4** Sistema de Alertas Visuais (Cores) ⭐⭐⭐
  - [ ] **Verde (🟢):** Validade > 30 dias
  - [ ] **Amarelo (🟡):** Validade entre 15-30 dias
  - [ ] **Laranja (🟠):** Validade entre 1-14 dias
  - [ ] **Vermelho (🔴):** Vencido (validade < hoje)
  - [ ] Aplicar cor na linha inteira do TreeView
  - [ ] Lógica de cálculo: `dias_restantes = (validade - hoje).days`
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **5.5** Dashboard de Alertas (dentro da aba) ⭐⭐
  - [ ] Frame no topo da aba
  - [ ] Badge: "⚠️ 3 documentos vencidos | 🟡 5 próximos de vencer"
  - [ ] Contadores dinâmicos (atualizam ao adicionar/remover doc)
  - [ ] Botão "Ver todos os alertas" → Dialog com lista filtrada
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **5.6** Dialog "Todos os Alertas"
  - [ ] TreeView apenas de docs vencidos/próximos
  - [ ] Abas: Vencidos | Próximos (15-30d) | Urgentes (1-14d)
  - [ ] Botão "Ir para documento" (seleciona na aba principal)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **5.7** Visualização de Anexos
  - [ ] Se PDF: abrir com app padrão sistema (subprocess)
  - [ ] Se imagem: mostrar em dialog interno (PIL/QPixmap)
  - [ ] Botão "Download" (salvar em local escolhido)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **5.8** Integração API Documentos
  - [ ] `GET /api/v1/colaboradores/{id}/documentos` (listar)
  - [ ] `POST /api/v1/colaboradores/{id}/documentos` (adicionar)
  - [ ] `PUT /api/v1/colaboradores/documentos/{doc_id}` (editar)
  - [ ] `DELETE /api/v1/colaboradores/documentos/{doc_id}` (deletar)
  - [ ] Threading para todas chamadas
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 5 COMPLETA:** [ ] Data: _____/_____/2025

---

### 📝 TAREFA 6: Aba 4 - Observações (4h) - Estimativa: 0.5 dia
**Status:** ⏳ Não iniciado

- [ ] **6.1** Observações Gerais
  - [ ] TextEdit multilinha (altura ~100px)
  - [ ] Contador de caracteres (opcional)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **6.2** Histórico Avaliações de Desempenho
  - [ ] TreeView: Data | Nota (1-5 ⭐) | Comentários
  - [ ] Botão "Adicionar Avaliação"
  - [ ] Dialog: Data (DatePicker), Nota (SpinBox 1-5), Comentários (TextEdit)
  - [ ] Botão "Editar" | "Excluir"
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **6.3** Histórico Férias
  - [ ] TreeView: Data Início | Data Fim | Dias | Observações
  - [ ] Botão "Adicionar Período de Férias"
  - [ ] Dialog: Data início, Data fim (auto-calcula dias), Obs
  - [ ] Botão "Editar" | "Excluir"
  - [ ] **Cálculo saldo dias:** Label "Saldo: XX dias disponíveis"
  - [ ] Lógica: 30 dias/ano - dias já tirados
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **6.4** Anexos Diversos
  - [ ] TreeView: Nome Arquivo | Tipo | Tamanho | Data Upload
  - [ ] Botão "Upload Arquivo" (múltiplos)
  - [ ] Botão "Visualizar" | "Download" | "Excluir"
  - [ ] Salvar em `assets/colaboradores/anexos/{id}/`
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 6 COMPLETA:** [ ] Data: _____/_____/2025

---

### 🔗 TAREFA 7: Integração Dashboard (2h) - Estimativa: 0.25 dia
**Status:** ⏳ Não iniciado

- [ ] **7.1** Atualizar `dashboard_principal.py`
  - [ ] Adicionar botão "👥 Colaboradores"
  - [ ] Click → Abrir `ColaboradoresWizard()`
  - [ ] Posição: Área de navegação rápida
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **7.2** Widget de Alertas no Dashboard
  - [ ] Frame/Card no dashboard
  - [ ] Texto: "⚠️ 3 documentos de colaboradores vencidos"
  - [ ] Botão "Ver detalhes"
  - [ ] Click → Abrir wizard na Aba 3 (Documentos)
  - [ ] Endpoint API: `GET /api/v1/colaboradores/alertas-expiracao`
  - [ ] Atualização automática (timer 60s ou botão refresh)
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 7 COMPLETA:** [ ] Data: _____/_____/2025

---

### 📄 TAREFA 8: PDF Ficha Colaborador (4h) - Estimativa: 0.5 dia
**Status:** ⏳ Não iniciado

- [ ] **8.1** Criar arquivo `frontend/desktop/colaborador_ficha_pdf.py`
  - [ ] Import ReportLab (canvas, lib.pagesizes, etc)
  - [ ] Função `gerar_ficha_colaborador(colaborador_id, filepath)`
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **8.2** Template PDF (ReportLab)
  - [ ] **Header:** Logo empresa (se disponível) + Título "FICHA DE COLABORADOR"
  - [ ] **Foto 3x4:** Topo direito (se existir)
  - [ ] **Seção 1 - Dados Pessoais:**
    - Nome, CPF, RG, Data Nascimento
    - Estado Civil, Sexo
    - Endereço completo
    - Telefones, Email
  - [ ] **Seção 2 - Dados Profissionais:**
    - Cargo, Departamento
    - Data Admissão, Tipo Contrato
    - Salário, Jornada, Status
    - Responsável Direto
  - [ ] **Seção 3 - Documentos (Tabela):**
    - Colunas: Tipo | Número | Emissão | Validade | Status
    - Cores nas linhas (verde/amarelo/laranja/vermelho)
  - [ ] **Seção 4 - Avaliações:**
    - Tabela: Data | Nota | Comentários
  - [ ] **Seção 5 - Férias:**
    - Tabela: Período | Dias
    - Saldo disponível
  - [ ] **Footer:** Data geração, Usuário gerador
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **8.3** Botão "Imprimir Ficha" no Wizard
  - [ ] Botão no rodapé do wizard
  - [ ] Click → Dialog "Salvar PDF"
  - [ ] Gerar PDF em thread separada
  - [ ] Loading indicator
  - [ ] Mensagem sucesso + opção "Abrir PDF"
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 8 COMPLETA:** [ ] Data: _____/_____/2025

---

### 🧪 TAREFA 9: Testes Desktop Colaboradores (4h) - Estimativa: 0.5 dia
**Status:** ⏳ Não iniciado

- [ ] **9.1** Criar `frontend/desktop/test_colaboradores_wizard.py`
  - [ ] Import unittest ou pytest
  - [ ] Setup/teardown fixtures
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **9.2** Testes Aba 1 (Dados Pessoais)
  - [ ] Test: Criação colaborador completo
  - [ ] Test: Validação CPF inválido
  - [ ] Test: Validação email inválido
  - [ ] Test: Busca CEP (mock API)
  - [ ] Test: Upload foto
  - [ ] Test: Captura webcam (mock)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **9.3** Testes Aba 2 (Profissionais)
  - [ ] Test: Populamento combos (mock API)
  - [ ] Test: Validação salário < 0
  - [ ] Test: Data admissão futura
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **9.4** Testes Aba 3 (Documentos) ⭐
  - [ ] Test: Adicionar documento
  - [ ] Test: Editar documento
  - [ ] Test: Excluir documento
  - [ ] Test: **Sistema de alertas (cores corretas)**
  - [ ] Test: Dashboard de alertas (contadores)
  - [ ] Test: Docs vencidos aparecem em vermelho
  - [ ] Test: Docs próximos (15d) em amarelo
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **9.5** Testes Aba 4 (Observações)
  - [ ] Test: Adicionar avaliação
  - [ ] Test: Adicionar período de férias
  - [ ] Test: **Cálculo saldo de férias correto**
  - [ ] Test: Upload anexo
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **9.6** Testes Integração API
  - [ ] Test: CRUD completo (create, read, update, delete)
  - [ ] Test: Endpoint alertas expiração
  - [ ] Test: Upload documentos (mock)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **9.7** Testes PDF
  - [ ] Test: Geração de PDF completo
  - [ ] Test: PDF sem foto (placeholder)
  - [ ] Test: PDF com documentos (cores corretas)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **9.8** Executar Suite de Testes
  - [ ] Executar: `pytest test_colaboradores_wizard.py -v`
  - [ ] **Meta:** Taxa de sucesso > 90% (mínimo 27/30 tests)
  - [ ] Corrigir falhas encontradas
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 9 COMPLETA:** [ ] Data: _____/_____/2025

---

## ✅ PARTE 1 COMPLETA: COLABORADORES
**Data Conclusão:** _____/_____/2025  
**Total de Horas:** 40h  
**Taxa de Sucesso Testes:** _____%

---

## 🎯 PARTE 2: PRODUTOS E SERVIÇOS (28 horas)

### 📦 TAREFA 10: Migrar para Wizard (6h) - Estimativa: 0.75 dia
**Status:** ⏳ Não iniciado

- [ ] **10.1** Criar `frontend/desktop/produtos_wizard.py`
  - [ ] Copiar código de `produtos_window_completo.py` (933 linhas)
  - [ ] Renomear classe para `ProdutosWizard`
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **10.2** Converter para Estrutura 4 Abas
  - [ ] Aba 1: Lista de Produtos (manter atual)
  - [ ] Aba 2: Dados Básicos (manter formulário atual)
  - [ ] Aba 3: Fotos e Código de Barras ⭐ NOVO
  - [ ] Aba 4: Observações e Fornecedores ⭐ NOVO
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **10.3** Manter Funcionalidades Existentes
  - [ ] Busca em tempo real (Aba 1)
  - [ ] Filtros categoria/status (Aba 1)
  - [ ] Threading para API calls
  - [ ] SessionManager integrado
  - [ ] Validações campos (Aba 2)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **10.4** Limpeza de Código
  - [ ] Remover código duplicado
  - [ ] Adicionar docstrings
  - [ ] Lint: 0 erros
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 10 COMPLETA:** [ ] Data: _____/_____/2025

---

### 📸 TAREFA 11: Aba 3 - Fotos e Código de Barras ⭐ (12h) - Estimativa: 1.5 dia
**Status:** ⏳ Não iniciado

**SUB-TAREFA 11A: Widget de Galeria de Fotos (8h)**

- [ ] **11A.1** Estrutura Grid 2x2
  - [ ] Frame principal de galeria
  - [ ] Layout grid 2 colunas x 2 linhas
  - [ ] 4 slots de foto (200x200px cada)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11A.2** Slot de Foto Individual
  - [ ] Frame com borda
  - [ ] Label para preview imagem
  - [ ] Checkbox "Foto Principal" (apenas 1 marcado)
  - [ ] Botão "Remover" (× no canto)
  - [ ] Placeholder quando vazio (ícone 📷)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11A.3** Upload de Foto
  - [ ] Botão "Upload Foto"
  - [ ] FileDialog (.jpg, .png, .jpeg)
  - [ ] Redimensionar para 800x800px (manter aspecto)
  - [ ] Salvar em `assets/produtos/fotos/{id}/foto_{1-4}.jpg`
  - [ ] Atualizar preview no slot
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11A.4** Captura Webcam ⭐
  - [ ] Instalar/verificar OpenCV: `pip install opencv-python`
  - [ ] Botão "Capturar Webcam"
  - [ ] Abrir dialog com preview da webcam
  - [ ] Botão "Tirar Foto" (captura frame)
  - [ ] Botão "Cancelar" (fecha webcam)
  - [ ] Salvar foto capturada no próximo slot vazio
  - [ ] Fechar webcam ao sair
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11A.5** Lightbox (Preview Ampliado)
  - [ ] Click na foto → Abrir dialog fullscreen
  - [ ] Imagem centralizada (800x800px ou maior)
  - [ ] Botões: ← | → (navegar fotos) | ✕ (fechar)
  - [ ] Fundo escuro (80% opaco)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11A.6** Gestão de Foto Principal
  - [ ] Apenas 1 checkbox marcado por vez
  - [ ] Marcar/desmarcar automático
  - [ ] Salvar no backend: campo `foto_principal` (1-4)
  - [ ] **Data conclusão:** _____/_____/2025

**SUB-TAREFA 11B: Widget de Código de Barras (4h)**

- [ ] **11B.1** Campo Código de Barras
  - [ ] Label "Código de Barras"
  - [ ] Entry (largura ~200px)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11B.2** Geração de Código (Integração)
  - [ ] Botão "Gerar Código"
  - [ ] Integrar com `codigo_barras_window.py` (importar função)
  - [ ] Dialog: Escolher formato (EAN13, Code128, EAN8, Code39, UPCA)
  - [ ] Opção: Gerar automático ou manual
  - [ ] Preencher campo Entry
  - [ ] Gerar imagem PNG → `assets/produtos/barcodes/{id}.png`
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11B.3** Preview do Barcode
  - [ ] Label com imagem do barcode (300x100px)
  - [ ] Atualizar ao gerar novo código
  - [ ] Placeholder se sem código
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **11B.4** Impressão de Etiqueta
  - [ ] Botão "Imprimir Etiqueta"
  - [ ] Gerar PDF com barcode + nome produto + preço
  - [ ] Dialog "Salvar PDF" ou imprimir direto
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 11 COMPLETA:** [ ] Data: _____/_____/2025

---

### 🏭 TAREFA 12: Aba 4 - Observações e Fornecedores (6h) - Estimativa: 0.75 dia
**Status:** ⏳ Não iniciado

- [ ] **12.1** Observações Gerais
  - [ ] TextEdit multilinha (altura ~80px)
  - [ ] Contador de caracteres (opcional)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **12.2** Especificações Técnicas
  - [ ] JSON editor ou key-value pairs
  - [ ] Botão "Adicionar Especificação"
  - [ ] Dialog: Chave (ex: "Peso") | Valor (ex: "2.5kg")
  - [ ] TreeView: Chave | Valor | Botões (Editar/Excluir)
  - [ ] Salvar como JSON no backend
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **12.3** Fornecedor Principal
  - [ ] ComboBox populado da API `/api/v1/fornecedores`
  - [ ] Exibir: Nome | CNPJ | Telefone
  - [ ] Threading para buscar fornecedores
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **12.4** Fornecedores Alternativos ⭐
  - [ ] TreeView: Prioridade | Fornecedor | Ações
  - [ ] Botão "Adicionar Fornecedor Alternativo"
  - [ ] Dialog: Selecionar fornecedor (combo) + Prioridade (spinbox)
  - [ ] Botão "Remover" (linha selecionada)
  - [ ] **Drag-and-Drop para Reordenar:**
    - [ ] Arrastar linha para cima/baixo
    - [ ] Atualizar prioridade automaticamente (1, 2, 3...)
    - [ ] Salvar nova ordem no backend
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **12.5** Backend - Tabela `produto_fornecedor`
  - [ ] Verificar se existe (many-to-many)
  - [ ] Criar se não existir:
    - `id`, `produto_id` (FK), `fornecedor_id` (FK), `prioridade` (Int)
  - [ ] Endpoint `PUT /api/v1/produtos/{id}/fornecedores` (salvar lista)
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 12 COMPLETA:** [ ] Data: _____/_____/2025

---

### 🔗 TAREFA 13: Integração Dashboard Produtos (2h) - Estimativa: 0.25 dia
**Status:** ⏳ Não iniciado

- [ ] **13.1** Atualizar `dashboard_principal.py`
  - [ ] Alterar botão "📦 Produtos"
  - [ ] Abrir `ProdutosWizard()` (novo) em vez de `produtos_window_completo.py`
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **13.2** Widget de Alertas no Dashboard
  - [ ] Frame/Card no dashboard
  - [ ] Texto: "⚠️ 5 produtos sem foto | 3 produtos sem barcode"
  - [ ] Endpoint API: `GET /api/v1/produtos/alertas` (criar se não existir)
  - [ ] Botão "Ver detalhes" → Abrir wizard filtrado
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 13 COMPLETA:** [ ] Data: _____/_____/2025

---

### 📷 TAREFA 14: Leitor Barcode - Implementação ⭐ (4h) - Estimativa: 0.5 dia
**Status:** ⏳ Não iniciado

- [ ] **14.1** Instalar Dependências
  - [ ] `pip install opencv-python` (se já não instalado)
  - [ ] `pip install pyzbar` (decodificador de barcode)
  - [ ] Testar imports: `import cv2`, `from pyzbar import pyzbar`
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **14.2** Criar `frontend/desktop/barcode_reader.py`
  - [ ] Classe `BarcodeReader`
  - [ ] Método `read_from_webcam()` (retorna código ou None)
  - [ ] Método `read_from_serial()` (USB scanner - opcional)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **14.3** Método `read_from_webcam()` ⭐
  - [ ] Abrir camera: `cv2.VideoCapture(0)`
  - [ ] Loop captura frames (max 30 segundos)
  - [ ] Detectar barcode em cada frame: `pyzbar.decode(frame)`
  - [ ] Se detectado: retornar código + fechar camera
  - [ ] Dialog de preview (mostrar camera ao vivo)
  - [ ] Botão "Cancelar" (sair do loop)
  - [ ] Fechar camera ao terminar
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **14.4** Método `read_from_serial()` (USB Scanner)
  - [ ] Listener de teclado (USB scanner simula input)
  - [ ] Timeout 5 segundos
  - [ ] Capturar string digitada
  - [ ] Retornar código
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **14.5** Integrar no Wizard (Aba 3)
  - [ ] Botão "Ler Barcode Webcam"
  - [ ] Click → Chamar `BarcodeReader().read_from_webcam()`
  - [ ] Loading indicator "Posicione o código de barras na frente da webcam..."
  - [ ] Preencher campo Entry com código lido
  - [ ] Mensagem sucesso ou erro
  - [ ] Botão "Ler Scanner USB"
  - [ ] Click → Chamar `BarcodeReader().read_from_serial()`
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 14 COMPLETA:** [ ] Data: _____/_____/2025

---

### 🧪 TAREFA 15: Testes Desktop Produtos (2h) - Estimativa: 0.25 dia
**Status:** ⏳ Não iniciado

- [ ] **15.1** Atualizar `test_produtos_wizard.py` (criar se não existir)
  - [ ] Import unittest ou pytest
  - [ ] Setup/teardown fixtures
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **15.2** Testes Aba 1-2 (Já Existentes)
  - [ ] Test: Busca em tempo real
  - [ ] Test: Filtros categoria/status
  - [ ] Test: Criação produto completo
  - [ ] Test: Validações campos
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **15.3** Testes Aba 3 (Fotos + Barcode) ⭐
  - [ ] Test: Upload de foto
  - [ ] Test: Captura webcam (mock camera)
  - [ ] Test: Seleção de foto principal
  - [ ] Test: Lightbox (abrir/fechar)
  - [ ] Test: Geração de código de barras
  - [ ] Test: Leitura barcode webcam (mock)
  - [ ] Test: Preview barcode
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **15.4** Testes Aba 4 (Fornecedores)
  - [ ] Test: Adicionar fornecedor alternativo
  - [ ] Test: Reordenar fornecedores (prioridade)
  - [ ] Test: Remover fornecedor
  - [ ] Test: Especificações técnicas (JSON)
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **15.5** Executar Suite de Testes
  - [ ] Executar: `pytest test_produtos_wizard.py -v`
  - [ ] **Meta:** Taxa de sucesso > 90% (mínimo 18/20 tests)
  - [ ] Corrigir falhas encontradas
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 15 COMPLETA:** [ ] Data: _____/_____/2025

---

## ✅ PARTE 2 COMPLETA: PRODUTOS
**Data Conclusão:** _____/_____/2025  
**Total de Horas:** 28h  
**Taxa de Sucesso Testes:** _____%

---

## 📚 DOCUMENTAÇÃO FINAL (4 horas)

### 📄 TAREFA 16: Documentação (4h) - Estimativa: 0.5 dia
**Status:** ⏳ Não iniciado

- [ ] **16.1** Criar `FASE_102_RELATORIO_FINAL.md`
  - [ ] Resumo executivo
  - [ ] Estatísticas (linhas de código, arquivos, testes)
  - [ ] Funcionalidades implementadas
  - [ ] Screenshots (opcional)
  - [ ] Problemas encontrados e soluções
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **16.2** Criar `GUIA_COLABORADORES_DESKTOP.md`
  - [ ] Como acessar o módulo
  - [ ] Como adicionar colaborador
  - [ ] Como usar sistema de alertas de documentos
  - [ ] Como gerar PDF da ficha
  - [ ] Screenshots de cada aba
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **16.3** Atualizar `GUIA_PRODUTOS_WIZARD.md`
  - [ ] Adicionar seção "Galeria de Fotos"
  - [ ] Adicionar seção "Leitor de Barcode"
  - [ ] Adicionar seção "Fornecedores Alternativos"
  - [ ] Screenshots das novas funcionalidades
  - [ ] **Data conclusão:** _____/_____/2025

- [ ] **16.4** Atualizar `.github/copilot-instructions.md`
  - [ ] Adicionar FASE 102 no histórico
  - [ ] Atualizar status dos módulos
  - [ ] Adicionar novos arquivos críticos
  - [ ] Atualizar estatísticas (linhas, arquivos)
  - [ ] **Data conclusão:** _____/_____/2025

**✅ TAREFA 16 COMPLETA:** [ ] Data: _____/_____/2025

---

## ✅ FASE 102 - VALIDAÇÃO FINAL

### 📊 CHECKLIST DE QUALIDADE

- [ ] **Compilação**
  - [ ] `python -m py_compile backend/models/*.py` → OK
  - [ ] `python -m py_compile backend/schemas/*.py` → OK
  - [ ] `python -m py_compile frontend/desktop/*.py` → OK
  - [ ] **Data validação:** _____/_____/2025

- [ ] **Lint (0 erros críticos)**
  - [ ] `get_errors()` → 0 erros ou < 10 warnings
  - [ ] Todos os arquivos novos: 0 erros
  - [ ] **Data validação:** _____/_____/2025

- [ ] **Backend Operacional**
  - [ ] Servidor inicia sem erros: `uvicorn backend.api.main:app --host 127.0.0.1 --port 8002`
  - [ ] Health check: `curl http://127.0.0.1:8002/health` → OK
  - [ ] Docs acessíveis: `http://127.0.0.1:8002/docs`
  - [ ] **Data validação:** _____/_____/2025

- [ ] **Testes Automatizados**
  - [ ] Colaboradores: Taxa sucesso > 90% (____/30 tests passando)
  - [ ] Produtos: Taxa sucesso > 90% (____/20 tests passando)
  - [ ] **Total:** ____/50 tests passando (____%)
  - [ ] **Data validação:** _____/_____/2025

- [ ] **Funcionalidades Desktop**
  - [ ] Colaboradores wizard abre sem erros
  - [ ] Todas 4 abas navegáveis
  - [ ] Sistema de alertas funcionando
  - [ ] PDF gerado com sucesso
  - [ ] Produtos wizard abre sem erros
  - [ ] Galeria de fotos funcional
  - [ ] Leitor de barcode funcional (webcam)
  - [ ] Fornecedores alternativos salvam corretamente
  - [ ] **Data validação:** _____/_____/2025

- [ ] **Integração API**
  - [ ] CRUD colaboradores (create/read/update/delete) → OK
  - [ ] Endpoint alertas documentos → OK
  - [ ] Upload fotos produtos → OK
  - [ ] Salvar fornecedores alternativos → OK
  - [ ] **Data validação:** _____/_____/2025

- [ ] **Nenhuma Funcionalidade Quebrada**
  - [ ] Login funciona
  - [ ] Dashboard abre
  - [ ] Clientes wizard funciona (FASE 100)
  - [ ] Fornecedores wizard funciona (FASE 101)
  - [ ] Módulos existentes não afetados
  - [ ] **Data validação:** _____/_____/2025

### 📄 DOCUMENTAÇÃO COMPLETA

- [ ] `FASE_102_ANALISE_GAP_E_PLANO.md` ✅ (já criado)
- [ ] `FASE_102_RESUMO_EXECUTIVO.md` ✅ (já criado)
- [ ] `FASE_102_COMPARACAO_VISUAL.md` ✅ (já criado)
- [ ] `FASE_102_RELATORIO_FINAL.md` ⏳ (criar ao final)
- [ ] `GUIA_COLABORADORES_DESKTOP.md` ⏳ (criar ao final)
- [ ] `GUIA_PRODUTOS_WIZARD.md` ⏳ (atualizar ao final)
- [ ] `.github/copilot-instructions.md` ⏳ (atualizar ao final)

---

## ✅ APROVAÇÃO FINAL FASE 102

**Critérios de Aprovação (TODOS devem ser ✅):**

- [ ] ✅ Colaboradores: 4 abas funcionando (100%)
- [ ] ✅ Sistema alertas documentos implementado
- [ ] ✅ PDF ficha colaborador gerado corretamente
- [ ] ✅ Produtos: 4 abas funcionando (100%)
- [ ] ✅ Galeria 4 fotos + captura webcam
- [ ] ✅ Leitor barcode (webcam + USB)
- [ ] ✅ Fornecedores alternativos ordenáveis
- [ ] ✅ 50+ testes (taxa > 90%)
- [ ] ✅ 0 erros de lint críticos
- [ ] ✅ Backend operacional
- [ ] ✅ Nenhuma funcionalidade quebrada
- [ ] ✅ Documentação completa (7 arquivos)

---

## 🎉 FASE 102 CONCLUÍDA!

**Data Conclusão:** _____/_____/2025  
**Total de Horas:** _____ horas  
**Linhas de Código Adicionadas:** _____  
**Arquivos Criados/Modificados:** _____  
**Taxa de Sucesso Testes:** _____%

**Assinatura Desenvolvedor:** _________________________

**Próxima Fase:** 🎯 **FASE 103 - OS Desktop Completo** (60h / 1.5 semanas)

---

**Documento gerado em:** 16/11/2025  
**Autor:** GitHub Copilot  
**Referência:** `FASE_102_ANALISE_GAP_E_PLANO.md`

