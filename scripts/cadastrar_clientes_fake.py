"""
Script para cadastrar 10 clientes PF e 10 clientes PJ automaticamente no ERP Primotex.
"""
import requests
from faker import Faker
import random
import string

BASE_URL = "http://127.0.0.1:8002"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
CLIENTES_URL = f"{BASE_URL}/api/v1/clientes"

fake = Faker('pt_BR')
codigos_usados = set()

# 1. Login para obter token
login_data = {"username": "admin", "password": "admin123"}
resp = requests.post(LOGIN_URL, json=login_data)
resp.raise_for_status()
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

def gerar_cliente_pf():
    # Garante código único
    while True:
        codigo = fake.unique.bothify(text="CLI###")
        if codigo not in codigos_usados:
            codigos_usados.add(codigo)
            break
    cpf = fake.cpf().replace(".", "").replace("-", "")
    if len(cpf) != 11:
        cpf = (cpf + "0"*11)[:11]
    return {
        "codigo": codigo,
        "tipo_pessoa": "Física",
        "nome": fake.name(),
        "cpf_cnpj": cpf,
        "rg_ie": fake.bothify(text="########"),
        "status": "Ativo",
        "origem": random.choice(["Indicação", "Site", "Instagram", "Feira"]),
        "tipo_cliente": random.choice(["Residencial", "Comercial"]),
        "endereco_cep": fake.postcode(),
        "endereco_logradouro": fake.street_name(),
        "endereco_numero": fake.building_number(),
        "endereco_complemento": "",
        "endereco_bairro": fake.bairro(),
        "endereco_cidade": fake.city(),
        "endereco_estado": fake.estado_sigla(),
        "telefone_fixo": fake.phone_number(),
        "telefone_celular": fake.cellphone_number(),
        "telefone_whatsapp": fake.cellphone_number(),
        "email_principal": fake.email(),
        "email_secundario": fake.free_email(),
        "observacoes_gerais": fake.sentence(nb_words=8)
    }

def gerar_cliente_pj():
    # Garante código único
    while True:
        codigo = fake.unique.bothify(text="CLI###")
        if codigo not in codigos_usados:
            codigos_usados.add(codigo)
            break
    cnpj = fake.cnpj().replace(".", "").replace("/", "").replace("-", "")
    if len(cnpj) != 14:
        cnpj = (cnpj + "0"*14)[:14]
    return {
        "codigo": codigo,
        "tipo_pessoa": "Jurídica",
        "nome": fake.company(),
        "cpf_cnpj": cnpj,
        "rg_ie": fake.bothify(text="##########"),
        "status": "Ativo",
        "origem": random.choice(["Indicação", "Site", "Instagram", "Feira"]),
        "tipo_cliente": random.choice(["Residencial", "Comercial"]),
        "endereco_cep": fake.postcode(),
        "endereco_logradouro": fake.street_name(),
        "endereco_numero": fake.building_number(),
        "endereco_complemento": "",
        "endereco_bairro": fake.bairro(),
        "endereco_cidade": fake.city(),
        "endereco_estado": fake.estado_sigla(),
        "telefone_fixo": fake.phone_number(),
        "telefone_celular": fake.cellphone_number(),
        "telefone_whatsapp": fake.cellphone_number(),
        "email_principal": fake.company_email(),
        "email_secundario": fake.free_email(),
        "observacoes_gerais": fake.sentence(nb_words=8)
    }

# 2. Cadastrar 10 PF
for i in range(10):
    cliente = gerar_cliente_pf()
    r = requests.post(CLIENTES_URL, headers=headers, json=cliente)
    try:
        resp_json = r.json()
        print(f"PF {i+1}: {r.status_code} - {resp_json}")
    except Exception:
        print(f"PF {i+1}: {r.status_code} - {r.text}")

# 3. Cadastrar 10 PJ
for i in range(10):
    cliente = gerar_cliente_pj()
    r = requests.post(CLIENTES_URL, headers=headers, json=cliente)
    try:
        resp_json = r.json()
        print(f"PJ {i+1}: {r.status_code} - {resp_json}")
    except Exception:
        print(f"PJ {i+1}: {r.status_code} - {r.text}")
