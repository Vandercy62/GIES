"""
IMPORTADOR COMPLETO - SISTEMA ERP PRIMOTEX
==========================================

Importador para todas as tabelas CSV:
- FORNECEDORES.csv (10 registros)
- COLABORADORES.csv (15 registros) 
- MATERIAIS E SERVIÇOS.csv (15 produtos)

Total: 40 registros adicionais para o sistema!
"""

import os
import csv
import re
import sqlite3
from datetime import datetime
from decimal import Decimal

# Caminho do banco
DB_PATH = "C:\\GIES\\primotex_erp.db"


class ImportadorCompleto:
    """Importador para todas as tabelas CSV restantes"""
    
    def __init__(self):
        self.conn = None
        self.sucessos_fornecedores = 0
        self.sucessos_colaboradores = 0
        self.sucessos_produtos = 0
        self.erros = 0
        self.pulos = 0
    
    def conectar_db(self):
        """Conectar ao banco SQLite"""
        try:
            self.conn = sqlite3.connect(DB_PATH)
            print(f"✅ Conectado ao banco: {DB_PATH}")
            return True
        except Exception as e:
            print(f"❌ Erro ao conectar: {e}")
            return False
    
    def log(self, mensagem):
        """Log com timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensagem}")
    
    def limpar_cnpj(self, cnpj):
        """Limpar CNPJ"""
        return re.sub(r'[^\d]', '', cnpj)
    
    def limpar_cpf(self, cpf):
        """Limpar CPF"""
        return re.sub(r'[^\d]', '', cpf)
    
    def formatar_telefone(self, telefone):
        """Formatar telefone"""
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
    
    def formatar_cep(self, cep):
        """Formatar CEP"""
        if not cep:
            return ""
        cep = re.sub(r'[^\d]', '', cep)
        if len(cep) == 8:
            return f"{cep[:5]}-{cep[5:]}"
        return cep
    
    def processar_endereco(self, endereco_completo):
        """Extrair componentes do endereço"""
        if not endereco_completo:
            return "", "", ""
        
        partes = endereco_completo.split(',')
        logradouro = partes[0].strip() if len(partes) > 0 else ""
        
        # Extrair número
        numero = ""
        match = re.search(r'\b(\d+)\b', logradouro)
        if match:
            numero = match.group(1)
            logradouro = re.sub(r',?\s*\b\d+\b', '', logradouro).strip()
        
        # Extrair bairro
        bairro = ""
        if len(partes) > 1:
            segunda_parte = partes[1].strip()
            if segunda_parte:
                bairro = segunda_parte.split(',')[0].strip()
        
        return logradouro, numero, bairro
    
    def converter_preco(self, preco_str):
        """Converter preço de string para decimal"""
        if not preco_str or preco_str == "None":
            return 0.0
        
        # Remover caracteres não numéricos exceto vírgula e ponto
        preco_limpo = re.sub(r'[^\d,.]', '', preco_str)
        
        # Substituir vírgula por ponto se for o separador decimal
        if ',' in preco_limpo and '.' not in preco_limpo:
            preco_limpo = preco_limpo.replace(',', '.')
        elif ',' in preco_limpo and '.' in preco_limpo:
            # Se tem ambos, vírgula é separador de milhares
            preco_limpo = preco_limpo.replace(',', '')
        
        try:
            return float(preco_limpo)
        except:
            return 0.0
    
    def converter_data(self, data_str):
        """Converter data para formato ISO"""
        if not data_str or data_str == "None":
            return None
        
        try:
            # Tentar formato DD/MM/YYYY
            if '/' in data_str:
                partes = data_str.split('/')
                if len(partes) == 3:
                    return f"{partes[2]}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
            
            # Tentar formato YYYY-MM-DD
            if '-' in data_str:
                return data_str
                
        except:
            pass
        
        return None
    
    # ========================================
    # IMPORTAÇÃO DE FORNECEDORES
    # ========================================
    
    def fornecedor_existe(self, cnpj):
        """Verificar se fornecedor existe"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM fornecedores WHERE cnpj = ?", (cnpj,))
        return cursor.fetchone() is not None
    
    def importar_fornecedores(self, arquivo_csv):
        """Importar fornecedores"""
        self.log("🏭 Importando Fornecedores")
        
        with open(arquivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for idx, linha in enumerate(reader, 1):
                try:
                    empresa = linha['Empresa'].strip()
                    cnpj = self.limpar_cnpj(linha['CNPJ'])
                    
                    if self.fornecedor_existe(cnpj):
                        self.log(f"⚠️  {empresa}: CNPJ já existe, pulando...")
                        self.pulos += 1
                        continue
                    
                    # Processar dados
                    logradouro, numero, bairro = self.processar_endereco(linha['Endereço'])
                    
                    # Inserir fornecedor
                    cursor = self.conn.cursor()
                    sql = """
                    INSERT INTO fornecedores (
                        codigo, nome, cnpj, email, telefone_principal, telefone_secundario,
                        whatsapp, endereco_logradouro, endereco_numero, endereco_bairro,
                        endereco_cidade, endereco_estado, endereco_cep, ramo_atividade,
                        responsavel, data_cadastro, status, data_criacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    valores = (
                        f"FOR{idx:03d}",  # codigo
                        empresa,  # nome
                        cnpj,  # cnpj
                        linha['Email'].strip(),  # email
                        self.formatar_telefone(linha['Telefone 1']),  # telefone_principal
                        self.formatar_telefone(linha['Telefone 2']),  # telefone_secundario
                        self.formatar_telefone(linha['WhatsApp']),  # whatsapp
                        logradouro,  # endereco_logradouro
                        numero,  # endereco_numero
                        bairro,  # endereco_bairro
                        linha['Cidade'].strip(),  # endereco_cidade
                        linha['Estado'].strip(),  # endereco_estado
                        self.formatar_cep(linha['CEP']),  # endereco_cep
                        linha['Ramo'].strip(),  # ramo_atividade
                        linha['Responsável'].strip(),  # responsavel
                        self.converter_data(linha['Data Cadastro']),  # data_cadastro
                        'Ativo',  # status
                        datetime.now().isoformat()  # data_criacao
                    )
                    
                    cursor.execute(sql, valores)
                    self.conn.commit()
                    
                    self.sucessos_fornecedores += 1
                    self.log(f"✅ Fornecedor: {empresa} importado (ID: {cursor.lastrowid})")
                    
                except Exception as e:
                    self.erros += 1
                    self.log(f"❌ Erro ao importar fornecedor {empresa}: {e}")
    
    # ========================================
    # IMPORTAÇÃO DE COLABORADORES
    # ========================================
    
    def colaborador_existe(self, cpf):
        """Verificar se colaborador existe"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM colaboradores WHERE cpf = ?", (cpf,))
        return cursor.fetchone() is not None
    
    def importar_colaboradores(self, arquivo_csv):
        """Importar colaboradores"""
        self.log("👥 Importando Colaboradores")
        
        with open(arquivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for linha in reader:
                try:
                    nome = linha['Nome Completo'].strip()
                    cpf = self.limpar_cpf(linha['CPF'])
                    
                    if self.colaborador_existe(cpf):
                        self.log(f"⚠️  {nome}: CPF já existe, pulando...")
                        self.pulos += 1
                        continue
                    
                    # Processar dados
                    logradouro, numero, bairro = self.processar_endereco(linha['Endereço Completo'])
                    codigo = linha['ID'].strip()
                    
                    # Extrair cidade e estado do endereço se possível
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
                    
                    # Inserir colaborador
                    cursor = self.conn.cursor()
                    sql = """
                    INSERT INTO colaboradores (
                        codigo, nome, cpf, rg, cargo, email, telefone_celular, telefone_fixo,
                        endereco_logradouro, endereco_numero, endereco_bairro, endereco_cidade,
                        endereco_estado, data_nascimento, data_admissao, salario, experiencia_anos,
                        estado_civil, especialidade, observacoes, status, data_criacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    valores = (
                        codigo,  # codigo
                        nome,  # nome
                        cpf,  # cpf
                        linha['RG'].strip(),  # rg
                        linha['Cargo'].strip(),  # cargo
                        linha['Email Corporativo'].strip(),  # email
                        self.formatar_telefone(linha['WhatsApp']),  # telefone_celular
                        self.formatar_telefone(linha['Telefone']),  # telefone_fixo
                        logradouro,  # endereco_logradouro
                        numero,  # endereco_numero
                        bairro,  # endereco_bairro
                        cidade,  # endereco_cidade
                        estado,  # endereco_estado
                        self.converter_data(linha['Data de Nascimento']),  # data_nascimento
                        self.converter_data(linha['Data de Admissão']),  # data_admissao
                        self.converter_preco(linha['Salário Mensal (R$)']),  # salario
                        int(linha['Experiência (anos)']) if linha['Experiência (anos)'].isdigit() else 0,  # experiencia_anos
                        linha['Estado Civil'].strip(),  # estado_civil
                        linha['Especialidade Técnica'].strip() if linha['Especialidade Técnica'] != 'None' else '',  # especialidade
                        linha['Observações'].strip() if linha['Observações'] != 'None' else '',  # observacoes
                        'Ativo',  # status
                        datetime.now().isoformat()  # data_criacao
                    )
                    
                    cursor.execute(sql, valores)
                    self.conn.commit()
                    
                    self.sucessos_colaboradores += 1
                    self.log(f"✅ Colaborador: {nome} importado (ID: {cursor.lastrowid})")
                    
                except Exception as e:
                    self.erros += 1
                    self.log(f"❌ Erro ao importar colaborador {nome}: {e}")
    
    # ========================================
    # IMPORTAÇÃO DE PRODUTOS/MATERIAIS
    # ========================================
    
    def produto_existe(self, codigo):
        """Verificar se produto existe"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM produtos WHERE codigo = ?", (codigo,))
        return cursor.fetchone() is not None
    
    def importar_produtos(self, arquivo_csv):
        """Importar produtos/materiais"""
        self.log("📦 Importando Produtos/Materiais")
        
        with open(arquivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for linha in reader:
                try:
                    codigo = linha['Código Produto'].strip()
                    
                    if self.produto_existe(codigo):
                        self.log(f"⚠️  {codigo}: Produto já existe, pulando...")
                        self.pulos += 1
                        continue
                    
                    # Processar dados
                    descricao = linha['Descrição Detalhada'].strip()
                    categoria = linha['Categoria'].strip()
                    unidade = linha['Unidade'].strip()
                    preco = self.converter_preco(linha['Preço Unitário (R$)'])
                    fornecedor = linha['Fornecedor'].strip()
                    margem = self.converter_preco(linha['Margem de Lucro (%)'])
                    observacoes = linha['Observações'].strip()
                    
                    # Inserir produto
                    cursor = self.conn.cursor()
                    sql = """
                    INSERT INTO produtos (
                        codigo, nome, descricao, categoria, unidade_medida, preco_custo,
                        preco_venda, margem_lucro, fornecedor_principal, observacoes,
                        status, data_criacao, data_atualizacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # Calcular preço de venda baseado na margem
                    preco_venda = preco * (1 + margem / 100) if margem > 0 else preco * 1.3
                    
                    valores = (
                        codigo,  # codigo
                        descricao[:100],  # nome (limitado)
                        descricao,  # descricao
                        categoria,  # categoria
                        unidade,  # unidade_medida
                        preco,  # preco_custo
                        preco_venda,  # preco_venda
                        margem,  # margem_lucro
                        fornecedor,  # fornecedor_principal
                        observacoes,  # observacoes
                        'Ativo',  # status
                        datetime.now().isoformat(),  # data_criacao
                        datetime.now().isoformat()   # data_atualizacao
                    )
                    
                    cursor.execute(sql, valores)
                    self.conn.commit()
                    
                    self.sucessos_produtos += 1
                    self.log(f"✅ Produto: {codigo} importado (ID: {cursor.lastrowid})")
                    
                except Exception as e:
                    self.erros += 1
                    self.log(f"❌ Erro ao importar produto {codigo}: {e}")
    
    def fechar_conexao(self):
        """Fechar conexão"""
        if self.conn:
            self.conn.close()
    
    def gerar_relatorio_final(self):
        """Relatório final completo"""
        total_sucessos = self.sucessos_fornecedores + self.sucessos_colaboradores + self.sucessos_produtos
        total_processados = total_sucessos + self.erros + self.pulos
        taxa = (total_sucessos / total_processados * 100) if total_processados > 0 else 0
        
        print(f"""
{'='*70}
🎯 RELATÓRIO FINAL - IMPORTAÇÃO COMPLETA SISTEMA ERP PRIMOTEX
{'='*70}
📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📊 RESUMO POR MÓDULO:
   🏭 Fornecedores: {self.sucessos_fornecedores} importados
   👥 Colaboradores: {self.sucessos_colaboradores} importados  
   📦 Produtos/Materiais: {self.sucessos_produtos} importados

📈 ESTATÍSTICAS GERAIS:
   ✅ Total de sucessos: {total_sucessos}
   ❌ Erros: {self.erros}
   ⚠️  Pulos (duplicados): {self.pulos}
   📊 Total processado: {total_processados}
   🎯 Taxa de sucesso: {taxa:.1f}%

🎉 DADOS AGORA DISPONÍVEIS NO SISTEMA:
   📋 Clientes: 20 registros (já importados)
   🏭 Fornecedores: {self.sucessos_fornecedores} registros
   👥 Colaboradores: {self.sucessos_colaboradores} registros
   📦 Produtos: {self.sucessos_produtos} registros
   🎯 TOTAL GERAL: {20 + total_sucessos} registros no sistema!

💡 PARA VERIFICAR:
   1. Iniciar servidor: python -m uvicorn backend.api.main:app --port 8002
   2. Abrir sistema: python frontend/desktop/login_tkinter.py
   3. Acessar cada módulo para verificar os dados

✅ SISTEMA ERP PRIMOTEX TOTALMENTE POPULADO!
{'='*70}""")


def main():
    """Executar importação completa"""
    print("🎯 IMPORTADOR COMPLETO - SISTEMA ERP PRIMOTEX")
    print("=" * 60)
    
    # Caminhos dos arquivos
    pasta_csv = r"C:\Users\Vanderci\OneDrive\Documentos\Banco de dados"
    arquivo_fornecedores = os.path.join(pasta_csv, "FORNECEDORES.csv")
    arquivo_colaboradores = os.path.join(pasta_csv, "COLABORADORES.csv")
    arquivo_produtos = os.path.join(pasta_csv, "MATERIAIS E SERVIÇOS.csv")
    
    # Verificar arquivos
    arquivos = [
        ("Fornecedores", arquivo_fornecedores),
        ("Colaboradores", arquivo_colaboradores),
        ("Produtos/Materiais", arquivo_produtos)
    ]
    
    arquivos_faltando = []
    for nome, arquivo in arquivos:
        if os.path.exists(arquivo):
            print(f"✅ {nome}: {arquivo}")
        else:
            print(f"❌ {nome}: ARQUIVO NÃO ENCONTRADO - {arquivo}")
            arquivos_faltando.append(nome)
    
    if arquivos_faltando:
        print(f"\n❌ Arquivos faltando: {', '.join(arquivos_faltando)}")
        return False
    
    # Confirmar importação
    print(f"\n📊 Total de registros a importar:")
    print(f"   🏭 Fornecedores: 10 registros")
    print(f"   👥 Colaboradores: 15 registros")
    print(f"   📦 Produtos/Materiais: 15 registros")
    print(f"   🎯 TOTAL: 40 novos registros")
    
    resposta = input("\n🚀 Iniciar importação completa? (s/n): ")
    if resposta.lower() != 's':
        print("❌ Importação cancelada.")
        return False
    
    # Executar importação
    importador = ImportadorCompleto()
    
    if not importador.conectar_db():
        return False
    
    try:
        print("\n" + "="*60)
        print("🚀 INICIANDO IMPORTAÇÃO COMPLETA...")
        print("="*60)
        
        # Importar cada módulo
        importador.importar_fornecedores(arquivo_fornecedores)
        importador.importar_colaboradores(arquivo_colaboradores)
        importador.importar_produtos(arquivo_produtos)
        
        # Relatório final
        importador.gerar_relatorio_final()
        
        return True
        
    finally:
        importador.fechar_conexao()


if __name__ == "__main__":
    main()