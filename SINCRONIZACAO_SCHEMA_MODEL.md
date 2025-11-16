# 🔄 Sincronização Schema ↔ Model - Ordem de Serviço

**Data:** 15/11/2025  
**Objetivo:** Identificar incompatibilidades entre schemas Pydantic e modelos SQLAlchemy

---

## 📊 **COMPARAÇÃO DE CAMPOS**

### **Schema: OrdemServicoCreate** (backend/schemas/ordem_servico_schemas.py)
```python
class OrdemServicoBase(BaseModel):
    numero_os: str
    cliente_id: int
    titulo: str                    # ❌ NÃO EXISTE NO MODELO
    descricao: str                 # ❌ NÃO EXISTE NO MODELO
    tipo_servico: TipoOS
    prioridade: PrioridadeOS
    endereco_servico: str          # ❌ Modelo usa: endereco_execucao
    cep_servico: str               # ❌ Modelo usa: cep_execucao
    cidade_servico: str            # ❌ Modelo usa: cidade_execucao
    estado_servico: str            # ❌ Modelo usa: estado_execucao
    data_solicitacao: datetime     # ❌ Modelo usa: data_abertura
    data_prazo: datetime           # ❌ Modelo usa: data_prevista_conclusao
    valor_estimado: Decimal        # ❌ Modelo usa: valor_orcamento
    valor_final: Decimal           # ✅ Existe
    observacoes: str               # ❌ Modelo usa: observacoes_abertura
    requer_orcamento: bool         # ❌ NÃO EXISTE NO MODELO
    urgente: bool                  # ❌ NÃO EXISTE NO MODELO
    usuario_criacao: str           # ❌ Modelo usa: usuario_abertura
```

### **Modelo: OrdemServico** (backend/models/ordem_servico_model.py)
```python
class OrdemServico(Base):
    __tablename__ = "ordens_servico"
    
    # Identificação
    id: int
    numero_os: str                   # ✅ Match
    cliente_id: int                  # ✅ Match
    
    # Tipo e categoria
    tipo_servico: str                # ✅ Match (enum no schema)
    categoria: str                   # ❌ NÃO EXISTE NO SCHEMA (obrigatório!)
    prioridade: str                  # ✅ Match (enum no schema)
    
    # Status
    status_fase: int                 # ❌ Schema usa: fase_atual (FaseOSEnum)
    status_geral: str                # ❌ Schema usa: status (StatusOS)
    
    # Datas
    data_abertura: datetime          # ❌ Schema usa: data_solicitacao
    data_prevista_conclusao: datetime # ❌ Schema usa: data_prazo
    data_conclusao: datetime         # ❌ NÃO EXISTE NO SCHEMA
    prazo_orcamento: datetime        # ❌ NÃO EXISTE NO SCHEMA
    
    # Responsáveis
    usuario_abertura: str            # ❌ Schema usa: usuario_criacao
    usuario_responsavel: str         # ❌ NÃO EXISTE NO SCHEMA
    tecnico_responsavel: str         # ❌ NÃO EXISTE NO SCHEMA
    
    # Valores
    valor_orcamento: Decimal         # ❌ Schema usa: valor_estimado
    valor_desconto: Decimal          # ❌ NÃO EXISTE NO SCHEMA
    valor_final: Decimal             # ✅ Match
    forma_pagamento: str             # ❌ NÃO EXISTE NO SCHEMA
    
    # Endereço
    endereco_execucao: str           # ❌ Schema usa: endereco_servico
    cidade_execucao: str             # ❌ Schema usa: cidade_servico
    estado_execucao: str             # ❌ Schema usa: estado_servico
    cep_execucao: str                # ❌ Schema usa: cep_servico
    
    # Observações
    observacoes_abertura: str        # ❌ Schema usa: titulo + descricao + observacoes
    observacoes_internas: str        # ❌ NÃO EXISTE NO SCHEMA
    motivo_cancelamento: str         # ❌ NÃO EXISTE NO SCHEMA
    
    # Controle de qualidade
    avaliacao_cliente: int           # ❌ NÃO EXISTE NO SCHEMA
    comentario_avaliacao: str        # ❌ NÃO EXISTE NO SCHEMA
    
    # Metadados
    created_at: datetime             # ❌ NÃO EXISTE NO SCHEMA
    updated_at: datetime             # ❌ NÃO EXISTE NO SCHEMA
```

---

## 📋 **RESUMO DE INCOMPATIBILIDADES**

### ❌ **Campos do Schema SEM correspondente no Modelo (11)**
1. `titulo` → Mapeado para `observacoes_abertura` (workaround)
2. `descricao` → Mapeado para `observacoes_abertura` (workaround)
3. `requer_orcamento` → Não persistido
4. `urgente` → Não persistido
5. `data_solicitacao` → Mapeado para `data_abertura`
6. `data_prazo` → Mapeado para `data_prevista_conclusao`
7. `valor_estimado` → Mapeado para `valor_orcamento`
8. `usuario_criacao` → Mapeado para `usuario_abertura`
9. `endereco_servico` → Mapeado para `endereco_execucao`
10. `cep_servico` → Mapeado para `cep_execucao`
11. `cidade_servico` → Mapeado para `cidade_execucao`

### ❌ **Campos do Modelo SEM correspondente no Schema (12)**
1. `categoria` → **OBRIGATÓRIO!** Hardcoded como "Comercial"
2. `status_fase` → Hardcoded como 1
3. `status_geral` → Hardcoded como "Aberta"
4. `data_conclusao` → Null
5. `prazo_orcamento` → Mapeado de `data_prazo`
6. `usuario_responsavel` → Null
7. `tecnico_responsavel` → Null
8. `valor_desconto` → Default 0.00
9. `forma_pagamento` → Null
10. `observacoes_internas` → Null
11. `motivo_cancelamento` → Null
12. `avaliacao_cliente` → Null

---

## ✅ **MAPEAMENTO ATUAL (Router)**

```python
# backend/api/routers/ordem_servico_router.py - linhas 161-193
os_obj = OrdemServico(
    # Campos básicos
    numero_os=os_data.numero_os,
    cliente_id=os_data.cliente_id,
    tipo_servico=os_data.tipo_servico.value,
    categoria="Comercial",  # ⚠️ HARDCODED
    prioridade=os_data.prioridade.value,
    
    # Status
    status_fase=1,  # ⚠️ HARDCODED
    status_geral="Aberta",  # ⚠️ HARDCODED
    
    # Datas
    data_prevista_conclusao=os_data.data_prazo,
    prazo_orcamento=os_data.data_prazo,
    
    # Responsáveis
    usuario_abertura=os_data.usuario_criacao,
    
    # Valores
    valor_orcamento=os_data.valor_estimado or 0.00,
    valor_final=os_data.valor_final or 0.00,
    
    # Endereço
    endereco_execucao=os_data.endereco_servico,
    cep_execucao=os_data.cep_servico,
    cidade_execucao=os_data.cidade_servico,
    estado_execucao=os_data.estado_servico,
    
    # Observações (concatenação)
    observacoes_abertura=f"{os_data.titulo}\n\n{os_data.descricao}\n\n{os_data.observacoes or ''}"
)
```

---

## 🔧 **RECOMENDAÇÕES**

### **Opção 1: Atualizar Schema (Menos invasivo)** ✅ RECOMENDADO
Alinhar `OrdemServicoBase` com campos reais do modelo:

```python
class OrdemServicoBase(BaseModel):
    numero_os: str
    cliente_id: int
    
    # NOVOS NOMES (alinhados com modelo)
    categoria: str = Field("Comercial", description="Categoria do serviço")
    tipo_servico: TipoOS
    prioridade: PrioridadeOS
    
    # Endereço (nomes corretos)
    endereco_execucao: str
    cep_execucao: str
    cidade_execucao: str
    estado_execucao: str
    
    # Datas (nomes corretos)
    data_prevista_conclusao: Optional[datetime] = None
    
    # Valores (nomes corretos)
    valor_orcamento: Optional[Decimal] = None
    valor_final: Optional[Decimal] = None
    
    # Observações (único campo)
    observacoes_abertura: Optional[str] = None
    
    # Usuário (nome correto)
    usuario_abertura: str
```

### **Opção 2: Adicionar Campos ao Modelo** ⚠️ REQUER MIGRATION
Adicionar campos faltantes ao `OrdemServico`:

```python
# Em ordem_servico_model.py
titulo = Column(String(200))
descricao = Column(Text)
requer_orcamento = Column(Boolean, default=True)
urgente = Column(Boolean, default=False)
```

**Requer:** `alembic revision` + `alembic upgrade head`

---

## 🎯 **DECISÃO**

**Status Atual:** ✅ **FUNCIONANDO** com mapeamento manual no router

**Ação Recomendada:** Manter workaround atual até Fase 4, depois refatorar schemas

**Prioridade:** 🟡 MÉDIA (não afeta funcionamento atual)

---

## 📝 **CAMPOS DE FASEOST - Verificação Adicional**

### **Modelo: FaseOS** (backend/models/ordem_servico_model.py)
```python
class FaseOS(Base):
    __tablename__ = "fases_os"
    
    id: int
    ordem_servico_id: int
    numero_fase: int                 # 1-7
    nome_fase: str
    descricao_fase: str              # ❌ criar_fases_iniciais() usa: descricao
    status: str
    obrigatoria: bool
    pode_pular: bool
    data_inicio: datetime
    data_prazo: datetime
    data_conclusao: datetime
    responsavel: str
    aprovador: str
    data_aprovacao: datetime
    checklist_itens: JSON
    observacoes: str
    observacoes_internas: str
    anexos: JSON
    fotos: JSON
    assinatura_cliente: str
    created_at: datetime
    updated_at: datetime
```

**Erro na função criar_fases_iniciais():**
```python
# ERRADO (linha 396):
descricao=fase_data["descricao"]

# CORRETO:
descricao_fase=fase_data["descricao"]
```

---

**Última atualização:** 15/11/2025 22:00
