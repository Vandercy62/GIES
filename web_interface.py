#!/usr/bin/env python3
"""
SISTEMA ERP PRIMOTEX - INTERFACE WEB COMPLETA
============================================

Interface web funcional para teste e monitoramento do sistema.
Permite acessar via navegador e acompanhar erros em tempo real.

Autor: GitHub Copilot
Data: 02/12/2025
"""

from flask import Flask, render_template_string, jsonify, request, redirect, url_for, session
import requests
from datetime import datetime
import logging
import traceback
import sqlite3
import os
import threading
import time

app = Flask(__name__)
app.secret_key = 'primotex_web_2025'

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs da API
API_BASE = "http://127.0.0.1:8002"
WEB_PORT = 8003

# Template base HTML
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP Primotex - {% block title %}Sistema{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .navbar-brand { font-weight: bold; }
        .error-box { background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 5px; padding: 10px; margin: 10px 0; }
        .success-box { background-color: #d1edff; border: 1px solid #b8daff; border-radius: 5px; padding: 10px; margin: 10px 0; }
        .log-container { max-height: 400px; overflow-y: auto; background: #f8f9fa; padding: 10px; border-radius: 5px; }
        .status-ok { color: #28a745; }
        .status-error { color: #dc3545; }
        .status-warning { color: #ffc107; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-cogs"></i> ERP Primotex
            </a>
            <div class="navbar-nav ms-auto">
                {% if session.get('logged_in') %}
                    <span class="navbar-text me-3">
                        <i class="fas fa-user"></i> {{ session.get('username', 'Admin') }}
                    </span>
                    <a class="btn btn-outline-light btn-sm" href="{{ url_for('logout') }}">
                        <i class="fas fa-sign-out-alt"></i> Sair
                    </a>
                {% else %}
                    <a class="btn btn-outline-light btn-sm" href="{{ url_for('login') }}">
                        <i class="fas fa-sign-in-alt"></i> Login
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Auto-refresh de logs a cada 5 segundos
        function refreshLogs() {
            const logContainer = document.getElementById('log-container');
            if (logContainer) {
                fetch('/api/logs')
                    .then(response => response.json())
                    .then(data => {
                        logContainer.innerHTML = data.logs.join('<br>');
                        logContainer.scrollTop = logContainer.scrollHeight;
                    });
            }
        }
        
        // Auto-refresh de status
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusElement = document.getElementById('system-status');
                    if (statusElement) {
                        statusElement.innerHTML = `
                            <i class="fas ${data.backend ? 'fa-check status-ok' : 'fa-times status-error'}"></i> Backend: ${data.backend ? 'Online' : 'Offline'}<br>
                            <i class="fas ${data.database ? 'fa-check status-ok' : 'fa-times status-error'}"></i> Database: ${data.database ? 'Conectado' : 'Erro'}<br>
                            <i class="fas fa-clock"></i> Última atualização: ${data.timestamp}
                        `;
                    }
                });
        }

        // Iniciar auto-refresh
        setInterval(refreshLogs, 5000);
        setInterval(refreshStatus, 10000);
        
        // Refresh inicial
        setTimeout(refreshLogs, 1000);
        setTimeout(refreshStatus, 1000);
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
"""

# Lista para logs em tempo real
system_logs = []
max_logs = 100

def add_log(message, level="INFO"):
    """Adicionar log ao sistema"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    system_logs.append(log_entry)
    
    # Manter apenas os últimos logs
    if len(system_logs) > max_logs:
        system_logs.pop(0)
    
    logger.info(log_entry)

def check_backend_status():
    """Verificar se o backend está rodando"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=3)
        return response.status_code == 200
    except:
        return False

def check_database_status():
    """Verificar se o banco de dados está acessível"""
    try:
        conn = sqlite3.connect('primotex_erp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        conn.close()
        return True
    except:
        return False

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        add_log(f"Tentativa de login: {username}")
        
        # Tentar autenticar via API
        try:
            response = requests.post(f"{API_BASE}/api/v1/auth/login", 
                                   json={"username": username, "password": password},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                session['logged_in'] = True
                session['username'] = username
                session['token'] = data.get('access_token')
                add_log(f"Login realizado com sucesso: {username}", "SUCCESS")
                return redirect(url_for('dashboard'))
            else:
                add_log(f"Erro no login: {response.status_code}", "ERROR")
                return render_template_string(LOGIN_TEMPLATE, error="Credenciais inválidas")
                
        except Exception as e:
            add_log(f"Erro de conexão no login: {str(e)}", "ERROR")
            return render_template_string(LOGIN_TEMPLATE, error="Erro de conexão com o servidor")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    username = session.get('username', 'Usuário')
    session.clear()
    add_log(f"Logout realizado: {username}")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Verificar status dos serviços
    backend_status = check_backend_status()
    db_status = check_database_status()
    
    add_log(f"Dashboard acessado por {session.get('username')}")
    
    return render_template_string(DASHBOARD_TEMPLATE,
                                backend_status=backend_status,
                                db_status=db_status,
                                logs=system_logs[-10:])  # Últimos 10 logs

@app.route('/clientes')
def clientes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        headers = {"Authorization": f"Bearer {session.get('token')}"}
        response = requests.get(f"{API_BASE}/api/v1/clientes", headers=headers, timeout=10)
        
        if response.status_code == 200:
            clientes_data = response.json()
            add_log(f"Listagem de clientes carregada: {len(clientes_data.get('clientes', []))} registros")
            return render_template_string(CLIENTES_TEMPLATE, clientes=clientes_data.get('clientes', []))
        else:
            error_msg = f"Erro ao carregar clientes: {response.status_code} - {response.text}"
            add_log(error_msg, "ERROR")
            return render_template_string(CLIENTES_TEMPLATE, error=error_msg, clientes=[])
            
    except Exception as e:
        error_msg = f"Erro de conexão ao carregar clientes: {str(e)}"
        add_log(error_msg, "ERROR")
        return render_template_string(CLIENTES_TEMPLATE, error=error_msg, clientes=[])

@app.route('/api/status')
def api_status():
    """API endpoint para verificar status do sistema"""
    return jsonify({
        'backend': check_backend_status(),
        'database': check_database_status(),
        'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

@app.route('/api/logs')
def api_logs():
    """API endpoint para obter logs em tempo real"""
    return jsonify({
        'logs': system_logs[-50:],  # Últimos 50 logs
        'count': len(system_logs)
    })

@app.route('/api/test-backend')
def test_backend():
    """Testar conectividade com o backend"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        result = {
            'status': 'success' if response.status_code == 200 else 'error',
            'code': response.status_code,
            'data': response.json() if response.status_code == 200 else response.text
        }
        add_log(f"Teste de backend: {result['status']}")
        return jsonify(result)
    except Exception as e:
        error = str(e)
        add_log(f"Erro no teste de backend: {error}", "ERROR")
        return jsonify({'status': 'error', 'error': error})

# Templates HTML simples sem herança
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - ERP Primotex</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white text-center">
                        <h4><i class="fas fa-lock"></i> Login no Sistema ERP Primotex</h4>
                    </div>
                    <div class="card-body">
                        {% if error %}
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> {{ error }}
                        </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label for="username" class="form-label">Usuário</label>
                                <input type="text" class="form-control" id="username" name="username" value="admin" required>
                            </div>
                            <div class="mb-3">
                                <label for="password" class="form-label">Senha</label>
                                <input type="password" class="form-control" id="password" name="password" value="admin123" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-sign-in-alt"></i> Entrar no Sistema
                            </button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                Credenciais padrão: admin / admin123
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - ERP Primotex</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-cogs"></i> ERP Primotex
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">
                    <i class="fas fa-user"></i> {{ session.get('username', 'Admin') }}
                </span>
                <a class="btn btn-outline-light btn-sm" href="/logout">
                    <i class="fas fa-sign-out-alt"></i> Sair
                </a>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
<div class="row">
    <div class="col-12">
        <h2><i class="fas fa-tachometer-alt"></i> Dashboard do Sistema</h2>
    </div>
</div>

<div class="row">
    <!-- Status do Sistema -->
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-info text-white">
                <h5><i class="fas fa-heartbeat"></i> Status do Sistema</h5>
            </div>
            <div class="card-body">
                <div id="system-status">
                    <i class="fas {% if backend_status %}fa-check status-ok{% else %}fa-times status-error{% endif %}"></i> 
                    Backend: {% if backend_status %}Online{% else %}Offline{% endif %}<br>
                    
                    <i class="fas {% if db_status %}fa-check status-ok{% else %}fa-times status-error{% endif %}"></i> 
                    Database: {% if db_status %}Conectado{% else %}Erro{% endif %}<br>
                    
                    <i class="fas fa-clock"></i> Última atualização: {{ moment().format('DD/MM/YYYY HH:mm:ss') }}
                </div>
                
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="location.reload()">
                        <i class="fas fa-sync"></i> Atualizar
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Navegação Rápida -->
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-success text-white">
                <h5><i class="fas fa-list"></i> Módulos Disponíveis</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="{{ url_for('clientes') }}" class="btn btn-outline-primary">
                        <i class="fas fa-users"></i> Clientes
                    </a>
                    <button class="btn btn-outline-secondary" disabled>
                        <i class="fas fa-box"></i> Produtos (Em breve)
                    </button>
                    <button class="btn btn-outline-secondary" disabled>
                        <i class="fas fa-clipboard-list"></i> Ordens de Serviço (Em breve)
                    </button>
                    <button class="btn btn-outline-secondary" disabled>
                        <i class="fas fa-dollar-sign"></i> Financeiro (Em breve)
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Testes -->
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-warning text-dark">
                <h5><i class="fas fa-flask"></i> Testes do Sistema</h5>
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-info" onclick="testBackend()">
                        <i class="fas fa-server"></i> Testar Backend
                    </button>
                    <button class="btn btn-outline-info" onclick="testDatabase()">
                        <i class="fas fa-database"></i> Testar Database
                    </button>
                    <button class="btn btn-outline-info" onclick="clearLogs()">
                        <i class="fas fa-trash"></i> Limpar Logs
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-dark text-white">
                <h5><i class="fas fa-terminal"></i> Logs do Sistema (Tempo Real)</h5>
            </div>
            <div class="card-body">
                <div id="log-container" class="log-container">
                    {% for log in logs %}
                        {{ log }}<br>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
function testBackend() {
    fetch('/api/test-backend')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Backend OK: ' + JSON.stringify(data.data, null, 2));
            } else {
                alert('Erro no Backend: ' + data.error);
            }
            refreshStatus();
        });
}

function testDatabase() {
    // Implementar teste de database
    alert('Teste de database não implementado ainda');
}

function clearLogs() {
    if (confirm('Limpar todos os logs?')) {
        fetch('/api/clear-logs', {method: 'POST'})
            .then(() => {
                refreshLogs();
            });
    }
}
</script>
{% endblock %}
"""

CLIENTES_TEMPLATE = BASE_TEMPLATE.replace('{% block title %}Sistema{% endblock %}', '{% block title %}Clientes{% endblock %}') + """
{% block content %}
<div class="row">
    <div class="col-12">
        <h2><i class="fas fa-users"></i> Gerenciamento de Clientes</h2>
        
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="{{ url_for('dashboard') }}">Dashboard</a></li>
                <li class="breadcrumb-item active">Clientes</li>
            </ol>
        </nav>
    </div>
</div>

{% if error %}
<div class="error-box">
    <h5><i class="fas fa-exclamation-triangle"></i> Erro ao Carregar Clientes</h5>
    <p>{{ error }}</p>
    <button class="btn btn-warning" onclick="location.reload()">
        <i class="fas fa-sync"></i> Tentar Novamente
    </button>
</div>
{% endif %}

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h5><i class="fas fa-table"></i> Lista de Clientes</h5>
            </div>
            <div class="card-body">
                {% if clientes %}
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>ID</th>
                                <th>Nome</th>
                                <th>Tipo</th>
                                <th>CPF/CNPJ</th>
                                <th>Email</th>
                                <th>Telefone</th>
                                <th>Cidade</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for cliente in clientes %}
                            <tr>
                                <td>{{ cliente.id }}</td>
                                <td>{{ cliente.nome }}</td>
                                <td>
                                    <span class="badge bg-{% if cliente.tipo_pessoa == 'fisica' %}info{% else %}warning{% endif %}">
                                        {{ cliente.tipo_pessoa.title() }}
                                    </span>
                                </td>
                                <td>{{ cliente.cpf_cnpj }}</td>
                                <td>{{ cliente.email or '-' }}</td>
                                <td>{{ cliente.telefone or '-' }}</td>
                                <td>{{ cliente.cidade or '-' }}</td>
                                <td>
                                    <span class="badge bg-{% if cliente.ativo %}success{% else %}danger{% endif %}">
                                        {% if cliente.ativo %}Ativo{% else %}Inativo{% endif %}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-3">
                    <small class="text-muted">
                        Total de clientes: {{ clientes|length }}
                    </small>
                </div>
                {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-users fa-3x text-muted mb-3"></i>
                    <h5>Nenhum cliente encontrado</h5>
                    <p class="text-muted">
                        {% if not error %}
                            O sistema não possui clientes cadastrados ainda.
                        {% else %}
                            Verifique a conectividade com o backend.
                        {% endif %}
                    </p>
                </div>
                {% endif %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

def start_backend_monitor():
    """Monitor para verificar e reiniciar o backend se necessário"""
    while True:
        if not check_backend_status():
            add_log("Backend offline detectado - tentando reiniciar", "WARNING")
            # Aqui poderia tentar reiniciar o backend automaticamente
        time.sleep(30)  # Verificar a cada 30 segundos

if __name__ == '__main__':
    add_log("Iniciando interface web do ERP Primotex", "INFO")
    add_log(f"Interface será acessível em: http://localhost:{WEB_PORT}", "INFO")
    
    # Iniciar monitor em background
    monitor_thread = threading.Thread(target=start_backend_monitor, daemon=True)
    monitor_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=WEB_PORT, debug=False)
    except Exception as e:
        add_log(f"Erro ao iniciar servidor web: {str(e)}", "ERROR")
        print(f"ERRO: {str(e)}")