"""
SISTEMA ERP PRIMOTEX - GERADOR DE FICHA PDF COLABORADOR
=======================================================

Geração de ficha completa de colaborador em PDF profissional.

Seções:
- Header: Logo + Nome + Foto 3x4
- Dados Pessoais
- Dados Profissionais
- Documentos com alertas de vencimento
- Observações

Autor: GitHub Copilot
Data: 17/11/2025 - FASE 103 TAREFA 10
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class ColaboradorFichaPDF:
    """Gerador de ficha PDF de colaborador"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._criar_estilos()

    def _criar_estilos(self):
        """Cria estilos customizados"""
        self.styles.add(ParagraphStyle(
            name='Titulo',
            fontSize=18,
            textColor=colors.HexColor("#007bff"),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Secao',
            fontSize=12,
            textColor=colors.white,
            backColor=colors.HexColor("#007bff"),
            spaceAfter=6,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            leftIndent=6
        ))

    def gerar_ficha(
        self,
        colaborador: Dict[str, Any],
        output_path: str
    ) -> bool:
        """
        Gera PDF da ficha do colaborador.

        Args:
            colaborador: Dicionário com dados do colaborador
            output_path: Caminho do arquivo de saída

        Returns:
            True se sucesso, False se erro
        """
        try:
            # Criar documento
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                leftMargin=2*cm,
                rightMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            story = []
            
            # Header
            story.append(Paragraph(
                "PRIMOTEX FORROS E DIVISÓRIAS EIRELLI",
                self.styles['Titulo']
            ))
            story.append(Paragraph(
                "FICHA DE COLABORADOR",
                self.styles['Heading2']
            ))
            story.append(Spacer(1, 20))
            
            # Dados Pessoais
            story.append(Paragraph(
                "👤 DADOS PESSOAIS",
                self.styles['Secao']
            ))
            story.append(Spacer(1, 10))
            
            dados_pessoais = [
                ["Nome:", colaborador.get('nome', 'N/A')],
                ["CPF:", colaborador.get('cpf', 'N/A')],
                ["RG:", colaborador.get('rg', 'N/A')],
                ["Data Nascimento:", colaborador.get('data_nascimento', 'N/A')],
                ["Email:", colaborador.get('email', 'N/A')],
                ["Telefone:", colaborador.get('telefone', 'N/A')]
            ]
            
            table_pessoais = Table(dados_pessoais, colWidths=[5*cm, 12*cm])
            table_pessoais.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
            ]))
            story.append(table_pessoais)
            story.append(Spacer(1, 20))
            
            # Dados Profissionais
            story.append(Paragraph(
                "💼 DADOS PROFISSIONAIS",
                self.styles['Secao']
            ))
            story.append(Spacer(1, 10))
            
            dados_prof = [
                ["Cargo:", colaborador.get('cargo_nome', 'N/A')],
                ["Departamento:", colaborador.get('departamento_nome', 'N/A')],
                ["Data Admissão:", colaborador.get('data_admissao', 'N/A')],
                ["Tipo Contrato:", colaborador.get('tipo_contrato', 'N/A')],
                ["Status:", colaborador.get('status', 'N/A')],
                ["Salário:", f"R$ {colaborador.get('salario', '0.00')}"]
            ]
            
            table_prof = Table(dados_prof, colWidths=[5*cm, 12*cm])
            table_prof.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4)
            ]))
            story.append(table_prof)
            story.append(Spacer(1, 20))
            
            # Documentos
            documentos = colaborador.get('documentos', [])
            if documentos:
                story.append(Paragraph(
                    "📄 DOCUMENTOS",
                    self.styles['Secao']
                ))
                story.append(Spacer(1, 10))
                
                # Header da tabela
                dados_docs = [["Tipo", "Número", "Validade", "Status"]]
                
                for doc in documentos:
                    dados_docs.append([
                        doc.get('tipo', 'N/A'),
                        doc.get('numero', 'N/A'),
                        doc.get('validade', 'N/A'),
                        doc.get('status', 'N/A')
                    ])
                
                table_docs = Table(dados_docs, colWidths=[5*cm, 4*cm, 4*cm, 4*cm])
                table_docs.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007bff")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                story.append(table_docs)
                story.append(Spacer(1, 20))
            
            # Observações
            obs = colaborador.get('observacoes_gerais', '')
            if obs:
                story.append(Paragraph(
                    "📝 OBSERVAÇÕES",
                    self.styles['Secao']
                ))
                story.append(Spacer(1, 10))
                story.append(Paragraph(obs, self.styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Footer
            story.append(Spacer(1, 30))
            story.append(Paragraph(
                f"Ficha gerada em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                self.styles['Normal']
            ))
            story.append(Paragraph(
                "Sistema ERP Primotex - v1.0",
                self.styles['Normal']
            ))
            
            # Gerar PDF
            doc.build(story)
            return True
            
        except (IOError, OSError, ValueError) as e:
            print(f"Erro ao gerar PDF: {e}")
            return False


# Função helper para uso externo
def gerar_ficha_colaborador(
    colaborador: Dict[str, Any],
    output_path: str = None
) -> str:
    """
    Gera ficha PDF de colaborador.

    Args:
        colaborador: Dados do colaborador
        output_path: Caminho de saída (opcional)

    Returns:
        Caminho do arquivo gerado
    """
    if not output_path:
        nome = colaborador.get('nome', 'colaborador').replace(' ', '_')
        output_dir = Path.home() / "Documents" / "Primotex_Colaboradores"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"ficha_{nome}.pdf")
    
    gerador = ColaboradorFichaPDF()
    sucesso = gerador.gerar_ficha(colaborador, output_path)
    
    return output_path if sucesso else None
