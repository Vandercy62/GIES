# 🔌 API Reference - PRIMOTEX ERP Mobile

> **Base URL**: `http://127.0.0.1:8002/api/v1`  
> **Authentication**: JWT Bearer Token  
> **Version**: 1.0.0

---

## 📋 **ÍNDICE**

1. [Autenticação](#-autenticação)
2. [Ordem de Serviço](#-ordem-de-serviço)
3. [Clientes](#-clientes)
4. [Agendamentos](#-agendamentos)
5. [Comunicação](#-comunicação)
6. [Financeiro](#-financeiro)
7. [Códigos de Status](#-códigos-de-status)
8. [Rate Limiting](#-rate-limiting)
9. [Webhooks](#-webhooks)

---

## 🔐 **AUTENTICAÇÃO**

### **POST** `/auth/login`
Autentica usuário e retorna JWT token.

#### **Request Body**
```json
{
  "username": "string",
  "password": "string"
}
```

#### **Response (200 OK)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer", 
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@primotex.com",
    "role": "administrador",
    "permissions": ["read", "write", "delete"],
    "profile": {
      "nome": "Administrador",
      "telefone": "+55 11 99999-9999",
      "avatar_url": "https://api.primotex.com/avatars/1.jpg"
    }
  }
}
```

#### **Response (401 Unauthorized)**
```json
{
  "detail": "Invalid credentials",
  "error_code": "AUTH_INVALID_CREDENTIALS",
  "timestamp": "2025-01-14T10:30:00Z"
}
```

### **POST** `/auth/refresh`
Renova token JWT válido.

#### **Headers**
```http
Authorization: Bearer <current_token>
```

#### **Response (200 OK)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### **POST** `/auth/logout`
Invalida token atual.

#### **Headers**
```http
Authorization: Bearer <token>
```

#### **Response (200 OK)**
```json
{
  "message": "Successfully logged out"
}
```

---

## 🛠️ **ORDEM DE SERVIÇO**

### **GET** `/os`
Lista ordens de serviço com paginação e filtros.

#### **Query Parameters**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | 1 | Página atual |
| `limit` | integer | 20 | Itens por página |
| `status` | string | - | Filtro por status |
| `cliente_id` | integer | - | Filtro por cliente |
| `tecnico_id` | integer | - | Filtro por técnico |
| `data_inicio` | date | - | Data início (YYYY-MM-DD) |
| `data_fim` | date | - | Data fim (YYYY-MM-DD) |
| `search` | string | - | Busca textual |

#### **Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "numero_os": "OS-2025-001",
      "cliente": {
        "id": 1,
        "nome": "João Silva",
        "telefone": "+55 11 99999-9999",
        "email": "joao@email.com"
      },
      "tipo_servico": "Instalação",
      "descricao": "Instalação de forro PVC no escritório",
      "status": "agendada",
      "prioridade": "media",
      "tecnico": {
        "id": 2,
        "nome": "Carlos Santos",
        "telefone": "+55 11 88888-8888"
      },
      "endereco": {
        "logradouro": "Rua das Flores, 123",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "cep": "01234-567",
        "latitude": -23.5505,
        "longitude": -46.6333
      },
      "agendamento": {
        "data_agendada": "2025-01-15T14:00:00Z",
        "tempo_estimado": 240
      },
      "valores": {
        "valor_orcamento": 1500.00,
        "valor_final": null,
        "desconto": 0.00
      },
      "anexos": [
        {
          "id": 1,
          "tipo": "foto",
          "url": "https://api.primotex.com/anexos/os1_foto1.jpg",
          "descricao": "Foto do local antes da instalação"
        }
      ],
      "created_at": "2025-01-14T10:00:00Z",
      "updated_at": "2025-01-14T10:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### **GET** `/os/{id}`
Obtém detalhes de uma ordem de serviço específica.

#### **Response (200 OK)**
```json
{
  "id": 1,
  "numero_os": "OS-2025-001",
  "cliente": {
    "id": 1,
    "nome": "João Silva",
    "telefone": "+55 11 99999-9999",
    "email": "joao@email.com",
    "endereco_principal": {
      "logradouro": "Rua Principal, 456",
      "bairro": "Vila Nova",
      "cidade": "São Paulo",
      "cep": "04567-890"
    }
  },
  "tipo_servico": "Instalação",
  "descricao": "Instalação de forro PVC no escritório",
  "status": "agendada",
  "prioridade": "media",
  "tecnico": {
    "id": 2,
    "nome": "Carlos Santos",
    "telefone": "+55 11 88888-8888",
    "especialidade": "Forros",
    "avaliacao": 4.8
  },
  "endereco_servico": {
    "logradouro": "Rua das Flores, 123",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "cep": "01234-567",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "observacoes": "Portão azul, tocar interfone 101"
  },
  "agendamento": {
    "data_agendada": "2025-01-15T14:00:00Z",
    "tempo_estimado": 240,
    "observacoes": "Cliente prefere período da tarde"
  },
  "materiais": [
    {
      "id": 1,
      "produto": "Forro PVC Branco",
      "quantidade": 15,
      "unidade": "m²",
      "valor_unitario": 25.00,
      "valor_total": 375.00
    }
  ],
  "valores": {
    "valor_materiais": 375.00,
    "valor_mao_obra": 1125.00,
    "valor_orcamento": 1500.00,
    "valor_final": null,
    "desconto": 0.00,
    "status_pagamento": "pendente"
  },
  "historico": [
    {
      "id": 1,
      "acao": "criacao",
      "descricao": "OS criada",
      "usuario": "Admin",
      "timestamp": "2025-01-14T10:00:00Z"
    },
    {
      "id": 2,
      "acao": "agendamento",
      "descricao": "OS agendada para 15/01/2025 às 14:00",
      "usuario": "Admin",
      "timestamp": "2025-01-14T10:30:00Z"
    }
  ],
  "anexos": [
    {
      "id": 1,
      "tipo": "foto",
      "url": "https://api.primotex.com/anexos/os1_foto1.jpg",
      "descricao": "Foto do local antes da instalação",
      "uploaded_at": "2025-01-14T10:15:00Z"
    }
  ],
  "assinatura_cliente": null,
  "created_at": "2025-01-14T10:00:00Z",
  "updated_at": "2025-01-14T10:30:00Z"
}
```

### **POST** `/os`
Cria nova ordem de serviço.

#### **Request Body**
```json
{
  "cliente_id": 1,
  "tipo_servico": "Instalação",
  "descricao": "Instalação de forro PVC no escritório",
  "prioridade": "media",
  "tecnico_id": 2,
  "endereco_servico": {
    "logradouro": "Rua das Flores, 123",
    "bairro": "Centro", 
    "cidade": "São Paulo",
    "cep": "01234-567",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "observacoes": "Portão azul, tocar interfone 101"
  },
  "agendamento": {
    "data_agendada": "2025-01-15T14:00:00Z",
    "tempo_estimado": 240,
    "observacoes": "Cliente prefere período da tarde"
  },
  "materiais": [
    {
      "produto_id": 1,
      "quantidade": 15,
      "valor_unitario": 25.00
    }
  ],
  "valor_orcamento": 1500.00
}
```

#### **Response (201 Created)**
```json
{
  "id": 1,
  "numero_os": "OS-2025-001",
  "status": "agendada",
  "message": "Ordem de serviço criada com sucesso"
}
```

### **PUT** `/os/{id}`
Atualiza ordem de serviço existente.

#### **Request Body** (campos opcionais)
```json
{
  "status": "em_andamento",
  "observacoes": "Iniciando serviço",
  "tecnico_id": 3,
  "valor_final": 1450.00
}
```

#### **Response (200 OK)**
```json
{
  "id": 1,
  "message": "Ordem de serviço atualizada com sucesso",
  "updated_fields": ["status", "observacoes", "valor_final"]
}
```

### **POST** `/os/{id}/status`
Atualiza status da ordem de serviço.

#### **Request Body**
```json
{
  "status": "concluida",
  "observacoes": "Serviço finalizado com sucesso",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "anexos": [
    {
      "tipo": "foto",
      "base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ...",
      "descricao": "Foto final do serviço"
    }
  ]
}
```

#### **Response (200 OK)**
```json
{
  "id": 1,
  "status": "concluida",
  "message": "Status atualizado com sucesso",
  "next_actions": [
    "gerar_nota_fiscal",
    "enviar_pesquisa_satisfacao"
  ]
}
```

### **POST** `/os/{id}/anexos`
Adiciona anexo à ordem de serviço.

#### **Request Body (multipart/form-data)**
```http
Content-Type: multipart/form-data

arquivo: [binary file data]
tipo: "foto"
descricao: "Foto do progresso do serviço"
latitude: -23.5505
longitude: -46.6333
```

#### **Response (201 Created)**
```json
{
  "id": 1,
  "url": "https://api.primotex.com/anexos/os1_anexo1.jpg",
  "tipo": "foto",
  "descricao": "Foto do progresso do serviço",
  "size": 2048576,
  "uploaded_at": "2025-01-14T15:30:00Z"
}
```

---

## 👥 **CLIENTES**

### **GET** `/clientes`
Lista clientes com paginação e busca.

#### **Query Parameters**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `page` | integer | 1 | Página atual |
| `limit` | integer | 20 | Itens por página |
| `search` | string | - | Busca por nome/email/telefone |
| `tipo` | string | - | "pessoa_fisica" ou "pessoa_juridica" |
| `ativo` | boolean | true | Filtro por status ativo |

#### **Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "nome": "João Silva",
      "email": "joao@email.com",
      "telefone": "+55 11 99999-9999",
      "tipo": "pessoa_fisica",
      "documento": "123.456.789-01",
      "endereco_principal": {
        "logradouro": "Rua Principal, 456",
        "bairro": "Vila Nova",
        "cidade": "São Paulo",
        "cep": "04567-890"
      },
      "stats": {
        "total_os": 5,
        "os_concluidas": 4,
        "valor_total": 7500.00
      },
      "ativo": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total": 1,
    "total_pages": 1
  }
}
```

### **GET** `/clientes/{id}`
Obtém detalhes completos de um cliente.

#### **Response (200 OK)**
```json
{
  "id": 1,
  "nome": "João Silva",
  "email": "joao@email.com",
  "telefone": "+55 11 99999-9999",
  "telefone_alternativo": "+55 11 88888-8888",
  "tipo": "pessoa_fisica",
  "documento": "123.456.789-01",
  "endereco_principal": {
    "logradouro": "Rua Principal, 456",
    "numero": "456",
    "complemento": "Apto 101",
    "bairro": "Vila Nova",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "04567-890",
    "latitude": -23.5505,
    "longitude": -46.6333
  },
  "enderecos_alternativos": [
    {
      "id": 1,
      "nome": "Escritório",
      "logradouro": "Av. Comercial, 789",
      "numero": "789",
      "bairro": "Centro",
      "cidade": "São Paulo",
      "estado": "SP",
      "cep": "01234-567"
    }
  ],
  "observacoes": "Cliente preferencial, atendimento VIP",
  "stats": {
    "total_os": 5,
    "os_concluidas": 4,
    "os_pendentes": 1,
    "valor_total": 7500.00,
    "ticket_medio": 1500.00,
    "ultima_os": "2025-01-10T00:00:00Z"
  },
  "preferencias": {
    "meio_comunicacao": "whatsapp",
    "periodo_contato": "manha",
    "receber_promocoes": true
  },
  "ativo": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-14T10:00:00Z"
}
```

### **POST** `/clientes`
Cria novo cliente.

#### **Request Body**
```json
{
  "nome": "Maria Santos",
  "email": "maria@email.com",
  "telefone": "+55 11 77777-7777",
  "tipo": "pessoa_fisica",
  "documento": "987.654.321-09",
  "endereco_principal": {
    "logradouro": "Rua Nova, 123",
    "numero": "123",
    "bairro": "Jardim Novo",
    "cidade": "São Paulo",
    "estado": "SP",
    "cep": "05678-901"
  },
  "observacoes": "Cliente indicado por João Silva",
  "preferencias": {
    "meio_comunicacao": "email",
    "periodo_contato": "tarde"
  }
}
```

#### **Response (201 Created)**
```json
{
  "id": 2,
  "nome": "Maria Santos",
  "message": "Cliente criado com sucesso"
}
```

---

## 📅 **AGENDAMENTOS**

### **GET** `/agendamentos`
Lista agendamentos por período.

#### **Query Parameters**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `data_inicio` | date | hoje | Data início (YYYY-MM-DD) |
| `data_fim` | date | +7 dias | Data fim (YYYY-MM-DD) |
| `tecnico_id` | integer | - | Filtro por técnico |
| `status` | string | - | Filtro por status |

#### **Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "os_id": 1,
      "numero_os": "OS-2025-001",
      "cliente": {
        "id": 1,
        "nome": "João Silva",
        "telefone": "+55 11 99999-9999"
      },
      "tecnico": {
        "id": 2,
        "nome": "Carlos Santos",
        "telefone": "+55 11 88888-8888"
      },
      "data_agendada": "2025-01-15T14:00:00Z",
      "tempo_estimado": 240,
      "tipo_servico": "Instalação",
      "status": "agendado",
      "endereco": {
        "logradouro": "Rua das Flores, 123",
        "bairro": "Centro",
        "cidade": "São Paulo"
      },
      "observacoes": "Cliente prefere período da tarde",
      "created_at": "2025-01-14T10:30:00Z"
    }
  ]
}
```

### **POST** `/agendamentos`
Cria novo agendamento.

#### **Request Body**
```json
{
  "os_id": 1,
  "tecnico_id": 2,
  "data_agendada": "2025-01-15T14:00:00Z",
  "tempo_estimado": 240,
  "observacoes": "Cliente prefere período da tarde"
}
```

#### **Response (201 Created)**
```json
{
  "id": 1,
  "message": "Agendamento criado com sucesso",
  "conflitos": []
}
```

### **PUT** `/agendamentos/{id}`
Atualiza agendamento existente.

#### **Request Body**
```json
{
  "data_agendada": "2025-01-16T09:00:00Z",
  "motivo_reagendamento": "Solicitação do cliente"
}
```

#### **Response (200 OK)**
```json
{
  "id": 1,
  "message": "Agendamento atualizado com sucesso",
  "notificacao_enviada": true
}
```

---

## 💬 **COMUNICAÇÃO**

### **GET** `/comunicacao/templates`
Lista templates de mensagem disponíveis.

#### **Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "nome": "confirmacao_agendamento",
      "titulo": "Confirmação de Agendamento",
      "tipo": "whatsapp",
      "template": "Olá {cliente_nome}! Seu agendamento está confirmado para {data_agendamento}. Técnico: {tecnico_nome}.",
      "variaveis": ["cliente_nome", "data_agendamento", "tecnico_nome"],
      "ativo": true
    }
  ]
}
```

### **POST** `/comunicacao/enviar`
Envia mensagem para cliente.

#### **Request Body**
```json
{
  "cliente_id": 1,
  "tipo": "whatsapp",
  "template_id": 1,
  "variaveis": {
    "cliente_nome": "João Silva",
    "data_agendamento": "15/01/2025 às 14:00",
    "tecnico_nome": "Carlos Santos"
  },
  "agendado_para": null
}
```

#### **Response (200 OK)**
```json
{
  "id": 1,
  "status": "enviado",
  "message": "Mensagem enviada com sucesso",
  "timestamp": "2025-01-14T11:00:00Z"
}
```

### **GET** `/comunicacao/historico/{cliente_id}`
Obtém histórico de comunicação com cliente.

#### **Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "tipo": "whatsapp",
      "template": "confirmacao_agendamento",
      "mensagem": "Olá João Silva! Seu agendamento está confirmado...",
      "status": "entregue",
      "enviado_em": "2025-01-14T11:00:00Z",
      "entregue_em": "2025-01-14T11:01:00Z",
      "lida_em": "2025-01-14T11:05:00Z"
    }
  ]
}
```

---

## 💰 **FINANCEIRO**

### **GET** `/financeiro/contas-receber`
Lista contas a receber.

#### **Query Parameters**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `status` | string | - | "pendente", "pago", "vencido" |
| `vencimento_inicio` | date | - | Data início vencimento |
| `vencimento_fim` | date | - | Data fim vencimento |

#### **Response (200 OK)**
```json
{
  "data": [
    {
      "id": 1,
      "os_id": 1,
      "numero_os": "OS-2025-001",
      "cliente": {
        "id": 1,
        "nome": "João Silva"
      },
      "valor": 1500.00,
      "data_vencimento": "2025-01-30",
      "status": "pendente",
      "forma_pagamento": "pix",
      "observacoes": "Pagamento via PIX após conclusão",
      "created_at": "2025-01-14T12:00:00Z"
    }
  ],
  "resumo": {
    "total_pendente": 1500.00,
    "total_vencido": 0.00,
    "total_recebido_mes": 5000.00
  }
}
```

### **POST** `/financeiro/registrar-pagamento`
Registra pagamento de conta.

#### **Request Body**
```json
{
  "conta_id": 1,
  "valor_pago": 1500.00,
  "forma_pagamento": "pix",
  "data_pagamento": "2025-01-14",
  "observacoes": "Pagamento via PIX confirmado"
}
```

#### **Response (200 OK)**
```json
{
  "id": 1,
  "status": "pago",
  "message": "Pagamento registrado com sucesso",
  "comprovante_url": "https://api.primotex.com/comprovantes/1.pdf"
}
```

---

## 📊 **CÓDIGOS DE STATUS**

### **Códigos HTTP**

| Código | Descrição | Uso |
|--------|-----------|-----|
| **200** | OK | Operação realizada com sucesso |
| **201** | Created | Recurso criado com sucesso |
| **400** | Bad Request | Dados inválidos na requisição |
| **401** | Unauthorized | Token inválido ou expirado |
| **403** | Forbidden | Sem permissão para a operação |
| **404** | Not Found | Recurso não encontrado |
| **422** | Unprocessable Entity | Erro de validação |
| **429** | Too Many Requests | Limite de requisições excedido |
| **500** | Internal Server Error | Erro interno do servidor |

### **Status de Ordem de Serviço**

| Status | Descrição | Ações Permitidas |
|--------|-----------|------------------|
| **orcamento** | Aguardando aprovação do orçamento | aprovar, rejeitar, editar |
| **agendada** | Serviço agendado | reagendar, iniciar, cancelar |
| **em_andamento** | Técnico executando serviço | finalizar, adicionar_anexo |
| **concluida** | Serviço finalizado | gerar_nota, pesquisa_satisfacao |
| **cancelada** | Serviço cancelado | reativar |
| **pausada** | Serviço temporariamente pausado | retomar, cancelar |

### **Prioridades de OS**

| Prioridade | Valor | SLA | Cor |
|------------|-------|-----|-----|
| **baixa** | 1 | 7 dias | Verde |
| **media** | 2 | 3 dias | Amarelo |
| **alta** | 3 | 1 dia | Laranja |
| **urgente** | 4 | 4 horas | Vermelho |

---

## ⚡ **RATE LIMITING**

### **Limites por Endpoint**

| Endpoint | Limite | Janela | Descrição |
|----------|--------|--------|-----------|
| `/auth/login` | 5 req | 15 min | Proteção força bruta |
| `/os` (GET) | 100 req | 1 min | Listagem geral |
| `/os` (POST) | 10 req | 1 min | Criação de OS |
| `/comunicacao/enviar` | 50 req | 1 hora | Envio de mensagens |
| **Global** | 1000 req | 1 hora | Limite geral por usuário |

### **Headers de Rate Limit**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1642176000
X-RateLimit-Retry-After: 60
```

### **Resposta Limit Exceeded (429)**

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Try again in 60 seconds.",
  "retry_after": 60,
  "limit": 100,
  "window": "1 minute"
}
```

---

## 🔔 **WEBHOOKS**

### **Configuração de Webhooks**

#### **POST** `/webhooks/configure`

```json
{
  "url": "https://app.cliente.com/webhooks/primotex",
  "events": ["os.criada", "os.concluida", "pagamento.recebido"],
  "secret": "webhook_secret_key",
  "active": true
}
```

### **Eventos Disponíveis**

| Evento | Descrição | Payload |
|--------|-----------|---------|
| **os.criada** | Nova OS criada | `{"event": "os.criada", "data": {...}}` |
| **os.status_changed** | Status de OS alterado | `{"event": "os.status_changed", "data": {...}}` |
| **os.concluida** | OS finalizada | `{"event": "os.concluida", "data": {...}}` |
| **agendamento.criado** | Novo agendamento | `{"event": "agendamento.criado", "data": {...}}` |
| **pagamento.recebido** | Pagamento confirmado | `{"event": "pagamento.recebido", "data": {...}}` |

### **Exemplo de Payload**

```json
{
  "event": "os.concluida",
  "timestamp": "2025-01-14T15:30:00Z",
  "data": {
    "id": 1,
    "numero_os": "OS-2025-001",
    "cliente_id": 1,
    "status": "concluida",
    "valor_final": 1450.00,
    "anexos": [
      {
        "tipo": "foto",
        "url": "https://api.primotex.com/anexos/os1_final.jpg"
      }
    ]
  },
  "signature": "sha256=abc123..."
}
```

### **Verificação de Assinatura**

```javascript
// Verificar webhook signature
const crypto = require('crypto');

function verifyWebhookSignature(payload, signature, secret) {
  const expectedSignature = 'sha256=' + crypto
    .createHmac('sha256', secret)
    .update(payload, 'utf8')
    .digest('hex');
  
  return signature === expectedSignature;
}
```

---

## 🔍 **FILTROS E ORDENAÇÃO**

### **Sintaxe de Filtros**

```http
# Filtros simples
GET /os?status=agendada&prioridade=alta

# Filtros de data
GET /os?data_inicio=2025-01-01&data_fim=2025-01-31

# Busca textual
GET /clientes?search=joão silva

# Filtros múltiplos
GET /os?status=agendada,em_andamento&cliente_id=1
```

### **Ordenação**

```http
# Ordenação simples
GET /os?sort=created_at&order=desc

# Ordenação múltipla
GET /os?sort=prioridade,created_at&order=desc,asc

# Campos disponíveis para ordenação
- created_at, updated_at
- numero_os, status, prioridade
- cliente_nome, tecnico_nome
- valor_orcamento, data_agendada
```

---

## 📞 **SUPORTE & RECURSOS**

### **🔗 Links Úteis**
- **Documentação Interativa**: `http://127.0.0.1:8002/docs`
- **OpenAPI Schema**: `http://127.0.0.1:8002/openapi.json`
- **Health Check**: `http://127.0.0.1:8002/health`

### **📧 Contato**
- **Suporte Técnico**: suporte@primotex.com
- **GitHub Issues**: Para reportar bugs
- **Slack**: #api-support

---

**🔄 Última Atualização**: Janeiro 2025  
**📡 Base URL**: `http://127.0.0.1:8002/api/v1`  
**🔐 Auth**: JWT Bearer Token