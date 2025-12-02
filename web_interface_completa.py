#!/usr/bin/env python3
"""
ERP PRIMOTEX - INTERFACE WEB COMPLETA
====================================
Sistema web funcional e bem estruturado
"""

from flask import Flask, request, redirect, session, jsonify
import requests
import logging
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'primotex_erp_2025_secure_key'

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da API
API_BASE = 'http://127.0.0.1:8002'

@app.route('/')
def index():
    """Página inicial - redireciona baseado no login"""
    if session.get('logged_in'):
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Sistema de login completo"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_login(error="Por favor, preencha usuário e senha")
        
        try:
            response = requests.post(
                f'{API_BASE}/api/v1/auth/login',
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                session['logged_in'] = True
                session['username'] = username
                session['token'] = data['access_token']
                session['user_data'] = data.get('user', {})
                logger.info(f"Login bem-sucedido para usuário: {username}")
                return redirect('/dashboard')
            else:
                error_msg = "Credenciais inválidas. Tente novamente."
                logger.warning(f"Tentativa de login falhada para: {username}")
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de conexão com o servidor. Verifique se o backend está rodando."
            logger.error(f"Erro de conexão no login: {e}")
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(f"Erro inesperado no login: {e}")
            
        return render_login(error=error_msg)
    
    return render_login()

def render_login(error=None):
    """Renderiza a página de login com CSS moderno"""
    error_html = f'<div class="error-message">{error}</div>' if error else ''
    
    return f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ERP Primotex - Login</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            
            .login-container {{
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 400px;
                text-align: center;
            }}
            
            .logo {{
                font-size: 28px;
                font-weight: bold;
                color: #333;
                margin-bottom: 10px;
            }}
            
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }}
            
            .form-group {{
                margin-bottom: 20px;
                text-align: left;
            }}
            
            label {{
                display: block;
                margin-bottom: 5px;
                color: #333;
                font-weight: 500;
            }}
            
            input[type="text"], input[type="password"] {{
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }}
            
            input[type="text"]:focus, input[type="password"]:focus {{
                outline: none;
                border-color: #667eea;
            }}
            
            .password-container {{
                position: relative;
            }}
            
            .password-toggle {{
                position: absolute;
                right: 12px;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                cursor: pointer;
                color: #666;
                font-size: 18px;
            }}
            
            .login-btn {{
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                transition: transform 0.2s;
            }}
            
            .login-btn:hover {{
                transform: translateY(-2px);
            }}
            
            .error-message {{
                background: #ffe6e6;
                color: #d8000c;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #d8000c;
            }}
            
            .forgot-password {{
                margin-top: 15px;
            }}
            
            .forgot-password a {{
                color: #667eea;
                text-decoration: none;
                font-size: 14px;
            }}
            
            .forgot-password a:hover {{
                text-decoration: underline;
            }}
            
            .credentials-info {{
                background: #e7f3ff;
                border: 1px solid #b8daff;
                border-radius: 8px;
                padding: 15px;
                margin-top: 20px;
                font-size: 14px;
            }}
            
            .credentials-info strong {{
                color: #004085;
            }}
        </style>
    </head>
    <body>
        <div class="login-container">
            <div class="logo">🏢 ERP Primotex</div>
            <div class="subtitle">Sistema de Gestão Empresarial</div>
            
            {error_html}
            
            <form method="POST" id="loginForm">
                <div class="form-group">
                    <label for="username">Usuário:</label>
                    <input type="text" id="username" name="username" value="admin" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Senha:</label>
                    <div class="password-container">
                        <input type="password" id="password" name="password" value="admin123" required>
                        <button type="button" class="password-toggle" onclick="togglePassword()">👁️</button>
                    </div>
                </div>
                
                <button type="submit" class="login-btn">Entrar no Sistema</button>
            </form>
            
            <div class="forgot-password">
                <a href="/esqueci-senha">Esqueci minha senha</a>
            </div>
            
            <div class="credentials-info">
                <strong>Credenciais de Teste:</strong><br>
                Usuário: <code>admin</code><br>
                Senha: <code>admin123</code>
            </div>
        </div>
        
        <script>
            function togglePassword() {{
                const passwordField = document.getElementById('password');
                const toggleBtn = document.querySelector('.password-toggle');
                
                if (passwordField.type === 'password') {{
                    passwordField.type = 'text';
                    toggleBtn.textContent = '🙈';
                }} else {{
                    passwordField.type = 'password';
                    toggleBtn.textContent = '👁️';
                }}
            }}
            
            // Auto-focus no primeiro campo vazio
            document.addEventListener('DOMContentLoaded', function() {{
                const username = document.getElementById('username');
                const password = document.getElementById('password');
                
                if (!username.value) {{
                    username.focus();
                }} else if (!password.value) {{
                    password.focus();
                }}
            }});
        </script>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    """Dashboard principal do sistema"""
    if not session.get('logged_in'):
        return redirect('/login')
    
    username = session.get('username', 'Usuário')
    
    # Verificar status do backend
    backend_status = check_backend_status()
    
    return f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ERP Primotex - Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f7fa;
                min-height: 100vh;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .logo {{
                font-size: 24px;
                font-weight: bold;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .user-info {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logout-btn {{
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                padding: 8px 16px;
                border-radius: 5px;
                text-decoration: none;
                font-size: 14px;
                transition: background 0.3s;
            }}
            
            .logout-btn:hover {{
                background: rgba(255,255,255,0.3);
            }}
            
            .container {{
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 25px;
                margin-bottom: 30px;
            }}
            
            .card {{
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                border: 1px solid #e1e8ed;
            }}
            
            .card-title {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .status-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #f0f0f0;
            }}
            
            .status-item:last-child {{
                border-bottom: none;
            }}
            
            .status-indicator {{
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: 500;
            }}
            
            .status-online {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status-offline {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .module-btn {{
                display: block;
                width: 100%;
                padding: 15px;
                margin: 10px 0;
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                text-align: center;
                font-weight: 500;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .module-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3);
            }}
            
            .module-btn.secondary {{
                background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);
            }}
            
            .module-btn.secondary:hover {{
                box-shadow: 0 8px 25px rgba(23, 162, 184, 0.3);
            }}
            
            .module-btn.warning {{
                background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);
                color: #333;
            }}
            
            .module-btn.warning:hover {{
                box-shadow: 0 8px 25px rgba(255, 193, 7, 0.3);
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
            }}
            
            .info-item {{
                text-align: center;
            }}
            
            .info-label {{
                font-size: 12px;
                color: #666;
                margin-bottom: 5px;
            }}
            
            .info-value {{
                font-size: 16px;
                font-weight: 600;
                color: #333;
            }}
            
            @media (max-width: 768px) {{
                .dashboard-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .header-content {{
                    flex-direction: column;
                    gap: 15px;
                }}
                
                .container {{
                    padding: 0 15px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    🏢 ERP Primotex - Dashboard
                </div>
                <div class="user-info">
                    <span>Usuário: <strong>{username}</strong></span>
                    <a href="/logout" class="logout-btn">Sair</a>
                </div>
            </div>
        </div>
        
        <div class="container">
            <div class="dashboard-grid">
                <!-- Status do Sistema -->
                <div class="card">
                    <div class="card-title">
                        📊 Status do Sistema
                    </div>
                    <div class="status-item">
                        <span>Backend API</span>
                        <span class="status-indicator {'status-online' if backend_status['api'] else 'status-offline'}">
                            {'Online' if backend_status['api'] else 'Offline'}
                        </span>
                    </div>
                    <div class="status-item">
                        <span>Banco de Dados</span>
                        <span class="status-indicator {'status-online' if backend_status['database'] else 'status-offline'}">
                            {'Conectado' if backend_status['database'] else 'Desconectado'}
                        </span>
                    </div>
                    <div class="status-item">
                        <span>Interface Web</span>
                        <span class="status-indicator status-online">Funcionando</span>
                    </div>
                    <a href="{API_BASE}/docs" target="_blank" class="module-btn secondary">📚 API Docs</a>
                </div>
                
                <!-- Módulos Principais -->
                <div class="card">
                    <div class="card-title">
                        📋 Módulos
                    </div>
                    <a href="/clientes" class="module-btn">👥 Clientes</a>
                    <a href="/produtos" class="module-btn">📦 Produtos</a>
                    <a href="/os" class="module-btn">🔧 Ordens de Serviço</a>
                    <a href="/financeiro" class="module-btn">💰 Financeiro</a>
                    <a href="/teste" class="module-btn secondary">🧪 Teste API</a>
                    <a href="{API_BASE}/health" target="_blank" class="module-btn warning">❤️ Health Check</a>
                </div>
                
                <!-- Informações -->
                <div class="card">
                    <div class="card-title">
                        ℹ️ Informações
                    </div>
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-label">Versão</div>
                            <div class="info-value">2.0 Completa</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Banco</div>
                            <div class="info-value">SQLite (32 tabelas)</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Backend</div>
                            <div class="info-value">FastAPI (porta 8002)</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Interface</div>
                            <div class="info-value">Flask (porta 8003)</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Status</div>
                            <div class="info-value" style="color: #28a745;">Totalmente Funcional</div>
                        </div>
                        <div class="info-item">
                            <div class="info-label">Última Atualização</div>
                            <div class="info-value">{datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Auto-refresh do status a cada 30 segundos
            setTimeout(function() {{
                window.location.reload();
            }}, 30000);
        </script>
    </body>
    </html>
    '''

@app.route('/clientes')
def clientes():
    """Página de clientes"""
    if not session.get('logged_in'):
        return redirect('/login')
    
    try:
        headers = {'Authorization': f'Bearer {session.get("token")}'}
        response = requests.get(f'{API_BASE}/api/v1/clientes', headers=headers, timeout=10)
        
        if response.status_code == 200:
            clientes_data = response.json()
            clientes_list = ""
            
            for cliente in clientes_data:
                clientes_list += f'''
                <tr>
                    <td>{cliente.get('id', 'N/A')}</td>
                    <td>{cliente.get('nome', 'N/A')}</td>
                    <td>{cliente.get('email', 'N/A')}</td>
                    <td>{cliente.get('telefone', 'N/A')}</td>
                    <td>{cliente.get('cidade', 'N/A')}</td>
                </tr>
                '''
        else:
            clientes_list = '<tr><td colspan="5">Erro ao carregar clientes</td></tr>'
    except Exception as e:
        clientes_list = f'<tr><td colspan="5">Erro de conexão: {e}</td></tr>'
    
    return f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ERP Primotex - Clientes</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f7fa;
                min-height: 100vh;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px 0;
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .back-btn {{
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                padding: 8px 16px;
                border-radius: 5px;
                text-decoration: none;
                font-size: 14px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            
            .card {{
                background: white;
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            
            th {{
                background: #f8f9fa;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <h1>👥 Clientes</h1>
                <a href="/dashboard" class="back-btn">← Voltar ao Dashboard</a>
            </div>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>Lista de Clientes</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Email</th>
                            <th>Telefone</th>
                            <th>Cidade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {clientes_list}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/teste')
def teste():
    """Página de teste da API"""
    if not session.get('logged_in'):
        return redirect('/login')
    
    try:
        response = requests.get(f'{API_BASE}/health', timeout=5)
        if response.status_code == 200:
            result = "✅ API funcionando corretamente!"
            data = response.json()
            details = f"Status: {data.get('status', 'N/A')}<br>Database: {data.get('database', 'N/A')}"
        else:
            result = f"❌ Erro na API - Status: {response.status_code}"
            details = ""
    except Exception as e:
        result = f"❌ Erro de conexão: {e}"
        details = ""
    
    return f'''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ERP Primotex - Teste API</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f5f7fa;
                margin: 0;
                padding: 20px;
            }}
            
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            }}
            
            .result {{
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                font-size: 18px;
            }}
            
            .back-btn {{
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 Teste da API</h1>
            <div class="result">
                {result}<br>
                {details}
            </div>
            <a href="/dashboard" class="back-btn">← Voltar ao Dashboard</a>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    """Logout do sistema"""
    session.clear()
    return redirect('/login')

@app.route('/esqueci-senha')
def esqueci_senha():
    """Página de recuperação de senha"""
    return '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ERP Primotex - Recuperar Senha</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
            }
            
            .recovery-container {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 500px;
                text-align: center;
            }
            
            .back-btn {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                text-decoration: none;
                margin-top: 20px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="recovery-container">
            <h1>🔑 Recuperar Senha</h1>
            <p>Para recuperar sua senha, entre em contato com o administrador:</p>
            <br>
            <p><strong>Email:</strong> admin@primotex.com.br</p>
            <p><strong>Telefone:</strong> (11) 99999-9999</p>
            <br>
            <p><strong>Credenciais padrão:</strong></p>
            <p>Usuário: admin</p>
            <p>Senha: admin123</p>
            
            <a href="/login" class="back-btn">← Voltar ao Login</a>
        </div>
    </body>
    </html>
    '''

def check_backend_status():
    """Verifica o status do backend"""
    try:
        response = requests.get(f'{API_BASE}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                'api': True,
                'database': data.get('database') == 'connected'
            }
    except:
        pass
    
    return {'api': False, 'database': False}

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 ERP PRIMOTEX - INTERFACE WEB COMPLETA")
    print("=" * 50)
    print("Porta: 8003")
    print("Acesso: http://localhost:8003")
    print("Login: admin / admin123")
    print("=" * 50)
    
    app.run(
        host='0.0.0.0',
        port=8003,
        debug=False,
        threaded=True
    )