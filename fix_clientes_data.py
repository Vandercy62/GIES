"""
Script para normalizar dados de clientes no banco
Corrige tipo_pessoa para lowercase sem acentos
"""
from backend.database.config import engine
from sqlalchemy import text

def normalizar_tipo_pessoa():
    """Normaliza campo tipo_pessoa para 'fisica' ou 'juridica'"""
    with engine.connect() as conn:
        # Atualizar 'Física' para 'fisica'
        conn.execute(text("""
            UPDATE clientes 
            SET tipo_pessoa = 'fisica' 
            WHERE tipo_pessoa IN ('Física', 'FISICA', 'física', 'F', 'f', 'PF')
        """))
        
        # Atualizar 'Jurídica' para 'juridica'
        conn.execute(text("""
            UPDATE clientes 
            SET tipo_pessoa = 'juridica' 
            WHERE tipo_pessoa IN ('Jurídica', 'JURIDICA', 'jurídica', 'J', 'j', 'PJ')
        """))
        
        conn.commit()
        print("✅ Tipos de pessoa normalizados!")

def adicionar_campos_timestamp():
    """Adiciona campos created_at e updated_at caso não existam"""
    with engine.connect() as conn:
        try:
            # Verificar se campos existem
            result = conn.execute(text("PRAGMA table_info(clientes)"))
            columns = {row[1] for row in result}
            
            if 'created_at' not in columns:
                conn.execute(text("""
                    ALTER TABLE clientes 
                    ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                """))
                print("✅ Campo created_at adicionado!")
            
            if 'updated_at' not in columns:
                conn.execute(text("""
                    ALTER TABLE clientes 
                    ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                """))
                print("✅ Campo updated_at adicionado!")
            
            conn.commit()
        except Exception as e:
            print(f"⚠️ Erro ao adicionar timestamps: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🔧 NORMALIZAÇÃO DE DADOS - CLIENTES")
    print("="*60)
    
    normalizar_tipo_pessoa()
    adicionar_campos_timestamp()
    
    print("\n✅ NORMALIZAÇÃO CONCLUÍDA!")
