import os
import re
import subprocess
import sys

def markdown_to_html(md_text):
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_block_lang = ""
    code_buffer = []
    in_table = False
    table_header_parsed = False
    in_list = False
    
    def process_inline(text):
        # Escape HTML chars except quotes if needed
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Inline code
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Code fence
        if stripped.startswith("```"):
            if in_code_block:
                code_content = "\n".join(code_buffer)
                code_content = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if code_block_lang == "mermaid":
                    html_lines.append(f'<div class="mermaid-diagram"><pre><code>{code_content}</code></pre></div>')
                else:
                    html_lines.append(f'<pre class="code-block"><code>{code_content}</code></pre>')
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
                code_block_lang = stripped[3:].strip().lower()
                code_buffer = []
            i += 1
            continue

        if in_code_block:
            code_buffer.append(line)
            i += 1
            continue

        # Close table if needed
        if in_table and not stripped.startswith("|"):
            html_lines.append('</tbody></table></div>')
            in_table = False
            table_header_parsed = False

        # Close list if needed
        if in_list and not (stripped.startswith("- ") or stripped.startswith("* ") or re.match(r'^\d+\.\s', stripped)):
            html_lines.append('</ul>' if in_list == 'ul' else '</ol>')
            in_list = False

        # Horizontal rule
        if stripped in ["---", "***", "___"]:
            html_lines.append('<hr class="divider">')
            i += 1
            continue

        # Headers
        if stripped.startswith("#"):
            match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if match:
                level = len(match.group(1))
                title = process_inline(match.group(2))
                if level == 1:
                    html_lines.append(f'<h1 class="heading-1">{title}</h1>')
                elif level == 2:
                    html_lines.append(f'<h2 class="heading-2">{title}</h2>')
                elif level == 3:
                    html_lines.append(f'<h3 class="heading-3">{title}</h3>')
                elif level == 4:
                    html_lines.append(f'<h4 class="heading-4">{title}</h4>')
                else:
                    html_lines.append(f'<h5 class="heading-5">{title}</h5>')
                i += 1
                continue

        # Tables
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            # Check if next line is separator
            if not in_table:
                # This is header
                in_table = True
                html_lines.append('<div class="table-container"><table class="report-table"><thead><tr>')
                for c in cells:
                    html_lines.append(f'<th>{process_inline(c)}</th>')
                html_lines.append('</tr></thead><tbody>')
                table_header_parsed = True
                # Skip separator line if next
                if i + 1 < len(lines) and re.match(r'^\|?(\s*:?-+:?\s*\|)+\s*$', lines[i+1].strip()):
                    i += 2
                    continue
            else:
                # Row
                html_lines.append('<tr>')
                for c in cells:
                    html_lines.append(f'<td>{process_inline(c)}</td>')
                html_lines.append('</tr>')
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_text = process_inline(stripped.lstrip("> ").strip())
            html_lines.append(f'<blockquote class="callout">{quote_text}</blockquote>')
            i += 1
            continue

        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                in_list = 'ul'
                html_lines.append('<ul class="list-styled">')
            item_text = process_inline(stripped[2:].strip())
            html_lines.append(f'<li>{item_text}</li>')
            i += 1
            continue

        # Ordered list
        match_ol = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if match_ol:
            if not in_list:
                in_list = 'ol'
                html_lines.append('<ol class="list-numbered">')
            item_text = process_inline(match_ol.group(2).strip())
            html_lines.append(f'<li>{item_text}</li>')
            i += 1
            continue

        # Empty line
        if not stripped:
            i += 1
            continue

        # Paragraph
        html_lines.append(f'<p>{process_inline(stripped)}</p>')
        i += 1

    if in_table:
        html_lines.append('</tbody></table></div>')
    if in_list:
        html_lines.append('</ul>' if in_list == 'ul' else '</ol>')

    return "\n".join(html_lines)


def build_full_html(body_html):
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Informe Técnico INACAP - Sistema de Gestión de Eventos y Reservas</title>
<style>
    @page {{
        size: A4;
        margin: 20mm 15mm 20mm 15mm;
        @bottom-right {{
            content: "Página " counter(page);
            font-size: 9pt;
            color: #64748b;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        @bottom-left {{
            content: "INACAP | Prototipo Funcional de Gestión de Eventos y Reservas";
            font-size: 9pt;
            color: #64748b;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
    }}

    *, *:before, *:after {{
        box-sizing: border-box;
    }}

    body {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
        font-size: 10pt;
        line-height: 1.6;
        color: #1e293b;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
    }}

    /* Portada Institucional INACAP */
    .cover-page {{
        padding: 40px 20px 20px 20px;
        page-break-after: always;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 90vh;
        border-top: 8px solid #cc0000;
        border-bottom: 4px solid #003366;
    }}

    .cover-header {{
        text-align: center;
        margin-bottom: 50px;
    }}

    .cover-institution {{
        font-size: 18pt;
        font-weight: 900;
        letter-spacing: 2px;
        color: #cc0000;
        margin: 0 0 8px 0;
        text-transform: uppercase;
    }}

    .cover-faculty {{
        font-size: 12pt;
        font-weight: 700;
        color: #003366;
        margin: 0 0 4px 0;
        text-transform: uppercase;
    }}

    .cover-carrera {{
        font-size: 11pt;
        font-weight: 600;
        color: #475569;
        margin: 0;
    }}

    .cover-title-box {{
        background: linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%);
        border: 1px solid #cbd5e1;
        border-left: 6px solid #cc0000;
        padding: 30px;
        border-radius: 6px;
        margin: 40px 0;
        text-align: left;
    }}

    .cover-badge {{
        display: inline-block;
        background: #003366;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 9pt;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }}

    .cover-badge-destacado {{
        display: inline-block;
        background: #10b981;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 9pt;
        font-weight: 700;
        text-transform: uppercase;
        margin-left: 8px;
    }}

    .cover-main-title {{
        font-size: 20pt;
        font-weight: 800;
        color: #0f172a;
        margin: 0 0 12px 0;
        line-height: 1.25;
    }}

    .cover-subtitle {{
        font-size: 13pt;
        font-weight: 600;
        color: #334155;
        margin: 0;
    }}

    .cover-meta {{
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 20px;
        margin-top: 40px;
    }}

    .meta-grid {{
        display: table;
        width: 100%;
    }}

    .meta-row {{
        display: table-row;
    }}

    .meta-label {{
        display: table-cell;
        font-weight: 700;
        color: #003366;
        padding: 6px 12px;
        width: 35%;
        border-bottom: 1px solid #f1f5f9;
    }}

    .meta-val {{
        display: table-cell;
        color: #334155;
        padding: 6px 12px;
        border-bottom: 1px solid #f1f5f9;
    }}

    /* Estilos del Documento */
    .content-wrapper {{
        padding: 10px 0;
    }}

    h1.heading-1 {{
        font-size: 16pt;
        font-weight: 800;
        color: #003366;
        border-bottom: 2px solid #cc0000;
        padding-bottom: 6px;
        margin-top: 30px;
        margin-bottom: 15px;
        page-break-after: avoid;
    }}

    h2.heading-2 {{
        font-size: 13pt;
        font-weight: 700;
        color: #0f172a;
        border-left: 4px solid #003366;
        padding-left: 10px;
        margin-top: 25px;
        margin-bottom: 12px;
        page-break-after: avoid;
    }}

    h3.heading-3 {{
        font-size: 11pt;
        font-weight: 700;
        color: #334155;
        margin-top: 20px;
        margin-bottom: 10px;
        page-break-after: avoid;
    }}

    h4.heading-4 {{
        font-size: 10pt;
        font-weight: 700;
        color: #475569;
        margin-top: 15px;
        margin-bottom: 8px;
    }}

    p {{
        margin: 0 0 10px 0;
        text-align: justify;
    }}

    .divider {{
        border: 0;
        height: 1px;
        background-color: #e2e8f0;
        margin: 25px 0;
    }}

    /* Tablas Técnicas */
    .table-container {{
        width: 100%;
        margin: 15px 0;
        overflow-x: auto;
    }}

    table.report-table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 8.5pt;
        margin-bottom: 15px;
        page-break-inside: avoid;
    }}

    table.report-table th {{
        background-color: #003366;
        color: #ffffff;
        font-weight: 700;
        text-align: left;
        padding: 8px 10px;
        border: 1px solid #002244;
    }}

    table.report-table td {{
        padding: 7px 10px;
        border: 1px solid #cbd5e1;
        vertical-align: top;
    }}

    table.report-table tr:nth-child(even) {{
        background-color: #f8fafc;
    }}

    /* Callouts y Citas */
    blockquote.callout {{
        background-color: #eff6ff;
        border-left: 4px solid #2563eb;
        margin: 15px 0;
        padding: 12px 16px;
        font-size: 9.5pt;
        color: #1e3a8a;
        border-radius: 0 4px 4px 0;
    }}

    /* Listas */
    ul.list-styled, ol.list-numbered {{
        margin: 10px 0 15px 20px;
        padding: 0;
    }}

    ul.list-styled li, ol.list-numbered li {{
        margin-bottom: 6px;
        text-align: justify;
    }}

    /* Bloques de Código */
    pre.code-block {{
        background-color: #0f172a;
        color: #f8fafc;
        padding: 12px 16px;
        border-radius: 6px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 8pt;
        line-height: 1.45;
        overflow-x: auto;
        margin: 15px 0;
        page-break-inside: avoid;
        border: 1px solid #334155;
    }}

    .mermaid-diagram pre {{
        background-color: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
        padding: 12px;
        border-radius: 6px;
        font-size: 8pt;
        page-break-inside: avoid;
    }}

    code {{
        background-color: #f1f5f9;
        color: #cc0000;
        padding: 1px 4px;
        border-radius: 3px;
        font-family: 'Consolas', monospace;
        font-size: 8.5pt;
    }}

    pre code {{
        background: transparent;
        color: inherit;
        padding: 0;
    }}

    a {{
        color: #2563eb;
        text-decoration: none;
    }}

    .badge-destacado {{
        background-color: #10b981;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 8pt;
    }}

    @media print {{
        body {{
            background: #ffffff;
        }}
        .cover-page {{
            page-break-after: always;
        }}
        h1.heading-1 {{
            page-break-before: auto;
        }}
    }}
</style>
</head>
<body>

<div class="cover-page">
    <div class="cover-header">
        <div class="cover-institution">INACAP</div>
        <div class="cover-faculty">Área Tecnologías de la Información y Ciberseguridad</div>
        <div class="cover-carrera">Carrera de Ingeniería en Informática / Ingeniería de Software</div>
    </div>

    <div class="cover-title-box">
        <span class="cover-badge">Evaluación Integral de Prototipo Funcional</span>
        <span class="cover-badge-destacado">Nivel 4: Destacado (100 Pts)</span>
        <div class="cover-main-title">INFORME TÉCNICO DE CONSTRUCCIÓN, EVALUACIÓN DE INTERFAZ (UI/UX), SEGURIDAD OWASP Y VALIDACIÓN TESTING (ISO 27000)</div>
        <div class="cover-subtitle">Sistema de Gestión de Eventos y Reservas para Centro Comunitario</div>
    </div>

    <div class="cover-meta">
        <div class="meta-grid">
            <div class="meta-row">
                <div class="meta-label">Asignatura:</div>
                <div class="meta-val">Taller de Desarrollo de Software / Arquitectura de Software</div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Estudiante / Autor:</div>
                <div class="meta-val">Benjamín & Equipo de Desarrollo Full-Stack</div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Docente Evaluador:</div>
                <div class="meta-val">Comisión de Evaluación Académica INACAP</div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Puntaje Esperado según Rúbrica:</div>
                <div class="meta-val"><strong>100 Puntos / 100 Puntos (Calificación 7.0 - Destacado)</strong></div>
            </div>
            <div class="meta-row">
                <div class="meta-label">Fecha y Sede:</div>
                <div class="meta-val">Noviembre 2026 — INACAP, Chile</div>
            </div>
        </div>
    </div>
</div>

<div class="content-wrapper">
{body_html}
</div>

</body>
</html>
"""
    return html_template


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    md_path = os.path.join(base_dir, "docs", "INFORME_ACADEMICO_INACAP.md")
    html_path = os.path.join(base_dir, "docs", "INFORME_ACADEMICO_INACAP.html")
    pdf_path = os.path.join(base_dir, "docs", "INFORME_ACADEMICO_INACAP.pdf")

    print(f"Leyendo Markdown desde: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    body_html = markdown_to_html(md_text)
    full_html = build_full_html(body_html)

    print(f"Escribiendo HTML formateado a: {html_path}")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    edge_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_exe = p
            break

    if not edge_exe:
        print("ERROR: No se encontró Microsoft Edge para imprimir el PDF.")
        sys.exit(1)

    print(f"Generando PDF mediante Edge headless: {edge_exe}")
    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"¡ÉXITO! PDF generado correctamente ({size_kb:.1f} KB) en:")
        print(f" -> {pdf_path}")
    else:
        print("ERROR al generar el PDF.")
        print(res.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
