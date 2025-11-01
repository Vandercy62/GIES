# 🔧 GUIA DE SOLUÇÃO - Backend ERP Primotex

## 📋 Problema Identificado

O erro ocorre porque o **backend FastAPI não está rodando** na porta 8002. 
Os testes tentam se conectar ao servidor, mas não encontram nada rodando naquela porta.

```
❌ Erro: HTTPConnectionPool(host='127.0.0.1', port=8002): Max retries exceeded
```

---

## ✅ SOLUÇÃO PASSO A PASSO

### Opção 1: Usando os Scripts Automáticos (RECOMENDADO)

#### 1️⃣ Copie os arquivos para o projeto

Salve os arquivos que criei na **raiz do seu projeto** (C:\GIES\):
- `iniciar_backend.ps1`
- `executar_testes.ps1`

#### 2️⃣ Abra o PowerShell como Administrador

```powershell
# Navegue até a pasta do projeto
cd C:\GIES
```

#### 3️⃣ Execute o script de inicialização do backend

```powershell
.\iniciar_backend.ps1
```

Se aparecer erro de execução de scripts, execute primeiro:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4️⃣ Aguarde o backend iniciar

Você verá uma mensagem como:
```
INFO:     Uvicorn running on http://127.0.0.1:8002
INFO:     Application startup complete.
```

**⚠️ NÃO FECHE ESTE TERMINAL!** Deixe o backend rodando.

#### 5️⃣ Abra um NOVO terminal e execute os testes

Em outro PowerShell:
```powershell
cd C:\GIES
.\executar_testes.ps1
```

---

### Opção 2: Método Manual

Se preferir fazer manualmente:

#### Terminal 1 - Backend:
```powershell
cd C:\GIES
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

#### Terminal 2 - Testes:
```powershell
cd C:\GIES
.\.venv\Scripts\Activate.ps1
python tests\test_fase1.py
```

---

## 🔍 Verificações Importantes

### 1. Verificar se a porta 8002 está livre

```powershell
Get-NetTCPConnection -LocalPort 8002
```

Se retornar algo, a porta está ocupada. Para liberar:
```powershell
# Identifique o PID do processo
Get-NetTCPConnection -LocalPort 8002 | Select-Object -Property OwningProcess

# Finalize o processo (substitua XXXX pelo PID)
Stop-Process -Id XXXX -Force
```

### 2. Verificar se o backend iniciou corretamente

Abra no navegador:
- **Health Check**: http://127.0.0.1:8002/health
- **Documentação**: http://127.0.0.1:8002/docs

Se carregar, o backend está funcionando!

### 3. Verificar dependências instaladas

```powershell
pip list | Select-String "fastapi|uvicorn|sqlalchemy"
```

Se faltar algo:
```powershell
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv
```

---

## 🎯 Resultado Esperado

Após seguir os passos, você deverá ver:

```
🧪 SISTEMA ERP PRIMOTEX - TESTE FINAL DA FASE 1
📊 Testando health check... ✅ API está online
🗃️ Testando modelos do banco... ✅ 21 modelos carregados
🔐 Testando login... ✅ Login realizado com sucesso
📚 Testando documentação da API... ✅ Documentação acessível

============================================================
📊 RESULTADO FINAL: 6/6 testes passaram
✅ TODOS OS TESTES PASSARAM COM SUCESSO!
```

---

## 🆘 Problemas Comuns

### Erro: "Não foi possível encontrar o arquivo especificado"
**Solução**: Verifique se está na pasta raiz do projeto (C:\GIES\)

### Erro: "uvicorn não é reconhecido"
**Solução**: Instale o uvicorn
```powershell
pip install uvicorn[standard]
```

### Erro: "ModuleNotFoundError"
**Solução**: Instale todas as dependências
```powershell
pip install -r backend\requirements.txt
```

### Firewall do Windows bloqueia a porta
**Solução**: Clique em "Permitir acesso" quando aparecer o alerta do Windows Defender

---

## 📞 Precisa de Mais Ajuda?

Se os testes ainda falharem depois de seguir este guia:

1. Compartilhe o **log completo** do terminal do backend
2. Compartilhe o **log completo** do terminal dos testes
3. Informe o **sistema operacional** e **versão do Python**

---

**Última atualização**: 2025-10-31
**Versão do guia**: 1.0
