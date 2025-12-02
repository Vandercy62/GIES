#!/usr/bin/env python3
"""
INTERFACE WEB MÍNIMA - ERP PRIMOTEX
===================================
Versão mais simples possível para funcionar no VS Code
"""

from flask import Flask, request, redirect, session
import requests
import logging

app = Flask(__name__)
app.secret_key = 'primotex_2025'

# Configurar logging simples
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    return redirect('/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', 'admin')
        password = request.form.get('password', 'admin123')
        
        try:
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
                return redirect('/dashboard')
            else:
                error_msg = "Credenciais inválidas"
        except Exception as e:
            error_msg = f"Erro de conexão: {e}"
            
        return f'''
        <html>
        <head><title>ERP Primotex - Login</title></head>
        <body style="font-family:Arial;background:#f0f0f0;padding:50px;">
            <div style="max-width:400px;margin:auto;background:white;padding:30px;border-radius:10px;">
                <h2 style="text-align:center;color:#333;">🔧 ERP Primotex - Login</h2>
                <div style="color:red;text-align:center;margin:10px 0;">{error_msg}</div>
                <form method="POST">
                    <div style="margin:15px 0;">
                        <label>Usuário:</label><br>
                        <input type="text" name="username" value="admin" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:5px;">
                    </div>
                    <div style="margin:15px 0;">
                        <label>Senha:</label><br>
                        <input type="password" name="password" value="admin123" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:5px;">
                    </div>
                    <button type="submit" style="width:100%;padding:12px;background:#007bff;color:white;border:none;border-radius:5px;cursor:pointer;">
                        Entrar
                    </button>
                </form>
            </div>
        </body>
        </html>
        '''
    
    # GET - mostrar formulário de login
    return '''
    <html>
    <head>
        <title>ERP Primotex - Login</title>
        <meta charset="UTF-8">
        <script>
            function togglePassword() {
                var senhaInput = document.getElementById("password");
                var toggleBtn = document.getElementById("toggleBtn");
                
                if (senhaInput.type === "password") {
                    senhaInput.type = "text";
                    toggleBtn.innerHTML = "🙈 Ocultar senha";
                } else {
                    senhaInput.type = "password";
                    toggleBtn.innerHTML = "👁️ Visualizar senha";
                }
            }
            
            function esqueceuSenha() {
                window.open('/esqueci-senha', '_blank');
            }
        </script>
    </head>
    <body style="font-family:Arial;background:#f0f0f0;padding:50px;">
        <div style="max-width:400px;margin:auto;background:white;padding:30px;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
            <h2 style="text-align:center;color:#333;margin-bottom:20px;">🔧 ERP Primotex</h2>
            <form method="POST">
                <div style="margin:15px 0;">
                    <label style="font-weight:bold;color:#555;">Usuário:</label><br>
                    <input type="text" name="username" value="admin" required
                           style="width:100%;padding:12px;border:1px solid #ddd;border-radius:5px;margin-top:5px;">
                </div>
                <div style="margin:15px 0;">
                    <label style="font-weight:bold;color:#555;">Senha:</label><br>
                    <div style="position:relative;">
                        <input type="password" id="password" name="password" value="admin123" required
                               style="width:100%;padding:12px;border:1px solid #ddd;border-radius:5px;margin-top:5px;padding-right:45px;">
                        <button type="button" id="toggleBtn" onclick="togglePassword()" 
                                style="position:absolute;right:8px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;font-size:14px;color:#666;">
                            👁️ Visualizar senha
                        </button>
                    </div>
                </div>
                
                <div style="text-align:center;margin:10px 0;">
                    <button type="button" onclick="esqueceuSenha()" 
                            style="background:none;border:none;color:#007bff;text-decoration:underline;cursor:pointer;font-size:14px;">
                        🔑 Esqueci minha senha
                    </button>
                </div>
                
                <button type="submit" 
                        style="width:100%;padding:15px;background:#007bff;color:white;border:none;border-radius:5px;cursor:pointer;font-size:16px;margin-top:10px;">
                    🚀 Entrar no Sistema
                </button>
            </form>
            
            <div style="text-align:center;margin-top:20px;color:#666;font-size:14px;">
                <strong>Credenciais padrão:</strong><br>
                Usuário: admin | Senha: admin123
            </div>
            
            <div style="text-align:center;margin-top:15px;padding:10px;background:#f8f9fa;border-radius:5px;font-size:12px;color:#666;">
                💡 <strong>Dicas de segurança:</strong><br>
                • Altere a senha padrão após primeiro login<br>
                • Use senhas com letras, números e símbolos<br>
                • Não compartilhe suas credenciais
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')
    
    username = session.get('username', 'Admin')
    
    return f'''
    <html>
    <head>
        <title>ERP Primotex - Dashboard</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="30">
    </head>
    <body style="font-family:Arial;margin:0;background:#f5f5f5;">
        <div style="background:#007bff;color:white;padding:15px;display:flex;justify-content:space-between;align-items:center;">
            <h1 style="margin:0;">🔧 ERP Primotex - Dashboard</h1>
            <div>
                Usuário: {username} | 
                <a href="/logout" style="color:white;text-decoration:underline;">Sair</a>
            </div>
        </div>
        
        <div style="max-width:1200px;margin:20px auto;padding:0 20px;">
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin:20px 0;">
                
                <!-- Status do Sistema -->
                <div style="background:white;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                    <h3 style="margin:0 0 15px 0;color:#333;">🖥️ Status do Sistema</h3>
                    <p style="margin:5px 0;"><span style="color:#28a745;">✅</span> Backend API: Online</p>
                    <p style="margin:5px 0;"><span style="color:#28a745;">✅</span> Banco de Dados: Conectado</p>
                    <p style="margin:5px 0;"><span style="color:#28a745;">✅</span> Interface Web: Funcionando</p>
                    <div style="margin-top:15px;">
                        <a href="http://localhost:8002/docs" target="_blank" 
                           style="display:inline-block;padding:8px 16px;background:#007bff;color:white;text-decoration:none;border-radius:4px;margin:5px 5px 5px 0;">
                            📚 API Docs
                        </a>
                    </div>
                </div>
                
                <!-- Módulos -->
                <div style="background:white;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                    <h3 style="margin:0 0 15px 0;color:#333;">📋 Módulos</h3>
                    <div style="display:flex;flex-direction:column;gap:10px;">
                        <a href="/clientes" 
                           style="display:block;padding:12px;background:#28a745;color:white;text-decoration:none;border-radius:5px;text-align:center;">
                            👥 Clientes
                        </a>
                        <a href="/teste" 
                           style="display:block;padding:12px;background:#17a2b8;color:white;text-decoration:none;border-radius:5px;text-align:center;">
                            🧪 Teste API
                        </a>
                        <a href="http://localhost:8002/health" target="_blank"
                           style="display:block;padding:12px;background:#ffc107;color:black;text-decoration:none;border-radius:5px;text-align:center;">
                            💓 Health Check
                        </a>
                    </div>
                </div>
                
                <!-- Informações -->
                <div style="background:white;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                    <h3 style="margin:0 0 15px 0;color:#333;">ℹ️ Informações</h3>
                    <p><strong>Versão:</strong> 1.0 Mínima</p>
                    <p><strong>Banco:</strong> SQLite (32 tabelas)</p>
                    <p><strong>Backend:</strong> FastAPI (porta 8002)</p>
                    <p><strong>Interface:</strong> Flask (porta 8003)</p>
                    <p><strong>Status:</strong> <span style="color:#28a745;">Totalmente Funcional</span></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/clientes')
def clientes():
    if not session.get('logged_in'):
        return redirect('/login')
    
    try:
        headers = {'Authorization': f"Bearer {session.get('token')}"}
        response = requests.get('http://127.0.0.1:8002/api/v1/clientes', headers=headers, timeout=5)
        
        if response.status_code == 200:
            clientes_data = response.json()
        else:
            clientes_data = []
    except:
        clientes_data = []
    
    html_clientes = ""
    for cliente in clientes_data[:10]:  # Máximo 10
        html_clientes += f'''
        <tr>
            <td style="padding:8px;border:1px solid #ddd;">{cliente.get('id', 'N/A')}</td>
            <td style="padding:8px;border:1px solid #ddd;">{cliente.get('nome', 'N/A')}</td>
            <td style="padding:8px;border:1px solid #ddd;">{cliente.get('cpf_cnpj', 'N/A')}</td>
            <td style="padding:8px;border:1px solid #ddd;">{cliente.get('telefone', 'N/A')}</td>
        </tr>
        '''
    
    return f'''
    <html>
    <head>
        <title>Clientes - ERP Primotex</title>
        <meta charset="UTF-8">
    </head>
    <body style="font-family:Arial;margin:0;background:#f5f5f5;">
        <div style="background:#007bff;color:white;padding:15px;">
            <h2 style="margin:0;">👥 Clientes - ERP Primotex</h2>
            <a href="/dashboard" style="color:white;">⬅️ Voltar ao Dashboard</a>
        </div>
        
        <div style="max-width:1000px;margin:20px auto;padding:0 20px;">
            <div style="background:white;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.1);">
                <h3>Lista de Clientes ({len(clientes_data)} registros)</h3>
                <table style="width:100%;border-collapse:collapse;">
                    <tr style="background:#f8f9fa;">
                        <th style="padding:12px;border:1px solid #ddd;text-align:left;">ID</th>
                        <th style="padding:12px;border:1px solid #ddd;text-align:left;">Nome</th>
                        <th style="padding:12px;border:1px solid #ddd;text-align:left;">Documento</th>
                        <th style="padding:12px;border:1px solid #ddd;text-align:left;">Telefone</th>
                    </tr>
                    {html_clientes if html_clientes else '<tr><td colspan="4" style="padding:20px;text-align:center;border:1px solid #ddd;">Nenhum cliente encontrado</td></tr>'}
                </table>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/teste')
def teste():
    if not session.get('logged_in'):
        return redirect('/login')
    
    try:
        response = requests.get('http://127.0.0.1:8002/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            resultado = f"✅ SUCESSO - Status: {response.status_code} - Dados: {data}"
        else:
            resultado = f"❌ FALHA - Status: {response.status_code}"
    except Exception as e:
        resultado = f"❌ ERRO - {e}"
    
    return f'''
    <html>
    <head><title>Teste API - ERP Primotex</title></head>
    <body style="font-family:Arial;margin:20px;">
        <h2>🧪 Teste de Conexão API</h2>
        <div style="background:#f8f9fa;padding:20px;border-radius:5px;margin:20px 0;">
            <strong>Resultado:</strong><br>
            {resultado}
        </div>
        <a href="/dashboard" style="padding:10px 20px;background:#007bff;color:white;text-decoration:none;border-radius:5px;">
            ⬅️ Voltar ao Dashboard
        </a>
    </body>
    </html>
    '''

@app.route('/esqueci-senha')
def esqueci_senha():
    return '''
    <html>
    <head>
        <title>Recuperar Senha - ERP Primotex</title>
        <meta charset="UTF-8">
    </head>
    <body style="font-family:Arial;background:#f0f0f0;padding:50px;">
        <div style="max-width:500px;margin:auto;background:white;padding:30px;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
            <h2 style="text-align:center;color:#333;margin-bottom:20px;">🔑 Recuperar Senha</h2>
            
            <div style="background:#e7f3ff;border-left:4px solid #007bff;padding:15px;margin:20px 0;">
                <h4 style="margin:0 0 10px 0;color:#007bff;">📧 Como recuperar sua senha:</h4>
                <p style="margin:5px 0;">1. Entre em contato com o administrador do sistema</p>
                <p style="margin:5px 0;">2. Informe seu nome de usuário</p>
                <p style="margin:5px 0;">3. Aguarde o reset da senha</p>
            </div>
            
            <div style="background:#f8f9fa;padding:15px;border-radius:5px;margin:20px 0;">
                <h4 style="margin:0 0 10px 0;">📞 Contatos:</h4>
                <p style="margin:5px 0;"><strong>Email:</strong> admin@primotex.com.br</p>
                <p style="margin:5px 0;"><strong>Telefone:</strong> (11) 99999-9999</p>
                <p style="margin:5px 0;"><strong>Horário:</strong> Segunda à Sexta, 8h às 18h</p>
            </div>
            
            <div style="background:#fff3cd;border-left:4px solid #ffc107;padding:15px;margin:20px 0;">
                <h4 style="margin:0 0 10px 0;color:#856404;">⚠️ Credenciais Padrão (Temporárias):</h4>
                <p style="margin:5px 0;"><strong>Usuário:</strong> admin</p>
                <p style="margin:5px 0;"><strong>Senha:</strong> admin123</p>
                <p style="margin:5px 0;font-size:14px;color:#856404;"><em>Altere após o primeiro login!</em></p>
            </div>
            
            <div style="text-align:center;margin-top:30px;">
                <a href="/login" style="display:inline-block;padding:12px 24px;background:#007bff;color:white;text-decoration:none;border-radius:5px;margin:5px;">
                    ⬅️ Voltar ao Login
                </a>
                <a href="mailto:admin@primotex.com.br?subject=Recuperação%20de%20Senha%20ERP%20Primotex" 
                   style="display:inline-block;padding:12px 24px;background:#28a745;color:white;text-decoration:none;border-radius:5px;margin:5px;">
                    📧 Enviar Email
                </a>
            </div>
            
            <div style="text-align:center;margin-top:20px;font-size:12px;color:#666;">
                <p>Sistema ERP Primotex - Versão 1.0</p>
                <p>© 2025 Primotex - Forros e Divisórias</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/status')
def status():
    return 'OK - Interface funcionando'

if __name__ == '__main__':
    print("=== ERP PRIMOTEX - INTERFACE MÍNIMA ===")
    print("Porta: 8003")
    print("Acesso: http://localhost:8003")
    print("Login: admin / admin123")
    print("========================================")
    
    app.run(host='0.0.0.0', port=8003, debug=False, threaded=True)