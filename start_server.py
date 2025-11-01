#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para iniciar o servidor backend
"""

import uvicorn
import logging

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Executar servidor
    try:
        uvicorn.run(
            "backend.api.main:app",
            host="127.0.0.1",
            port=8002,
            log_level="info",
            reload=False,  # Sem reload automático
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n✅ Servidor parado pelo usuário")
    except Exception as e:
        print(f"❌ Erro no servidor: {e}")
        import traceback
        traceback.print_exc()