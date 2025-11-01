#!/usr/bin/env python3
"""
Sistema de Backup Completo - ERP Primotex
Backup de todos os arquivos e configurações do sistema
Data: 01/11/2025 - Pós Fase 3 Concluída
"""

import os
import shutil
import json
import datetime
from pathlib import Path
import zipfile
import hashlib

class BackupSistemaCompleto:
    def __init__(self):
        self.root_dir = Path("C:/GIES")
        self.backup_dir = self.root_dir / "backups" / f"backup_fase3_completa_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_info = {
            "data_backup": datetime.datetime.now().isoformat(),
            "fase": "3 - CONCLUÍDA",
            "versao_sistema": "3.0.0",
            "status": "PRODUÇÃO READY",
            "arquivos_incluidos": [],
            "diretorios_incluidos": [],
            "checksums": {},
            "estatisticas": {}
        }

    def criar_estrutura_backup(self):
        """Cria a estrutura de diretórios para o backup"""
        print("🏗️ Criando estrutura de backup...")
        
        # Criar diretório principal do backup
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Criar subdiretórios organizados
        subdirs = [
            "backend",
            "frontend", 
            "shared",
            "tests",
            "docs",
            "scripts",
            "logs",
            "configuracoes",
            "relatorios_fase3",
            "ambiente"
        ]
        
        for subdir in subdirs:
            (self.backup_dir / subdir).mkdir(exist_ok=True)
            
        print(f"✅ Estrutura criada em: {self.backup_dir}")

    def calcular_checksum(self, filepath):
        """Calcula checksum MD5 de um arquivo"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None

    def backup_backend(self):
        """Backup completo do backend"""
        print("🔧 Fazendo backup do backend...")
        
        src_backend = self.root_dir / "backend"
        dst_backend = self.backup_dir / "backend"
        
        if src_backend.exists():
            shutil.copytree(src_backend, dst_backend, dirs_exist_ok=True)
            self.backup_info["diretorios_incluidos"].append("backend")
            
            # Contar arquivos Python
            py_files = list(dst_backend.rglob("*.py"))
            self.backup_info["estatisticas"]["backend_py_files"] = len(py_files)
            
            # Calcular checksums dos arquivos principais
            for py_file in py_files:
                if py_file.is_file():
                    checksum = self.calcular_checksum(py_file)
                    if checksum:
                        rel_path = py_file.relative_to(self.backup_dir)
                        self.backup_info["checksums"][str(rel_path)] = checksum
        
        print("✅ Backend backup concluído")

    def backup_frontend(self):
        """Backup completo do frontend"""
        print("💻 Fazendo backup do frontend...")
        
        src_frontend = self.root_dir / "frontend"
        dst_frontend = self.backup_dir / "frontend"
        
        if src_frontend.exists():
            shutil.copytree(src_frontend, dst_frontend, dirs_exist_ok=True)
            self.backup_info["diretorios_incluidos"].append("frontend")
            
            # Contar arquivos Python do desktop
            desktop_files = list((dst_frontend / "desktop").rglob("*.py")) if (dst_frontend / "desktop").exists() else []
            self.backup_info["estatisticas"]["frontend_desktop_files"] = len(desktop_files)
            
            # Calcular checksums
            for py_file in desktop_files:
                if py_file.is_file():
                    checksum = self.calcular_checksum(py_file)
                    if checksum:
                        rel_path = py_file.relative_to(self.backup_dir)
                        self.backup_info["checksums"][str(rel_path)] = checksum
        
        print("✅ Frontend backup concluído")

    def backup_shared_e_scripts(self):
        """Backup dos módulos compartilhados e scripts"""
        print("🔄 Fazendo backup shared e scripts...")
        
        # Backup shared
        src_shared = self.root_dir / "shared"
        if src_shared.exists():
            dst_shared = self.backup_dir / "shared"
            shutil.copytree(src_shared, dst_shared, dirs_exist_ok=True)
            self.backup_info["diretorios_incluidos"].append("shared")
        
        # Backup scripts
        src_scripts = self.root_dir / "scripts"
        if src_scripts.exists():
            dst_scripts = self.backup_dir / "scripts"
            shutil.copytree(src_scripts, dst_scripts, dirs_exist_ok=True)
            self.backup_info["diretorios_incluidos"].append("scripts")
        
        print("✅ Shared e scripts backup concluído")

    def backup_testes(self):
        """Backup de todos os testes"""
        print("🧪 Fazendo backup dos testes...")
        
        src_tests = self.root_dir / "tests"
        dst_tests = self.backup_dir / "tests"
        
        if src_tests.exists():
            shutil.copytree(src_tests, dst_tests, dirs_exist_ok=True)
            self.backup_info["diretorios_incluidos"].append("tests")
        
        # Backup dos arquivos de teste na raiz
        test_files = [
            "test_basico_comunicacao.py",
            "test_comunicacao_final.py", 
            "test_comunicacao_integration.py",
            "test_dashboard_integration.py",
            "test_performance.py",
            "test_sistema_completo.py",
            "teste_final_sistema_completo.py"
        ]
        
        for test_file in test_files:
            src_file = self.root_dir / test_file
            if src_file.exists():
                dst_file = self.backup_dir / "tests" / test_file
                shutil.copy2(src_file, dst_file)
                self.backup_info["arquivos_incluidos"].append(test_file)
        
        print("✅ Testes backup concluído")

    def backup_documentacao(self):
        """Backup de toda documentação"""
        print("📚 Fazendo backup da documentação...")
        
        # Backup pasta docs
        src_docs = self.root_dir / "docs"
        if src_docs.exists():
            dst_docs = self.backup_dir / "docs"
            shutil.copytree(src_docs, dst_docs, dirs_exist_ok=True)
            self.backup_info["diretorios_incluidos"].append("docs")
        
        # Backup relatórios da Fase 3
        relatorios_fase3 = [
            "FASE3_CONCLUIDA_RELATORIO_FINAL.md",
            "ANALISE_CONSOLIDADA_FASES_1_2_3.md",
            "FASE2_RESUMO_FINAL.md",
            "RELATORIO_PERFORMANCE_FASE3.md",
            "PROXIMOS_PASSOS_CONCLUIDOS_NOV2025.md",
            "RELATORIO_TESTE_FINAL_INTEGRADO.md",
            "RELATORIO_FINAL_VALIDACAO_SISTEMA_NOV2025.md"
        ]
        
        dst_relatorios = self.backup_dir / "relatorios_fase3"
        for relatorio in relatorios_fase3:
            src_file = self.root_dir / relatorio
            if src_file.exists():
                dst_file = dst_relatorios / relatorio
                shutil.copy2(src_file, dst_file)
                self.backup_info["arquivos_incluidos"].append(relatorio)
        
        # Backup README principal
        src_readme = self.root_dir / "README.md"
        if src_readme.exists():
            dst_readme = self.backup_dir / "README.md"
            shutil.copy2(src_readme, dst_readme)
            self.backup_info["arquivos_incluidos"].append("README.md")
        
        print("✅ Documentação backup concluída")

    def backup_configuracoes(self):
        """Backup de arquivos de configuração"""
        print("⚙️ Fazendo backup das configurações...")
        
        config_files = [
            "requirements.txt",
            "requirements_corrigido.txt",
            ".github/copilot-instructions.md"
        ]
        
        dst_config = self.backup_dir / "configuracoes"
        
        for config_file in config_files:
            src_file = self.root_dir / config_file
            if src_file.exists():
                # Criar subdiretórios se necessário
                dst_file = dst_config / config_file
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
                self.backup_info["arquivos_incluidos"].append(config_file)
        
        print("✅ Configurações backup concluídas")

    def backup_ambiente(self):
        """Backup de informações do ambiente"""
        print("🌍 Fazendo backup das informações do ambiente...")
        
        dst_ambiente = self.backup_dir / "ambiente"
        
        # Informações do ambiente Python
        try:
            import sys
            import platform
            
            ambiente_info = {
                "python_version": sys.version,
                "platform": platform.platform(),
                "architecture": platform.architecture(),
                "sistema_operacional": platform.system(),
                "data_backup": datetime.datetime.now().isoformat(),
                "diretorio_projeto": str(self.root_dir),
                "virtual_env": ".venv311"
            }
            
            with open(dst_ambiente / "ambiente_info.json", "w", encoding="utf-8") as f:
                json.dump(ambiente_info, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erro ao salvar info do ambiente: {e}")
        
        print("✅ Ambiente backup concluído")

    def backup_logs(self):
        """Backup de logs se existirem"""
        print("📝 Fazendo backup dos logs...")
        
        src_logs = self.root_dir / "logs"
        if src_logs.exists():
            dst_logs = self.backup_dir / "logs"
            shutil.copytree(src_logs, dst_logs, dirs_exist_ok=True)
            self.backup_info["diretorios_incluidos"].append("logs")
        
        print("✅ Logs backup concluído")

    def gerar_relatorio_backup(self):
        """Gera relatório detalhado do backup"""
        print("📊 Gerando relatório do backup...")
        
        # Calcular estatísticas finais
        total_files = len(self.backup_info["arquivos_incluidos"])
        total_dirs = len(self.backup_info["diretorios_incluidos"])
        total_checksums = len(self.backup_info["checksums"])
        
        self.backup_info["estatisticas"].update({
            "total_arquivos_individuais": total_files,
            "total_diretorios": total_dirs,
            "total_checksums": total_checksums,
            "backup_directory": str(self.backup_dir)
        })
        
        # Salvar informações do backup
        backup_info_file = self.backup_dir / "BACKUP_INFO.json"
        with open(backup_info_file, "w", encoding="utf-8") as f:
            json.dump(self.backup_info, f, indent=2, ensure_ascii=False)
        
        # Criar relatório markdown
        relatorio_md = self.backup_dir / "RELATORIO_BACKUP.md"
        with open(relatorio_md, "w", encoding="utf-8") as f:
            f.write(f"""# 📦 RELATÓRIO DE BACKUP - SISTEMA ERP PRIMOTEX
## Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

### 🎯 INFORMAÇÕES GERAIS
- **Fase:** {self.backup_info['fase']}
- **Versão:** {self.backup_info['versao_sistema']}
- **Status:** {self.backup_info['status']}
- **Diretório Backup:** `{self.backup_info['estatisticas']['backup_directory']}`

### 📊 ESTATÍSTICAS
- **Arquivos Individuais:** {total_files}
- **Diretórios:** {total_dirs}
- **Checksums:** {total_checksums}
- **Backend Python Files:** {self.backup_info['estatisticas'].get('backend_py_files', 0)}
- **Frontend Desktop Files:** {self.backup_info['estatisticas'].get('frontend_desktop_files', 0)}

### 📁 DIRETÓRIOS INCLUÍDOS
{chr(10).join([f'- {dir_name}' for dir_name in self.backup_info['diretorios_incluidos']])}

### 📄 ARQUIVOS PRINCIPAIS INCLUÍDOS
{chr(10).join([f'- {arquivo}' for arquivo in self.backup_info['arquivos_incluidos']])}

### ✅ BACKUP COMPLETO REALIZADO COM SUCESSO!
Todos os componentes do Sistema ERP Primotex foram preservados para backup.
""")
        
        print("✅ Relatório gerado")

    def criar_zip_backup(self):
        """Cria arquivo ZIP do backup"""
        print("🗜️ Criando arquivo ZIP do backup...")
        
        zip_name = f"ERP_Primotex_Backup_Fase3_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = self.root_dir / "backups" / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, self.backup_dir)
                    zipf.write(file_path, arc_name)
        
        print(f"✅ ZIP criado: {zip_path}")
        return zip_path

    def executar_backup_completo(self):
        """Executa o backup completo do sistema"""
        print("🚀 INICIANDO BACKUP COMPLETO DO SISTEMA ERP PRIMOTEX")
        print("=" * 60)
        
        try:
            self.criar_estrutura_backup()
            self.backup_backend()
            self.backup_frontend()
            self.backup_shared_e_scripts()
            self.backup_testes()
            self.backup_documentacao()
            self.backup_configuracoes()
            self.backup_ambiente()
            self.backup_logs()
            self.gerar_relatorio_backup()
            zip_path = self.criar_zip_backup()
            
            print("=" * 60)
            print("🎉 BACKUP COMPLETO REALIZADO COM SUCESSO!")
            print(f"📂 Backup em: {self.backup_dir}")
            print(f"🗜️ ZIP criado: {zip_path}")
            print("✅ Sistema totalmente preservado para GitHub")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro durante backup: {e}")
            return False

if __name__ == "__main__":
    backup_system = BackupSistemaCompleto()
    backup_system.executar_backup_completo()