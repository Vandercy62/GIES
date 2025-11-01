"""
Migration para consolidar tabelas de ordens de serviço duplicadas.
- Move dados de 'ordem_servico' para 'ordens_servico' (se existirem)
- Remove tabela antiga
"""
from sqlalchemy import create_engine, text
import os

# Carregar URL do banco do .env
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv("DATABASE_URL", "sqlite:///./primotex_erp.db")

engine = create_engine(db_url)

with engine.connect() as conn:
    # Verificar se ambas as tabelas existem
    tables = [row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()]
    if "ordem_servico" in tables and "ordens_servico" in tables:
        # Verificar se há dados a migrar
        count = conn.execute(text("SELECT COUNT(*) FROM ordem_servico")).scalar()
        if count > 0:
            print(f"Migrando {count} registros de 'ordem_servico' para 'ordens_servico'...")
            # Exemplo: copiar campos compatíveis (ajuste conforme o schema real)
            conn.execute(text("""
                INSERT INTO ordens_servico (id, cliente_id, descricao, status, data_criacao)
                SELECT id, cliente_id, descricao, status, data_criacao FROM ordem_servico
            """))
            print("Dados migrados com sucesso!")
        # Remover tabela antiga
        conn.execute(text("DROP TABLE ordem_servico"))
        print("Tabela 'ordem_servico' removida.")
    else:
        print("Tabelas necessárias não encontradas ou já consolidadas.")
