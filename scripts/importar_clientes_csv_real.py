"""
IMPORTADOR DE CLIENTES PRIMOTEX - CSV REAL
==========================================

Importador especializado para os arquivos CSV fornecidos:
- Clientes PF.csv (Pessoas Físicas)
- Clientes PJ.csv (Pessoas Jurídicas)

Total: 20 clientes para importação e testes
"""

import sys
import os
import csv
import re
from datetime import datetime

# Path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.models.cliente_model import Cliente
from backend.database.config import engine


class ImportadorClientesCSV:
    """Importador de clientes dos arquivos CSV reais"""
    
    def __init__(self):
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.sucessos = 0
        self.erros = 0
        self.pulos = 0
        self.logs = []
    
    def log(self, mensagem):
        """Log com timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {mensagem}")
        self.logs.append(f"[{timestamp}] {mensagem}")
    
    def limpar_cpf_cnpj(self, documento):
        """Limpar formatação de CPF/CNPJ"""
        return re.sub(r'[^\d]', '', documento)
    
    def formatar_telefone(self, telefone):
        """Formatar telefone brasileiro"""
        if not telefone:
            return ""
        
        # Limpar caracteres especiais
        telefone = re.sub(r'[^\d]', '', telefone)
        
        # Remover código do país se presente
        if telefone.startswith('55') and len(telefone) > 11:
            telefone = telefone[2:]
        
        # Formatar conforme tamanho
        if len(telefone) == 11:  # Celular
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 10:  # Fixo
            return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        else:
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
            return {}, "", "", ""
        
        # Tentar extrair logradouro, bairro
        partes = endereco_completo.split(',')
        
        logradouro = partes[0].strip() if len(partes) > 0 else ""
        
        # Procurar por número no logradouro
        numero = ""
        match = re.search(r'\b(\d+)\b', logradouro)
        if match:
            numero = match.group(1)
            logradouro = re.sub(r',?\s*\b\d+\b', '', logradouro).strip()
        
        # Tentar extrair bairro (geralmente após ' - ')
        bairro = ""
        if ' - ' in endereco_completo:
            partes_bairro = endereco_completo.split(' - ')
            if len(partes_bairro) > 1:
                bairro = partes_bairro[1].split(',')[0].strip()
        
        return logradouro, numero, bairro
    
    def importar_clientes_pf(self, arquivo_csv):
        """Importar clientes Pessoa Física"""
        self.log("🏠 Iniciando importação de Clientes Pessoa Física")
        
        try:
            with open(arquivo_csv, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for linha in reader:
                    try:
                        # Extrair dados
                        nome = linha['Nome Completo'].strip()
                        cpf = self.limpar_cpf_cnpj(linha['CPF'])
                        rg = linha['RG'].strip()
                        email = linha['Email'].strip()
                        whatsapp = self.formatar_telefone(linha['WhatsApp'])
                        telefone_res = self.formatar_telefone(linha['Telefone Residencial'])
                        endereco_completo = linha['Endereço Completo']
                        cidade = linha['Cidade'].strip()
                        estado = linha['Estado (UF)'].strip()
                        cep = self.formatar_cep(linha['CEP'])
                        
                        # Processar endereço
                        logradouro, numero, bairro = self.processar_endereco(endereco_completo)
                        
                        # Verificar se já existe
                        if self._cliente_existe(cpf):
                            self.log(f"⚠️  {nome}: CPF já cadastrado, pulando...")
                            self.pulos += 1
                            continue
                        
                        # Gerar código único
                        codigo = f"PF{len(str(self.sucessos + 1).zfill(3))}"
                        
                        # Criar cliente
                        self._criar_cliente_pf(
                            codigo=codigo,
                            nome=nome,
                            cpf=cpf,
                            rg=rg,
                            email=email,
                            whatsapp=whatsapp,
                            telefone_res=telefone_res,
                            logradouro=logradouro,
                            numero=numero,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            cep=cep
                        )
                        
                    except Exception as e:
                        self.erros += 1
                        self.log(f"❌ Erro ao processar {nome}: {str(e)}")
                        
        except Exception as e:
            self.log(f"❌ Erro ao ler arquivo PF: {str(e)}")
    
    def importar_clientes_pj(self, arquivo_csv):
        """Importar clientes Pessoa Jurídica"""
        self.log("🏢 Iniciando importação de Clientes Pessoa Jurídica")
        
        try:
            with open(arquivo_csv, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for linha in reader:
                    try:
                        # Extrair dados
                        razao_social = linha['Razão Social'].strip()
                        nome_fantasia = linha['Nome Fantasia'].strip()
                        cnpj = self.limpar_cpf_cnpj(linha['CNPJ'])
                        email = linha['Email Corporativo'].strip()
                        whatsapp = self.formatar_telefone(linha['WhatsApp'])
                        telefone_com = self.formatar_telefone(linha['Telefone Comercial'])
                        endereco_completo = linha['Endereço Completo']
                        cidade = linha['Cidade'].strip()
                        estado = linha['Estado (UF)'].strip()
                        cep = self.formatar_cep(linha['CEP'])
                        responsavel = linha['Nome do Responsável'].strip()
                        
                        # Processar endereço
                        logradouro, numero, bairro = self.processar_endereco(endereco_completo)
                        
                        # Verificar se já existe
                        if self._cliente_existe(cnpj):
                            self.log(f"⚠️  {razao_social}: CNPJ já cadastrado, pulando...")
                            self.pulos += 1
                            continue
                        
                        # Gerar código único
                        codigo = f"PJ{str(self.sucessos + 1).zfill(3)}"
                        
                        # Criar cliente
                        self._criar_cliente_pj(
                            codigo=codigo,
                            razao_social=razao_social,
                            nome_fantasia=nome_fantasia,
                            cnpj=cnpj,
                            email=email,
                            whatsapp=whatsapp,
                            telefone_com=telefone_com,
                            logradouro=logradouro,
                            numero=numero,
                            bairro=bairro,
                            cidade=cidade,
                            estado=estado,
                            cep=cep,
                            responsavel=responsavel
                        )
                        
                    except Exception as e:
                        self.erros += 1
                        self.log(f"❌ Erro ao processar {razao_social}: {str(e)}")
                        
        except Exception as e:
            self.log(f"❌ Erro ao ler arquivo PJ: {str(e)}")
    
    def _cliente_existe(self, cpf_cnpj):
        """Verificar se cliente já existe"""
        session = self.SessionLocal()
        try:
            existe = session.query(Cliente).filter(Cliente.cpf_cnpj == cpf_cnpj).first()
            return existe is not None
        finally:
            session.close()
    
    def _criar_cliente_pf(self, **dados):
        """Criar cliente Pessoa Física"""
        session = self.SessionLocal()
        try:
            cliente = Cliente(
                codigo=dados['codigo'],
                nome=dados['nome'],
                cpf_cnpj=dados['cpf'],
                tipo_pessoa="Física",
                rg_ie=dados['rg'],
                email_principal=dados['email'],
                telefone_whatsapp=dados['whatsapp'],
                telefone_fixo=dados['telefone_res'],
                endereco_logradouro=dados['logradouro'],
                endereco_numero=dados['numero'],
                endereco_bairro=dados['bairro'],
                endereco_cidade=dados['cidade'],
                endereco_estado=dados['estado'],
                endereco_cep=dados['cep'],
                status='Ativo',
                origem='Importação CSV'
            )
            
            session.add(cliente)
            session.commit()
            
            self.sucessos += 1
            self.log(f"✅ PF: {dados['nome']} importado (ID: {cliente.id})")
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _criar_cliente_pj(self, **dados):
        """Criar cliente Pessoa Jurídica"""
        session = self.SessionLocal()
        try:
            cliente = Cliente(
                codigo=dados['codigo'],
                nome=dados['razao_social'],
                cpf_cnpj=dados['cnpj'],
                tipo_pessoa="Jurídica",
                email_principal=dados['email'],
                telefone_whatsapp=dados['whatsapp'],
                telefone_fixo=dados['telefone_com'],
                endereco_logradouro=dados['logradouro'],
                endereco_numero=dados['numero'],
                endereco_bairro=dados['bairro'],
                endereco_cidade=dados['cidade'],
                endereco_estado=dados['estado'],
                endereco_cep=dados['cep'],
                status='Ativo',
                origem='Importação CSV',
                observacoes_gerais=f"Nome Fantasia: {dados['nome_fantasia']}\nResponsável: {dados['responsavel']}"
            )
            
            session.add(cliente)
            session.commit()
            
            self.sucessos += 1
            self.log(f"✅ PJ: {dados['razao_social']} importado (ID: {cliente.id})")
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def gerar_relatorio_final(self):
        """Gerar relatório da importação"""
        total = self.sucessos + self.erros + self.pulos
        taxa_sucesso = (self.sucessos / total * 100) if total > 0 else 0
        
        relatorio = f"""
{'='*60}
📊 RELATÓRIO FINAL DE IMPORTAÇÃO - CLIENTES PRIMOTEX
{'='*60}

📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

📈 ESTATÍSTICAS:
   ✅ Sucessos: {self.sucessos}
   ❌ Erros: {self.erros}
   ⚠️  Pulos (duplicados): {self.pulos}
   📊 Total processado: {total}
   🎯 Taxa de sucesso: {taxa_sucesso:.1f}%

💡 PRÓXIMOS PASSOS:
   1. Iniciar servidor: python -m uvicorn backend.api.main:app --port 8002
   2. Abrir sistema: python frontend/desktop/login_tkinter.py
   3. Acessar módulo de Clientes para verificar dados

✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!
{'='*60}
"""
        
        print(relatorio)
        return relatorio


def main():
    """Função principal de importação"""
    print("🎯 IMPORTADOR DE CLIENTES PRIMOTEX - CSV REAL")
    print("=" * 60)
    
    # Caminhos dos arquivos
    pasta_csv = r"C:\Users\Vanderci\OneDrive\Documentos\Banco de dados"
    arquivo_pf = os.path.join(pasta_csv, "Clientes PF.csv")
    arquivo_pj = os.path.join(pasta_csv, "Clientes PJ.csv")
    
    # Verificar se arquivos existem
    if not os.path.exists(arquivo_pf):
        print(f"❌ Arquivo não encontrado: {arquivo_pf}")
        return False
    
    if not os.path.exists(arquivo_pj):
        print(f"❌ Arquivo não encontrado: {arquivo_pj}")
        return False
    
    print(f"📁 Arquivo PF: {arquivo_pf}")
    print(f"📁 Arquivo PJ: {arquivo_pj}")
    
    # Confirmar importação
    resposta = input("\n🚀 Deseja iniciar a importação dos 20 clientes? (s/n): ")
    
    if resposta.lower() != 's':
        print("❌ Importação cancelada pelo usuário.")
        return False
    
    # Iniciar importação
    importador = ImportadorClientesCSV()
    
    print("\n" + "="*60)
    print("🚀 INICIANDO IMPORTAÇÃO...")
    print("="*60)
    
    # Importar Pessoas Físicas
    importador.importar_clientes_pf(arquivo_pf)
    
    # Importar Pessoas Jurídicas
    importador.importar_clientes_pj(arquivo_pj)
    
    # Relatório final
    importador.gerar_relatorio_final()
    
    return importador.sucessos > 0


if __name__ == "__main__":
    main()