#!/usr/bin/env python3
"""
INTERFACE WEB SIMPLES - ERP PRIMOTEX
====================================

Interface web Flask simples e funcional.
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import requests
import logging
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'primotex_secret_key_2025'

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sistema de logs simples
system_logs = []

def add_log(message, level="INFO"):
    """Adicionar log ao sistema"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    system_logs.append(log_entry)
    if len(system_logs) > 100:  # Manter apenas últimos 100 logs
        system_logs.pop(0)
    logger.info(message)

# Templates HTML limpos
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - ERP Primotex</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .card-header { border-radius: 15px 15px 0 0 !important; }
        .btn { border-radius: 8px; }
    </style>
</head>
<body class="d-flex align-items-center">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white text-center">
                        <h4><i class="fas fa-lock"></i> ERP Primotex - Login</h4>
                    </div>
                    <div class="card-body p-4">
                        {% if error %}
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle"></i> {{ error }}
                        </div>
                        {% endif %}
                        
                        <form method="POST">
                            <div class="mb-3">
                                <label class="form-label">
                                    <i class="fas fa-user"></i> Usuário
                                </label>
                                <input type="text" name="username" class="form-control" 
                                       value="admin" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">
                                    <i class="fas fa-key"></i> Senha
                                </label>
                                <input type="password" name="password" class="form-control" 
                                       value="admin123" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                <i class="fas fa-sign-in-alt"></i> Entrar no Sistema
                            </button>
                        </form>
                        
                        <div class="text-center mt-3">
                            <small class="text-muted">
                                <i class="fas fa-info-circle"></i> 
                                Credenciais: admin / admin123
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - ERP Primotex</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-ok { color: #28a745; }
        .status-error { color: #dc3545; }
        .card { margin-bottom: 20px; border-radius: 10px; }
        .card-header { border-radius: 10px 10px 0 0 !important; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-cogs"></i> ERP Primotex
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">
                    <i class="fas fa-user"></i> {{ username }}
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
                <p class="text-muted">Bem-vindo ao painel de controle do ERP Primotex</p>
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
                            <p><i class="fas fa-server"></i> Backend: 
                               <span class="status-ok">Online</span></p>
                            <p><i class="fas fa-database"></i> Database: 
                               <span class="status-ok">Conectado</span></p>
                            <p><i class="fas fa-clock"></i> Atualizado: 
                               <span id="last-update">{{ now }}</span></p>
                        </div>
                        
                        <div class="mt-3">
                            <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
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
                            <a href="/clientes" class="btn btn-outline-primary">
                                <i class="fas fa-users"></i> Clientes
                            </a>
                            <button class="btn btn-outline-secondary" disabled>
                                <i class="fas fa-box"></i> Produtos (Em breve)
                            </button>
                            <button class="btn btn-outline-secondary" disabled>
                                <i class="fas fa-clipboard-list"></i> OS (Em breve)
                            </button>
                            <button class="btn btn-outline-secondary" disabled>
                                <i class="fas fa-dollar-sign"></i> Financeiro (Em breve)
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Informações -->
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header bg-warning text-dark">
                        <h5><i class="fas fa-info-circle"></i> Sistema</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Versão:</strong> 1.0 Web</p>
                        <p><strong>Banco:</strong> SQLite</p>
                        <p><strong>API:</strong> FastAPI</p>
                        <p><strong>Interface:</strong> Flask</p>
                        <div class="mt-3">
                            <a href="http://localhost:8002/docs" target="_blank" 
                               class="btn btn-outline-info btn-sm">
                                <i class="fas fa-book"></i> API Docs
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Logs -->
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-dark text-white">
                        <h5><i class="fas fa-terminal"></i> Logs do Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div style="height: 200px; overflow-y: auto; background: #f8f9fa; padding: 10px; font-family: monospace; font-size: 12px;">
                            {% for log in logs %}
                                {{ log }}<br>
                            {% endfor %}
                        </div>
                        <div class="mt-2">
                            <button class="btn btn-outline-primary btn-sm" onclick="location.reload()">
                                <i class="fas fa-sync"></i> Atualizar Logs
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Rotas da aplicação
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Fazer login na API
            response = requests.post('http://127.0.0.1:8002/api/v1/auth/login', 
                                   json={'username': username, 'password': password},
                                   timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                session['logged_in'] = True
                session['username'] = username
                session['token'] = data['access_token']
                add_log(f"Login realizado com sucesso: {username}")
                return redirect(url_for('dashboard'))
            else:
                add_log(f"Falha no login para: {username}", "ERROR")
                return render_template_string(LOGIN_HTML, error="Credenciais inválidas")
                
        except Exception as e:
            add_log(f"Erro no login: {e}", "ERROR")
            return render_template_string(LOGIN_HTML, error="Erro de conexão com servidor")
    
    return render_template_string(LOGIN_HTML)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return render_template_string(DASHBOARD_HTML, 
                                username=session.get('username', 'Admin'),
                                logs=system_logs[-10:],  # Últimos 10 logs
                                now=now)

@app.route('/clientes')
def clientes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        headers = {'Authorization': f"Bearer {session.get('token')}"}
        response = requests.get('http://127.0.0.1:8002/api/v1/clientes', 
                              headers=headers, timeout=5)
        
        if response.status_code == 200:
            clientes_data = response.json()
            add_log(f"Carregados {len(clientes_data)} clientes")
        else:
            clientes_data = []
            add_log("Erro ao carregar clientes", "ERROR")
            
    except Exception as e:
        clientes_data = []
        add_log(f"Erro ao conectar API clientes: {e}", "ERROR")
    
    # Template simples para clientes
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Clientes - ERP Primotex</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-dark bg-dark">
            <div class="container">
                <a class="navbar-brand" href="/dashboard"><i class="fas fa-cogs"></i> ERP Primotex</a>
                <a class="btn btn-outline-light btn-sm" href="/logout">
                    <i class="fas fa-sign-out-alt"></i> Sair
                </a>
            </div>
        </nav>
        
        <div class="container mt-4">
            <div class="row">
                <div class="col-12">
                    <h2><i class="fas fa-users"></i> Clientes</h2>
                    <nav aria-label="breadcrumb">
                        <ol class="breadcrumb">
                            <li class="breadcrumb-item"><a href="/dashboard">Dashboard</a></li>
                            <li class="breadcrumb-item active">Clientes</li>
                        </ol>
                    </nav>
                </div>
            </div>
            
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5>Lista de Clientes ({len(clientes_data)} registros)</h5>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Nome</th>
                                            <th>Documento</th>
                                            <th>Telefone</th>
                                            <th>Email</th>
                                        </tr>
                                    </thead>
                                    <tbody>
    '''
    
    if clientes_data:
        for cliente in clientes_data[:10]:  # Mostrar apenas 10 primeiros
            html += f'''
                                        <tr>
                                            <td>{cliente.get('id', 'N/A')}</td>
                                            <td>{cliente.get('nome', 'N/A')}</td>
                                            <td>{cliente.get('cpf_cnpj', 'N/A')}</td>
                                            <td>{cliente.get('telefone', 'N/A')}</td>
                                            <td>{cliente.get('email', 'N/A')}</td>
                                        </tr>
            '''
    else:
        html += '''
                                        <tr>
                                            <td colspan="5" class="text-center">Nenhum cliente encontrado</td>
                                        </tr>
        '''
    
    html += '''
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return html

@app.route('/logout')
def logout():
    session.clear()
    add_log("Logout realizado")
    return redirect(url_for('login'))

@app.route('/api/status')
def api_status():
    try:
        response = requests.get('http://127.0.0.1:8002/health', timeout=2)
        backend_status = response.status_code == 200
    except:
        backend_status = False
    
    return jsonify({
        'backend': backend_status,
        'database': True,  # Assumir true por simplicidade
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    add_log("Iniciando interface web do ERP Primotex")
    add_log("Interface será acessível em: http://localhost:8003")
    app.run(host='0.0.0.0', port=8003, debug=False)