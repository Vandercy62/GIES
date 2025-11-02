"""
IMPORTADOR FINAL DE COLABORADORES 
================================

Importador corrigido com cargo_id obrigatório
"""

import os
import csv
import re
import sqlite3
from datetime import datetime

DB_PATH = "C:\\GIES\\primotex_erp.db"


def mapear_cargo_por_funcao(funcao):
    """Mapear função para cargo_id baseado na descrição"""
    funcao_lower = funcao.lower()
    
    if any(palavra in funcao_lower for palavra in ['gerente', 'coordenador', 'diretor']):
        return 1  # Gerente
    elif any(palavra in funcao_lower for palavra in ['supervisor', 'encarregado', 'líder']):
        return 2  # Supervisor  
    elif any(palavra in funcao_lower for palavra in ['técnico', 'especialista', 'analista']):
        return 3  # Técnico
    elif any(palavra in funcao_lower for palavra in ['operador', 'operário', 'montador']):
        return 4  # Operador
    elif any(palavra in funcao_lower for palavra in ['assistente', 'secretário', 'administrativo']):
        return 5  # Assistente
    else:
        return 6  # Auxiliar (padrão)


def importar_colaboradores_final():
    """Importar colaboradores com cargo_id correto"""
    
    print("👥 IMPORTAÇÃO FINAL DE COLABORADORES")
    print("=" * 40)
    
    arquivo_csv = r"C:\Users\Vanderci\OneDrive\Documentos\Banco de dados\COLABORADORES.csv"
    
    if not os.path.exists(arquivo_csv):
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
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
    
    def processar_endereco(endereco_completo):
        if not endereco_completo:
            return "", "", ""
        
        partes = endereco_completo.split(',')
        logradouro = partes[0].strip() if len(partes) > 0 else ""
        
        numero = ""
        match = re.search(r'\b(\d+)\b', logradouro)
        if match:
            numero = match.group(1)
            logradouro = re.sub(r',?\s*\b\d+\b', '', logradouro).strip()
        
        bairro = ""
        if len(partes) > 1:
            segunda_parte = partes[1].strip()
            if segunda_parte:
                bairro = segunda_parte.split(',')[0].strip()
        
        return logradouro, numero, bairro
    
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
    
    print(f"📂 Lendo arquivo: {arquivo_csv}")
    
    with open(arquivo_csv, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for linha in reader:
            try:
                nome = linha['Nome Completo'].strip()
                cpf = limpar_cpf(linha['CPF'])
                funcao = linha['Cargo'].strip()
                
                # Verificar se já existe
                cursor.execute("SELECT id FROM colaboradores WHERE cpf = ?", (cpf,))
                if cursor.fetchone():
                    print(f"⚠️  {nome}: CPF já existe, pulando...")
                    pulos += 1
                    continue
                
                # Mapear cargo
                cargo_id = mapear_cargo_por_funcao(funcao)
                
                logradouro, numero, bairro = processar_endereco(linha['Endereço Completo'])
                
                # Extrair cidade e estado
                endereco_completo = linha['Endereço Completo']
                cidade, estado = "", ""
                if ' - ' in endereco_completo:
                    partes = endereco_completo.split(' - ')
                    if len(partes) >= 2:
                        ultima_parte = partes[-1].strip()
                        if ', ' in ultima_parte:
                            cidade_estado = ultima_parte.split(', ')[-1]
                            if ' - ' in cidade_estado:
                                cidade, estado = cidade_estado.split(' - ')[:2]
                                cidade = cidade.strip()
                                estado = estado.strip()
                
                sql = """
                INSERT INTO colaboradores (
                    user_id, cargo_id, matricula, nome_completo, cpf, rg, 
                    telefone_principal, email_corporativo, logradouro, numero, 
                    bairro, cidade, estado, data_nascimento, data_admissao, 
                    salario_atual, estado_civil, status, ativo, observacoes, 
                    data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                valores = (
                    1,                                          # user_id (obrigatório)
                    cargo_id,                                   # cargo_id (obrigatório)
                    linha['ID'].strip(),                       # matricula
                    nome,                                      # nome_completo
                    cpf,                                       # cpf
                    linha['RG'].strip(),                       # rg
                    formatar_telefone(linha['WhatsApp']),      # telefone_principal
                    linha['Email Corporativo'].strip(),        # email_corporativo
                    logradouro,                               # logradouro
                    numero,                                   # numero
                    bairro,                                   # bairro
                    cidade,                                   # cidade
                    estado,                                   # estado
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
                cargo_nome = ['', 'Gerente', 'Supervisor', 'Técnico', 'Operador', 'Assistente', 'Auxiliar'][cargo_id]
                print(f"✅ {nome} → {cargo_nome} (ID: {cursor.lastrowid})")
                
            except Exception as e:
                erros += 1
                print(f"❌ Erro ao importar {nome}: {e}")
    
    conn.close()
    
    print(f"\n" + "="*50)
    print(f"🎯 RESULTADO FINAL:")
    print(f"   ✅ Sucessos: {sucessos}/15")
    print(f"   ❌ Erros: {erros}")
    print(f"   ⚠️  Pulos: {pulos}")
    print(f"   📊 Taxa: {(sucessos/15)*100:.1f}%")
    
    if sucessos == 15:
        print(f"\n🎉 TODOS OS COLABORADORES IMPORTADOS COM SUCESSO!")
        print(f"🚀 SISTEMA ERP AGORA TEM 60 REGISTROS COMPLETOS!")
        return True
    
    return sucessos > 0


if __name__ == "__main__":
    importar_colaboradores_final()