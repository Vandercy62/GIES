# 📥 INSTALAÇÃO PASSO A PASSO - ERP PRIMOTEX
## Guia Completo com Explicações Detalhadas

---

## 🎯 **O QUE VAMOS FAZER:**
1. ✅ Verificar pré-requisitos
2. ✅ Baixar o sistema
3. ✅ Instalar dependências
4. ✅ Testar funcionamento
5. ✅ Configurar conforme sua necessidade

---

## 📋 **PRÉ-REQUISITOS (5 minutos)**

### **PASSO 1: Verificar Python**
```bash
# Abrir PowerShell (Windows + R → digite "powershell")
python --version
```

**✅ Resultado esperado:** `Python 3.8.x` ou superior  
**❌ Se der erro:** [Baixar Python](https://www.python.org/downloads/)

**💡 Explicação:** Python é a linguagem que executa o sistema

---

### **PASSO 2: Verificar Git**
```bash
git --version
```

**✅ Resultado esperado:** `git version 2.x.x`  
**❌ Se der erro:** [Baixar Git](https://git-scm.com/download/win)

**💡 Explicação:** Git baixa o código do sistema do GitHub

---

## 💾 **BAIXAR O SISTEMA (2 minutos)**

### **PASSO 3: Escolher pasta de instalação**
```bash
# Criar pasta para o sistema (exemplo: C:\ERP_Primotex)
mkdir C:\ERP_Primotex
cd C:\ERP_Primotex
```

**💡 Explicação:** Organiza os arquivos em uma pasta específica

---

### **PASSO 4: Baixar código do GitHub**
```bash
# Baixar sistema completo
git clone https://github.com/Vandercy62/GIES.git

# Entrar na pasta
cd GIES
```

**✅ Resultado esperado:** Pasta `GIES` criada com arquivos do sistema  
**💡 Explicação:** Baixa todo o código do sistema para seu computador

---

## 🔧 **INSTALAR DEPENDÊNCIAS (3 minutos)**

### **PASSO 5: Verificar arquivos baixados**
```bash
# Listar arquivos principais
dir
```

**✅ Deve aparecer:** `backend/`, `frontend/`, `requirements.txt`, etc.

---

### **PASSO 6: Instalar bibliotecas Python**
```bash
# Instalar todas as dependências de uma vez
pip install -r requirements.txt
```

**⏳ Aguarde:** Pode demorar 1-3 minutos  
**✅ Resultado esperado:** "Successfully installed..." várias vezes  
**💡 Explicação:** Instala todas as bibliotecas que o sistema precisa

---

### **PASSO 7: Verificar instalação**
```bash
# Testar se as principais bibliotecas foram instaladas
python -c "import fastapi, uvicorn, sqlalchemy, tkinter; print('✅ Todas as dependências OK!')"
```

**✅ Resultado esperado:** `✅ Todas as dependências OK!`  
**❌ Se der erro:** Repetir passo 6

---

## 🚀 **TESTAR O SISTEMA (5 minutos)**

### **PASSO 8: Teste básico - Sistema de Recepção**
```bash
# Testar sistema mais simples primeiro
python sistema_recepcao_simples.py
```

**✅ O que deve aparecer:**
```
==================================================
    SISTEMA ERP PRIMOTEX - RECEPÇÃO
==================================================
1. 🔍 Buscar Cliente
2. 👤 Cadastrar Novo Cliente
3. 📅 Agendar Visita Técnica
...
```

**🎯 Como testar:**
1. Digite `2` → Cadastrar um cliente teste
2. Digite `1` → Buscar o cliente
3. Digite `0` → Sair

**💡 Explicação:** Este é o sistema básico offline. Se funcionar, todo o resto funcionará!

---

### **PASSO 9: Teste intermediário - Sistema Híbrido**
```bash
# Testar sistema com interface gráfica
python sistema_recepcao_completo.py
```

**✅ O que deve aparecer:** Janela gráfica com abas "Clientes" e "Agendamentos"  
**🎯 Como testar:** Clique no botão "🆕 Novo Cliente" e cadastre um cliente

**💡 Explicação:** Este sistema funciona online (com servidor) ou offline automaticamente

---

### **PASSO 10: Configuração automática**
```bash
# Usar o configurador inteligente
python configurador_rede.py
```

**✅ O que deve aparecer:**
```
============================================================
    CONFIGURADOR AUTOMÁTICO - ERP PRIMOTEX
============================================================
🔍 DETECTANDO SISTEMA...
...
1. 🏢 RECEPÇÃO HÍBRIDA - Interface gráfica (online/offline)
2. 🖥️  LOCAL - Servidor no mesmo computador
...
```

**🎯 Como testar:** Digite `1` e siga as instruções

**💡 Explicação:** Este script detecta seu sistema e configura automaticamente

---

## ⚙️ **CONFIGURAR PARA SUA NECESSIDADE**

### **CENÁRIO A: Apenas computador da recepção**
```bash
# Use sistema híbrido (recomendado)
python sistema_recepcao_completo.py

# OU sistema terminal simples
python sistema_recepcao_simples.py
```

**💡 Vantagem:** Funciona sem servidor, dados salvos localmente

---

### **CENÁRIO B: Servidor no escritório + recepção**
```bash
# 1. No computador do escritório (servidor)
python configurador_rede.py
# Escolha opção 2 (LOCAL)

# 2. Execute o arquivo criado
iniciar_local.bat

# 3. No computador da recepção
cd frontend/desktop
python login_tkinter.py
# Login: admin / admin123
```

**💡 Vantagem:** Sistema completo com todas as funcionalidades

---

### **CENÁRIO C: Múltiplos computadores em rede**
```bash
# 1. No computador servidor
python configurador_rede.py
# Escolha opção 3 (REDE)

# 2. Execute arquivo criado
iniciar_rede.bat

# 3. Anote o IP que aparece (ex: 192.168.1.100)

# 4. Nos outros computadores
# Abrir navegador: http://192.168.1.100:8002/docs
# OU usar sistema desktop configurado para o IP
```

**💡 Vantagem:** Todos acessam os mesmos dados centralizados

---

## 🆘 **RESOLUÇÃO DE PROBLEMAS**

### **Problema 1: "Python não é reconhecido"**
**Solução:**
1. Baixar Python em python.org
2. **IMPORTANTE:** Marcar "Add Python to PATH"
3. Reiniciar PowerShell

---

### **Problema 2: "pip não funciona"**
**Solução:**
```bash
# Usar caminho completo
python -m pip install -r requirements.txt
```

---

### **Problema 3: "Erro ao instalar dependências"**
**Solução:**
```bash
# Atualizar pip primeiro
python -m pip install --upgrade pip

# Instalar uma por vez
pip install fastapi
pip install uvicorn
pip install sqlalchemy
pip install requests
```

---

### **Problema 4: "tkinter não encontrado"**
**Solução:**
- **Windows:** tkinter vem com Python (reinstale Python)
- **Linux:** `sudo apt-get install python3-tk`

---

### **Problema 5: "Porta 8002 em uso"**
**Solução:**
```bash
# Matar processos Python
taskkill /F /IM python.exe

# Usar outra porta
python -m uvicorn backend.api.main:app --port 8003
```

---

### **Problema 6: "Sistema não conecta na rede"**
**Solução:**
```bash
# Verificar IP do servidor
ipconfig

# Liberar firewall (como administrador)
netsh advfirewall firewall add rule name="ERP Primotex" dir=in action=allow protocol=TCP localport=8002
```

---

## ✅ **VALIDAÇÃO FINAL**

### **Checklist de funcionamento:**
- [ ] Sistema de recepção simples abre e funciona
- [ ] Sistema híbrido abre interface gráfica
- [ ] Configurador detecta sistema corretamente
- [ ] Consegue cadastrar cliente de teste
- [ ] Dados são salvos (pasta `dados_recepcao/` criada)

### **Se TODOS os itens estão ✅:**
🎉 **PARABÉNS! Sistema instalado com sucesso!**

---

## 🎯 **PRÓXIMOS PASSOS**

### **Para uso imediato:**
```bash
# Sistema mais completo
python sistema_recepcao_completo.py
```

### **Para configuração avançada:**
```bash
# Configurador automático
python configurador_rede.py
```

### **Para sistema completo com servidor:**
```bash
# Configurar servidor
python configurador_rede.py → Opção 2

# Acessar interface desktop
cd frontend/desktop
python login_tkinter.py
```

---

## 📞 **SUPORTE**

### **Se ainda tiver problemas:**
1. **Verifique:** Todos os passos foram seguidos?
2. **Teste:** `python sistema_recepcao_simples.py` funciona?
3. **Verifique:** Python versão 3.8+ instalado?
4. **Reinicie:** Computador e tente novamente

### **Arquivos de ajuda:**
- `RESUMO_EXECUTIVO.md` - Comandos essenciais
- `GUIA_COMPLETO_USO_SISTEMA.md` - Manual detalhado
- `configurador_rede.py` - Configuração automática

---

## 📱 **RESUMO DOS COMANDOS PRINCIPAIS**

```bash
# INSTALAÇÃO
git clone https://github.com/Vandercy62/GIES.git
cd GIES
pip install -r requirements.txt

# TESTES
python sistema_recepcao_simples.py      # Básico
python sistema_recepcao_completo.py     # Híbrido
python configurador_rede.py             # Automático

# SISTEMA COMPLETO
python configurador_rede.py → Opção 2   # Servidor local
cd frontend/desktop && python login_tkinter.py  # Interface
```

---

**🎯 Tempo total estimado:** 15-20 minutos  
**💾 Espaço necessário:** ~100MB  
**🔧 Dificuldade:** Fácil (seguindo o passo a passo)  

*Última atualização: 01/11/2025*