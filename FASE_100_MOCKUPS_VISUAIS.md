# 🎨 MOCKUP VISUAL - INTERFACE 4 ABAS DE CLIENTES

## 📋 ABA 1 - LISTA DE CLIENTES

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏢 PRIMOTEX - GERENCIAMENTO DE CLIENTES                     👤 admin | 🚪 Sair │
├─────────────────────────────────────────────────────────────────────────────────┤
│  [📋 Lista]  [ Dados Básicos ]  [ Complementares ]  [ Observações ]            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  🔍 Buscar: [________________________]  Status: [Todos ▼]  Tipo: [Todos ▼]     │
│                                                                                  │
│  [➕ NOVO CLIENTE]  [✏️ EDITAR]  [🗑️ EXCLUIR]  [🖨️ IMPRIMIR LISTA]           │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │ ID │ Código  │ Nome/Razão Social     │ Tipo    │ CPF/CNPJ       │ Telefone│ │
│  ├────┼─────────┼──────────────────────┼─────────┼────────────────┼─────────┤ │
│  │ 1  │ CLI001  │ João Silva Construç..│ Comerci │ 12.345.678/000 │ (16)333 │ │
│  │ 2  │ CLI002  │ Maria Santos         │ Residen │ 123.456.789-00 │ (16)999 │ │
│  │ 3  │ CLI003  │ Prefeitura Municipal │ Público │ 45.678.901/000 │ (16)333 │ │
│  │... │ ...     │ ...                  │ ...     │ ...            │ ...     │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  📊 Total: 127 clientes | ✅ Ativos: 95 | ⏸️ Inativos: 32                      │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 👤 ABA 2 - DADOS BÁSICOS

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏢 PRIMOTEX - GERENCIAMENTO DE CLIENTES                     👤 admin | 🚪 Sair │
├─────────────────────────────────────────────────────────────────────────────────┤
│  [ Lista ]  [👤 Dados Básicos]  [ Complementares ]  [ Observações ]     2/4     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  📝 DADOS BÁSICOS DO CLIENTE                                                    │
│                                                                                  │
│  Código: CLI004 (automático)                                    [📷 FOTO]       │
│                                                                  ┌──────────┐    │
│  Tipo de Pessoa: ⦿ Pessoa Física    ○ Pessoa Jurídica          │          │    │
│                                                                  │   Foto   │    │
│  Nome Completo: ⭐                                              │  Cliente │    │
│  [________________________________________________]              └──────────┘    │
│                                                                  [CAPTURAR]     │
│  CPF: ⭐                                                        [UPLOAD]       │
│  [___.___.___-__]  ✅                                                          │
│                                                                                  │
│  RG:                                                                             │
│  [_______________________]                                                       │
│                                                                                  │
│  Data de Nascimento:                                                             │
│  [__/__/____]  📅                                                               │
│                                                                                  │
│  Status:                                                                         │
│  [Ativo ▼]                                                                      │
│                                                                                  │
│  Como conheceu a Primotex?                                                       │
│  [Indicação ▼]                                                                  │
│                                                                                  │
│  Tipo de Cliente:                                                                │
│  [Residencial ▼]                                                                │
│                                                                                  │
│                                                                                  │
│  [⬅️ VOLTAR]              [💾 SALVAR E CONTINUAR]              [➡️ PRÓXIMO] │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏠 ABA 3 - DADOS COMPLEMENTARES

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏢 PRIMOTEX - GERENCIAMENTO DE CLIENTES                     👤 admin | 🚪 Sair │
├─────────────────────────────────────────────────────────────────────────────────┤
│  [ Lista ]  [ Dados Básicos ]  [🏠 Complementares]  [ Observações ]      3/4    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─ 📍 ENDEREÇO ───────────────┐  ┌─ 📞 CONTATOS ──────────────┐               │
│  │                              │  │                             │               │
│  │  CEP: ⭐                    │  │  Telefone Fixo:             │               │
│  │  [_____-___] 🔍             │  │  [(__) ____-____]          │               │
│  │                              │  │                             │               │
│  │  Logradouro:                 │  │  Celular: ⭐               │               │
│  │  [_______________________]   │  │  [(__) _____-____]         │               │
│  │                              │  │                             │               │
│  │  Número:      Compl.:        │  │  WhatsApp:                  │               │
│  │  [_____]      [_________]    │  │  [(__) _____-____]         │               │
│  │                              │  │                             │               │
│  │  Bairro:                     │  │  Email Principal: ⭐       │               │
│  │  [_______________________]   │  │  [___________________]     │               │
│  │                              │  │                             │               │
│  │  Cidade:          UF:        │  │  Email Secundário:          │               │
│  │  [_____________]  [SP ▼]    │  │  [___________________]     │               │
│  │                              │  │                             │               │
│  └──────────────────────────────┘  │  Site:                      │               │
│                                     │  [___________________]     │               │
│  ┌─ 💳 DADOS COMERCIAIS ───────┐  │                             │               │
│  │                              │  │  [➕ ADICIONAR CONTATO]    │               │
│  │  Limite de Crédito:          │  │                             │               │
│  │  R$ [_____________.00]       │  └─────────────────────────────┘               │
│  │                              │                                                 │
│  │  Vencimento Preferencial:    │                                                 │
│  │  Dia [__] de cada mês        │                                                 │
│  │                              │                                                 │
│  │  Banco:                      │                                                 │
│  │  [_______________________]   │                                                 │
│  │                              │                                                 │
│  │  Agência:         Conta:     │                                                 │
│  │  [_______]        [________] │                                                 │
│  │                              │                                                 │
│  └──────────────────────────────┘                                                 │
│                                                                                  │
│  [⬅️ ANTERIOR]            [💾 SALVAR E CONTINUAR]             [➡️ PRÓXIMO]  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📝 ABA 4 - OBSERVAÇÕES E IMPRESSÃO

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏢 PRIMOTEX - GERENCIAMENTO DE CLIENTES                     👤 admin | 🚪 Sair │
├─────────────────────────────────────────────────────────────────────────────────┤
│  [ Lista ]  [ Dados Básicos ]  [ Complementares ]  [📝 Observações]       4/4   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─ 📝 OBSERVAÇÕES ────────────────────────┐  ┌─ 🎯 AÇÕES ────────────────┐    │
│  │                                          │  │                            │    │
│  │  Observações Gerais:                     │  │  [📄 IMPRIMIR FICHA]      │    │
│  │  ┌────────────────────────────────────┐  │  │     COMPLETA              │    │
│  │  │                                    │  │  │                            │    │
│  │  │                                    │  │  ├────────────────────────────┤    │
│  │  │                                    │  │  │                            │    │
│  │  │                                    │  │  │  [📧 ENVIAR POR EMAIL]    │    │
│  │  │                                    │  │  │                            │    │
│  │  │                                    │  │  │  [📱 ENVIAR WHATSAPP]     │    │
│  │  │                                    │  │  │                            │    │
│  │  └────────────────────────────────────┘  │  ├────────────────────────────┤    │
│  │                                          │  │                            │    │
│  │  Tags/Categorias:                        │  │  [💾 SALVAR E FECHAR]     │    │
│  │  [VIP] [Cliente Frequente] [+]           │  │                            │    │
│  │                                          │  │  [❌ CANCELAR]            │    │
│  └──────────────────────────────────────────┘  │                            │    │
│                                                 └────────────────────────────┘    │
│  ┌─ 📎 ANEXOS ─────────────────────────────────────────────────────────────────┐ │
│  │                                                                              │ │
│  │  📄 Contrato_Assinado.pdf        (125 KB)    15/11/2025    [👁️] [🗑️]   │ │
│  │  🖼️ Planta_Baixa.jpg            (2.3 MB)    14/11/2025    [👁️] [🗑️]   │ │
│  │  📷 Foto_Local.jpg               (1.8 MB)    14/11/2025    [👁️] [🗑️]   │ │
│  │                                                                              │ │
│  │  [➕ ADICIONAR ANEXO]                                                       │ │
│  │                                                                              │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌─ 📊 HISTÓRICO DE INTERAÇÕES ────────────────────────────────────────────────┐ │
│  │                                                                              │ │
│  │  🕐 16/11/2025 10:30 - Cadastro criado por admin                           │ │
│  │  🕐 15/11/2025 14:20 - Orçamento #123 enviado por vendedor1                │ │
│  │  🕐 14/11/2025 09:15 - Visita técnica realizada por tecnico1               │ │
│  │  🕐 13/11/2025 16:45 - Primeiro contato por telefone                       │ │
│  │                                                                              │ │
│  └──────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  [⬅️ ANTERIOR]                              [💾 SALVAR E FECHAR]              │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🖨️ EXEMPLO DE FICHA IMPRESSA (PDF)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                       │
│   [LOGO PRIMOTEX]          FICHA CADASTRAL DE CLIENTE                │
│                                                                       │
│   Primotex - Forros e Divisórias Eireli                             │
│   Emitido em: 16/11/2025 às 18:30 por admin                         │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   DADOS BÁSICOS                                    [FOTO DO CLIENTE] │
│   ──────────────                                   ┌──────────────┐  │
│   Código: CLI004                                   │              │  │
│   Nome: João Silva Construções LTDA                │              │  │
│   Tipo: Pessoa Jurídica - Comercial               │              │  │
│   CNPJ: 12.345.678/0001-90                         └──────────────┘  │
│   Insc. Estadual: 123.456.789.123                                    │
│   Status: ✅ Ativo                                                   │
│   Origem: Indicação                                                  │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ENDEREÇO                                                            │
│   ────────                                                            │
│   Av. Industrial, 1500 - Sala 2                                      │
│   Centro - Araraquara/SP                                             │
│   CEP: 14800-123                                                     │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   CONTATOS                                                            │
│   ────────                                                            │
│   Telefone: (16) 3333-4444                                           │
│   Celular/WhatsApp: (16) 99999-8888                                  │
│   Email: contato@joaosilva.com.br                                    │
│   Site: www.joaosilva.com.br                                         │
│                                                                       │
│   Contato Adicional:                                                 │
│   - Maria Silva (Gerente Compras) - (16) 99888-7777                 │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   DADOS COMERCIAIS                                                    │
│   ────────────────                                                    │
│   Limite de Crédito: R$ 50.000,00                                    │
│   Vencimento Preferencial: Dia 10                                    │
│   Banco: Banco do Brasil - Ag: 1234-5 - CC: 12345-6                 │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   OBSERVAÇÕES                                                         │
│   ───────────                                                         │
│   Cliente VIP - Sempre solicita desconto de 5%                       │
│   Obras geralmente acima de 200m²                                    │
│   Preferência por forro PVC branco                                   │
│                                                                       │
│   Tags: [VIP] [Cliente Frequente] [Comercial]                       │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   HISTÓRICO                                                           │
│   ─────────                                                           │
│   Total de OS: 12 | Valor total: R$ 245.000,00                      │
│   Última compra: 15/11/2025 - OS #234                               │
│   Cliente desde: 10/01/2023                                          │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 PALETA DE CORES

```
PRIMÁRIAS:
- Verde Primotex:    #27ae60  (Botões de ação positiva)
- Azul Header:       #2c3e50  (Cabeçalhos)
- Azul Navegação:    #3498db  (Botão Anterior)

SECUNDÁRIAS:
- Cinza Claro:       #ecf0f1  (Fundos)
- Branco:            #ffffff  (Cards, campos)
- Cinza Médio:       #95a5a6  (Textos secundários)

FEEDBACK:
- Verde Sucesso:     #16a085  (Validação OK)
- Vermelho Erro:     #e74c3c  (Validação Erro / Cancelar)
- Amarelo Alerta:    #f39c12  (Avisos)
- Azul Info:         #3498db  (Informações)
```

---

## 📱 RESPONSIVIDADE

- **Mínimo:** 1024x768 (funciona, mas com scroll)
- **Recomendado:** 1366x768 ou superior
- **Ideal:** 1920x1080 (full HD)

---

**Criado por:** GitHub Copilot  
**Data:** 16/11/2025
