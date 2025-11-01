# 🚀 Scripts de Automação - ERP Primotex

## 📦 Arquivos Incluídos

1. **diagnostico.ps1** - Verifica se o ambiente está configurado corretamente
2. **iniciar_backend.ps1** - Inicia o servidor FastAPI automaticamente
3. **executar_testes.ps1** - Executa os testes da Fase 1
4. **GUIA_SOLUCAO_BACKEND.md** - Guia completo de resolução de problemas

## 🎯 Como Usar

### Primeira Vez? Comece Aqui! 👇

1. **Copie todos os arquivos** para a pasta raiz do projeto (C:\GIES\)

2. **Execute o diagnóstico** para verificar se está tudo OK:
   ```powershell
   .\diagnostico.ps1
   ```

3. Se tudo estiver OK, **inicie o backend**:
   ```powershell
   .\iniciar_backend.ps1
   ```

4. **Abra um NOVO terminal** e execute os testes:
   ```powershell
   .\executar_testes.ps1
   ```

---

## 📋 Ordem de Execução

```
┌─────────────────────┐
│  1. diagnostico.ps1 │  ← Execute primeiro para verificar tudo
└─────────────────────┘
           │
           ↓
┌─────────────────────┐
│2. iniciar_backend.ps1│ ← Deixe rodando (não feche!)
└─────────────────────┘
           │
           ↓
┌─────────────────────┐
│3. executar_testes.ps1│ ← Execute em outro terminal
└─────────────────────┘
```

---

## ⚠️ Problemas com Execução de Scripts?

Se aparecer erro tipo:
```
não pode ser carregado porque a execução de scripts foi desabilitada
```

**Solução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🔧 Atalhos Rápidos

### Verificar se backend está rodando:
```powershell
Get-NetTCPConnection -LocalPort 8002
```

### Acessar documentação da API:
Abra no navegador: http://127.0.0.1:8002/docs

### Parar o backend:
Pressione `Ctrl + C` no terminal onde está rodando

### Liberar porta 8002 se estiver ocupada:
```powershell
# Ver qual processo está usando
Get-NetTCPConnection -LocalPort 8002

# Finalizar processo (substitua XXXX pelo PID)
Stop-Process -Id XXXX -Force
```

---

## 📊 Resultado Esperado dos Testes

✅ **Sucesso completo:**
```
📊 RESULTADO FINAL: 6/6 testes passaram
✅ TODOS OS TESTES PASSARAM COM SUCESSO!
```

❌ **Se falhar:**
1. Verifique se o backend está rodando
2. Execute o `diagnostico.ps1` novamente
3. Consulte o `GUIA_SOLUCAO_BACKEND.md`

---

## 💡 Dicas Importantes

- ✅ Sempre execute o `diagnostico.ps1` quando tiver dúvidas
- ✅ Mantenha o backend rodando em um terminal separado
- ✅ Não feche o terminal do backend enquanto estiver testando
- ✅ Se algo der errado, reinicie o backend e tente novamente
- ✅ Verifique se está na pasta raiz do projeto (C:\GIES\)

---

## 🆘 Ainda com Problemas?

Leia o arquivo **GUIA_SOLUCAO_BACKEND.md** para soluções detalhadas de problemas comuns.

---

**Bons testes! 🚀**
