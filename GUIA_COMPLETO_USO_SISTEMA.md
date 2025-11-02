# GUIA COMPLETO - SISTEMA ERP PRIMOTEX
## Como Usar em Diferentes Situações

---

## 📖 ÍNDICE
1. [Cenário 1: Desktop da Recepção (Sem Banco)](#cenário-1)
2. [Cenário 2: Com Servidor no Escritório](#cenário-2)
3. [Cenário 3: Usando em Rede Local](#cenário-3)
4. [Cenário 4: Servidor na Nuvem](#cenário-4)

---

## 🏢 CENÁRIO 1: DESKTOP DA RECEPÇÃO (SEM BANCO DE DADOS)
**Situação:** Computador simples na recepção, sem servidor, sem internet

### O QUE VOCÊ PRECISA:
- ✅ Computador com Windows
- ✅ Python instalado
- ✅ Arquivo do sistema

### PASSO A PASSO:

#### 1️⃣ **Preparar o Sistema**
```bash
# Baixar apenas 1 arquivo:
sistema_recepcao_simples.py
```

#### 2️⃣ **Usar o Sistema**
```bash
# Abrir terminal (cmd ou PowerShell)
cd C:\pasta_do_sistema
python sistema_recepcao_simples.py
```

#### 3️⃣ **Menu Principal**
```
========================================
    SISTEMA ERP PRIMOTEX - RECEPÇÃO
========================================
1. Buscar Cliente
2. Cadastrar Novo Cliente  
3. Agendar Visita Técnica
4. Ver Agendamentos do Dia
5. Registrar Visita Realizada
6. Agenda da Semana
0. Sair
========================================
```

#### 4️⃣ **Como Usar Cada Função**

**📋 CADASTRAR CLIENTE:**
- Digite 2 → ENTER
- Nome: João Silva
- Telefone: (11) 99999-9999
- CPF: 123.456.789-00 (opcional)
- Endereço: Rua das Flores, 123 (opcional)

**🔍 BUSCAR CLIENTE:**
- Digite 1 → ENTER  
- Digite: João (ou telefone ou CPF)
- Sistema mostra todos os dados

**📅 AGENDAR VISITA:**
- Digite 3 → ENTER
- Busca cliente: João
- Data: 15/11/2025
- Horário: 14:30
- Serviço: Instalação de forro

### ✅ **VANTAGENS:**
- ✅ Funciona sem internet
- ✅ Não precisa de servidor
- ✅ Dados salvos em arquivos locais
- ✅ Interface simples de terminal

### ⚠️ **LIMITAÇÕES:**
- ❌ Apenas 1 computador
- ❌ Sem backup automático
- ❌ Funcionalidades básicas

---

## 🖥️ CENÁRIO 2: COM SERVIDOR NO ESCRITÓRIO
**Situação:** Você instalou um servidor no escritório principal

### O QUE VOCÊ PRECISA:
- ✅ Computador servidor (escritório)
- ✅ Sistema ERP completo
- ✅ Banco de dados SQLite

### PASSO A PASSO:

#### 1️⃣ **No Computador Servidor**
```bash
# 1. Ir para a pasta do sistema
cd C:\GIES

# 2. Iniciar o servidor
python -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8002
```

#### 2️⃣ **Verificar se Funcionou**
```bash
# Abrir navegador e acessar:
http://127.0.0.1:8002/docs

# Ou testar com script:
python teste_sistema_rapido.py
```

#### 3️⃣ **Usar Interface Desktop**
```bash
# No mesmo computador servidor:
cd frontend/desktop
python login_tkinter.py

# Login:
Usuário: admin
Senha: admin123
```

### ✅ **FUNCIONALIDADES DISPONÍVEIS:**
- ✅ Sistema completo de clientes
- ✅ Controle de produtos e estoque
- ✅ Códigos de barras
- ✅ Relatórios em PDF
- ✅ Sistema de agendamento
- ✅ Dashboard completo

---

## 🌐 CENÁRIO 3: USANDO EM REDE LOCAL
**Situação:** Servidor no escritório + computadores da recepção/técnicos na mesma rede

### O QUE VOCÊ PRECISA:
- ✅ Servidor (escritório) 
- ✅ Computadores clientes (recepção, técnicos)
- ✅ Rede local (WiFi ou cabo)

### PASSO A PASSO:

#### 1️⃣ **Configurar Servidor para Rede**
```bash
# No computador servidor, descobrir IP local:
ipconfig

# Exemplo de resultado:
# IPv4: 192.168.1.100

# Iniciar servidor para rede:
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8002
```

#### 2️⃣ **Configurar Firewall (Windows)**
```bash
# Permitir porta 8002 no firewall:
# Painel de Controle → Firewall → Permitir programa
# Adicionar porta 8002 TCP
```

#### 3️⃣ **Nos Computadores Clientes**

**📱 OPÇÃO A: Interface Web**
```bash
# Abrir navegador em qualquer computador da rede:
http://192.168.1.100:8002/docs

# Para login via web:
http://192.168.1.100:8002/api/v1/auth/login
```

**🖥️ OPÇÃO B: Sistema Desktop**
```bash
# Modificar arquivo de configuração no cliente:
# frontend/desktop/config.py
API_BASE_URL = "http://192.168.1.100:8002"

# Executar:
python login_tkinter.py
```

#### 4️⃣ **Testar Conectividade**
```bash
# Em qualquer computador da rede:
ping 192.168.1.100
curl http://192.168.1.100:8002/health
```

### ✅ **VANTAGENS:**
- ✅ Múltiplos usuários simultâneos
- ✅ Dados centralizados
- ✅ Backup único
- ✅ Mesma versão para todos

---

## ☁️ CENÁRIO 4: SERVIDOR NA NUVEM
**Situação:** Sistema hospedado na internet (AWS, Azure, etc.)

### O QUE VOCÊ PRECISA:
- ✅ Servidor na nuvem (VPS)
- ✅ Domínio ou IP público
- ✅ Internet em todos os locais

### PASSO A PASSO:

#### 1️⃣ **Configurar Servidor na Nuvem**

**🌐 OPÇÃO A: VPS Simples**
```bash
# No servidor remoto (Linux):
sudo apt update
sudo apt install python3 python3-pip
git clone https://github.com/Vandercy62/GIES.git
cd GIES
pip3 install -r requirements.txt

# Iniciar servidor público:
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8002
```

**🔒 OPÇÃO B: Com Domínio e SSL**
```bash
# Usar nginx + Let's Encrypt
# Domínio: https://primotex-erp.com.br
# Porta padrão: 443 (HTTPS)
```

#### 2️⃣ **Configurar Segurança**
```bash
# Configurar firewall no servidor:
sudo ufw allow 8002
sudo ufw allow ssh
sudo ufw enable

# Alterar senha padrão:
# admin/admin123 → senha_segura_empresa
```

#### 3️⃣ **Acessar de Qualquer Local**

**📱 MODO WEB:**
```bash
# Qualquer navegador, qualquer lugar:
https://seu-dominio.com.br:8002/docs

# Login via API:
POST https://seu-dominio.com.br:8002/api/v1/auth/login
```

**🖥️ MODO DESKTOP:**
```bash
# Configurar clientes para servidor remoto:
# config.py
API_BASE_URL = "https://seu-dominio.com.br:8002"

# Funciona de qualquer computador com internet
```

#### 4️⃣ **Backup e Monitoramento**
```bash
# Backup automático do banco:
# Cron job diário para backup do primotex_erp.db

# Monitoramento:
# Verificar se API responde a cada 5 minutos
```

### ✅ **VANTAGENS:**
- ✅ Acesso de qualquer lugar do mundo
- ✅ Backup profissional
- ✅ Escalabilidade
- ✅ Múltiplos usuários
- ✅ Atualizações centralizadas

### 💰 **CUSTOS ESTIMADOS:**
- **VPS Básico:** R$ 20-50/mês
- **Domínio:** R$ 40/ano  
- **SSL:** Gratuito (Let's Encrypt)

---

## 🚀 COMPARAÇÃO RÁPIDA

| Cenário | Complexidade | Custo | Usuários | Internet | Backup |
|---------|-------------|-------|----------|----------|---------|
| **Recepção Local** | ⭐ | Grátis | 1 | ❌ | Manual |
| **Servidor Escritório** | ⭐⭐ | Grátis | 3-5 | ❌ | Local |
| **Rede Local** | ⭐⭐⭐ | Grátis | 10+ | ❌ | Centralizado |
| **Nuvem** | ⭐⭐⭐⭐ | R$ 60/mês | Ilimitado | ✅ | Profissional |

---

## 📞 SUPORTE RÁPIDO

### 🔧 **Comandos Úteis:**
```bash
# Testar sistema local:
python teste_sistema_rapido.py

# Iniciar servidor simples:
python sistema_recepcao_simples.py

# Iniciar servidor completo:
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8002

# Ver IP da máquina:
ipconfig (Windows) / ifconfig (Linux)

# Testar conectividade:
ping IP_DO_SERVIDOR
curl http://IP_DO_SERVIDOR:8002/health
```

### 🆘 **Solução de Problemas:**
- **Erro de porta:** Mude para 8003, 8004, etc.
- **Não conecta na rede:** Verificar firewall
- **Dados perdidos:** Verificar pasta `dados_recepcao/`
- **Login não funciona:** Usar `admin` / `admin123`

---

## ✅ **PRÓXIMOS PASSOS:**

1. **Hoje:** Use sistema da recepção local
2. **Amanhã:** Configure servidor no escritório  
3. **Próxima semana:** Conecte todos os computadores
4. **Próximo mês:** Considere migrar para nuvem

**🎯 RECOMENDAÇÃO:** Comece com o sistema local da recepção e evolua conforme a necessidade!