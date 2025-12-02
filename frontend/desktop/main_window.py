"""
SISTEMA ERP PRIMOTEX - JANELA PRINCIPAL
=======================================

Interface principal do sistema desktop usando PyQt6.
Janela principal com menu, toolbar e área de trabalho.

Autor: GitHub Copilot
Data: 29/10/2025
"""

import sys
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QMenuBar, QMenu, QToolBar, QStatusBar, QLabel,
    QTabWidget, QMessageBox, QFrame, QGridLayout,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QAction, QPixmap, QIcon, QFont

class DashboardWidget(QWidget):
    """Widget do dashboard principal"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QGridLayout()

        # Resumo Financeiro
        financeiro_group = QGroupBox("💰 Resumo Financeiro")
        financeiro_layout = QVBoxLayout()

        financeiro_layout.addWidget(QLabel("Contas a Receber Hoje: R$ 2.500,00"))
        financeiro_layout.addWidget(QLabel("Contas a Pagar Hoje: R$ 1.200,00"))
        financeiro_layout.addWidget(QLabel("Saldo em Caixa: R$ 15.000,00"))

        financeiro_group.setLayout(financeiro_layout)
        layout.addWidget(financeiro_group, 0, 0)

        # OSs em Aberto
        os_group = QGroupBox("⚙️ Ordens de Serviço")
        os_layout = QVBoxLayout()

        os_layout.addWidget(QLabel("Aguardando Visita: 5"))
        os_layout.addWidget(QLabel("Aguardando Orçamento: 8"))
        os_layout.addWidget(QLabel("Em Execução: 15"))

        os_group.setLayout(os_layout)
        layout.addWidget(os_group, 0, 1)

        # Alertas
        alertas_group = QGroupBox("⚠️ Alertas")
        alertas_layout = QVBoxLayout()

        alertas_layout.addWidget(QLabel("3 produtos abaixo do estoque"))
        alertas_layout.addWidget(QLabel("5 contas vencidas"))
        alertas_layout.addWidget(QLabel("2 documentos a vencer"))

        alertas_group.setLayout(alertas_layout)
        layout.addWidget(alertas_group, 1, 0)

        # Agenda Hoje
        agenda_group = QGroupBox("📅 Agenda Hoje")
        agenda_layout = QVBoxLayout()

        agenda_layout.addWidget(QLabel("14:00 - Visita técnica João Silva"))
        agenda_layout.addWidget(QLabel("16:00 - Reunião fornecedores"))
        agenda_layout.addWidget(QLabel("18:00 - Entrega material"))

        agenda_group.setLayout(agenda_layout)
        layout.addWidget(agenda_group, 1, 1)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    """Janela principal do Sistema ERP Primotex"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        """Configurar a interface do usuário"""
        # Configurações da janela
        self.setWindowTitle("Sistema ERP Primotex - Forros e Divisórias Eireli")
        self.setGeometry(100, 100, 1200, 800)

        # Widget central com abas
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header com logo e informações
        header = self.create_header()
        main_layout.addWidget(header)

        # Criar abas principais
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Adicionar abas
        self.add_tabs()

        # Criar menu
        self.create_menu()

        # Criar toolbar
        self.create_toolbar()

        # Criar status bar
        self.create_status_bar()

    def create_header(self):
        """Criar cabeçalho com logo e informações"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 5px;
                margin: 5px;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)

        layout = QHBoxLayout()

        # Logo (placeholder)
        logo_label = QLabel("🏢")
        logo_label.setFont(QFont("Arial", 24))
        layout.addWidget(logo_label)

        # Informações da empresa
        info_layout = QVBoxLayout()
        empresa_label = QLabel("PRIMOTEX - FORROS E DIVISÓRIAS EIRELI")
        empresa_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        sistema_label = QLabel("Sistema de Gerenciamento Empresarial Integrado")
        sistema_label.setFont(QFont("Arial", 10))

        info_layout.addWidget(empresa_label)
        info_layout.addWidget(sistema_label)
        layout.addLayout(info_layout)

        # Espaçador
        layout.addStretch()

        # Status do sistema
        status_layout = QVBoxLayout()
        status_label = QLabel("SISTEMA ONLINE")
        status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")

        usuario_label = QLabel("Usuário: Administrador")
        usuario_label.setFont(QFont("Arial", 9))

        status_layout.addWidget(status_label)
        status_layout.addWidget(usuario_label)
        layout.addLayout(status_layout)

        header.setLayout(layout)
        return header

    def add_tabs(self):
        """Adicionar todas as abas do sistema"""

        # 1. Dashboard
        dashboard = DashboardWidget()
        self.tabs.addTab(dashboard, "🏠 Dashboard")

        # 2. Cadastros
        cadastros_widget = QWidget()
        cadastros_layout = QVBoxLayout()
        cadastros_layout.addWidget(QLabel("Módulo de Cadastros em desenvolvimento..."))

        # Botões rápidos
        botoes_layout = QHBoxLayout()
        botoes_layout.addWidget(QPushButton("👥 Clientes"))
        botoes_layout.addWidget(QPushButton("🏭 Fornecedores"))
        botoes_layout.addWidget(QPushButton("👷 Colaboradores"))
        botoes_layout.addWidget(QPushButton("📦 Produtos"))
        cadastros_layout.addLayout(botoes_layout)

        cadastros_widget.setLayout(cadastros_layout)
        self.tabs.addTab(cadastros_widget, "👥 Cadastros")

        # 3. Ordem de Serviço
        os_widget = QWidget()
        os_layout = QVBoxLayout()
        os_layout.addWidget(QLabel("Módulo de OS em desenvolvimento..."))

        # Tabela de OSs
        os_table = QTableWidget(5, 4)
        os_table.setHorizontalHeaderLabels(["Nº OS", "Cliente", "Status", "Data"])
        os_table.setItem(0, 0, QTableWidgetItem("00234"))
        os_table.setItem(0, 1, QTableWidgetItem("João Silva"))
        os_table.setItem(0, 2, QTableWidgetItem("Aguardando Visita"))
        os_table.setItem(0, 3, QTableWidgetItem("29/10/2025"))

        os_layout.addWidget(os_table)
        os_widget.setLayout(os_layout)
        self.tabs.addTab(os_widget, "⚙️ OS / Pedidos")

        # 4. Estoque
        estoque_widget = QWidget()
        estoque_layout = QVBoxLayout()
        estoque_layout.addWidget(QLabel("Módulo de Estoque em desenvolvimento..."))
        estoque_widget.setLayout(estoque_layout)
        self.tabs.addTab(estoque_widget, "📦 Estoque")

        # 5. Financeiro
        financeiro_widget = QWidget()
        financeiro_layout = QVBoxLayout()
        financeiro_layout.addWidget(QLabel("Módulo Financeiro em desenvolvimento..."))
        financeiro_widget.setLayout(financeiro_layout)
        self.tabs.addTab(financeiro_widget, "💰 Financeiro")

        # 6. Agenda
        agenda_widget = QWidget()
        agenda_layout = QVBoxLayout()
        agenda_layout.addWidget(QLabel("Módulo de Agenda em desenvolvimento..."))
        agenda_widget.setLayout(agenda_layout)
        self.tabs.addTab(agenda_widget, "📅 Agenda")

        # 7. Relatórios
        relatorios_widget = QWidget()
        relatorios_layout = QVBoxLayout()
        relatorios_layout.addWidget(QLabel("Módulo de Relatórios em desenvolvimento..."))
        relatorios_widget.setLayout(relatorios_layout)
        self.tabs.addTab(relatorios_widget, "📊 Relatórios")

    def create_menu(self):
        """Criar menu principal"""
        menubar = self.menuBar()

        # Menu Sistema
        sistema_menu = menubar.addMenu("Sistema")
        sistema_menu.addAction("Configurações", self.show_config)
        sistema_menu.addAction("Backup", self.show_backup)
        sistema_menu.addSeparator()
        sistema_menu.addAction("Sair", self.close)

        # Menu Cadastros
        cadastros_menu = menubar.addMenu("Cadastros")
        cadastros_menu.addAction("Clientes", self.show_clientes)
        cadastros_menu.addAction("Fornecedores", self.show_fornecedores)
        cadastros_menu.addAction("Colaboradores", self.show_colaboradores)
        cadastros_menu.addAction("Produtos/Serviços", self.show_produtos)

        # Menu OS
        os_menu = menubar.addMenu("OS / Pedidos")
        os_menu.addAction("Nova OS", self.nova_os)
        os_menu.addAction("Consultar OS", self.consultar_os)
        os_menu.addAction("Relatório de Serviços", self.relatorio_servicos)

        # Menu Ajuda
        ajuda_menu = menubar.addMenu("Ajuda")
        ajuda_menu.addAction("Sobre", self.show_about)
        ajuda_menu.addAction("Manual", self.show_manual)

    def create_toolbar(self):
        """Criar barra de ferramentas"""
        toolbar = self.addToolBar("Principal")

        # Ações principais
        toolbar.addAction("🏠 Dashboard", lambda: self.tabs.setCurrentIndex(0))
        toolbar.addAction("👥 Clientes", self.show_clientes)
        toolbar.addAction("⚙️ Nova OS", self.nova_os)
        toolbar.addAction("💰 Financeiro", lambda: self.tabs.setCurrentIndex(4))
        toolbar.addSeparator()
        toolbar.addAction("📊 Relatórios", lambda: self.tabs.setCurrentIndex(6))
        toolbar.addAction("⚙️ Config", self.show_config)

    def create_status_bar(self):
        """Criar barra de status"""
        status_bar = self.statusBar()

        # Status do sistema
        self.status_label = QLabel("Sistema Online")
        status_bar.addWidget(self.status_label)

        # Usuário atual
        status_bar.addPermanentWidget(QLabel("Usuário: Administrador"))

        # Data/hora atual
        self.datetime_label = QLabel()
        status_bar.addPermanentWidget(self.datetime_label)

    def setup_timer(self):
        """Configurar timer para atualizar data/hora"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)  # Atualizar a cada segundo
        self.update_datetime()

    def update_datetime(self):
        """Atualizar data/hora na status bar"""
        current_time = QDateTime.currentDateTime()
        self.datetime_label.setText(current_time.toString("dd/MM/yyyy hh:mm:ss"))

    # =======================================
    # SLOTS DOS MENUS E AÇÕES
    # =======================================

    def show_config(self):
        """Mostrar configurações"""
        QMessageBox.information(self, "Configurações", "Módulo de configurações em desenvolvimento...")

    def show_backup(self):
        """Mostrar backup"""
        QMessageBox.information(self, "Backup", "Sistema de backup em desenvolvimento...")

    def show_clientes(self):
        """Mostrar cadastro de clientes"""
        self.tabs.setCurrentIndex(1)
        QMessageBox.information(self, "Clientes", "Módulo de clientes em desenvolvimento...")

    def show_fornecedores(self):
        """Mostrar cadastro de fornecedores"""
        QMessageBox.information(self, "Fornecedores", "Módulo de fornecedores em desenvolvimento...")

    def show_colaboradores(self):
        """Mostrar cadastro de colaboradores"""
        QMessageBox.information(self, "Colaboradores", "Módulo de colaboradores em desenvolvimento...")

    def show_produtos(self):
        """Mostrar cadastro de produtos"""
        QMessageBox.information(self, "Produtos", "Módulo de produtos em desenvolvimento...")

    def nova_os(self):
        """Criar nova OS"""
        QMessageBox.information(self, "Nova OS", "Módulo de OS em desenvolvimento...")

    def consultar_os(self):
        """Consultar OS"""
        self.tabs.setCurrentIndex(2)

    def relatorio_servicos(self):
        """Relatório de serviços"""
        QMessageBox.information(self, "Relatórios", "Módulo de relatórios em desenvolvimento...")

    def show_about(self):
        """Mostrar sobre o sistema"""
        QMessageBox.about(self, "Sobre o Sistema", 
            """
            <h2>Sistema ERP Primotex</h2>
            <p><b>Versão:</b> 1.0.0</p>
            <p><b>Empresa:</b> Primotex - Forros e Divisórias Eireli</p>
            <p><b>Data de Início:</b> 29/10/2025</p>
            <p><b>Status:</b> Fase 1 - Fundação em desenvolvimento</p>
            <br>
            <p>Sistema de gerenciamento empresarial integrado desenvolvido especificamente para controle completo das operações da empresa.</p>
            """)

    def show_manual(self):
        """Mostrar manual do usuário"""
        QMessageBox.information(self, "Manual", "Manual do usuário em desenvolvimento...")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())