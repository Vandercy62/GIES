"""
Gerador de PDF para Orçamentos - FASE 104 TAREFA 4
Sistema ERP Primotex

Gera PDFs profissionais com:
- Logo e cabeçalho da empresa
- Dados da Ordem de Serviço
- Tabela de itens com formatação
- Subtotal, impostos (17%) e total destacados
- Rodapé com termos e condições
- Informações de contato

Autor: GitHub Copilot
Data: 19/11/2025
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import locale

# Configura locale para formatação brasileira
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except:
        pass


class PDFOrcamentoGenerator:
    """
    Gerador de PDF profissional para orçamentos.
    
    Uso:
        generator = PDFOrcamentoGenerator()
        generator.gerar_pdf(
            output_path="orcamento_123.pdf",
            os_data={"numero": "OS-123", "cliente": "João Silva", ...},
            orcamento_data={"itens": [...], "subtotal": 1000, ...}
        )
    """
    
    # Configurações da empresa
    EMPRESA = {
        "nome": "PRIMOTEX - Forros e Divisórias Eirelli",
        "endereco": "Rua Exemplo, 123 - Centro",
        "cidade": "São Paulo - SP",
        "cep": "01234-567",
        "telefone": "(11) 3456-7890",
        "email": "contato@primotex.com.br",
        "cnpj": "12.345.678/0001-90"
    }
    
    # Cores padrão
    CORES = {
        "primaria": colors.HexColor("#2c3e50"),      # Azul escuro
        "secundaria": colors.HexColor("#3498db"),    # Azul claro
        "sucesso": colors.HexColor("#27ae60"),       # Verde
        "destaque": colors.HexColor("#f39c12"),      # Laranja
        "texto": colors.HexColor("#34495e"),         # Cinza escuro
        "borda": colors.HexColor("#bdc3c7"),         # Cinza claro
        "fundo": colors.HexColor("#ecf0f1")          # Cinza muito claro
    }
    
    def __init__(self):
        """Inicializa o gerador de PDF"""
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
        
    def _criar_estilos_customizados(self):
        """Cria estilos customizados para o documento"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=self.CORES["primaria"],
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=self.CORES["texto"],
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.CORES["texto"],
            fontName='Helvetica'
        ))
        
        # Destaque
        self.styles.add(ParagraphStyle(
            name='Destaque',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=self.CORES["sucesso"],
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT
        ))
        
    def formatar_moeda(self, valor: float) -> str:
        """Formata valor como moeda brasileira"""
        try:
            return f"R$ {valor:,.2f}".replace(",", "X").replace(
                ".", ","
            ).replace("X", ".")
        except:
            return f"R$ {valor}"
    
    def formatar_data(self, data_str: Optional[str] = None) -> str:
        """Formata data para padrão brasileiro"""
        try:
            if data_str:
                # Tenta parsear ISO format
                if 'T' in data_str:
                    data = datetime.fromisoformat(
                        data_str.replace('Z', '+00:00')
                    )
                else:
                    data = datetime.strptime(data_str, "%Y-%m-%d")
            else:
                data = datetime.now()
            
            return data.strftime("%d/%m/%Y")
        except:
            return datetime.now().strftime("%d/%m/%Y")
    
    def _criar_cabecalho(
        self,
        os_data: Dict[str, Any]
    ) -> List:
        """Cria cabeçalho do PDF com logo e dados da empresa"""
        elementos = []
        
        # Logo (se existir)
        logo_path = Path("assets/images/logo.png")
        if logo_path.exists():
            try:
                logo = Image(str(logo_path), width=4*cm, height=2*cm)
                elementos.append(logo)
                elementos.append(Spacer(1, 0.3*cm))
            except:
                pass
        
        # Nome da empresa
        elementos.append(Paragraph(
            self.EMPRESA["nome"],
            self.styles['TituloPrincipal']
        ))
        
        # Informações de contato
        contato = (
            f"{self.EMPRESA['endereco']} - {self.EMPRESA['cidade']}<br/>"
            f"Tel: {self.EMPRESA['telefone']} | "
            f"Email: {self.EMPRESA['email']}<br/>"
            f"CNPJ: {self.EMPRESA['cnpj']}"
        )
        elementos.append(Paragraph(contato, self.styles['Subtitulo']))
        elementos.append(Spacer(1, 0.5*cm))
        
        # Linha separadora
        elementos.append(self._criar_linha_separadora())
        elementos.append(Spacer(1, 0.5*cm))
        
        # Título do documento
        elementos.append(Paragraph(
            "ORÇAMENTO",
            self.styles['TituloPrincipal']
        ))
        elementos.append(Spacer(1, 0.3*cm))
        
        return elementos
    
    def _criar_linha_separadora(self, largura: float = 19*cm) -> Table:
        """Cria linha horizontal separadora"""
        linha = Table([['']], colWidths=[largura])
        linha.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, self.CORES["primaria"]),
        ]))
        return linha
    
    def _criar_info_os(self, os_data: Dict[str, Any]) -> List:
        """Cria seção com informações da OS"""
        elementos = []
        
        # Dados da OS em tabela
        data = [
            ["OS Nº:", os_data.get("numero", "N/A")],
            ["Cliente:", os_data.get("cliente", "N/A")],
            ["Data:", self.formatar_data(os_data.get("data"))],
            ["Validade:", "30 dias"],
        ]
        
        tabela = Table(data, colWidths=[4*cm, 15*cm])
        tabela.setStyle(TableStyle([
            # Header (coluna esquerda)
            ('BACKGROUND', (0, 0), (0, -1), self.CORES["fundo"]),
            ('TEXTCOLOR', (0, 0), (0, -1), self.CORES["primaria"]),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Dados (coluna direita)
            ('TEXTCOLOR', (1, 0), (1, -1), self.CORES["texto"]),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 0), (1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, self.CORES["borda"]),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.5*cm))
        
        return elementos
    
    def _criar_tabela_itens(
        self,
        orcamento_data: Dict[str, Any]
    ) -> List:
        """Cria tabela com itens do orçamento"""
        elementos = []
        
        # Título da seção
        elementos.append(Paragraph(
            "Itens do Orçamento",
            self.styles['Heading2']
        ))
        elementos.append(Spacer(1, 0.3*cm))
        
        # Cabeçalho da tabela
        data = [[
            "Código",
            "Descrição",
            "Qtd",
            "Un.",
            "Preço Unit.",
            "Desc. (%)",
            "Total"
        ]]
        
        # Itens
        itens = orcamento_data.get("itens", [])
        for item in itens:
            data.append([
                item.get("codigo", "-"),
                item.get("produto", ""),
                f"{item.get('qtd', 0):.2f}",
                item.get("unidade", "UN"),
                self.formatar_moeda(item.get("preco_unit", 0)),
                f"{item.get('desconto', 0):.1f}%",
                self.formatar_moeda(item.get("total", 0))
            ])
        
        # Larguras das colunas
        col_widths = [2*cm, 7*cm, 2*cm, 1.5*cm, 2.5*cm, 2*cm, 2.5*cm]
        
        tabela = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Estilo da tabela
        estilo = [
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.CORES["primaria"]),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.CORES["texto"]),
            
            # Alinhamentos
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Código
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Descrição
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Qtd
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Unidade
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),   # Preço
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Desconto
            ('ALIGN', (6, 1), (6, -1), 'RIGHT'),   # Total
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, self.CORES["borda"]),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.white),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            
            # Zebra striping
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
                colors.white, self.CORES["fundo"]
            ]),
        ]
        
        tabela.setStyle(TableStyle(estilo))
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.5*cm))
        
        return elementos
    
    def _criar_totais(self, orcamento_data: Dict[str, Any]) -> List:
        """Cria seção com totais (subtotal, impostos, total)"""
        elementos = []
        
        subtotal = orcamento_data.get("subtotal", 0)
        impostos = orcamento_data.get("impostos", 0)
        total_geral = orcamento_data.get("total_geral", 0)
        
        # Tabela de totais
        data = [
            ["Subtotal:", self.formatar_moeda(subtotal)],
            ["Impostos (17%):", self.formatar_moeda(impostos)],
            ["", ""],  # Linha separadora
            ["TOTAL:", self.formatar_moeda(total_geral)]
        ]
        
        tabela = Table(data, colWidths=[15*cm, 4.5*cm])
        
        estilo = [
            # Subtotal e impostos
            ('FONTNAME', (0, 0), (0, 1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, 1), 10),
            ('ALIGN', (0, 0), (0, 1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (0, 1), self.CORES["texto"]),
            
            ('FONTNAME', (1, 0), (1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, 1), 10),
            ('ALIGN', (1, 0), (1, 1), 'RIGHT'),
            ('TEXTCOLOR', (1, 0), (1, 1), self.CORES["texto"]),
            
            # Linha separadora
            ('LINEABOVE', (0, 2), (-1, 2), 1, self.CORES["borda"]),
            
            # Total
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 3), (-1, 3), 14),
            ('ALIGN', (0, 3), (0, 3), 'RIGHT'),
            ('ALIGN', (1, 3), (1, 3), 'RIGHT'),
            ('TEXTCOLOR', (0, 3), (-1, 3), self.CORES["sucesso"]),
            ('BACKGROUND', (0, 3), (-1, 3), self.CORES["fundo"]),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        tabela.setStyle(TableStyle(estilo))
        elementos.append(tabela)
        elementos.append(Spacer(1, 0.5*cm))
        
        return elementos
    
    def _criar_rodape(self) -> List:
        """Cria rodapé com termos e condições"""
        elementos = []
        
        elementos.append(self._criar_linha_separadora())
        elementos.append(Spacer(1, 0.3*cm))
        
        # Termos e condições
        termos = """
        <b>Termos e Condições:</b><br/>
        • Orçamento válido por 30 dias a partir da data de emissão.<br/>
        • Valores sujeitos a alteração sem aviso prévio.<br/>
        • Pagamento: 50% entrada + 50% na entrega.<br/>
        • Prazo de entrega: Conforme acordo.<br/>
        • Garantia: 12 meses contra defeitos de fabricação.<br/>
        """
        
        elementos.append(Paragraph(
            termos,
            self.styles['TextoNormal']
        ))
        elementos.append(Spacer(1, 0.3*cm))
        
        # Observações finais
        obs = (
            "<i>Este documento foi gerado automaticamente pelo "
            "Sistema ERP Primotex.</i>"
        )
        elementos.append(Paragraph(obs, self.styles['TextoNormal']))
        
        return elementos
    
    def gerar_pdf(
        self,
        output_path: str,
        os_data: Dict[str, Any],
        orcamento_data: Dict[str, Any]
    ) -> bool:
        """
        Gera PDF do orçamento.
        
        Args:
            output_path: Caminho completo para salvar o PDF
            os_data: Dados da Ordem de Serviço
            orcamento_data: Dados do orçamento (itens, totais)
            
        Returns:
            True se gerado com sucesso, False caso contrário
        """
        try:
            # Cria documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Elementos do documento
            elementos = []
            
            # Cabeçalho
            elementos.extend(self._criar_cabecalho(os_data))
            
            # Informações da OS
            elementos.extend(self._criar_info_os(os_data))
            
            # Tabela de itens
            elementos.extend(self._criar_tabela_itens(orcamento_data))
            
            # Totais
            elementos.extend(self._criar_totais(orcamento_data))
            
            # Rodapé
            elementos.extend(self._criar_rodape())
            
            # Gera PDF
            doc.build(elementos)
            
            return True
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            return False


# ============================================================================
# TESTE STANDALONE
# ============================================================================

def teste_pdf():
    """Função de teste standalone"""
    print("\n" + "="*70)
    print("🧪 TESTE GERADOR DE PDF - FASE 104 TAREFA 4")
    print("="*70 + "\n")
    
    # Dados de exemplo
    os_data = {
        "numero": "OS-2025-001",
        "cliente": "João Silva - Construtora ABC Ltda",
        "data": "2025-11-19"
    }
    
    orcamento_data = {
        "itens": [
            {
                "codigo": "FPV-200",
                "produto": "Forro PVC Branco 200mm - 6 metros",
                "qtd": 50.00,
                "unidade": "M²",
                "preco_unit": 35.90,
                "desconto": 10.0,
                "total": 1615.50
            },
            {
                "codigo": "DRY-120",
                "produto": "Placa Drywall 1,20x2,40x12,5mm",
                "qtd": 20.00,
                "unidade": "UN",
                "preco_unit": 28.50,
                "desconto": 5.0,
                "total": 541.50
            },
            {
                "codigo": "PERF-70",
                "produto": "Perfil Metálico para Drywall 70mm - 3m",
                "qtd": 40.00,
                "unidade": "M",
                "preco_unit": 12.90,
                "desconto": 0.0,
                "total": 516.00
            }
        ],
        "subtotal": 2673.00,
        "impostos": 454.41,  # 17%
        "total_geral": 3127.41
    }
    
    # Gera PDF
    output_path = "teste_orcamento_primotex.pdf"
    
    print(f"📄 Gerando PDF: {output_path}")
    print(f"📊 OS: {os_data['numero']}")
    print(f"👤 Cliente: {os_data['cliente']}")
    print(f"🛒 Itens: {len(orcamento_data['itens'])}")
    print(f"💰 Total: R$ {orcamento_data['total_geral']:,.2f}\n")
    
    generator = PDFOrcamentoGenerator()
    sucesso = generator.gerar_pdf(output_path, os_data, orcamento_data)
    
    if sucesso:
        print("✅ PDF gerado com sucesso!")
        print(f"📁 Arquivo: {Path(output_path).absolute()}")
        print("\n💡 Abra o arquivo para visualizar o orçamento\n")
    else:
        print("❌ Erro ao gerar PDF")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    teste_pdf()
