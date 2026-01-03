import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


def build_pdf(md_path: Path, pdf_path: Path) -> None:
    content = md_path.read_text(encoding="utf-8").splitlines()

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Heading1Custom",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            spaceAfter=12,
            textColor=colors.HexColor("#6495ed"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading2Custom",
            parent=styles["Heading2"],
            fontSize=16,
            leading=20,
            spaceAfter=10,
            textColor=colors.HexColor("#7f2d4b"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="Heading3Custom",
            parent=styles["Heading3"],
            fontSize=14,
            leading=18,
            spaceAfter=8,
            textColor=colors.HexColor("#6495ed"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["BodyText"],
            fontSize=11,
            leading=15,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
            leftIndent=12,
            textColor=colors.grey,
        )
    )

    story = []
    buffer_paragraph = []
    bullet_buffer = []
    image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")

    def flush_paragraph():
        nonlocal buffer_paragraph
        if buffer_paragraph:
            text = " ".join(buffer_paragraph).strip()
            if text:
                story.append(Paragraph(text, styles["BodyCustom"]))
                story.append(Spacer(1, 6))
        buffer_paragraph = []

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            items = [
                ListItem(Paragraph(item.strip(), styles["BodyCustom"]))
                for item in bullet_buffer
                if item.strip()
            ]
            if items:
                story.append(ListFlowable(items, bulletType="bullet", leftIndent=18))
                story.append(Spacer(1, 6))
        bullet_buffer = []

    project_root = Path(__file__).resolve().parent.parent

    for line in content:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_bullets()
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(stripped[2:].strip(), styles["Heading1Custom"]))
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(stripped[3:].strip(), styles["Heading2Custom"]))
            continue
        if stripped.startswith("### "):
            flush_paragraph()
            flush_bullets()
            story.append(Paragraph(stripped[4:].strip(), styles["Heading3Custom"]))
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            bullet_buffer.append(stripped[2:])
            continue

        match = image_pattern.search(stripped)
        if match:
            flush_paragraph()
            flush_bullets()
            alt_text, path = match.groups()
            clean_path = path.split()[0].strip()
            img_path = Path(clean_path)
            if not img_path.is_absolute():
                img_path = project_root / img_path
            if img_path.exists():
                try:
                    img = Image(str(img_path))
                    img._restrictSize(6.5 * inch, 3.8 * inch)
                    story.append(img)
                    story.append(Spacer(1, 6))
                    if alt_text:
                        story.append(Paragraph(alt_text, styles["Caption"]))
                    story.append(Spacer(1, 12))
                except Exception as exc:  # noqa: BLE001
                    story.append(
                        Paragraph(
                            f"[Imagem não pôde ser carregada: {alt_text} - {exc}]",
                            styles["Caption"],
                        )
                    )
                    story.append(Spacer(1, 12))
            else:
                story.append(
                    Paragraph(f"[Imagem não encontrada: {clean_path}]", styles["Caption"])
                )
                story.append(Spacer(1, 12))
            continue

        buffer_paragraph.append(stripped)

    flush_paragraph()
    flush_bullets()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        topMargin=60,
        bottomMargin=40,
        leftMargin=50,
        rightMargin=50,
    )
    doc.build(story)


if __name__ == "__main__":
    md_file = Path("RELATORIO_APRESENTACAO_SISTEMA.md")
    if not md_file.exists():
        raise SystemExit("Arquivo RELATORIO_APRESENTACAO_SISTEMA.md não encontrado.")
    output_pdf = Path("relatorio_apresentacao_sistema.pdf")
    build_pdf(md_file, output_pdf)
    print(f"PDF gerado em: {output_pdf.resolve()}")

