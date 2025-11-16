"""
Verifica se as fases foram criadas no banco após criação de OS
"""
import sys
sys.path.append("C:\\GIES")

from sqlalchemy.orm import Session
from backend.database.config import get_db
from backend.models.ordem_servico_model import OrdemServico, FaseOS

# Criar sessão
db = next(get_db())

print("🔍 Verificando OS e Fases no banco...\n")

# Buscar última OS criada
os = db.query(OrdemServico).order_by(OrdemServico.id.desc()).first()

if os:
    print(f"📋 Ordem de Serviço:")
    print(f"   ID: {os.id}")
    print(f"   Número: {os.numero_os}")
    print(f"   Cliente: {os.cliente_id}")
    print(f"   Status Geral: {os.status_geral}")
    print(f"   Status Fase: {os.status_fase}")
    print(f"   Data Abertura: {os.data_abertura}")
    print(f"   Usuário: {os.usuario_abertura}")
    
    # Buscar fases da OS
    fases = db.query(FaseOS).filter(FaseOS.ordem_servico_id == os.id).order_by(FaseOS.numero_fase).all()
    
    print(f"\n🔢 Fases Encontradas: {len(fases)}/7")
    if fases:
        print("\n" + "="*70)
        for fase in fases:
            status_icon = "✅" if fase.status == "Concluída" else "⏳"
            print(f"{status_icon} Fase {fase.numero_fase}: {fase.nome_fase}")
            print(f"   Descrição: {fase.descricao_fase}")
            print(f"   Status: {fase.status}")
            print(f"   Obrigatória: {fase.obrigatoria}")
            print(f"   Data Criação: {fase.created_at}")
            print("-"*70)
        
        print(f"\n✅ TESTE COMPLETO: OS {os.numero_os} criada com {len(fases)} fases!")
    else:
        print("\n❌ ERRO: Nenhuma fase foi criada para a OS!")
else:
    print("❌ Nenhuma OS encontrada no banco!")

db.close()
