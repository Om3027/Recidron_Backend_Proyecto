import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def generar_pdf_reportes(reportes: list, usuario: dict = None) -> io.BytesIO:
    """
    Recibe una lista de diccionarios de reportes y genera un PDF.
    Retorna un objeto BytesIO con el contenido del PDF.
    """
    buffer = io.BytesIO()
    
    # Orientación horizontal para que quepan más columnas
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    
    # Título y datos de quien genera
    elements.append(Paragraph("Reporte General de Residuos - Recidron", title_style))
    
    if usuario and "nombre" in usuario:
        from time import strftime
        fecha_actual = strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"<b>Generado por:</b> {usuario['nombre']} ({usuario.get('email', '')})", normal_style))
        elements.append(Paragraph(f"<b>Fecha de exportación:</b> {fecha_actual}", normal_style))
    
    elements.append(Spacer(1, 20))
    
    # Encabezados de tabla
    data = [
        ["ID", "Fecha", "Tipo", "Material", "Zona", "Tamaño", "Estado"]
    ]
    
    for r in reportes:
        estado = "Activo" if r.get("es_activo") else "Inactivo"
        data.append([
            str(r.get("id", "")),
            str(r.get("fecha_reporte", "")).split()[0] if r.get("fecha_reporte") else "",
            str(r.get("tipo_nombre", "N/A")),
            str(r.get("material_nombre", "N/A")),
            str(r.get("zona_nombre", "N/A")),
            str(r.get("tamano_nombre", "N/A")),
            estado
        ])
        
    # Crear la tabla
    table = Table(data, colWidths=[40, 80, 100, 100, 120, 80, 60])
    
    # Estilos de la tabla
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#22c55e")), # Verde primario de la app
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f8fafc")), # Slate 50
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")), # Slate 300
    ]))
    
    elements.append(table)
    
    # Construir el PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer
