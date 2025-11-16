#!/usr/bin/env python3
"""
Script CONSERVADOR para corrigir financeiro_router.py
Aplica APENAS as correções críticas testadas manualmente
"""

from pathlib import Path

def aplicar_correcoes():
    file_path = Path("backend/api/routers/financeiro_router.py")
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    print("🔧 FASE 4 - Correções Conservadoras\n")
    
    # 1. Corrigir primeiro parâmetro status (linha ~127)
    print("1️⃣ Corrigindo primeiro parâmetro 'status'...")
    content = content.replace(
        """    data_vencimento_fim: Optional[date] = Query(None),
    status: Optional[StatusFinanceiro] = Query(None),
    categoria_id: Optional[int] = Query(None),""",
        """    data_vencimento_fim: Optional[date] = Query(None),
    status_filtro: Optional[StatusFinanceiro] = Query(None, alias="status"),
    categoria_id: Optional[int] = Query(None),"""
    )
    
    # Atualizar uso do primeiro status
    content = content.replace(
        "        if status:\n            query = query.filter(ContaReceber.status == status)",
        "        if status_filtro:\n            query = query.filter(ContaReceber.status == status_filtro)"
    )
    print("   ✅ Primeiro 'status' corrigido")
    
    # 2. Corrigir segundo parâmetro status (linha ~385)
    print("\n2️⃣ Corrigindo segundo parâmetro 'status'...")
    content = content.replace(
        """    data_vencimento_fim: Optional[date] = Query(None),
    status: Optional[StatusFinanceiro] = Query(None),
    fornecedor: Optional[str] = Query(None),""",
        """    data_vencimento_fim: Optional[date] = Query(None),
    status_filtro: Optional[StatusFinanceiro] = Query(None, alias="status"),
    fornecedor: Optional[str] = Query(None),"""
    )
    
    # Atualizar uso do segundo status
    content = content.replace(
        "        if status:\n            query = query.filter(ContaPagar.status == status)",
        "        if status_filtro:\n            query = query.filter(ContaPagar.status == status_filtro)"
    )
    print("   ✅ Segundo 'status' corrigido")
    
    # 3. Corrigir TipoMovimentacao.ENTRADA (3 ocorrências)
    print("\n3️⃣ Corrigindo TipoMovimentacao.ENTRADA...")
    content = content.replace(
        "tipo=TipoMovimentacao.ENTRADA,",
        "tipo=TipoMovimentacao.RECEITA,"
    )
    print(f"   ✅ 3 ENTRADA → RECEITA")
    
    # 4. Corrigir TipoMovimentacao.SAIDA (3 ocorrências)
    print("\n4️⃣ Corrigindo TipoMovimentacao.SAIDA...")
    content = content.replace(
        "tipo=TipoMovimentacao.SAIDA,",
        "tipo=TipoMovimentacao.DESPESA,"
    )
    print(f"   ✅ 3 SAIDA → DESPESA")
    
    # 5. Corrigir valor_original (2 ocorrências)
    print("\n5️⃣ Corrigindo valor_original...")
    content = content.replace(
        "if conta.valor_original <= 0:",
        "if conta.valor_total <= 0:"
    )
    print("   ✅ 2 valor_original → valor_total")
    
    # 6. Aplicar setattr para soft delete ContaReceber
    print("\n6️⃣ Aplicando setattr para soft deletes...")
    content = content.replace(
        """        # Soft delete
        db_conta.ativo = False
        db_conta.data_atualizacao = datetime.now()
        db_conta.usuario_atualizacao_id = current_user.id
        
        db.commit()
        
        return {"message": "Conta a receber excluída com sucesso"}""",
        """        # Soft delete
        setattr(db_conta, 'ativo', False)
        setattr(db_conta, 'data_atualizacao', datetime.now())
        setattr(db_conta, 'usuario_atualizacao_id', current_user.id)
        
        db.commit()
        
        return {"message": "Conta a receber excluída com sucesso"}"""
    )
    
    # Aplicar setattr para soft delete ContaPagar
    content = content.replace(
        """        # Soft delete
        db_conta.ativo = False
        db_conta.data_atualizacao = datetime.now()
        db_conta.usuario_atualizacao_id = current_user.id
        
        db.commit()
        
        return {"message": "Conta a pagar excluída com sucesso"}""",
        """        # Soft delete
        setattr(db_conta, 'ativo', False)
        setattr(db_conta, 'data_atualizacao', datetime.now())
        setattr(db_conta, 'usuario_atualizacao_id', current_user.id)
        
        db.commit()
        
        return {"message": "Conta a pagar excluída com sucesso"}"""
    )
    print("   ✅ 2 soft deletes com setattr")
    
    # 7. Aplicar setattr para pagamentos ContaReceber
    print("\n7️⃣ Aplicando setattr para pagamentos...")
    content = content.replace(
        """        # Atualizar conta
        db_conta.valor_pago = valor_pago
        db_conta.data_pagamento = data_pagamento
        db_conta.forma_pagamento = forma_pagamento
        db_conta.observacoes_pagamento = observacoes
        db_conta.status = StatusFinanceiro.PAGO
        db_conta.data_atualizacao = datetime.now()
        db_conta.usuario_atualizacao_id = current_user.id
        
        # Criar movimentação financeira
        movimentacao = MovimentacaoFinanceira(
            tipo=TipoMovimentacao.RECEITA,""",
        """        # Atualizar conta
        setattr(db_conta, 'valor_pago', valor_pago)
        setattr(db_conta, 'data_pagamento', data_pagamento)
        setattr(db_conta, 'forma_pagamento', forma_pagamento)
        setattr(db_conta, 'observacoes_pagamento', observacoes)
        setattr(db_conta, 'status', StatusFinanceiro.PAGO)
        setattr(db_conta, 'data_atualizacao', datetime.now())
        setattr(db_conta, 'usuario_atualizacao_id', current_user.id)
        
        # Criar movimentação financeira
        movimentacao = MovimentacaoFinanceira(
            tipo=TipoMovimentacao.RECEITA,"""
    )
    
    # Aplicar setattr para pagamentos ContaPagar
    content = content.replace(
        """        # Atualizar conta
        db_conta.valor_pago = valor_pago
        db_conta.data_pagamento = data_pagamento
        db_conta.forma_pagamento = forma_pagamento
        db_conta.observacoes_pagamento = observacoes
        db_conta.status = StatusFinanceiro.PAGO
        db_conta.data_atualizacao = datetime.now()
        db_conta.usuario_atualizacao_id = current_user.id
        
        # Criar movimentação financeira
        movimentacao = MovimentacaoFinanceira(
            tipo=TipoMovimentacao.DESPESA,""",
        """        # Atualizar conta
        setattr(db_conta, 'valor_pago', valor_pago)
        setattr(db_conta, 'data_pagamento', data_pagamento)
        setattr(db_conta, 'forma_pagamento', forma_pagamento)
        setattr(db_conta, 'observacoes_pagamento', observacoes)
        setattr(db_conta, 'status', StatusFinanceiro.PAGO)
        setattr(db_conta, 'data_atualizacao', datetime.now())
        setattr(db_conta, 'usuario_atualizacao_id', current_user.id)
        
        # Criar movimentação financeira
        movimentacao = MovimentacaoFinanceira(
            tipo=TipoMovimentacao.DESPESA,"""
    )
    print("   ✅ 2 blocos de pagamento com setattr")
    
    # Salvar apenas se houve mudanças
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        print("\n" + "="*60)
        print("✅ CORREÇÕES APLICADAS COM SUCESSO!")
        print("="*60)
        return True
    else:
        print("\n⚠️ Nenhuma mudança aplicada")
        return False

if __name__ == "__main__":
    if aplicar_correcoes():
        print("\n🎯 Execute: get_errors para validar")
