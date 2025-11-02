"""
IMPORTADOR DIRETO DE CLIENTES - SEM DEPENDÊNCIAS
================================================

Importador simplificado que evita conflitos de relacionamento
e importa apenas os dados de clientes dos CSVs.
"""

import sys
import os
import csv
import re
from datetime import datetime
import sqlite3

# Caminho do banco
DB_PATH = "C:\\GIES\\primotex_erp.db"


class ImportadorClientesDireto:
    """Importador direto via SQLite, sem SQLAlchemy"""
    
    def __init__(self):
        self.sucessos = 0
        self.erros = 0
        self.pulos = 0
        self.conn = None
    
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
        """Log simples"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensagem}")
    
    def limpar_cpf_cnpj(self, documento):
        """Limpar formatação"""
        return re.sub(r'[^\d]', '', documento)
    
    def formatar_telefone(self, telefone):
        """Formatar telefone"""
        if not telefone:
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
        if ' - ' in endereco_completo:
            partes_bairro = endereco_completo.split(' - ')
            if len(partes_bairro) > 1:
                bairro = partes_bairro[1].split(',')[0].strip()
        
        return logradouro, numero, bairro
    
    def cliente_existe(self, cpf_cnpj):
        """Verificar se cliente existe"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE cpf_cnpj = ?", (cpf_cnpj,))
        return cursor.fetchone() is not None
    
    def inserir_cliente(self, dados):
        """Inserir cliente no banco"""
        cursor = self.conn.cursor()
        
        sql = """
        INSERT INTO clientes (
            codigo, nome, cpf_cnpj, tipo_pessoa, rg_ie, 
            email_principal, telefone_whatsapp, telefone_fixo,
            endereco_logradouro, endereco_numero, endereco_bairro,
            endereco_cidade, endereco_estado, endereco_cep,
            status, origem, observacoes_gerais, data_criacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        valores = (
            dados['codigo'], dados['nome'], dados['cpf_cnpj'], dados['tipo_pessoa'],
            dados.get('rg_ie', ''), dados.get('email', ''), dados.get('whatsapp', ''),
            dados.get('telefone', ''), dados.get('logradouro', ''), dados.get('numero', ''),
            dados.get('bairro', ''), dados.get('cidade', ''), dados.get('estado', ''),
            dados.get('cep', ''), 'Ativo', 'Importação CSV', dados.get('observacoes', ''),
            datetime.now().isoformat()
        )
        
        try:
            cursor.execute(sql, valores)
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def importar_clientes_pf(self, arquivo_csv):
        """Importar Pessoas Físicas"""
        self.log("🏠 Importando Clientes Pessoa Física")
        
        with open(arquivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for idx, linha in enumerate(reader, 1):
                try:
                    nome = linha['Nome Completo'].strip()
                    cpf = self.limpar_cpf_cnpj(linha['CPF'])
                    
                    if self.cliente_existe(cpf):
                        self.log(f"⚠️  {nome}: CPF já existe, pulando...")
                        self.pulos += 1
                        continue
                    
                    # Processar dados
                    logradouro, numero, bairro = self.processar_endereco(linha['Endereço Completo'])
                    
                    dados = {
                        'codigo': f"PF{idx:03d}",
                        'nome': nome,
                        'cpf_cnpj': cpf,
                        'tipo_pessoa': 'Física',
                        'rg_ie': linha['RG'].strip(),
                        'email': linha['Email'].strip(),
                        'whatsapp': self.formatar_telefone(linha['WhatsApp']),
                        'telefone': self.formatar_telefone(linha['Telefone Residencial']),
                        'logradouro': logradouro,
                        'numero': numero,
                        'bairro': bairro,
                        'cidade': linha['Cidade'].strip(),
                        'estado': linha['Estado (UF)'].strip(),
                        'cep': self.formatar_cep(linha['CEP'])
                    }
                    
                    cliente_id = self.inserir_cliente(dados)
                    self.sucessos += 1
                    self.log(f"✅ PF: {nome} importado (ID: {cliente_id})")
                    
                except Exception as e:
                    self.erros += 1
                    self.log(f"❌ Erro ao importar {nome}: {e}")
    
    def importar_clientes_pj(self, arquivo_csv):
        """Importar Pessoas Jurídicas"""
        self.log("🏢 Importando Clientes Pessoa Jurídica")
        
        with open(arquivo_csv, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for idx, linha in enumerate(reader, 1):
                try:
                    razao_social = linha['Razão Social'].strip()
                    cnpj = self.limpar_cpf_cnpj(linha['CNPJ'])
                    
                    if self.cliente_existe(cnpj):
                        self.log(f"⚠️  {razao_social}: CNPJ já existe, pulando...")
                        self.pulos += 1
                        continue
                    
                    # Processar dados
                    logradouro, numero, bairro = self.processar_endereco(linha['Endereço Completo'])
                    nome_fantasia = linha['Nome Fantasia'].strip()
                    responsavel = linha['Nome do Responsável'].strip()
                    
                    observacoes = f"Nome Fantasia: {nome_fantasia}\nResponsável: {responsavel}"
                    
                    dados = {
                        'codigo': f"PJ{idx:03d}",
                        'nome': razao_social,
                        'cpf_cnpj': cnpj,
                        'tipo_pessoa': 'Jurídica',
                        'email': linha['Email Corporativo'].strip(),
                        'whatsapp': self.formatar_telefone(linha['WhatsApp']),
                        'telefone': self.formatar_telefone(linha['Telefone Comercial']),
                        'logradouro': logradouro,
                        'numero': numero,
                        'bairro': bairro,
                        'cidade': linha['Cidade'].strip(),
                        'estado': linha['Estado (UF)'].strip(),
                        'cep': self.formatar_cep(linha['CEP']),
                        'observacoes': observacoes
                    }
                    
                    cliente_id = self.inserir_cliente(dados)
                    self.sucessos += 1
                    self.log(f"✅ PJ: {razao_social} importado (ID: {cliente_id})")
                    
                except Exception as e:
                    self.erros += 1
                    self.log(f"❌ Erro ao importar {razao_social}: {e}")
    
    def fechar_conexao(self):
        """Fechar conexão"""
        if self.conn:
            self.conn.close()
    
    def gerar_relatorio(self):
        """Relatório final"""
        total = self.sucessos + self.erros + self.pulos
        taxa = (self.sucessos / total * 100) if total > 0 else 0
        
        print(f"""
{'='*60}
📊 RELATÓRIO DE IMPORTAÇÃO - CLIENTES PRIMOTEX
{'='*60}
📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📈 RESULTADOS:
   ✅ Sucessos: {self.sucessos}
   ❌ Erros: {self.erros}
   ⚠️  Pulos: {self.pulos}
   📊 Total: {total}
   🎯 Taxa de sucesso: {taxa:.1f}%

💡 COMO VERIFICAR:
   1. Inicie o servidor: python -m uvicorn backend.api.main:app --port 8002
   2. Abra o sistema: python frontend/desktop/login_tkinter.py
   3. Acesse módulo Clientes

✅ IMPORTAÇÃO CONCLUÍDA!
{'='*60}""")


def main():
    """Executar importação"""
    print("🎯 IMPORTADOR DIRETO DE CLIENTES - CSV")
    print("=" * 50)
    
    # Caminhos
    pasta_csv = r"C:\Users\Vanderci\OneDrive\Documentos\Banco de dados"
    arquivo_pf = os.path.join(pasta_csv, "Clientes PF.csv")
    arquivo_pj = os.path.join(pasta_csv, "Clientes PJ.csv")
    
    # Verificar arquivos
    if not os.path.exists(arquivo_pf):
        print(f"❌ Arquivo não encontrado: {arquivo_pf}")
        return
    
    if not os.path.exists(arquivo_pj):
        print(f"❌ Arquivo não encontrado: {arquivo_pj}")
        return
    
    print(f"📁 Encontrados:")
    print(f"   - {arquivo_pf}")
    print(f"   - {arquivo_pj}")
    
    # Confirmar
    resposta = input("\n🚀 Importar 20 clientes? (s/n): ")
    if resposta.lower() != 's':
        print("❌ Cancelado.")
        return
    
    # Importar
    importador = ImportadorClientesDireto()
    
    if not importador.conectar_db():
        return
    
    try:
        print("\n" + "="*50)
        importador.importar_clientes_pf(arquivo_pf)
        importador.importar_clientes_pj(arquivo_pj)
        importador.gerar_relatorio()
    finally:
        importador.fechar_conexao()


if __name__ == "__main__":
    main()