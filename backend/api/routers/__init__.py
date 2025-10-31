#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ROUTERS FASTAPI - SISTEMA ERP PRIMOTEX
======================================

Centralização dos routers para a API.
Importa todos os routers dos módulos específicos.

Criado em: 29/10/2025
Autor: GitHub Copilot
"""

from .ordem_servico_router import router as ordem_servico_router

__all__ = [
    "ordem_servico_router",
]