"""
IMPORTADOR SIMPLIFICADO DE CLIENTES - SISTEMA ERP PRIMOTEX
=========================================================

Script simples e direto para importar clientes de dados tabulares.
Focado na praticidade para testes rápidos.

Uso:
1. Defina os dados dos clientes na lista 'dados_clientes'
2. Execute o script
3. Verifique os resultados no banco

Autor: GitHub Copilot
Data: 01/11/2025
"""

import sys
import os
import re
from datetime import datetime

# Adicionar path do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import sessionmaker
from backend.models.cliente_model import Cliente
from backend.database.config import engine


class ImportadorClientesSimples:
    """Importador simplificado de clientes"""
    
    def __init__(self):
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.sucessos = 0
        self.erros = 0
        self.logs = []
    
    def log(self, mensagem):
        """Registrar log"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {mensagem}")
        self.logs.append(mensagem)
    
    def validar_cpf_simples(self, cpf):
        """Validação básica de CPF"""
        cpf = re.sub(r'\D', '', cpf)
        return len(cpf) == 11 and not cpf == cpf[0] * 11
    
    def validar_cnpj_simples(self, cnpj):
        """Validação básica de CNPJ"""
        cnpj = re.sub(r'\D', '', cnpj)
        return len(cnpj) == 14 and not cnpj == cnpj[0] * 14
    
    def formatar_telefone(self, telefone):
        """Formatar telefone"""
        if not telefone:
            return ""
        telefone = re.sub(r'\D', '', telefone)
        if len(telefone) == 11:
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 10:
            return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        return telefone
    
    def importar_clientes(self, dados_clientes):
        """Importar lista de clientes"""
        self.log(f"🚀 Iniciando importação de {len(dados_clientes)} clientes")
        
        session = self.SessionLocal()
        
        try:
            for idx, dados in enumerate(dados_clientes, 1):
                try:
                    # Validações básicas
                    nome = dados.get('nome', '').strip()
                    cpf_cnpj = re.sub(r'\D', '', dados.get('cpf_cnpj', ''))
                    
                    if not nome:
                        self.log(f"❌ Cliente {idx}: Nome obrigatório")
                        self.erros += 1
                        continue
                    
                    if not cpf_cnpj:
                        self.log(f"❌ Cliente {idx}: CPF/CNPJ obrigatório")
                        self.erros += 1
                        continue
                    
                    # Verificar se já existe
                    existe = session.query(Cliente).filter(Cliente.cpf_cnpj == cpf_cnpj).first()
                    if existe:
                        self.log(f"⚠️  Cliente {nome}: CPF/CNPJ já cadastrado")
                        continue
                    
                    # Determinar tipo de pessoa
                    if len(cpf_cnpj) == 11:
                        if not self.validar_cpf_simples(cpf_cnpj):
                            self.log(f"❌ Cliente {nome}: CPF inválido")
                            self.erros += 1
                            continue
                        tipo_pessoa = "Física"
                    elif len(cpf_cnpj) == 14:
                        if not self.validar_cnpj_simples(cpf_cnpj):
                            self.log(f"❌ Cliente {nome}: CNPJ inválido")
                            self.erros += 1
                            continue
                        tipo_pessoa = "Jurídica"
                    else:
                        self.log(f"❌ Cliente {nome}: CPF/CNPJ deve ter 11 ou 14 dígitos")
                        self.erros += 1
                        continue
                    
                    # Gerar código único
                    codigo = f"CLI{idx:04d}"
                    
                    # Criar cliente
                    cliente = Cliente(
                        codigo=codigo,
                        nome=nome,
                        cpf_cnpj=cpf_cnpj,
                        tipo_pessoa=tipo_pessoa,
                        rg_ie=dados.get('rg_ie', ''),
                        status=dados.get('status', 'Ativo'),
                        origem=dados.get('origem', 'Importação'),
                        
                        # Endereço
                        endereco_cep=dados.get('cep', ''),
                        endereco_logradouro=dados.get('endereco', ''),
                        endereco_numero=dados.get('numero', ''),
                        endereco_bairro=dados.get('bairro', ''),
                        endereco_cidade=dados.get('cidade', ''),
                        endereco_estado=dados.get('estado', ''),
                        
                        # Contatos
                        telefone_celular=self.formatar_telefone(dados.get('celular', '')),
                        telefone_fixo=self.formatar_telefone(dados.get('telefone', '')),
                        telefone_whatsapp=self.formatar_telefone(dados.get('whatsapp', '') or dados.get('celular', '')),
                        email_principal=dados.get('email', ''),
                        
                        # Observações
                        observacoes_gerais=dados.get('observacoes', '')
                    )
                    
                    session.add(cliente)
                    session.commit()
                    
                    self.sucessos += 1
                    self.log(f"✅ Cliente {nome} importado com sucesso (ID: {cliente.id})")
                    
                except Exception as e:
                    session.rollback()
                    self.erros += 1
                    self.log(f"❌ Erro ao importar {nome}: {str(e)}")
            
            session.close()
            
            # Relatório final
            self.log(f"\n📊 IMPORTAÇÃO CONCLUÍDA:")
            self.log(f"   ✅ Sucessos: {self.sucessos}")
            self.log(f"   ❌ Erros: {self.erros}")
            self.log(f"   📈 Taxa de sucesso: {(self.sucessos/(self.sucessos+self.erros)*100):.1f}%")
            
            return self.sucessos > 0
            
        except Exception as e:
            session.rollback()
            session.close()
            self.log(f"❌ Erro geral: {str(e)}")
            return False


# =================================================================
# DADOS DE EXEMPLO PARA TESTE
# =================================================================

# EXEMPLO 1: Clientes residenciais
dados_exemplo_residencial = [
    {
        'nome': 'Maria Silva Santos',
        'cpf_cnpj': '12345678901',  # CPF teste (formato válido para teste)
        'rg_ie': '123456789',
        'email': 'maria.santos@email.com',
        'celular': '11999887766',
        'telefone': '1133334444',
        'endereco': 'Rua das Flores, 123',
        'numero': '123',
        'bairro': 'Jardim Primavera',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01234-567',
        'status': 'Ativo',
        'origem': 'Indicação',
        'observacoes': 'Cliente interessado em forro PVC para sala'
    },
    {
        'nome': 'João Carlos Oliveira',
        'cpf_cnpj': '98765432100',
        'email': 'joao.oliveira@gmail.com',
        'celular': '11988776655',
        'endereco': 'Av. Santos Dumont, 456',
        'bairro': 'Centro',
        'cidade': 'Guarulhos',
        'estado': 'SP',
        'cep': '07010-100',
        'observacoes': 'Orçamento para escritório home office'
    },
    {
        'nome': 'Ana Paula Costa',
        'cpf_cnpj': '11122233344',
        'email': 'ana.costa@hotmail.com',
        'celular': '11977665544',
        'endereco': 'Rua Amazonas, 789',
        'bairro': 'Vila Madalena',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'observacoes': 'Cliente VIP - atendimento prioritário'
    }
]

# EXEMPLO 2: Clientes empresariais
dados_exemplo_empresarial = [
    {
        'nome': 'Construtech Engenharia Ltda',
        'cpf_cnpj': '12345678000195',  # CNPJ teste
        'rg_ie': '123456789.00112',
        'email': 'contato@construtech.com.br',
        'celular': '11999888777',
        'telefone': '1130005000',
        'endereco': 'Av. Paulista, 1000',
        'numero': '1000',
        'bairro': 'Bela Vista',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01310-100',
        'status': 'Ativo',
        'origem': 'Site',
        'observacoes': 'Empresa de grande porte - projetos comerciais'
    },
    {
        'nome': 'Decorações Modernas ME',
        'cpf_cnpj': '98765432000188',
        'email': 'vendas@decoracoesmodernas.com',
        'celular': '11988887777',
        'endereco': 'Rua do Comércio, 250',
        'bairro': 'Brás',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'observacoes': 'Parceiro comercial - revenda'
    }
]


def executar_importacao_teste():
    """Executar importação de teste"""
    importador = ImportadorClientesSimples()
    
    print("=" * 60)
    print("🎯 IMPORTADOR DE CLIENTES - TESTE")
    print("=" * 60)
    
    # Escolher qual conjunto importar
    print("\nEscolha os dados para importar:")
    print("1 - Clientes Residenciais (3 registros)")
    print("2 - Clientes Empresariais (2 registros)")
    print("3 - Todos (5 registros)")
    
    escolha = input("\nDigite sua opção (1-3): ").strip()
    
    if escolha == "1":
        dados = dados_exemplo_residencial
        print("\n🏠 Importando clientes RESIDENCIAIS...")
    elif escolha == "2":
        dados = dados_exemplo_empresarial
        print("\n🏢 Importando clientes EMPRESARIAIS...")
    elif escolha == "3":
        dados = dados_exemplo_residencial + dados_exemplo_empresarial
        print("\n🌟 Importando TODOS os clientes...")
    else:
        print("❌ Opção inválida!")
        return False
    
    # Executar importação
    resultado = importador.importar_clientes(dados)
    
    print("\n" + "=" * 60)
    
    if resultado:
        print("🎉 IMPORTAÇÃO BEM SUCEDIDA!")
        print("\n💡 Para verificar os dados importados:")
        print("   1. Inicie o servidor: python -m uvicorn backend.api.main:app --port 8002")
        print("   2. Abra o sistema desktop: python frontend/desktop/login_tkinter.py")
        print("   3. Acesse o módulo de Clientes")
    else:
        print("❌ IMPORTAÇÃO FALHOU!")
        print("Verifique os logs acima para detalhes.")
    
    return resultado


if __name__ == "__main__":
    executar_importacao_teste()