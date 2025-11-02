"""
SISTEMA ERP PRIMOTEX - IMPORTADOR DE CLIENTES
=============================================

Script para importar dados de clientes de tabelas/planilhas para o banco de dados.
Suporta múltiplos formatos: CSV, Excel, JSON, ou dados diretos via código.

FUNCIONALIDADES:
- Validação automática de CPF/CNPJ
- Formatação de telefones e CEP
- Validação de email
- Geração automática de códigos de cliente
- Tratamento de erros e duplicados
- Preview antes da importação
- Relatório de importação

Autor: GitHub Copilot
Data: 01/11/2025
"""

import sys
import os
import pandas as pd
import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.cliente_model import Cliente, TIPOS_PESSOA, STATUS_CLIENTE
from backend.database.config import get_db, engine
from backend.schemas.cliente_schemas import ClienteCreate

class ImportadorClientes:
    """Classe para importar dados de clientes"""
    
    def __init__(self):
        self.session = None
        self.logger = self._setup_logger()
        self.dados_importacao = []
        self.erros_validacao = []
        self.sucessos = 0
        self.erros = 0
        
    def _setup_logger(self):
        """Configurar logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('importacao_clientes.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def validar_cpf(self, cpf: str) -> bool:
        """Validar CPF"""
        if not cpf:
            return False
            
        # Remover caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)
        
        # Verificar se tem 11 dígitos
        if len(cpf) != 11:
            return False
            
        # Verificar se não são todos iguais
        if cpf == cpf[0] * 11:
            return False
            
        # Validar dígitos verificadores
        for i in range(9, 11):
            valor = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
            digito = ((valor * 10) % 11) % 10
            if digito != int(cpf[i]):
                return False
                
        return True
    
    def validar_cnpj(self, cnpj: str) -> bool:
        """Validar CNPJ"""
        if not cnpj:
            return False
            
        # Remover caracteres não numéricos
        cnpj = re.sub(r'\D', '', cnpj)
        
        # Verificar se tem 14 dígitos
        if len(cnpj) != 14:
            return False
            
        # Verificar se não são todos iguais
        if cnpj == cnpj[0] * 14:
            return False
            
        # Validar primeiro dígito verificador
        sequencia = cnpj[:12]
        digitos_validacao = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(sequencia[i]) * digitos_validacao[i] for i in range(12))
        resto = soma % 11
        primeiro_digito = 0 if resto < 2 else 11 - resto
        
        if int(cnpj[12]) != primeiro_digito:
            return False
            
        # Validar segundo dígito verificador
        sequencia = cnpj[:13]
        digitos_validacao = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(int(sequencia[i]) * digitos_validacao[i] for i in range(13))
        resto = soma % 11
        segundo_digito = 0 if resto < 2 else 11 - resto
        
        return int(cnpj[13]) == segundo_digito
    
    def formatar_telefone(self, telefone: str) -> str:
        """Formatar telefone"""
        if not telefone:
            return ""
            
        # Remover caracteres não numéricos
        telefone = re.sub(r'\D', '', telefone)
        
        # Formatar conforme o tamanho
        if len(telefone) == 11:  # Celular
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 10:  # Fixo
            return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        else:
            return telefone
    
    def formatar_cep(self, cep: str) -> str:
        """Formatar CEP"""
        if not cep:
            return ""
            
        # Remover caracteres não numéricos
        cep = re.sub(r'\D', '', cep)
        
        # Formatar CEP
        if len(cep) == 8:
            return f"{cep[:5]}-{cep[5:]}"
        else:
            return cep
    
    def validar_email(self, email: str) -> bool:
        """Validar email"""
        if not email:
            return True  # Email é opcional
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def gerar_codigo_cliente(self, nome: str, sequencia: int) -> str:
        """Gerar código único para o cliente"""
        # Pegar as 3 primeiras letras do nome
        prefixo = re.sub(r'[^A-Za-z]', '', nome.upper())[:3]
        if len(prefixo) < 3:
            prefixo = prefixo.ljust(3, 'X')
            
        return f"CLI{prefixo}{sequencia:03d}"
    
    def validar_dados_cliente(self, dados: Dict[str, Any], linha: int) -> Dict[str, Any]:
        """Validar dados de um cliente"""
        erros = []
        cliente_validado = {}
        
        # Nome (obrigatório)
        nome = dados.get('nome', '').strip()
        if not nome:
            erros.append(f"Linha {linha}: Nome é obrigatório")
        else:
            cliente_validado['nome'] = nome
            
        # CPF/CNPJ (obrigatório)
        cpf_cnpj = dados.get('cpf_cnpj', '').strip()
        if not cpf_cnpj:
            erros.append(f"Linha {linha}: CPF/CNPJ é obrigatório")
        else:
            # Limpar formatação
            cpf_cnpj_limpo = re.sub(r'\D', '', cpf_cnpj)
            
            # Determinar tipo de pessoa
            if len(cpf_cnpj_limpo) == 11:
                if self.validar_cpf(cpf_cnpj):
                    cliente_validado['cpf_cnpj'] = cpf_cnpj_limpo
                    cliente_validado['tipo_pessoa'] = "Física"
                else:
                    erros.append(f"Linha {linha}: CPF inválido")
            elif len(cpf_cnpj_limpo) == 14:
                if self.validar_cnpj(cpf_cnpj):
                    cliente_validado['cpf_cnpj'] = cpf_cnpj_limpo
                    cliente_validado['tipo_pessoa'] = "Jurídica"
                else:
                    erros.append(f"Linha {linha}: CNPJ inválido")
            else:
                erros.append(f"Linha {linha}: CPF/CNPJ deve ter 11 ou 14 dígitos")
        
        # Email (opcional, mas se preenchido deve ser válido)
        email = dados.get('email_principal', '').strip()
        if email and not self.validar_email(email):
            erros.append(f"Linha {linha}: Email inválido")
        elif email:
            cliente_validado['email_principal'] = email
            
        # Telefone celular
        telefone_celular = dados.get('telefone_celular', '').strip()
        if telefone_celular:
            cliente_validado['telefone_celular'] = self.formatar_telefone(telefone_celular)
            
        # WhatsApp (se não informado, usar celular)
        whatsapp = dados.get('telefone_whatsapp', '').strip()
        if not whatsapp and telefone_celular:
            cliente_validado['telefone_whatsapp'] = cliente_validado.get('telefone_celular', '')
        elif whatsapp:
            cliente_validado['telefone_whatsapp'] = self.formatar_telefone(whatsapp)
            
        # Telefone fixo
        telefone_fixo = dados.get('telefone_fixo', '').strip()
        if telefone_fixo:
            cliente_validado['telefone_fixo'] = self.formatar_telefone(telefone_fixo)
            
        # CEP
        cep = dados.get('endereco_cep', '').strip()
        if cep:
            cliente_validado['endereco_cep'] = self.formatar_cep(cep)
            
        # Outros campos opcionais
        campos_opcionais = [
            'rg_ie', 'endereco_logradouro', 'endereco_numero', 
            'endereco_complemento', 'endereco_bairro', 'endereco_cidade', 
            'endereco_estado', 'email_secundario', 'observacoes_gerais'
        ]
        
        for campo in campos_opcionais:
            valor = dados.get(campo, '').strip()
            if valor:
                cliente_validado[campo] = valor
                
        # Status (padrão: Ativo)
        status = dados.get('status', 'Ativo').strip()
        if status not in STATUS_CLIENTE:
            status = 'Ativo'
        cliente_validado['status'] = status
        
        # Origem (opcional)
        origem = dados.get('origem', '').strip()
        if origem:
            cliente_validado['origem'] = origem
            
        return cliente_validado, erros
    
    def carregar_dados_csv(self, caminho_arquivo: str) -> List[Dict[str, Any]]:
        """Carregar dados de arquivo CSV"""
        try:
            df = pd.read_csv(caminho_arquivo, encoding='utf-8')
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Erro ao ler CSV: {e}")
            return []
    
    def carregar_dados_excel(self, caminho_arquivo: str, planilha: str = None) -> List[Dict[str, Any]]:
        """Carregar dados de arquivo Excel"""
        try:
            df = pd.read_excel(caminho_arquivo, sheet_name=planilha)
            return df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Erro ao ler Excel: {e}")
            return []
    
    def importar_dados_diretos(self, dados: List[Dict[str, Any]]) -> bool:
        """Importar dados fornecidos diretamente"""
        self.dados_importacao = dados
        return self._processar_importacao()
    
    def importar_de_arquivo(self, caminho_arquivo: str, tipo: str = 'auto', planilha: str = None) -> bool:
        """Importar dados de arquivo"""
        # Detectar tipo automaticamente
        if tipo == 'auto':
            extensao = os.path.splitext(caminho_arquivo)[1].lower()
            if extensao == '.csv':
                tipo = 'csv'
            elif extensao in ['.xlsx', '.xls']:
                tipo = 'excel'
            else:
                self.logger.error(f"Tipo de arquivo não suportado: {extensao}")
                return False
        
        # Carregar dados
        if tipo == 'csv':
            self.dados_importacao = self.carregar_dados_csv(caminho_arquivo)
        elif tipo == 'excel':
            self.dados_importacao = self.carregar_dados_excel(caminho_arquivo, planilha)
        else:
            self.logger.error(f"Tipo não suportado: {tipo}")
            return False
            
        if not self.dados_importacao:
            self.logger.error("Nenhum dado foi carregado")
            return False
            
        return self._processar_importacao()
    
    def _processar_importacao(self) -> bool:
        """Processar importação dos dados"""
        self.logger.info(f"Iniciando importação de {len(self.dados_importacao)} registros")
        
        # Validar todos os dados primeiro
        dados_validos = []
        self.erros_validacao = []
        
        for idx, linha_dados in enumerate(self.dados_importacao, 1):
            cliente_validado, erros = self.validar_dados_cliente(linha_dados, idx)
            
            if erros:
                self.erros_validacao.extend(erros)
            else:
                # Gerar código único
                codigo = self.gerar_codigo_cliente(cliente_validado['nome'], idx)
                cliente_validado['codigo'] = codigo
                dados_validos.append(cliente_validado)
        
        # Se há erros de validação, não importar
        if self.erros_validacao:
            self.logger.error(f"Erros de validação encontrados: {len(self.erros_validacao)}")
            for erro in self.erros_validacao:
                self.logger.error(erro)
            return False
        
        # Iniciar importação no banco
        return self._salvar_no_banco(dados_validos)
    
    def _salvar_no_banco(self, dados_validos: List[Dict[str, Any]]) -> bool:
        """Salvar dados validados no banco"""
        try:
            # Criar sessão
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            self.session = SessionLocal()
            
            self.sucessos = 0
            self.erros = 0
            
            for dados_cliente in dados_validos:
                try:
                    # Verificar se CPF/CNPJ já existe
                    cliente_existente = self.session.query(Cliente).filter(
                        Cliente.cpf_cnpj == dados_cliente['cpf_cnpj']
                    ).first()
                    
                    if cliente_existente:
                        self.logger.warning(f"Cliente com CPF/CNPJ {dados_cliente['cpf_cnpj']} já existe. Pulando...")
                        continue
                    
                    # Criar novo cliente
                    novo_cliente = Cliente(**dados_cliente)
                    self.session.add(novo_cliente)
                    self.session.commit()
                    
                    self.sucessos += 1
                    self.logger.info(f"Cliente {dados_cliente['nome']} importado com sucesso")
                    
                except Exception as e:
                    self.session.rollback()
                    self.erros += 1
                    self.logger.error(f"Erro ao salvar cliente {dados_cliente.get('nome', 'N/A')}: {e}")
            
            self.session.close()
            
            # Relatório final
            self.logger.info(f"Importação concluída: {self.sucessos} sucessos, {self.erros} erros")
            
            return self.sucessos > 0
            
        except Exception as e:
            if self.session:
                self.session.rollback()
                self.session.close()
            self.logger.error(f"Erro geral na importação: {e}")
            return False
    
    def preview_dados(self, limite: int = 5) -> None:
        """Visualizar preview dos dados a serem importados"""
        if not self.dados_importacao:
            print("Nenhum dado carregado para preview")
            return
            
        print(f"\n=== PREVIEW DOS DADOS ({min(limite, len(self.dados_importacao))} primeiros registros) ===")
        
        for idx, dados in enumerate(self.dados_importacao[:limite], 1):
            print(f"\nRegistro {idx}:")
            for campo, valor in dados.items():
                if valor and str(valor).strip():
                    print(f"  {campo}: {valor}")
    
    def gerar_relatorio(self) -> str:
        """Gerar relatório da importação"""
        relatorio = f"""
=== RELATÓRIO DE IMPORTAÇÃO DE CLIENTES ===
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

Registros processados: {len(self.dados_importacao)}
Sucessos: {self.sucessos}
Erros: {self.erros}
Erros de validação: {len(self.erros_validacao)}

Taxa de sucesso: {(self.sucessos / len(self.dados_importacao) * 100) if len(self.dados_importacao) > 0 else 0:.1f}%

Erros de validação:
"""
        for erro in self.erros_validacao:
            relatorio += f"- {erro}\n"
            
        return relatorio

def exemplo_uso():
    """Exemplo de como usar o importador"""
    
    # Dados de exemplo para teste
    dados_exemplo = [
        {
            'nome': 'João da Silva',
            'cpf_cnpj': '12345678901',  # CPF de exemplo (não válido)
            'email_principal': 'joao@email.com',
            'telefone_celular': '11999887766',
            'endereco_logradouro': 'Rua das Flores, 123',
            'endereco_bairro': 'Centro',
            'endereco_cidade': 'São Paulo',
            'endereco_estado': 'SP',
            'endereco_cep': '01234567',
            'status': 'Ativo',
            'origem': 'Indicação'
        },
        {
            'nome': 'Empresa ABC Ltda',
            'cpf_cnpj': '12345678000195',  # CNPJ de exemplo (não válido)
            'email_principal': 'contato@empresaabc.com',
            'telefone_celular': '11988776655',
            'endereco_logradouro': 'Av. Paulista, 1000',
            'endereco_bairro': 'Bela Vista',
            'endereco_cidade': 'São Paulo',
            'endereco_estado': 'SP',
            'endereco_cep': '01310100',
            'status': 'Ativo',
            'origem': 'Google'
        }
    ]
    
    # Usar o importador
    importador = ImportadorClientes()
    
    # Preview dos dados
    importador.dados_importacao = dados_exemplo
    importador.preview_dados()
    
    # Importar dados
    sucesso = importador.importar_dados_diretos(dados_exemplo)
    
    # Gerar relatório
    print(importador.gerar_relatorio())
    
    return sucesso

if __name__ == "__main__":
    exemplo_uso()