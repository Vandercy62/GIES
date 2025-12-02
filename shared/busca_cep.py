"""
SISTEMA ERP PRIMOTEX - BUSCA DE CEP
===================================

Integração com API ViaCEP para busca automática de endereços.

API: https://viacep.com.br/
Exemplo: https://viacep.com.br/ws/01310100/json/

Autor: GitHub Copilot
Data: 16/11/2025 - FASE 100
"""

import requests  # type: ignore
from typing import Optional, Dict


def buscar_endereco_por_cep(cep: str) -> Optional[Dict[str, str]]:
    """
    Busca endereço completo através do CEP usando API ViaCEP.

    Args:
        cep: CEP com ou sem formatação (ex: "01310-100" ou "01310100")

    Returns:
        Dict com dados do endereço ou None se não encontrado
        {
            'cep': '01310-100',
            'logradouro': 'Avenida Paulista',
            'complemento': '',
            'bairro': 'Bela Vista',
            'localidade': 'São Paulo',
            'uf': 'SP',
            'erro': False
        }
    """
    try:
        # Remove formatação do CEP
        cep_limpo = cep.replace('-', '').replace('.', '').strip()

        # Valida tamanho
        if len(cep_limpo) != 8 or not cep_limpo.isdigit():
            return None

        # Monta URL da API
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

        # Faz requisição
        response = requests.get(url, timeout=5)

        # Verifica status
        if response.status_code != 200:
            return None

        # Parse JSON
        dados = response.json()

        # Verifica se encontrou
        if dados.get('erro'):
            return None

        # Retorna dados formatados
        return {
            'cep': dados.get('cep', ''),
            'logradouro': dados.get('logradouro', ''),
            'complemento': dados.get('complemento', ''),
            'bairro': dados.get('bairro', ''),
            'cidade': dados.get('localidade', ''),
            'estado': dados.get('uf', ''),
            'ibge': dados.get('ibge', ''),
            'ddd': dados.get('ddd', '')
        }

    except requests.exceptions.Timeout:
        print("⚠️ Timeout ao buscar CEP")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erro ao buscar CEP: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"⚠️ Erro ao processar dados do CEP: {e}")
        return None


# Teste rápido
if __name__ == "__main__":
    print("🔍 Testando busca de CEP...")

    # Teste 1: CEP da Av. Paulista
    resultado = buscar_endereco_por_cep("01310-100")
    if resultado:
        print("\n✅ CEP encontrado:")
        print(f"  Logradouro: {resultado['logradouro']}")
        print(f"  Bairro: {resultado['bairro']}")
        print(f"  Cidade: {resultado['cidade']}")
        print(f"  Estado: {resultado['estado']}")
    else:
        print("\n❌ CEP não encontrado")

    # Teste 2: CEP inválido
    resultado2 = buscar_endereco_por_cep("00000-000")
    if resultado2:
        print("\n✅ CEP 2 encontrado")
    else:
        print("\n❌ CEP 2 não encontrado (esperado)")
