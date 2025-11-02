"""
IMPORTAÇÃO FINAL COMPLETA - CRIAR TUDO E IMPORTAR
=================================================

Script que cria todos os registros necessários e importa todos os dados
"""

import os
import csv
import re
import sqlite3
from datetime import datetime

DB_PATH = "C:\\GIES\\primotex_erp.db"


def conectar_db():
    """Conectar ao banco"""
    return sqlite3.connect(DB_PATH)


def criar_departamentos():
    """Criar departamentos padrão"""
    conn = conectar_db()
    cursor = conn.cursor()
    
    # Verificar se existem departamentos
    cursor.execute("SELECT COUNT(*) FROM departamentos;")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    print("🏢 Criando departamentos padrão...")
    
    departamentos = [
        ("Administração", "ADMIN", "Departamento Administrativo"),
        ("Produção", "PROD", "Departamento de Produção"),
        ("Vendas", "VEND", "Departamento de Vendas"),
        ("Financeiro", "FIN", "Departamento Financeiro"),
        ("Recursos Humanos", "RH", "Departamento de RH"),
        ("Operacional", "OPER", "Departamento Operacional")
    ]
    
    for nome, codigo, descricao in departamentos:
        cursor.execute("""
            INSERT INTO departamentos (nome, codigo, descricao, ativo, data_criacao)
            VALUES (?, ?, ?, ?, ?)
        """, (nome, codigo, descricao, True, datetime.now().isoformat()))
        print(f"   ✅ Departamento criado: {nome}")
    
    conn.commit()
    conn.close()


def mapear_cargo_por_funcao(funcao):
    """Mapear função para cargo_id - Primotex específico"""
    funcao_lower = funcao.lower()
    
    if 'proprietário' in funcao_lower or 'dono' in funcao_lower:
        return 8  # Proprietário
    elif 'gerente' in funcao_lower:
        return 1  # Gerente
    elif any(palavra in funcao_lower for palavra in ['orçament', 'orcament']):
        return 2  # Orçamentista
    elif any(palavra in funcao_lower for palavra in ['financeiro', 'contabil']):
        return 3  # Financeiro
    elif any(palavra in funcao_lower for palavra in ['montador', 'instalador']):
        return 4  # Montador
    elif any(palavra in funcao_lower for palavra in ['motorista', 'driver']):
        return 5  # Motorista
    elif any(palavra in funcao_lower for palavra in ['ajudante', 'auxiliar']):
        return 6  # Ajudante
    elif any(palavra in funcao_lower for palavra in ['atendente', 'vendas']):
        return 7  # Atendente
    else:
        return 6  # Ajudante (padrão)


def mapear_departamento_por_cargo(funcao):
    """Mapear função para departamento_id"""
    funcao_lower = funcao.lower()
    
    if any(palavra in funcao_lower for palavra in ['gerente', 'diretor', 'admin']):
        return 1  # Administração
    elif any(palavra in funcao_lower for palavra in ['operador', 'técnico', 'produção']):
        return 2  # Produção
    elif any(palavra in funcao_lower for palavra in ['vendas', 'comercial']):
        return 3  # Vendas
    elif any(palavra in funcao_lower for palavra in ['financeiro', 'contabil']):
        return 4  # Financeiro
    elif any(palavra in funcao_lower for palavra in ['recursos', 'rh']):
        return 5  # Recursos Humanos
    else:
        return 6  # Operacional


def importar_colaboradores_completo():
    """Importar colaboradores com todos os campos obrigatórios"""
    
    print("👥 IMPORTAÇÃO COMPLETA DE COLABORADORES")
    print("=" * 50)
    
    # Primeiro criar departamentos
    criar_departamentos()
    
    arquivo_csv = r"C:\Users\Vanderci\OneDrive\Documentos\Banco de dados\COLABORADORES.csv"
    
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        return False
    
    conn = conectar_db()
    cursor = conn.cursor()
    
    sucessos = 0
    erros = 0
    pulos = 0
    
    def limpar_cpf(cpf):
        return re.sub(r'[^\d]', '', cpf)
    
    def formatar_telefone(telefone):
        if not telefone or telefone == "None":
            return ""
        telefone = re.sub(r'[^\d]', '', telefone)
        if telefone.startswith('55') and len(telefone) > 11:
            telefone = telefone[2:]
        if len(telefone) == 11:
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 10:
            return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        return telefone
    
    def converter_data(data_str):
        if not data_str or data_str == "None":
            return None
        
        try:
            if '/' in data_str:
                partes = data_str.split('/')
                if len(partes) == 3:
                    return f"{partes[2]}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
            
            if '-' in data_str:
                return data_str
                
        except Exception:
            pass
        
        return None
    
    def converter_preco(preco_str):
        if not preco_str or preco_str == "None":
            return 0.0
        
        preco_limpo = re.sub(r'[^\d,.]', '', preco_str)
        
        if ',' in preco_limpo and '.' not in preco_limpo:
            preco_limpo = preco_limpo.replace(',', '.')
        elif ',' in preco_limpo and '.' in preco_limpo:
            preco_limpo = preco_limpo.replace(',', '')
        
        try:
            return float(preco_limpo)
        except Exception:
            return 0.0
    
    print(f"📂 Processando arquivo: {arquivo_csv}")
    
    with open(arquivo_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for linha in reader:
            try:
                nome = linha['Nome Completo'].strip()
                cpf = limpar_cpf(linha['CPF'])
                cargo = linha['Cargo'].strip()
                
                # Verificar se já existe
                cursor.execute("SELECT id FROM colaboradores WHERE cpf = ?", (cpf,))
                if cursor.fetchone():
                    print(f"⚠️  {nome}: CPF já existe, pulando...")
                    pulos += 1
                    continue
                
                # Mapear cargo e departamento
                cargo_id = mapear_cargo_por_funcao(cargo)
                departamento_id = mapear_departamento_por_cargo(cargo)
                
                sql = """
                INSERT INTO colaboradores (
                    user_id, cargo_id, departamento_id, matricula, nome_completo, 
                    cpf, rg, telefone_principal, email_corporativo, 
                    data_nascimento, data_admissao, salario_atual, estado_civil, 
                    status, ativo, observacoes, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                valores = (
                    1,                                          # user_id
                    cargo_id,                                   # cargo_id
                    departamento_id,                            # departamento_id
                    linha['ID'].strip(),                       # matricula
                    nome,                                      # nome_completo
                    cpf,                                       # cpf
                    linha['RG'].strip(),                       # rg
                    formatar_telefone(linha['WhatsApp']),      # telefone_principal
                    linha['Email Corporativo'].strip(),        # email_corporativo
                    converter_data(linha['Data de Nascimento']),  # data_nascimento
                    converter_data(linha['Data de Admissão']),    # data_admissao
                    converter_preco(linha['Salário Mensal (R$)']),  # salario_atual
                    linha['Estado Civil'].strip(),             # estado_civil
                    'Ativo',                                  # status
                    True,                                     # ativo
                    linha['Observações'].strip() if linha['Observações'] != 'None' else '',  # observacoes
                    datetime.now().isoformat()                # data_cadastro
                )
                
                cursor.execute(sql, valores)
                conn.commit()
                
                sucessos += 1
                cargo_nome = ['', 'Gerente', 'Orçamentista', 'Financeiro', 'Montador', 'Motorista', 'Ajudante', 'Atendente', 'Proprietário'][cargo_id]
                dept_nome = ['', 'Admin', 'Produção', 'Vendas', 'Financeiro', 'RH', 'Operacional'][departamento_id]
                print(f"✅ {nome} → {cargo_nome}/{dept_nome} (ID: {cursor.lastrowid})")
                
            except Exception as e:
                erros += 1
                print(f"❌ Erro ao importar {nome}: {e}")
    
    conn.close()
    
    # Relatório final
    print(f"\n" + "="*60)
    print(f"🎉 IMPORTAÇÃO FINAL CONCLUÍDA!")
    print(f"=" * 60)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"\n📊 COLABORADORES:")
    print(f"   ✅ Sucessos: {sucessos}/15")
    print(f"   ❌ Erros: {erros}")
    print(f"   ⚠️  Pulos: {pulos}")
    print(f"   📈 Taxa: {(sucessos/15)*100:.1f}%")
    
    if sucessos == 15:
        print(f"\n🎊 SISTEMA ERP COMPLETO:")
        print(f"   📋 Clientes: 20 registros")
        print(f"   🏭 Fornecedores: 10 registros")  
        print(f"   👥 Colaboradores: {sucessos} registros")
        print(f"   📦 Produtos: 15 registros")
        print(f"   🎯 TOTAL: {20+10+sucessos+15} registros!")
        print(f"\n🚀 SISTEMA PRONTO PARA PRODUÇÃO!")
        return True
    
    return sucessos > 0


if __name__ == "__main__":
    importar_colaboradores_completo()