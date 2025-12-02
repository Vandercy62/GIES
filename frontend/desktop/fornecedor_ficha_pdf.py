"""
SISTEMA ERP PRIMOTEX - GERADOR DE FICHA PDF FORNECEDOR
======================================================

Geração de ficha completa de fornecedor em PDF profissional
usando ReportLab com logo, dados completos e formatação elegante.

Autor: GitHub Copilot
Data: 16/11/2025
Versão: 1.0
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# ReportLab imports
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# SessionManager para pegar usuário logado (import condicional)
try:
    from shared.session_manager import session
except ImportError:
    # Fallback quando rodado standalone
    session = None

logger = logging.getLogger(__name__)


# =======================================
# CONSTANTES
# =======================================

# Cores Primotex
COR_PRIMARIA = colors.HexColor("#007bf")  # Azul
COR_SECUNDARIA = colors.HexColor("#6c757d")  # Cinza
COR_SUCESSO = colors.HexColor("#28a745")  # Verde
COR_PERIGO = colors.HexColor("#dc3545")  # Vermelho
COR_AVISO = colors.HexColor("#ffc107")  # Amarelo
COR_INFO = colors.HexColor("#17a2b8")  # Ciano

# Unicode stars para avaliação
STAR_FILLED = "★"
STAR_EMPTY = "☆"

# Diretório padrão para salvar PDFs
DEFAULT_PDF_DIR = Path.home() / "Documents" / "Primotex_Fichas_Fornecedores"


# =======================================
# CLASSE GERADOR DE FICHA PDF
# =======================================

class FornecedorFichaPDF:
    """
    Gera ficha completa de fornecedor em PDF profissional.

    Seções da ficha:
    1. Header: Logo Primotex + Razão Social + CNPJ
    2. Dados Básicos: Tipo, Categoria, Avaliação, Status
    3. Dados Complementares: Endereço, Contatos
    4. Dados Comerciais/Bancários: Pagamento, Banco
    5. Observações: Notas, Histórico, Tags
    6. Footer: Data/Hora geração + Usuário logado
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Inicializa gerador de PDF.

        Args:
            output_dir: Diretório para salvar PDFs (usa padrão se None)
        """
        self.output_dir = output_dir or DEFAULT_PDF_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Configurações de página
        self.page_width, self.page_height = A4
        self.margin_left = 2 * cm
        self.margin_right = 2 * cm
        self.margin_top = 2 * cm
        self.margin_bottom = 2 * cm

        # Estilos
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

        logger.info(f"FornecedorFichaPDF inicializado. Dir: {self.output_dir}")

    def _create_custom_styles(self):
        """Cria estilos personalizados para o PDF"""

        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=COR_PRIMARIA,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COR_SECUNDARIA,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Seção
        self.styles.add(ParagraphStyle(
            name='Secao',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.white,
            backColor=COR_PRIMARIA,
            spaceAfter=6,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            leftIndent=6,
            rightIndent=6,
            leading=16
        ))

        # Campo label
        self.styles.add(ParagraphStyle(
            name='CampoLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=COR_SECUNDARIA,
            fontName='Helvetica-Bold'
        ))

        # Campo valor
        self.styles.add(ParagraphStyle(
            name='CampoValor',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            fontName='Helvetica'
        ))

        # Footer
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=COR_SECUNDARIA,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))

        # Observações
        self.styles.add(ParagraphStyle(
            name='Observacoes',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            leading=12
        ))

    def _formatar_cnpj_cpf(self, valor: Optional[str]) -> str:
        """Formata CNPJ ou CPF com máscaras"""
        if not valor:
            return "N/A"

        # Remove caracteres não numéricos
        numeros = ''.join(filter(str.isdigit, valor))

        if len(numeros) == 14:  # CNPJ
            return f"{numeros[:2]}.{numeros[2:5]}.{numeros[5:8]}/{numeros[8:12]}-{numeros[12:]}"
        elif len(numeros) == 11:  # CPF
            return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
        else:
            return valor

    def _formatar_telefone(self, valor: Optional[str]) -> str:
        """Formata telefone com máscara"""
        if not valor:
            return "N/A"

        numeros = ''.join(filter(str.isdigit, valor))

        if len(numeros) == 11:  # Celular
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        elif len(numeros) == 10:  # Fixo
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        else:
            return valor

    def _formatar_cep(self, valor: Optional[str]) -> str:
        """Formata CEP com máscara"""
        if not valor:
            return "N/A"

        numeros = ''.join(filter(str.isdigit, valor))

        if len(numeros) == 8:
            return f"{numeros[:5]}-{numeros[5:]}"
        else:
            return valor

    def _formatar_moeda(self, valor: Optional[float]) -> str:
        """Formata valor monetário"""
        if valor is None:
            return "R$ 0,00"

        try:
            return f"R$ {float(valor):,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
        except (ValueError, TypeError):
            return "R$ 0,00"

    def _gerar_estrelas(self, avaliacao: Optional[int]) -> str:
        """Gera string com estrelas Unicode para avaliação"""
        if not avaliacao or avaliacao < 1 or avaliacao > 5:
            return f"{STAR_EMPTY * 5} (Sem avaliação)"

        filled = STAR_FILLED * avaliacao
        empty = STAR_EMPTY * (5 - avaliacao)
        return f"{filled}{empty} ({avaliacao}/5)"

    def _criar_header(self, dados: Dict[str, Any]) -> List:
        """Cria header do PDF com logo e dados principais"""
        elements = []

        # Título PRIMOTEX (substitui logo se não tiver imagem)
        titulo_empresa = Paragraph(
            "<b>PRIMOTEX - FORROS E DIVISÓRIAS EIRELLI</b>",
            self.styles['TituloPrincipal']
        )
        elements.append(titulo_empresa)
        elements.append(Spacer(1, 0.3 * cm))

        # Subtítulo
        subtitulo = Paragraph(
            "<b>FICHA CADASTRAL DE FORNECEDOR</b>",
            self.styles['Subtitulo']
        )
        elements.append(subtitulo)
        elements.append(Spacer(1, 0.5 * cm))

        # Dados principais em destaque
        razao_social = dados.get('razao_social', 'N/A')
        cnpj_cpf = self._formatar_cnpj_cpf(dados.get('cnpj_cp'))

        dados_principais = [
            ['<b>Razão Social:</b>', razao_social],
            ['<b>CNPJ/CPF:</b>', cnpj_cpf]
        ]

        tabela_principal = Table(dados_principais, colWidths=[4*cm, 12*cm])
        tabela_principal.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), COR_PRIMARIA),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, COR_SECUNDARIA),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        elements.append(tabela_principal)
        elements.append(Spacer(1, 0.8 * cm))

        return elements

    def _criar_secao_dados_basicos(self, dados: Dict[str, Any]) -> List:
        """Cria seção de Dados Básicos"""
        elements = []

        # Título da seção
        secao_titulo = Paragraph("📋 DADOS BÁSICOS", self.styles['Secao'])
        elements.append(secao_titulo)
        elements.append(Spacer(1, 0.3 * cm))

        # Dados básicos
        tipo_pessoa = dados.get('tipo_pessoa', 'N/A')
        nome_fantasia = dados.get('nome_fantasia', 'N/A')
        inscricao_estadual = dados.get('inscricao_estadual', 'N/A')
        categoria = dados.get('categoria', 'N/A')
        subcategoria = dados.get('subcategoria', 'N/A')
        porte_empresa = dados.get('porte_empresa', 'N/A')
        status = dados.get('status', 'Ativo')
        avaliacao = dados.get('avaliacao')

        # Cor do status
        status_color = COR_SUCESSO if status == 'Ativo' else COR_PERIGO

        dados_basicos = [
            ['<b>Tipo Pessoa:</b>', tipo_pessoa, '<b>Nome Fantasia:</b>', nome_fantasia],
            ['<b>Inscrição Estadual:</b>', inscricao_estadual, '<b>Categoria:</b>', categoria],
            ['<b>Subcategoria:</b>', subcategoria, '<b>Porte Empresa:</b>', porte_empresa],
            ['<b>Status:</b>', f'<font color="{status_color.hexval()}">{status}</font>', '<b>Avaliação:</b>', self._gerar_estrelas(avaliacao)]
        ]

        tabela_basicos = Table(dados_basicos, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        tabela_basicos.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, COR_SECUNDARIA),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ]))

        elements.append(tabela_basicos)
        elements.append(Spacer(1, 0.5 * cm))

        return elements

    def _criar_secao_complementares(self, dados: Dict[str, Any]) -> List:
        """Cria seção de Dados Complementares (Endereço + Contatos)"""
        elements = []

        # ENDEREÇO
        secao_titulo = Paragraph("🏠 ENDEREÇO", self.styles['Secao'])
        elements.append(secao_titulo)
        elements.append(Spacer(1, 0.3 * cm))

        cep = self._formatar_cep(dados.get('cep'))
        logradouro = dados.get('logradouro', 'N/A')
        numero = dados.get('numero', 'N/A')
        complemento = dados.get('complemento', 'N/A')
        bairro = dados.get('bairro', 'N/A')
        cidade = dados.get('cidade', 'N/A')
        estado = dados.get('estado', 'N/A')
        pais = dados.get('pais', 'Brasil')

        dados_endereco = [
            ['<b>CEP:</b>', cep, '<b>Logradouro:</b>', logradouro],
            ['<b>Número:</b>', numero, '<b>Complemento:</b>', complemento],
            ['<b>Bairro:</b>', bairro, '<b>Cidade:</b>', cidade],
            ['<b>Estado:</b>', estado, '<b>País:</b>', pais]
        ]

        tabela_endereco = Table(dados_endereco, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        tabela_endereco.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, COR_SECUNDARIA),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ]))

        elements.append(tabela_endereco)
        elements.append(Spacer(1, 0.5 * cm))

        # CONTATOS
        secao_titulo = Paragraph("📞 CONTATOS", self.styles['Secao'])
        elements.append(secao_titulo)
        elements.append(Spacer(1, 0.3 * cm))

        contato_principal = dados.get('contato_principal', 'N/A')
        telefone1 = self._formatar_telefone(dados.get('telefone1'))
        telefone2 = self._formatar_telefone(dados.get('telefone2'))
        email1 = dados.get('email1', 'N/A')
        email2 = dados.get('email2', 'N/A')
        site = dados.get('site', 'N/A')

        dados_contatos = [
            ['<b>Contato Principal:</b>', contato_principal, '<b>Telefone 1:</b>', telefone1],
            ['<b>Telefone 2:</b>', telefone2, '<b>Email 1:</b>', email1],
            ['<b>Email 2:</b>', email2, '<b>Site:</b>', site]
        ]

        tabela_contatos = Table(dados_contatos, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        tabela_contatos.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, COR_SECUNDARIA),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ]))

        elements.append(tabela_contatos)
        elements.append(Spacer(1, 0.5 * cm))

        return elements

    def _criar_secao_comercial_bancario(self, dados: Dict[str, Any]) -> List:
        """Cria seção de Dados Comerciais e Bancários"""
        elements = []

        # COMERCIAL
        secao_titulo = Paragraph("💰 DADOS COMERCIAIS", self.styles['Secao'])
        elements.append(secao_titulo)
        elements.append(Spacer(1, 0.3 * cm))

        condicoes_pagamento = dados.get('condicoes_pagamento', 'N/A')
        prazo_entrega_dias = dados.get('prazo_entrega_dias', 'N/A')
        valor_pedido_minimo = self._formatar_moeda(dados.get('valor_pedido_minimo'))
        desconto_padrao = dados.get('desconto_padrao', 0)
        desconto_str = f"{desconto_padrao}%" if desconto_padrao else "0%"

        dados_comerciais = [
            ['<b>Condições de Pagamento:</b>', condicoes_pagamento],
            ['<b>Prazo de Entrega (dias):</b>', str(prazo_entrega_dias)],
            ['<b>Valor Pedido Mínimo:</b>', valor_pedido_minimo],
            ['<b>Desconto Padrão:</b>', desconto_str]
        ]

        tabela_comercial = Table(dados_comerciais, colWidths=[6*cm, 10*cm])
        tabela_comercial.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, COR_SECUNDARIA),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))

        elements.append(tabela_comercial)
        elements.append(Spacer(1, 0.5 * cm))

        # BANCÁRIO
        secao_titulo = Paragraph("🏦 DADOS BANCÁRIOS", self.styles['Secao'])
        elements.append(secao_titulo)
        elements.append(Spacer(1, 0.3 * cm))

        banco = dados.get('banco', 'N/A')
        agencia = dados.get('agencia', 'N/A')
        conta = dados.get('conta', 'N/A')
        chave_pix = dados.get('chave_pix', 'N/A')

        dados_bancarios = [
            ['<b>Banco:</b>', banco, '<b>Agência:</b>', agencia],
            ['<b>Conta:</b>', conta, '<b>Chave PIX:</b>', chave_pix]
        ]

        tabela_bancario = Table(dados_bancarios, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        tabela_bancario.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, COR_SECUNDARIA),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
        ]))

        elements.append(tabela_bancario)
        elements.append(Spacer(1, 0.5 * cm))

        return elements

    def _criar_secao_observacoes(self, dados: Dict[str, Any]) -> List:
        """Cria seção de Observações, Histórico e Tags"""
        elements = []

        # OBSERVAÇÕES
        observacoes = (dados.get('observacoes') or '').strip()
        if observacoes:
            secao_titulo = Paragraph("📝 OBSERVAÇÕES GERAIS", self.styles['Secao'])
            elements.append(secao_titulo)
            elements.append(Spacer(1, 0.3 * cm))

            obs_texto = Paragraph(observacoes, self.styles['Observacoes'])
            elements.append(obs_texto)
            elements.append(Spacer(1, 0.5 * cm))

        # HISTÓRICO DE PROBLEMAS
        historico_problemas = (dados.get('historico_problemas') or '').strip()
        if historico_problemas:
            secao_titulo = Paragraph("🚨 HISTÓRICO DE PROBLEMAS", self.styles['Secao'])
            elements.append(secao_titulo)
            elements.append(Spacer(1, 0.3 * cm))

            historico_texto = Paragraph(historico_problemas, self.styles['Observacoes'])
            elements.append(historico_texto)
            elements.append(Spacer(1, 0.5 * cm))

        # TAGS
        tags = dados.get('tags', [])
        if tags and isinstance(tags, list) and len(tags) > 0:
            secao_titulo = Paragraph("🏷️ TAGS E CATEGORIAS", self.styles['Secao'])
            elements.append(secao_titulo)
            elements.append(Spacer(1, 0.3 * cm))

            tags_str = ", ".join([f"<b>{tag}</b>" for tag in tags])
            tags_texto = Paragraph(tags_str, self.styles['Observacoes'])
            elements.append(tags_texto)
            elements.append(Spacer(1, 0.5 * cm))

        # MOTIVO DE INATIVAÇÃO (se aplicável)
        motivo_inativacao = (dados.get('motivo_inativacao') or '').strip()
        status = dados.get('status', 'Ativo')

        if status == 'Inativo' and motivo_inativacao:
            secao_titulo = Paragraph("🚫 MOTIVO DE INATIVAÇÃO", self.styles['Secao'])
            elements.append(secao_titulo)
            elements.append(Spacer(1, 0.3 * cm))

            motivo_texto = Paragraph(
                f'<font color="{COR_PERIGO.hexval()}"><b>{motivo_inativacao}</b></font>',
                self.styles['Observacoes']
            )
            elements.append(motivo_texto)
            elements.append(Spacer(1, 0.5 * cm))

        return elements

    def _criar_footer(self) -> Paragraph:
        """Cria footer com data/hora e usuário logado"""
        agora = datetime.now()
        data_hora = agora.strftime("%d/%m/%Y às %H:%M:%S")

        # Pega usuário logado do SessionManager
        usuario_logado = "Sistema"
        if session and session.is_authenticated():
            user_data = session.get_user_data()
            if user_data:
                usuario_logado = user_data.get('username', 'Sistema')

        footer_texto = (
            f"Documento gerado em {data_hora} por {usuario_logado} - "
            "Sistema ERP Primotex"
        )
        return Paragraph(footer_texto, self.styles['Footer'])

    def gerar_ficha(self, dados: Dict[str, Any]) -> Optional[str]:
        """
        Gera ficha completa de fornecedor em PDF.

        Args:
            dados: Dicionário com todos os dados do fornecedor

        Returns:
            str: Caminho completo do arquivo PDF gerado
            None: Se houver erro

        Exemplo de uso:
            >>> gerador = FornecedorFichaPDF()
            >>> filepath = gerador.gerar_ficha(dados_fornecedor)
            >>> print(f"PDF gerado: {filepath}")
        """
        try:
            # Gera nome do arquivo
            razao_social = dados.get('razao_social', 'SemNome')
            # Remove caracteres especiais do nome
            razao_safe = "".join(c for c in razao_social if c.isalnum() or c in (' ', '_')).strip()
            razao_safe = razao_safe.replace(' ', '_')[:50]  # Max 50 chars

            agora = datetime.now()
            timestamp = agora.strftime("%Y%m%d_%H%M%S")

            filename = f"Ficha_Fornecedor_{razao_safe}_{timestamp}.pd"
            filepath = self.output_dir / filename

            logger.info(f"Gerando ficha PDF: {filepath}")

            # Cria documento PDF
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=A4,
                leftMargin=self.margin_left,
                rightMargin=self.margin_right,
                topMargin=self.margin_top,
                bottomMargin=self.margin_bottom,
                title=f"Ficha Fornecedor - {razao_social}",
                author="Sistema ERP Primotex"
            )

            # Monta elementos do PDF
            elements = []

            # Header
            elements.extend(self._criar_header(dados))

            # Dados Básicos
            elements.extend(self._criar_secao_dados_basicos(dados))

            # Dados Complementares (Endereço + Contatos)
            elements.extend(self._criar_secao_complementares(dados))

            # Dados Comerciais e Bancários
            elements.extend(self._criar_secao_comercial_bancario(dados))

            # Observações
            elements.extend(self._criar_secao_observacoes(dados))

            # Footer
            elements.append(Spacer(1, 1 * cm))
            elements.append(self._criar_footer())

            # Gera PDF
            doc.build(elements)

            logger.info(f"✅ Ficha PDF gerada com sucesso: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"❌ Erro ao gerar ficha PDF: {e}", exc_info=True)
            return None


# =======================================
# TESTE STANDALONE
# =======================================

if __name__ == "__main__":
    """Teste standalone do gerador de ficha PDF"""

    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Dados de teste completos
    dados_teste = {
        # Dados Básicos
        'razao_social': 'FORNECEDOR TESTE LTDA',
        'cnpj_cp': '12345678000190',
        'tipo_pessoa': 'Jurídica',
        'nome_fantasia': 'Fornecedor Teste',
        'inscricao_estadual': '123.456.789.012',
        'categoria': 'Materiais de Construção',
        'subcategoria': 'Forros e Divisórias',
        'porte_empresa': 'Média Empresa',
        'status': 'Ativo',
        'avaliacao': 4,

        # Endereço
        'cep': '12345678',
        'logradouro': 'Rua Teste da Silva',
        'numero': '123',
        'complemento': 'Sala 456',
        'bairro': 'Centro',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'pais': 'Brasil',

        # Contatos
        'contato_principal': 'João da Silva',
        'telefone1': '11987654321',
        'telefone2': '1133334444',
        'email1': 'contato@fornecedorteste.com.br',
        'email2': 'vendas@fornecedorteste.com.br',
        'site': 'www.fornecedorteste.com.br',

        # Comercial
        'condicoes_pagamento': '30/60/90 dias',
        'prazo_entrega_dias': 15,
        'valor_pedido_minimo': 1500.00,
        'desconto_padrao': 5,

        # Bancário
        'banco': 'Banco do Brasil',
        'agencia': '1234-5',
        'conta': '12345-6',
        'chave_pix': '12.345.678/0001-90',

        # Observações
        'observacoes': 'Fornecedor confiável com ótimo histórico de entregas. Sempre cumpre prazos e oferece produtos de qualidade superior.',
        'historico_problemas': 'Pequeno atraso em agosto/2024 devido a greve dos caminhoneiros. Problema resolvido com reposição prioritária.',
        'tags': ['Premium', 'Entrega Rápida', 'Bom Atendimento'],
        'motivo_inativacao': None
    }

    # Gera PDF de teste
    print("\n" + "="*60)
    print("TESTE: Gerador de Ficha PDF Fornecedor")
    print("="*60 + "\n")

    gerador = FornecedorFichaPDF()
    filepath = gerador.gerar_ficha(dados_teste)

    if filepath:
        print("\n✅ PDF gerado com sucesso!")
        print(f"📄 Arquivo: {filepath}")
        print(f"📂 Diretório: {gerador.output_dir}")

        # Verifica tamanho do arquivo
        file_size = Path(filepath).stat().st_size / 1024  # KB
        print(f"💾 Tamanho: {file_size:.1f} KB")
    else:
        print("\n❌ Erro ao gerar PDF!")

    print("\n" + "="*60)
