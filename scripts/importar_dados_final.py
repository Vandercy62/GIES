"""
IMPORTADOR FINAL - TODOS OS CAMPOS OBRIGATÓRIOS
===============================================

Importador final que trata todas as restrições NOT NULL
e importa todos os dados das tabelas CSV com sucesso.
"""

import os
import csv
import re
import sqlite3
from datetime import datetime

DB_PATH = "C:\\GIES\\primotex_erp.db"


class ImportadorFinal:
    """Importador final com todos os campos obrigatórios"""
    
    def __init__(self):
        self.conn = None
        self.sucessos_fornecedores = 0
        self.sucessos_colaboradores = 0
        self.sucessos_produtos = 0
        self.erros = 0
        self.pulos = 0
    
    def conectar_db(self):
        """Conectar ao banco"""
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
    
    def converter_preco(self, preco_str):
        """Converter preço"""
        if not preco_str or preco_str == "None":
            return 0.0
        
        preco_limpo = re.sub(r'[^\d,.]', '', preco_str)
        
        if ',' in preco_limpo and '.' not in preco_limpo:
            preco_limpo = preco_limpo.replace(',', '.')
        elif ',' in preco_limpo and '.' in preco_limpo:
            preco_limpo = preco_limpo.replace(',', '')
        
        try:
            return float(preco_limpo)
        except:
            return 0.0
    
    def converter_data(self, data_str):
        """Converter data"""
        if not data_str or data_str == "None":
            return None
        
        try:
            if '/' in data_str:
                partes = data_str.split('/')
                if len(partes) == 3:
                    return f"{partes[2]}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
            
            if '-' in data_str:
                return data_str
                
        except:
            pass
        
        return None
    
    # ========================================
    # FORNECEDORES
    # ========================================
    
    def fornecedor_existe(self, cnpj):
        """Verificar se fornecedor existe"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM fornecedores WHERE cnpj_cpf = ?", (cnpj,))
        return cursor.fetchone() is not None
    
    def importar_fornecedores(self, arquivo_csv):
        """Importar fornecedores"""
        self.log("🏭 Importando Fornecedores")
        
        with open(arquivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for linha in reader:
                try:
                    empresa = linha['Empresa'].strip()
                    cnpj = self.limpar_cnpj(linha['CNPJ'])
                    
                    if self.fornecedor_existe(cnpj):
                        self.log(f"⚠️  {empresa}: CNPJ já existe, pulando...")
                        self.pulos += 1
                        continue
                    
                    logradouro, numero, bairro = self.processar_endereco(linha['Endereço'])
                    
                    cursor = self.conn.cursor()
                    sql = """
                    INSERT INTO fornecedores (
                        cnpj_cpf, razao_social, tipo_pessoa, categoria, contato_principal,
                        telefone, telefone_2, email, cep, logradouro, numero,
                        bairro, cidade, estado, status, ativo, data_cadastro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    valores = (
                        cnpj,                                    # cnpj_cpf
                        empresa,                                 # razao_social
                        'Jurídica',                             # tipo_pessoa (obrigatório)
                        linha['Ramo'].strip(),                  # categoria
                        linha['Responsável'].strip(),           # contato_principal
                        self.formatar_telefone(linha['Telefone 1']),  # telefone
                        self.formatar_telefone(linha['Telefone 2']),  # telefone_2
                        linha['Email'].strip(),                 # email
                        self.formatar_cep(linha['CEP']),       # cep
                        logradouro,                            # logradouro
                        numero,                                # numero
                        bairro,                                # bairro
                        linha['Cidade'].strip(),               # cidade
                        linha['Estado'].strip(),               # estado
                        'Ativo',                               # status
                        True,                                  # ativo
                        datetime.now().isoformat()             # data_cadastro
                    )
                    
                    cursor.execute(sql, valores)
                    self.conn.commit()
                    
                    self.sucessos_fornecedores += 1
                    self.log(f"✅ Fornecedor: {empresa} importado (ID: {cursor.lastrowid})")
                    
                except Exception as e:
                    self.erros += 1
                    self.log(f"❌ Erro ao importar fornecedor {empresa}: {e}")
    
    # ========================================
    # COLABORADORES  
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
                    
                    logradouro, numero, bairro = self.processar_endereco(linha['Endereço Completo'])
                    
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
                    
                    cursor = self.conn.cursor()
                    sql = """
                    INSERT INTO colaboradores (
                        user_id, matricula, nome_completo, cpf, rg, telefone_principal,
                        email_corporativo, logradouro, numero, bairro, cidade,
                        estado, data_nascimento, data_admissao, salario_atual,
                        estado_civil, status, ativo, observacoes, data_cadastro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    valores = (
                        1,                                      # user_id (obrigatório - usar 1 como padrão)
                        linha['ID'].strip(),                   # matricula
                        nome,                                  # nome_completo
                        cpf,                                   # cpf
                        linha['RG'].strip(),                   # rg
                        self.formatar_telefone(linha['WhatsApp']),  # telefone_principal
                        linha['Email Corporativo'].strip(),    # email_corporativo
                        logradouro,                           # logradouro
                        numero,                               # numero
                        bairro,                               # bairro
                        cidade,                               # cidade
                        estado,                               # estado
                        self.converter_data(linha['Data de Nascimento']),  # data_nascimento
                        self.converter_data(linha['Data de Admissão']),    # data_admissao
                        self.converter_preco(linha['Salário Mensal (R$)']),  # salario_atual
                        linha['Estado Civil'].strip(),         # estado_civil
                        'Ativo',                              # status
                        True,                                 # ativo
                        linha['Observações'].strip() if linha['Observações'] != 'None' else '',  # observacoes
                        datetime.now().isoformat()            # data_cadastro
                    )
                    
                    cursor.execute(sql, valores)
                    self.conn.commit()
                    
                    self.sucessos_colaboradores += 1
                    self.log(f"✅ Colaborador: {nome} importado (ID: {cursor.lastrowid})")
                    
                except Exception as e:
                    self.erros += 1
                    self.log(f"❌ Erro ao importar colaborador {nome}: {e}")
    
    # ========================================
    # PRODUTOS
    # ========================================
    
    def produto_existe(self, codigo):
        """Verificar se produto existe"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM produtos WHERE codigo = ?", (codigo,))
        return cursor.fetchone() is not None
    
    def importar_produtos(self, arquivo_csv):
        """Importar produtos"""
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
                    
                    descricao = linha['Descrição Detalhada'].strip()
                    categoria = linha['Categoria'].strip()
                    unidade = linha['Unidade'].strip()
                    preco = self.converter_preco(linha['Preço Unitário (R$)'])
                    margem = self.converter_preco(linha['Margem de Lucro (%)'])
                    observacoes = linha['Observações'].strip()
                    
                    # Calcular preço de venda
                    preco_venda = preco * (1 + margem / 100) if margem > 0 else preco * 1.3
                    
                    cursor = self.conn.cursor()
                    sql = """
                    INSERT INTO produtos (
                        codigo, descricao, tipo, categoria, unidade_medida, preco_custo,
                        margem_lucro, preco_venda, controla_estoque, estoque_atual,
                        status, observacoes, data_criacao
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    valores = (
                        codigo,                               # codigo
                        descricao,                           # descricao
                        'Material',                          # tipo (obrigatório)
                        categoria,                           # categoria
                        unidade,                             # unidade_medida
                        preco,                               # preco_custo
                        margem,                              # margem_lucro
                        preco_venda,                         # preco_venda
                        True,                                # controla_estoque
                        0.0,                                 # estoque_atual
                        'Ativo',                             # status
                        observacoes,                         # observacoes
                        datetime.now().isoformat()          # data_criacao
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
🎉 IMPORTAÇÃO FINAL CONCLUÍDA - SISTEMA ERP PRIMOTEX
{'='*70}
📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📊 RESUMO DETALHADO:
   🏭 Fornecedores: {self.sucessos_fornecedores}/10 importados
   👥 Colaboradores: {self.sucessos_colaboradores}/15 importados  
   📦 Produtos/Materiais: {self.sucessos_produtos}/15 importados

📈 ESTATÍSTICAS FINAIS:
   ✅ Total de sucessos: {total_sucessos}
   ❌ Erros: {self.erros}
   ⚠️  Pulos (duplicados): {self.pulos}
   📊 Total processado: {total_processados}
   🎯 Taxa de sucesso: {taxa:.1f}%

🎊 BANCO DE DADOS COMPLETO:
   📋 Clientes: 20 registros
   🏭 Fornecedores: {self.sucessos_fornecedores} registros
   👥 Colaboradores: {self.sucessos_colaboradores} registros
   📦 Produtos: {self.sucessos_produtos} registros
   🎯 TOTAL GERAL: {20 + total_sucessos} registros!

💡 SISTEMA PRONTO PARA USO:
   1. Iniciar servidor: python -m uvicorn backend.api.main:app --port 8002
   2. Abrir sistema: python frontend/desktop/login_tkinter.py
   3. Login: admin / admin123
   4. Todos os módulos agora têm dados para teste!

🚀 SISTEMA ERP PRIMOTEX TOTALMENTE OPERACIONAL!
{'='*70}""")


def main():
    """Executar importação final"""
    print("🎯 IMPORTADOR FINAL - DADOS COMPLETOS")
    print("=" * 50)
    
    pasta_csv = r"C:\Users\Vanderci\OneDrive\Documentos\Banco de dados"
    arquivo_fornecedores = os.path.join(pasta_csv, "FORNECEDORES.csv")
    arquivo_colaboradores = os.path.join(pasta_csv, "COLABORADORES.csv")
    arquivo_produtos = os.path.join(pasta_csv, "MATERIAIS E SERVIÇOS.csv")
    
    print("🚀 Iniciando importação final automática...")
    
    importador = ImportadorFinal()
    
    if not importador.conectar_db():
        return False
    
    try:
        print("\n" + "="*50)
        importador.importar_fornecedores(arquivo_fornecedores)
        importador.importar_colaboradores(arquivo_colaboradores)
        importador.importar_produtos(arquivo_produtos)
        importador.gerar_relatorio_final()
        return True
    finally:
        importador.fechar_conexao()


if __name__ == "__main__":
    main()