#!/usr/bin/env python3
"""
Script de backup automático do banco de dados e arquivos críticos do ERP Primotex.
Salva cópias em backups/ com timestamp para fácil restauração.
"""
import os
from pathlib import Path
from datetime import datetime
import shutil

# Caminhos principais
DB_PATH = Path("primotex_erp.db")
BACKUP_DIR = Path("backups/auto")
LOG_PATH = Path("logs/primotex_erp.log")
ENV_PATH = Path(".env")

BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def backup_file(src: Path, backup_dir: Path):
    if src.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = backup_dir / f"{src.stem}_{timestamp}{src.suffix}"
        shutil.copy2(src, dest)
        print(f"✅ Backup criado: {dest}")
    else:
        print(f"⚠️ Arquivo não encontrado: {src}")

def main():
    print("\n🔒 INICIANDO BACKUP AUTOMÁTICO PRIMOTEX ERP\n")
    backup_file(DB_PATH, BACKUP_DIR)
    backup_file(LOG_PATH, BACKUP_DIR)
    backup_file(ENV_PATH, BACKUP_DIR)
    print("\nBackup finalizado com sucesso!\n")

if __name__ == "__main__":
    main()
