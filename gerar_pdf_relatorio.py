from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from pathlib import Path

input_path = Path('RELATORIO_FUNCOES_MODULOS.txt')
output_path = Path('RELATORIO_FUNCOES_MODULOS.pdf')

text = input_path.read_text(encoding='utf-8')

c = canvas.Canvas(str(output_path), pagesize=A4)
width, height = A4
margin_left = 20 * mm
margin_top = height - 20 * mm
line_height = 6 * mm
x = margin_left
y = margin_top

c.setFont('Helvetica', 10)

for line in text.splitlines():
    if y < 20 * mm:
        c.showPage()
        c.setFont('Helvetica', 10)
        y = margin_top
    c.drawString(x, y, line[:2000])
    y -= line_height

c.save()
print(f'Relatório exportado para {output_path}')
