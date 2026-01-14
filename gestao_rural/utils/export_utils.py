"""
UTILITÁRIOS DE EXPORTAÇÃO PARA MONPEC
Funções seguras para exportação PDF/Excel no GCP
"""

import logging
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO

logger = logging.getLogger(__name__)

def exportar_pdf_seguro(response, template_name, context, filename):
    """
    Função segura para exportação PDF no GCP
    """
    try:
        from django.template.loader import get_template
        from django.http import HttpResponse

        # Tentar ReportLab primeiro
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Título
            title = Paragraph(f"<b>Relatório MONPEC</b>", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Dados da tabela
            if 'dados' in context and context['dados']:
                data = context['dados']
                if data:
                    # Criar tabela
                    table_data = [list(data[0].keys())]  # Cabeçalhos
                    for item in data:
                        table_data.append(list(item.values()))

                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(table)

            doc.build(elements)
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)

        except ImportError:
            # Fallback simples
            response.write(b"PDF nao disponivel - instalar reportlab")

        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Erro na exportação PDF: {e}", exc_info=True)
        return HttpResponse("Erro ao gerar PDF", status=500)


def exportar_excel_seguro(data, filename, sheet_name='Dados'):
    """
    Função segura para exportação Excel no GCP
    """
    try:
        from django.http import HttpResponse
        import pandas as pd
        from io import BytesIO

        # Criar DataFrame
        df = pd.DataFrame(data)

        # Criar arquivo Excel
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Formatação básica
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        buffer.seek(0)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Erro na exportação Excel: {e}", exc_info=True)
        return HttpResponse("Erro ao gerar Excel", status=500)