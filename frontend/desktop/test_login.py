"""
TESTE SIMPLES - LOGIN APENAS
=============================
"""

import sys
import tkinter as tk
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from login_tkinter import LoginWindow

def main():
    print("=== TESTE LOGIN ===")
    
    # Testar apenas o login
    login = LoginWindow()
    user_data = login.run()
    
    if user_data:
        print(f"✅ Login realizado: {user_data}")
    else:
        print("❌ Login cancelado")

if __name__ == "__main__":
    main()