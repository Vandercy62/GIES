# PLANO DE CORREÇÃO DE LINT - SISTEMA ERP PRIMOTEX

**Data:** 17/11/2025  
**Total de Erros:** 1774  
**Meta:** 0 erros  
**Restrição:** ZERO mudanças funcionais

---

## 📊 ANÁLISE DE ESCOPO

### Erros por Categoria

| Categoria | Quantidade | Prioridade | Arquivos Afetados |
|-----------|------------|------------|-------------------|
| **Linhas Longas (>79)** | ~1500 | 🔴 ALTA | Backend schemas (todos) |
| **Complexidade Cognitiva** | ~200 | 🟡 MÉDIA | login_tkinter.py, outros |
| **String Literals Duplicados** | ~50 | 🟢 BAIXA | login_tkinter.py, components |
| **Imports Não Usados** | ~24 | 🟢 BAIXA | Schemas, components |

### Arquivos Prioritários

1. **backend/schemas/cliente_schemas.py** - 35+ erros (line length + import)
2. **backend/schemas/fornecedor_schemas.py** - ~30 erros estimados
3. **backend/schemas/produto_schemas.py** - ~25 erros estimados
4. **backend/schemas/colaborador_schemas.py** - ~25 erros estimados
5. **backend/schemas/financeiro_schemas.py** - ~20 erros estimados
6. **backend/schemas/agendamento_schemas.py** - ~20 erros estimados
7. **backend/schemas/ordem_servico_schemas.py** - ~20 erros estimados
8. **frontend/desktop/login_tkinter.py** - 2 erros (complexity + duplicates)

---

## 🎯 ESTRATÉGIA DE CORREÇÃO

### FASE 1: Backend Schemas (Line Length) - PRIORIDADE MÁXIMA

**Padrão Identificado:**
```python
# ❌ ANTES (111 chars)
nome: str = Field(..., min_length=3, max_length=200, description="Nome completo (PF) ou Razão Social (PJ)")

# ✅ DEPOIS (quebrado em múltiplas linhas)
nome: str = Field(
    ...,
    min_length=3,
    max_length=200,
    description="Nome completo (PF) ou Razão Social (PJ)"
)
```

**Arquivos a Corrigir:**
- ✅ `backend/schemas/cliente_schemas.py` (35+ linhas)
- ⏳ `backend/schemas/fornecedor_schemas.py` (~30 linhas)
- ⏳ `backend/schemas/produto_schemas.py` (~25 linhas)
- ⏳ `backend/schemas/colaborador_schemas.py` (~25 linhas)
- ⏳ `backend/schemas/financeiro_schemas.py` (~20 linhas)
- ⏳ `backend/schemas/agendamento_schemas.py` (~20 linhas)
- ⏳ `backend/schemas/ordem_servico_schemas.py` (~20 linhas)

**Regras de Formatação:**
1. Quebrar quando Field() ultrapassar 79 caracteres
2. Um parâmetro por linha (exceto parâmetros curtos relacionados)
3. Manter indentação de 4 espaços
4. Preservar TODOS os validators (min_length, max_length, pattern, ge, le)
5. Preservar TODAS as descriptions (apenas quebrar texto)

### FASE 2: Login Module (Cognitive Complexity)

**Problema:**
- `handle_login()` tem complexidade 19 (limite 15)
- Múltiplos níveis de if/else aninhados
- Lógica de autenticação + salvamento + navegação misturados

**Solução:**
```python
# ❌ ANTES (1 método gigante)
def handle_login(self):
    # 100+ linhas de código
    if validar:
        if autenticar:
            if salvar:
                if navegar:
                    ...

# ✅ DEPOIS (refatorado)
def handle_login(self):
    if not self._validate_credentials():
        return
    
    auth_result = self._authenticate_user()
    if not auth_result:
        return
    
    self._handle_auth_success(auth_result)

def _validate_credentials(self) -> bool:
    # Validação de campos
    ...

def _authenticate_user(self) -> Optional[Dict]:
    # Chamada API
    ...

def _handle_auth_success(self, auth_result: Dict):
    # Salvar credenciais + navegar
    ...
```

**Constantes a Extrair:**
```python
# No início do arquivo
CREDENTIALS_FILE = '.primotex_credentials.json'
SESSION_EXPIRY_DAYS = 30
MIN_USERNAME_LENGTH = 3
MIN_PASSWORD_LENGTH = 6
```

### FASE 3: Imports Não Usados

**Padrão Identificado:**
```python
# ❌ ANTES
from typing import Optional, List, Dict, Any  # Any não usado
from pydantic import BaseModel, Field
import json  # Não usado

# ✅ DEPOIS
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
```

**Checklist:**
- [ ] cliente_schemas.py: remover `typing.Any`
- [ ] Verificar outros schemas com grep: `from typing import.*Any`
- [ ] Verificar imports de json/os/sys não usados

### FASE 4: F-Strings Desnecessárias

**Padrão Identificado:**
```python
# ❌ ANTES
mensagem = f"Erro ao conectar"  # Sem placeholders!
titulo = f'Aviso'

# ✅ DEPOIS
mensagem = "Erro ao conectar"
titulo = 'Aviso'
```

**Comando de Busca:**
```bash
# Buscar f-strings sem {}
grep -r "f['\"]" --include="*.py" | grep -v "{" | grep -v "#"
```

---

## 🔧 PROCEDIMENTO TÉCNICO

### Workflow de Correção

1. **Backup Automático**
   ```bash
   # Git commit antes das mudanças
   git add .
   git commit -m "Pre-lint: backup antes de correções"
   ```

2. **Correção por Arquivo**
   - Abrir arquivo no VS Code
   - Aplicar correções categoria por categoria
   - Verificar sintaxe: `python -m py_compile arquivo.py`
   - Commit: `git commit -m "lint: corrige linha longa em arquivo.py"`

3. **Validação Contínua**
   ```bash
   # Após cada arquivo corrigido
   .\.venv\Scripts\python.exe -m pylint arquivo.py
   ```

4. **Teste de Regressão**
   - Iniciar backend: `uvicorn backend.api.main:app --port 8002`
   - Testar endpoint: `curl http://127.0.0.1:8002/health`
   - Testar login API
   - Executar suite de testes

### Ferramentas de Verificação

```bash
# 1. Checagem completa de erros
get_errors()  # Via VS Code API

# 2. Pylint específico
.\.venv\Scripts\python.exe -m pylint backend/schemas/cliente_schemas.py

# 3. Verificar sintaxe Python
.\.venv\Scripts\python.exe -m py_compile arquivo.py

# 4. Black para formatação automática (se disponível)
.\.venv\Scripts\python.exe -m black --check arquivo.py
```

---

## ✅ CRITÉRIOS DE SUCESSO

### Métricas Objetivas

- [ ] **0 erros de lint** (redução de 1774 → 0)
- [ ] **100% arquivos sem linhas >79 chars** (exceto URLs/strings longas inevitáveis)
- [ ] **Complexidade <15** em todos os métodos
- [ ] **0 imports não usados**
- [ ] **0 f-strings sem placeholders**

### Testes de Regressão

- [ ] Backend inicia sem erros
- [ ] `/health` retorna 200 OK
- [ ] Login API funciona (POST `/api/v1/auth/login`)
- [ ] Dashboard abre corretamente
- [ ] Clientes/Produtos/Fornecedores abrem sem erros
- [ ] PDF generation funciona
- [ ] Suite de testes passa (>80% success rate)

---

## 📋 CHECKLIST DE EXECUÇÃO

### FASE 1: Backend Schemas
- [ ] cliente_schemas.py (35+ linhas)
- [ ] fornecedor_schemas.py (~30 linhas)
- [ ] produto_schemas.py (~25 linhas)
- [ ] colaborador_schemas.py (~25 linhas)
- [ ] financeiro_schemas.py (~20 linhas)
- [ ] agendamento_schemas.py (~20 linhas)
- [ ] ordem_servico_schemas.py (~20 linhas)
- [ ] Validar: `get_errors()` mostra 0 erros em schemas

### FASE 2: Login Module
- [ ] Extrair constantes (CREDENTIALS_FILE, etc.)
- [ ] Refatorar `handle_login()` em 4 métodos
- [ ] Reduzir complexidade <15
- [ ] Testar login funcional
- [ ] Validar: `get_errors()` mostra 0 erros em login_tkinter.py

### FASE 3: Cleanup Geral
- [ ] Remover imports não usados
- [ ] Corrigir f-strings desnecessárias
- [ ] Remover string literals duplicados
- [ ] Validar: `get_errors()` mostra <10 erros totais

### FASE 4: Validação Final
- [ ] Backend inicializa
- [ ] API funcional (/health, /docs)
- [ ] Frontend abre
- [ ] Login funciona
- [ ] Módulos navegam
- [ ] Suite de testes >80% pass
- [ ] `get_errors()` mostra 0 erros

---

## 📝 TEMPLATE DE CORREÇÃO

### Para Schemas (Line Length)

```python
# ANTES
campo: str = Field(..., min_length=3, max_length=100, description="Descrição muito longa que ultrapassa 79 caracteres")

# DEPOIS
campo: str = Field(
    ...,
    min_length=3,
    max_length=100,
    description="Descrição muito longa que ultrapassa 79 caracteres"
)
```

### Para Complexidade (Login)

```python
# ANTES
def metodo_grande(self):
    if condicao1:
        if condicao2:
            if condicao3:
                # 50 linhas
                ...

# DEPOIS
def metodo_grande(self):
    if not self._validar_entrada():
        return
    resultado = self._processar()
    self._finalizar(resultado)

def _validar_entrada(self) -> bool:
    return condicao1 and condicao2

def _processar(self):
    # Lógica extraída
    ...

def _finalizar(self, resultado):
    # Finalização extraída
    ...
```

---

## 🚀 PRÓXIMOS PASSOS

1. **Começar Fase 1** - Corrigir `cliente_schemas.py` (maior arquivo)
2. **Validar Incrementalmente** - `get_errors()` após cada arquivo
3. **Manter Log** - Documentar cada correção
4. **Testar Continuamente** - Backend + Frontend após cada batch
5. **Gerar Relatório Final** - Estatísticas antes/depois

---

**Status:** 📋 Plano Pronto  
**Próxima Ação:** Corrigir `backend/schemas/cliente_schemas.py`  
**Meta:** Sistema 100% limpo de erros de lint
