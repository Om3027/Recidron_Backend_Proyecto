import io
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

def generar_pdf_reportes(reportes: list, usuario: dict = None, filtros: dict = None) -> io.BytesIO:
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
    
    if filtros:
        filtros_str = []
        if filtros.get('tipo_nombre') and filtros['tipo_nombre'] != 'Todos':
            filtros_str.append(f"Tipo: {filtros['tipo_nombre']}")
        else:
            filtros_str.append("Tipo: Todos")
        if filtros.get('limit'):
            filtros_str.append(f"Límite: {filtros['limit']} registros")
        
        texto_filtros = " | ".join(filtros_str)
        elements.append(Paragraph(f"<b>Filtros aplicados:</b> {texto_filtros}", normal_style))
    
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Total de registros exportados:</b> {len(reportes)}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Encabezados de tabla
    data = [
        ["ID", "Fecha", "Autor", "Tipo", "Material", "Zona", "Tamaño", "Estado"]
    ]
    
    for r in reportes:
        estado = "Activo" if r.get("es_activo") else "Inactivo"
        fecha_str = str(r.get("fecha_reporte", "")).split()[0] if r.get("fecha_reporte") else ""
        data.append([
            str(r.get("id", "")),
            fecha_str,
            Paragraph(str(r.get("usuario_nombre", "N/A")), normal_style),
            Paragraph(str(r.get("tipo_nombre", "N/A")), normal_style),
            Paragraph(str(r.get("material_nombre", "N/A")), normal_style),
            Paragraph(str(r.get("zona_nombre", "N/A")), normal_style),
            Paragraph(str(r.get("tamano_nombre", "N/A")), normal_style),
            estado
        ])
        
    # Crear la tabla
    table = Table(data, colWidths=[30, 65, 80, 90, 90, 100, 80, 50])
    
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
    
    # Dynamic calculations for the filtered reports
    if reportes:
        tipos_count = {}
        zonas_count = {}
        mat_count = {}
        tam_count = {}
        for r in reportes:
            t = str(r.get("tipo_nombre", "N/A"))
            z = str(r.get("zona_nombre", "N/A"))
            m = str(r.get("material_nombre", "N/A"))
            tam = str(r.get("tamano_nombre", "N/A"))
            tipos_count[t] = tipos_count.get(t, 0) + 1
            zonas_count[z] = zonas_count.get(z, 0) + 1
            mat_count[m] = mat_count.get(m, 0) + 1
            tam_count[tam] = tam_count.get(tam, 0) + 1
            
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Resumen Visual de esta Exportación", styles['Heading2']))
        
        # Tipo solo si es más de 1
        if len(tipos_count) > 1:
            d_pie = Drawing(400, 180)
            pie = Pie()
            pie.x = 125; pie.y = 20; pie.width = 140; pie.height = 140
            t_labels = list(tipos_count.keys())
            t_values = list(tipos_count.values())
            t_total = sum(t_values)
            if t_total > 0:
                pie.data = t_values
                pie.labels = [f"{l} ({v/t_total*100:.1f}%)" for l, v in zip(t_labels, t_values)]
                pie.sideLabels = 1; pie.slices.strokeWidth = 0.5
                d_pie.add(pie)
                elements.append(KeepTogether([
                    Paragraph("Distribución por Tipo", styles['Heading3']),
                    d_pie,
                    Spacer(1, 20)
                ]))
                
        # Material
        if len(mat_count) > 1:
            d_mat = Drawing(400, 220)
            bc_m = VerticalBarChart()
            bc_m.x = 50; bc_m.y = 70; bc_m.height = 125; bc_m.width = 300
            m_labels = list(mat_count.keys())
            m_values = list(mat_count.values())
            m_total = sum(m_values)
            if m_total > 0:
                bc_m.data = [m_values]
                bc_m.categoryAxis.categoryNames = [f"{l[:8]}.. ({v/m_total*100:.0f}%)" if len(l)>8 else f"{l} ({v/m_total*100:.0f}%)" for l, v in zip(m_labels, m_values)]
                bc_m.categoryAxis.labels.angle = 30; bc_m.categoryAxis.labels.dy = -15
                bc_m.valueAxis.valueMin = 0
                bc_m.bars[0].fillColor = colors.HexColor("#0ea5e9") # Blue for materials
                bc_m.barSpacing = 5
                d_mat.add(bc_m)
                elements.append(KeepTogether([
                    Paragraph("Distribución por Material", styles['Heading3']),
                    d_mat,
                    Spacer(1, 20)
                ]))
            
        # Zonas
        if len(zonas_count) > 1:
            d_bar = Drawing(400, 220)
            bc = VerticalBarChart()
            bc.x = 50; bc.y = 70; bc.height = 125; bc.width = 300
            z_labels = list(zonas_count.keys())
            z_values = list(zonas_count.values())
            z_total = sum(z_values)
            if z_total > 0:
                bc.data = [z_values]
                bc.categoryAxis.categoryNames = [f"{l[:8]}.. ({v/z_total*100:.0f}%)" if len(l)>8 else f"{l} ({v/z_total*100:.0f}%)" for l, v in zip(z_labels, z_values)]
                bc.categoryAxis.labels.angle = 30; bc.categoryAxis.labels.dy = -15
                bc.valueAxis.valueMin = 0
                bc.bars[0].fillColor = colors.HexColor("#22c55e") # Verde
                bc.barSpacing = 5
                d_bar.add(bc)
                elements.append(KeepTogether([
                    Paragraph("Distribución por Zona", styles['Heading3']),
                    d_bar,
                    Spacer(1, 20)
                ]))
            
        # Tamaño
        if len(tam_count) > 1:
            d_tam = Drawing(400, 180)
            pie_tam = Pie()
            pie_tam.x = 125; pie_tam.y = 20; pie_tam.width = 140; pie_tam.height = 140
            tam_labels = list(tam_count.keys())
            tam_values = list(tam_count.values())
            tam_total = sum(tam_values)
            if tam_total > 0:
                pie_tam.data = tam_values
                pie_tam.labels = [f"{l} ({v/tam_total*100:.1f}%)" for l, v in zip(tam_labels, tam_values)]
                pie_tam.sideLabels = 1; pie_tam.slices.strokeWidth = 0.5
                d_tam.add(pie_tam)
                elements.append(KeepTogether([
                    Paragraph("Distribución por Tamaño", styles['Heading3']),
                    d_tam,
                    Spacer(1, 20)
                ]))
    
    # Construir el PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer

def generar_pdf_resumen(stats: dict, trends: list, recent_reports: list, usuario: dict = None) -> io.BytesIO:
    """
    Genera un PDF con el resumen ejecutivo del dashboard.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    h2_style = styles['Heading2']
    
    elements.append(Paragraph("Resumen Ejecutivo de Residuos", title_style))
    
    if usuario and "nombre" in usuario:
        from time import strftime
        fecha_actual = strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"<b>Generado por:</b> {usuario['nombre']} ({usuario.get('email', '')})", normal_style))
        elements.append(Paragraph(f"<b>Fecha de exportación:</b> {fecha_actual}", normal_style))
        
    elements.append(Spacer(1, 20))
    
    # KPIs
    elements.append(Paragraph("Indicadores Principales (KPIs)", h2_style))
    kpi_data = [
        ["Total Reportes", "Usuarios Activos"],
        [str(stats.get('total_reportes', 0)), str(stats.get('usuarios_activos', 0))]
    ]
    kpi_table = Table(kpi_data, colWidths=[200, 200])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#22c55e")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 18),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))
    
    # Distribución Tipos
    t_title = Paragraph("Distribución por Tipo de Residuo", h2_style)
    tipos_data = [["Tipo", "Cantidad"]]
    for t in stats.get('distribucion_tipos', []):
        tipos_data.append([Paragraph(t.get('label', ''), normal_style), str(t.get('value', 0))])
    if len(tipos_data) > 1:
        t_table = Table(tipos_data, colWidths=[250, 150])
        t_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ]))
        
        # Render Pie Chart
        d = Drawing(400, 180)
        pie = Pie()
        pie.x = 125
        pie.y = 20
        pie.width = 140
        pie.height = 140
        valid_data = [t.get('value', 0) for t in stats.get('distribucion_tipos', []) if t.get('value', 0) > 0]
        valid_labels = [t.get('label', '') for t in stats.get('distribucion_tipos', []) if t.get('value', 0) > 0]
        if valid_data:
            total_pie = sum(valid_data)
            pie.data = valid_data
            pie.labels = [f"{l} ({v/total_pie*100:.1f}%)" for l, v in zip(valid_labels, valid_data)]
            pie.sideLabels = 1
            pie.slices.strokeWidth = 0.5
            d.add(pie)
            elements.append(KeepTogether([
                t_title,
                Spacer(1, 10),
                t_table,
                Spacer(1, 10),
                d
            ]))
        else:
            elements.append(KeepTogether([t_title, Spacer(1, 10), t_table]))

    else:
        elements.append(KeepTogether([t_title, Paragraph("No hay datos.", normal_style)]))
        
    elements.append(Spacer(1, 20))
    
    # Distribución Zonas
    z_title = Paragraph("Reportes por Zona", h2_style)
    zonas_data = [["Zona", "Cantidad"]]
    for z in stats.get('distribucion_zonas', []):
        zonas_data.append([Paragraph(z.get('label', ''), normal_style), str(z.get('value', 0))])
    if len(zonas_data) > 1:
        z_table = Table(zonas_data, colWidths=[250, 150])
        z_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ]))
        
        # Render Bar Chart
        d = Drawing(400, 220)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 70
        bc.height = 125
        bc.width = 300
        
        values = [z.get('value', 0) for z in stats.get('distribucion_zonas', [])]
        labels = [z.get('label', '') for z in stats.get('distribucion_zonas', [])]
        
        if values and max(values) > 0:
            total_bar = sum(values)
            bc.data = [values]
            bc.categoryAxis.categoryNames = [f"{l[:8]}.. ({v/total_bar*100:.0f}%)" if len(l)>8 else f"{l} ({v/total_bar*100:.0f}%)" for l, v in zip(labels, values)]
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.dy = -15
            bc.valueAxis.valueMin = 0
            bc.bars[0].fillColor = colors.HexColor("#22c55e")
            bc.barSpacing = 5
            d.add(bc)
            elements.append(KeepTogether([
                z_title,
                Spacer(1, 10),
                z_table,
                Spacer(1, 10),
                d
            ]))
        else:
            elements.append(KeepTogether([z_title, Spacer(1, 10), z_table]))

    else:
        elements.append(KeepTogether([z_title, Paragraph("No hay datos.", normal_style)]))
        
    elements.append(Spacer(1, 20))
    
    # Materiales
    m_title = Paragraph("Materiales más Reportados", h2_style)
    mats_data = [["Material", "Cantidad"]]
    for m in stats.get('distribucion_materiales', []):
        mats_data.append([Paragraph(m.get('label', ''), normal_style), str(m.get('value', 0))])
    
    if len(mats_data) > 1:
        m_table = Table(mats_data, colWidths=[250, 150])
        m_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ]))
        
        # Render Bar Chart for Materiales
        d_m = Drawing(400, 220)
        bc_m = VerticalBarChart()
        bc_m.x = 50; bc_m.y = 70; bc_m.height = 125; bc_m.width = 300
        m_values = [m.get('value', 0) for m in stats.get('distribucion_materiales', [])]
        m_labels = [m.get('label', '') for m in stats.get('distribucion_materiales', [])]
        if m_values and max(m_values) > 0:
            total_m = sum(m_values)
            bc_m.data = [m_values]
            bc_m.categoryAxis.categoryNames = [f"{l[:8]}.. ({v/total_m*100:.0f}%)" if len(l)>8 else f"{l} ({v/total_m*100:.0f}%)" for l, v in zip(m_labels, m_values)]
            bc_m.categoryAxis.labels.angle = 30; bc_m.categoryAxis.labels.dy = -15
            bc_m.valueAxis.valueMin = 0
            bc_m.bars[0].fillColor = colors.HexColor("#0ea5e9") # Blue
            bc_m.barSpacing = 5
            d_m.add(bc_m)
            elements.append(KeepTogether([
                m_title,
                Spacer(1, 10),
                m_table,
                Spacer(1, 10),
                d_m
            ]))
        else:
            elements.append(KeepTogether([m_title, Spacer(1, 10), m_table]))
    else:
        elements.append(KeepTogether([m_title, Paragraph("No hay datos.", normal_style)]))

    elements.append(Spacer(1, 20))

    # Reportes Recientes
    r_title = Paragraph("Últimos 5 Reportes Recientes", h2_style)
    rep_data = [["Fecha", "Autor", "Tipo", "Zona", "Material"]]
    for r in recent_reports:
        fecha = str(r.get("fecha_reporte", "")).split()[0] if r.get("fecha_reporte") else ""
        rep_data.append([
            fecha,
            Paragraph(str(r.get("usuario_nombre", "N/A")), normal_style),
            Paragraph(str(r.get("tipo_nombre", "N/A")), normal_style),
            Paragraph(str(r.get("zona_nombre", "N/A")), normal_style),
            Paragraph(str(r.get("material_nombre", "N/A")), normal_style)
        ])
    
    if len(rep_data) > 1:
        rep_table = Table(rep_data, colWidths=[65, 80, 80, 100, 100])
        rep_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ]))
        elements.append(KeepTogether([r_title, Spacer(1, 10), rep_table]))
    else:
        elements.append(KeepTogether([r_title, Paragraph("No hay reportes.", normal_style)]))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer
