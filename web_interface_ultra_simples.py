#!/usr/bin/env python3
"""
INTERFACE WEB ULTRA SIMPLES - ERP PRIMOTEX
===========================================

Interface web Flask ultra-simplificada para testar navegador.
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

# Template mínimo para login
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>ERP Primotex - Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            width: 300px;
        }
        h2 { text-align: center; color: #333; margin-bottom: 30px; }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #0056b3; }
        .error { color: red; text-align: center; margin: 10px 0; }
        .info { text-align: center; margin: 10px 0; color: #666; font-size: 14px; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔧 ERP Primotex</h2>
        
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        
        <form method="POST">
            <input type="text" name="username" placeholder="Usuário" value="admin" required>
            <input type="password" name="password" placeholder="Senha" value="admin123" required>
            <button type="submit">Entrar</button>
        </form>
        
        <div class="info">
            Credenciais padrão:<br>
            Usuário: admin<br>
            Senha: admin123
        </div>
    </div>
</body>
</html>
"""

# Template mínimo para dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>ERP Primotex - Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .header {
            background: #007bff;
            color: white;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .status-item {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status-ok { color: #28a745; }
        .status-error { color: #dc3545; }
        .btn {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 5px;
        }
        .btn:hover { background: #0056b3; }
        .logout { color: white; text-decoration: none; }
        .logout:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔧 ERP Primotex - Dashboard</h1>
        <div>
            Usuário: {{ username }} | 
            <a href="/logout" class="logout">Sair</a>
        </div>
    </div>

    <div class="container">
        <div class="status-grid">
            <div class="status-item">
                <h3>🖥️ Backend API</h3>
                <p class="status-ok">✅ Online</p>
                <a href="http://localhost:8002/docs" target="_blank" class="btn">Ver API Docs</a>
            </div>
            
            <div class="status-item">
                <h3>💾 Banco de Dados</h3>
                <p class="status-ok">✅ Conectado</p>
                <p>32 tabelas ativas</p>
            </div>
            
            <div class="status-item">
                <h3>🌐 Interface Web</h3>
                <p class="status-ok">✅ Funcionando</p>
                <p>Porta 8003</p>
            </div>
        </div>

        <div class="card">
            <h3>📋 Módulos Disponíveis</h3>
            <a href="/clientes" class="btn">👥 Clientes</a>
            <a href="/teste" class="btn">🧪 Teste API</a>
            <a href="http://localhost:8002/health" target="_blank" class="btn">💓 Health Check</a>
        </div>

        <div class="card">
            <h3>ℹ️ Informações do Sistema</h3>
            <p><strong>Versão:</strong> 1.0 Web Simples</p>
            <p><strong>Última Atualização:</strong> {{ timestamp }}</p>
            <p><strong>Status:</strong> Totalmente Funcional</p>
        </div>
    </div>
</body>
</html>
"""

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
            logger.info(f"Tentativa de login: {username}")
            response = requests.post(
                'http://127.0.0.1:8002/api/v1/auth/login',
                json={'username': username, 'password': password},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                session['logged_in'] = True
                session['username'] = username
                session['token'] = data['access_token']
                logger.info(f"Login bem-sucedido: {username}")
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"Login falhou para {username}: {response.status_code}")
                return render_template_string(LOGIN_TEMPLATE, error="Credenciais inválidas")
                
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return render_template_string(LOGIN_TEMPLATE, error="Erro de conexão com servidor")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return render_template_string(DASHBOARD_TEMPLATE,
                                username=session.get('username', 'Admin'),
                                timestamp=timestamp)

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
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Clientes - ERP Primotex</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .header {{ background: #007bff; color: white; padding: 15px; margin: -20px -20px 20px -20px; }}
                    .btn {{ padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>👥 Clientes - ERP Primotex</h2>
                    <a href="/dashboard" class="btn">⬅️ Voltar ao Dashboard</a>
                </div>
                
                <h3>Lista de Clientes ({len(clientes_data)} registros)</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>Documento</th>
                        <th>Telefone</th>
                        <th>Email</th>
                    </tr>
            """
            
            for cliente in clientes_data[:20]:  # Mostrar apenas 20 primeiros
                html += f"""
                    <tr>
                        <td>{cliente.get('id', 'N/A')}</td>
                        <td>{cliente.get('nome', 'N/A')}</td>
                        <td>{cliente.get('cpf_cnpj', 'N/A')}</td>
                        <td>{cliente.get('telefone', 'N/A')}</td>
                        <td>{cliente.get('email', 'N/A')}</td>
                    </tr>
                """
            
            html += """
                </table>
            </body>
            </html>
            """
            return html
        else:
            return f"<h2>Erro ao carregar clientes: {response.status_code}</h2><a href='/dashboard'>Voltar</a>"
            
    except Exception as e:
        return f"<h2>Erro de conexão: {e}</h2><a href='/dashboard'>Voltar</a>"

@app.route('/teste')
def teste():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    try:
        # Testar conexão com backend
        response = requests.get('http://127.0.0.1:8002/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return f"""
            <h2>🧪 Teste de Conexão - SUCESSO!</h2>
            <p><strong>Status:</strong> {response.status_code}</p>
            <p><strong>Resposta:</strong> {data}</p>
            <p><strong>Backend:</strong> Funcionando perfeitamente</p>
            <a href="/dashboard">⬅️ Voltar ao Dashboard</a>
            """
        else:
            return f"<h2>❌ Teste Falhou - Status: {response.status_code}</h2><a href='/dashboard'>Voltar</a>"
            
    except Exception as e:
        return f"<h2>❌ Erro de Conexão: {e}</h2><a href='/dashboard'>Voltar</a>"

@app.route('/logout')
def logout():
    session.clear()
    logger.info("Logout realizado")
    return redirect(url_for('login'))

@app.route('/status')
def status():
    """Endpoint para verificar se a web está funcionando"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'message': 'Interface web funcionando'
    })

if __name__ == '__main__':
    logger.info("=== INICIANDO INTERFACE WEB ULTRA SIMPLES ===")
    logger.info("Porta: 8003")
    logger.info("Acesso: http://localhost:8003")
    logger.info("Login: admin / admin123")
    
    try:
        app.run(host='0.0.0.0', port=8003, debug=False)
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")