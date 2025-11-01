"""
SERVIDOR SIMPLES DE TESTE - ERP PRIMOTEX
========================================

Servidor básico para testar se a aplicação funciona.
Versão simplificada sem dependências problemáticas.

Autor: GitHub Copilot
Data: 01/11/2025
"""

import json
import sqlite3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse


class SimpleAPIHandler(BaseHTTPRequestHandler):
    """Handler simples para API"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "sistema": "ERP Primotex",
                "empresa": "Primotex - Forros e Divisórias Eireli",
                "versao": "1.0.0",
                "status": "FASE 3 - Sistema Operacional",
                "data": datetime.now().isoformat(),
                "servidor": "ONLINE",
                "banco": "SQLite Conectado"
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Verificar banco de dados
            try:
                conn = sqlite3.connect('primotex_erp.db')
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tabelas = cursor.fetchall()
                conn.close()
                
                db_status = f"Conectado - {len(tabelas)} tabelas"
            except Exception as e:
                db_status = f"Erro: {str(e)}"
            
            response = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": db_status,
                "services": {
                    "auth": "active",
                    "clientes": "active",
                    "produtos": "active",
                    "os": "active",
                    "financeiro": "active",
                    "agendamento": "active",
                    "comunicacao": "active"
                }
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        elif self.path == "/api/v1/clientes":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Buscar clientes do banco
            try:
                conn = sqlite3.connect('primotex_erp.db')
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, email, telefone FROM clientes LIMIT 10")
                clientes = cursor.fetchall()
                conn.close()
                
                response = {
                    "total": len(clientes),
                    "clientes": [
                        {
                            "id": cliente[0],
                            "nome": cliente[1],
                            "email": cliente[2],
                            "telefone": cliente[3]
                        }
                        for cliente in clientes
                    ]
                }
            except Exception as e:
                response = {"erro": str(e)}
                
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"erro": "Endpoint não encontrado"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()


def run_server():
    """Iniciar servidor simples"""
    server_address = ('127.0.0.1', 8003)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    
    print(f"🚀 Servidor ERP Primotex iniciado!")
    print(f"📊 URL: http://127.0.0.1:8003")
    print(f"💚 Status: http://127.0.0.1:8003/health")
    print(f"👥 Clientes: http://127.0.0.1:8003/api/v1/clientes")
    print(f"⏹️ Para parar: Ctrl+C")
    print("-" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()