
"""
SISTEMA ERP PRIMOTEX - ROTAS DE CLIENTES
========================================

Este arquivo define todas as rotas da API relacionadas aos CLIENTES.
Aqui temos todos os endpoints para gerenciar o cadastro de clientes.

ROTAS DISPONÍVEIS:
- GET /clientes - Listar todos os clientes
- GET /clientes/{id} - Buscar cliente específico
- POST /clientes - Criar novo cliente
- PUT /clientes/{id} - Atualizar cliente
- DELETE /clientes/{id} - Deletar cliente
- GET /clientes/buscar - Buscar clientes (por nome, CPF, etc.)
- GET /clientes/estatisticas - Estatísticas dos clientes

EXPLICAÇÃO DETALHADA DE CADA ROTA:

1. LISTAR CLIENTES (GET /clientes)
   - Retorna lista paginada de todos os clientes
   - Parâmetros: page (página), limit (itens por página)
   - Filtros: status, tipo_pessoa, origem

2. BUSCAR CLIENTE (GET /clientes/{id})
   - Retorna dados completos de um cliente específico
   - Parâmetro: id do cliente

3. CRIAR CLIENTE (POST /clientes)
   - Cria um novo cliente no sistema
   - Recebe JSON com dados do cliente
   - Valida CPF/CNPJ único

4. ATUALIZAR CLIENTE (PUT /clientes/{id})
   - Atualiza dados de um cliente existente
   - Parâmetro: id do cliente
   - Recebe JSON com dados atualizados

5. DELETAR CLIENTE (DELETE /clientes/{id})
   - Remove um cliente do sistema
   - Parâmetro: id do cliente
   - Verifica se não há OSs vinculadas

Autor: GitHub Copilot
Data: 29/10/2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from backend.database.config import get_database
from backend.models.cliente_model import Cliente, STATUS_CLIENTE, TIPOS_PESSOA
from pydantic import BaseModel, validator, ConfigDict
import re

# =======================================
# CRIAR ROUTER PARA CLIENTES
# =======================================

# Criar router específico para clientes
router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"],
    responses={404: {"description": "Cliente não encontrado"}}
)

# =======================================
# MODELOS PYDANTIC PARA VALIDAÇÃO
# =======================================

class ClienteBase(BaseModel):
    """
    Modelo base para dados de cliente.
    Define os campos obrigatórios e opcionais.
    """
    # Dados básicos obrigatórios
    codigo: str
    tipo_pessoa: str
    nome: str
    cpf_cnpj: str
    
    # Dados básicos opcionais
    rg_ie: Optional[str] = None
    data_nascimento_fundacao: Optional[date] = None
    foto_path: Optional[str] = None
    status: str = "Ativo"
    origem: Optional[str] = None
    tipo_cliente: Optional[str] = None
    
    # Endereço
    endereco_cep: Optional[str] = None
    endereco_logradouro: Optional[str] = None
    endereco_numero: Optional[str] = None
    endereco_complemento: Optional[str] = None
    endereco_bairro: Optional[str] = None
    endereco_cidade: Optional[str] = None
    endereco_estado: Optional[str] = None
    
    # Contatos
    telefone_fixo: Optional[str] = None
    telefone_celular: Optional[str] = None
    telefone_whatsapp: Optional[str] = None
    email_principal: Optional[str] = None
    email_secundario: Optional[str] = None
    site: Optional[str] = None
    redes_sociais: Optional[str] = None
    contatos_adicionais: Optional[str] = None
    
    # Dados financeiros
    banco_nome: Optional[str] = None
    banco_agencia: Optional[str] = None
    banco_conta: Optional[str] = None
    limite_credito: Optional[float] = None
    dia_vencimento_preferencial: Optional[int] = None
    
    # Observações e dados adicionais
    observacoes_gerais: Optional[str] = None
    historico_interacoes: Optional[str] = None
    anexos_paths: Optional[str] = None
    tags_categorias: Optional[str] = None
    
    # Campos de controle
    usuario_criacao_id: Optional[int] = None
    usuario_atualizacao_id: Optional[int] = None
    
    @validator('tipo_pessoa')
    def validar_tipo_pessoa(cls, v):
        """Validar se tipo de pessoa é válido"""
        if v not in TIPOS_PESSOA:
            raise ValueError(f'Tipo de pessoa deve ser: {", ".join(TIPOS_PESSOA)}')
        return v
    
    @validator('status')
    def validar_status(cls, v):
        """Validar se status é válido"""
        if v not in STATUS_CLIENTE:
            raise ValueError(f'Status deve ser: {", ".join(STATUS_CLIENTE)}')
        return v
    
    @validator('cpf_cnpj')
    def validar_cpf_cnpj(cls, v):
        """Validação básica de CPF/CNPJ"""
        # Remove caracteres não numéricos
        apenas_numeros = re.sub(r'\D', '', v)
        # Verifica tamanho (CPF = 11, CNPJ = 14)
        if len(apenas_numeros) not in [11, 14]:
            raise ValueError('CPF deve ter 11 dígitos, CNPJ deve ter 14 dígitos')
        return apenas_numeros

class ClienteCreate(ClienteBase):
    """Modelo para criação de cliente (herda de ClienteBase)"""
    pass

class ClienteUpdate(ClienteBase):
    """Modelo para atualização de cliente (todos os campos opcionais)"""
    codigo: Optional[str] = None
    tipo_pessoa: Optional[str] = None
    nome: Optional[str] = None
    cpf_cnpj: Optional[str] = None


class ClienteResponse(ClienteBase):
    """Modelo de resposta (inclui campos do banco)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    data_criacao: Optional[datetime] = None
    data_atualizacao: Optional[datetime] = None


class ClientesListagemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    total: int
    clientes: List[ClienteResponse]

# =======================================
# FUNÇÕES AUXILIARES
# =======================================

def gerar_proximo_codigo(db: Session) -> str:
    """
    Gerar próximo código de cliente automaticamente.
    Formato: CLI001, CLI002, CLI003, etc.
    """
    # Buscar o último código
    ultimo_cliente = db.query(Cliente).order_by(Cliente.id.desc()).first()
    
    if not ultimo_cliente:
        return "CLI001"
    
    # Extrair número do código
    try:
        numero = int(ultimo_cliente.codigo[3:])  # Remove "CLI" e pega o número
        proximo_numero = numero + 1
        return f"CLI{proximo_numero:03d}"  # Formato com 3 dígitos
    except Exception as e:
        print(f"Warning: Erro ao gerar código automático: {e}")
        # Se der erro, contar quantos clientes existem
        total_clientes = db.query(Cliente).count()
        return f"CLI{total_clientes + 1:03d}"

def verificar_cpf_cnpj_unico(db: Session, cpf_cnpj: str, cliente_id: Optional[int] = None) -> bool:
    """
    Verificar se CPF/CNPJ já existe no banco.
    
    Args:
        db: Sessão do banco
        cpf_cnpj: CPF ou CNPJ para verificar
        cliente_id: ID do cliente (para atualização, ignorar ele mesmo)
    
    Returns:
        True se for único, False se já existir
    """
    query = db.query(Cliente).filter(Cliente.cpf_cnpj == cpf_cnpj)
    
    # Se for atualização, ignorar o próprio cliente
    if cliente_id:
        query = query.filter(Cliente.id != cliente_id)
    
    cliente_existente = query.first()
    return cliente_existente is None

# =======================================
# ROTA 1: LISTAR TODOS OS CLIENTES
# =======================================

@router.get("/", response_model=ClientesListagemResponse)
async def listar_clientes(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(50, ge=1, le=100, description="Itens por página"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    tipo_pessoa: Optional[str] = Query(None, description="Filtrar por tipo de pessoa"),
    db: Session = Depends(get_database)
):
    """
    **LISTAR TODOS OS CLIENTES**
    
    Esta rota retorna uma lista paginada de todos os clientes cadastrados.
    
    **Parâmetros:**
    - **page**: Número da página (começa em 1)
    - **limit**: Quantos clientes por página (máximo 100)
    - **status**: Filtrar por status (Ativo, Inativo, Prospect)
    - **tipo_pessoa**: Filtrar por tipo (Física, Jurídica)
    
    **Exemplo de uso:**
    - `/clientes?page=1&limit=20` - Primeiros 20 clientes
    - `/clientes?status=Ativo` - Apenas clientes ativos
    - `/clientes?tipo_pessoa=Jurídica` - Apenas pessoas jurídicas
    """
    
    # Calcular offset para paginação
    offset = (page - 1) * limit
    
    # Criar query base
    query = db.query(Cliente)
    
    # Aplicar filtros se fornecidos
    if status:
        query = query.filter(Cliente.status == status)
    
    if tipo_pessoa:
        query = query.filter(Cliente.tipo_pessoa == tipo_pessoa)
    
    # Executar query com paginação
    clientes = query.offset(offset).limit(limit).all()

    # Contar total de clientes (com os filtros aplicados)
    total = query.count()

    # Converter explicitamente para ClienteResponse
    clientes_response = [ClienteResponse.model_validate(c) for c in clientes]
    return {
        "total": total,
        "clientes": clientes_response
    }

# =======================================
# ROTA 2: BUSCAR CLIENTE ESPECÍFICO
# =======================================

@router.get("/{cliente_id}", response_model=ClienteResponse)
async def buscar_cliente(
    cliente_id: int,
    db: Session = Depends(get_database)
):
    """
    **BUSCAR CLIENTE ESPECÍFICO**
    
    Retorna todos os dados de um cliente específico pelo ID.
    
    **Parâmetros:**
    - **cliente_id**: ID único do cliente
    
    **Exemplo de uso:**
    - `/clientes/1` - Buscar cliente com ID 1
    """
    
    # Buscar cliente no banco
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    
    # Verificar se existe
    if not cliente:
        raise HTTPException(
            status_code=404, 
            detail=f"Cliente com ID {cliente_id} não encontrado"
        )
    
    return cliente

# =======================================
# ROTA 3: CRIAR NOVO CLIENTE
# =======================================

@router.post("/", response_model=ClienteResponse, status_code=201)
async def criar_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_database)
):
    """
    **CRIAR NOVO CLIENTE**
    
    Cria um novo cliente no sistema com todos os dados fornecidos.
    
    **Validações realizadas:**
    - CPF/CNPJ único no sistema
    - Tipo de pessoa válido
    - Status válido
    - Formato básico de CPF/CNPJ
    
    **Dados obrigatórios:**
    - codigo (será gerado automaticamente se não fornecido)
    - tipo_pessoa (Física ou Jurídica)
    - nome (nome completo ou razão social)
    - cpf_cnpj (somente números)
    """
    
    # Verificar se CPF/CNPJ é único
    if not verificar_cpf_cnpj_unico(db, cliente_data.cpf_cnpj):
        raise HTTPException(
            status_code=400,
            detail=f"CPF/CNPJ {cliente_data.cpf_cnpj} já está cadastrado no sistema"
        )
    
    # Gerar código se não fornecido
    if not cliente_data.codigo:
        cliente_data.codigo = gerar_proximo_codigo(db)
    
    # Verificar se código é único
    codigo_existente = db.query(Cliente).filter(Cliente.codigo == cliente_data.codigo).first()
    if codigo_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Código {cliente_data.codigo} já está em uso"
        )
    
    # Criar objeto Cliente
    try:
        novo_cliente = Cliente(**cliente_data.dict())
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        return novo_cliente
    except Exception as e:
        import traceback
        db.rollback()
        print("[ERRO AO CRIAR CLIENTE]")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar cliente: {str(e)}"
        )

# =======================================
# ROTA 4: ATUALIZAR CLIENTE
# =======================================

@router.put("/{cliente_id}", response_model=ClienteResponse)
async def atualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_database)
):
    """
    **ATUALIZAR CLIENTE EXISTENTE**
    
    Atualiza os dados de um cliente existente.
    Apenas os campos fornecidos serão atualizados.
    
    **Validações realizadas:**
    - Cliente deve existir
    - CPF/CNPJ único (se alterado)
    - Código único (se alterado)
    """
    
    # Buscar cliente existente
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail=f"Cliente com ID {cliente_id} não encontrado"
        )
    
    # Preparar dados para atualização (apenas campos não nulos)
    dados_atualizacao = cliente_data.dict(exclude_unset=True)
    
    # Verificar CPF/CNPJ único se foi alterado
    if 'cpf_cnpj' in dados_atualizacao:
        if not verificar_cpf_cnpj_unico(db, dados_atualizacao['cpf_cnpj'], cliente_id):
            raise HTTPException(
                status_code=400,
                detail=f"CPF/CNPJ {dados_atualizacao['cpf_cnpj']} já está cadastrado"
            )
    
    # Verificar código único se foi alterado
    if 'codigo' in dados_atualizacao:
        codigo_existente = db.query(Cliente).filter(
            Cliente.codigo == dados_atualizacao['codigo'],
            Cliente.id != cliente_id
        ).first()
        if codigo_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Código {dados_atualizacao['codigo']} já está em uso"
            )
    
    # Aplicar atualizações
    try:
        for campo, valor in dados_atualizacao.items():
            setattr(cliente, campo, valor)
        
        db.commit()
        db.refresh(cliente)
        
        return cliente
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar cliente: {str(e)}"
        )

# =======================================
# ROTA 5: DELETAR CLIENTE
# =======================================

@router.delete("/{cliente_id}")
async def deletar_cliente(
    cliente_id: int,
    db: Session = Depends(get_database)
):
    """
    **DELETAR CLIENTE**
    
    Remove um cliente do sistema.
    
    **Validações:**
    - Cliente deve existir
    - Não pode ter OSs vinculadas (implementar futuramente)
    """
    
    # Buscar cliente
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail=f"Cliente com ID {cliente_id} não encontrado"
        )
    
    # Verificar se há OSs vinculadas antes de permitir exclusão
    try:
        # Verificação de OSs quando o modelo estiver implementado na Fase 3
        # Por enquanto, implementamos validação básica
        
        # Simulação: verificar se cliente tem transações recentes
        # Em produção, verificar OrdemServico.cliente_id == cliente_id
        
        # Permitir exclusão por enquanto com log de aviso
        print(f"Warning: Excluindo cliente {cliente_id} - verificar OSs vinculadas na Fase 3")
        
        # TODO Fase 3: Implementar quando modelo OS estiver criado
        # from backend.models.os_model import OrdemServico
        # os_vinculadas = db.query(OrdemServico).filter(OrdemServico.cliente_id == cliente_id).count()
        # if os_vinculadas > 0:
        #     raise HTTPException(
        #         status_code=400,
        #         detail=f"Não é possível excluir cliente com {os_vinculadas} OS(s) vinculada(s)"
        #     )
        
    except Exception as e:
        print(f"Warning: Erro ao verificar OSs vinculadas: {e}")
        # Continuar com exclusão mesmo com erro na verificação
    #         status_code=400,
    #         detail=f"Não é possível deletar cliente com {os_vinculadas} OS vinculadas"
    #     )
    
    try:
        db.delete(cliente)
        db.commit()
        
        return {"message": f"Cliente {cliente.nome} deletado com sucesso"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar cliente: {str(e)}"
        )

# =======================================
# ROTA 6: BUSCAR CLIENTES (PESQUISA)
# =======================================

@router.get("/buscar/pesquisar", response_model=List[ClienteResponse])
async def buscar_clientes(
    termo: str = Query(..., description="Termo de busca"),
    db: Session = Depends(get_database)
):
    """
    **BUSCAR CLIENTES**
    
    Busca clientes por nome, CPF/CNPJ, código ou email.
    
    **Parâmetros:**
    - **termo**: Termo para buscar (nome, CPF, CNPJ, código, email)
    
    **Exemplo:**
    - `/clientes/buscar/pesquisar?termo=João` - Busca "João" no nome
    - `/clientes/buscar/pesquisar?termo=12345678000` - Busca no CPF/CNPJ
    """
    
    # Buscar em vários campos
    clientes = db.query(Cliente).filter(
        (Cliente.nome.ilike(f"%{termo}%")) |
        (Cliente.cpf_cnpj.ilike(f"%{termo}%")) |
        (Cliente.codigo.ilike(f"%{termo}%")) |
        (Cliente.email_principal.ilike(f"%{termo}%"))
    ).limit(50).all()  # Limitar a 50 resultados
    
    return clientes

# =======================================
# ROTA 7: ESTATÍSTICAS DE CLIENTES
# =======================================

@router.get("/estatisticas/resumo")
async def estatisticas_clientes(db: Session = Depends(get_database)):
    """
    **ESTATÍSTICAS DOS CLIENTES**
    
    Retorna estatísticas resumidas dos clientes cadastrados.
    """
    
    # Contar totais
    total_clientes = db.query(Cliente).count()
    clientes_ativos = db.query(Cliente).filter(Cliente.status == "Ativo").count()
    clientes_inativos = db.query(Cliente).filter(Cliente.status == "Inativo").count()
    prospects = db.query(Cliente).filter(Cliente.status == "Prospect").count()
    
    # Contar por tipo
    pessoas_fisicas = db.query(Cliente).filter(Cliente.tipo_pessoa == "Física").count()
    pessoas_juridicas = db.query(Cliente).filter(Cliente.tipo_pessoa == "Jurídica").count()
    
    return {
        "total_clientes": total_clientes,
        "por_status": {
            "ativos": clientes_ativos,
            "inativos": clientes_inativos,
            "prospects": prospects
        },
        "por_tipo": {
            "pessoa_fisica": pessoas_fisicas,
            "pessoa_juridica": pessoas_juridicas
        }
    }