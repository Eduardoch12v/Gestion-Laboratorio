from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from .models import Resultado
from pacientes.models import Paciente
from doctores.models import Doctor
from citas.models import Cita


def lista_resultados(request):

    q = request.GET.get('q')

    resultados = Resultado.objects.all().order_by('-fecha')

    if q:
        resultados = resultados.filter(
            paciente__nombre__icontains=q
        )

    return render(request,'resultados/lista.html',{
        'resultados': resultados
    })


def nuevo_resultado(request):

    pacientes = Paciente.objects.all()
    doctores = Doctor.objects.all()
    citas = Cita.objects.all()

    if request.method == 'POST':

        Resultado.objects.create(
            paciente_id=request.POST['paciente'],
            doctor_id=request.POST['doctor'],
            cita_id=request.POST['cita'],
            diagnostico=request.POST['diagnostico'],
            observaciones=request.POST['observaciones']
        )

        return redirect('/resultados/')

    return render(request,'resultados/nuevo.html',{
        'pacientes': pacientes,
        'doctores': doctores,
        'citas': citas
    })


def ver_resultado(request,id):

    resultado = get_object_or_404(Resultado,id=id)

    return render(request,'resultados/ver.html',{
        'resultado': resultado
    })


def editar_resultado(request,id):

    resultado = get_object_or_404(Resultado,id=id)

    pacientes = Paciente.objects.all()
    doctores = Doctor.objects.all()
    citas = Cita.objects.all()

    if request.method == 'POST':

        resultado.paciente_id = request.POST['paciente']
        resultado.doctor_id = request.POST['doctor']
        resultado.cita_id = request.POST['cita']
        resultado.diagnostico = request.POST['diagnostico']
        resultado.observaciones = request.POST['observaciones']

        resultado.save()

        return redirect('/resultados/')

    return render(request,'resultados/editar.html',{
        'resultado': resultado,
        'pacientes': pacientes,
        'doctores': doctores,
        'citas': citas
    })


def eliminar_resultado(request,id):

    resultado = get_object_or_404(Resultado,id=id)
    resultado.delete()

    return redirect('/resultados/')


# ---------- PDF ----------

def pdf_resultado(request, id):
    
    import qrcode
    import qrcode.image.svg
    from io import BytesIO
    from datetime import datetime

    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable,
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.graphics.shapes import Drawing, Rect, String, Line
    from reportlab.graphics import renderPDF

    
    # PALETA PREMIUM
    
    MARINO        = colors.HexColor("#0a1628")   # fondo header
    AZUL          = colors.HexColor("#0d6efd")   # acento principal
    AZUL_MED      = colors.HexColor("#1a3a6b")   # banda media header
    DORADO        = colors.HexColor("#c9a84c")   # detalle premium
    DORADO_CLARO  = colors.HexColor("#f0d080")   # resalte dorado suave
    MARFIL        = colors.HexColor("#faf8f3")   # fondo secciones
    GRIS_LINEA    = colors.HexColor("#dde3ec")
    GRIS_TEXTO    = colors.HexColor("#4a5568")
    GRIS_LABEL    = colors.HexColor("#718096")
    VERDE_ESTADO  = colors.HexColor("#1a7a4a")
    VERDE_FONDO   = colors.HexColor("#e6f4ed")
    BLANCO        = colors.white

    
    # DATOS
    
    resultado       = get_object_or_404(Resultado, id=id)
    paciente        = resultado.paciente
    nombre_completo = f"{paciente.nombre} {paciente.apellido}"
    folio           = f"SC-{resultado.id:06d}"
    fecha_emision   = datetime.now().strftime("%d de %B de %Y")

    
    # RESPUESTA HTTP
    
    filename = f"resultado_{paciente.nombre}_{paciente.apellido}_{folio}.pdf"
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    
    # DOCUMENTO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=24 * mm,
        title=f"Resultado Médico – {nombre_completo}",
        author="Sistema Clínico",
        subject="Resultado médico oficial",
    )

    W, H = letter
    UW = W - doc.leftMargin - doc.rightMargin  # ancho útil

    
    # ESTILOS DE PÁRRAFO
    
    def E(nombre, **kw):
        return ParagraphStyle(nombre, **kw)

    # Header
    st_inst     = E("Inst",     fontSize=19, fontName="Helvetica-Bold",
                    textColor=BLANCO,       alignment=TA_LEFT,  leading=23)
    st_dep      = E("Dep",      fontSize=8,  fontName="Helvetica",
                    textColor=DORADO_CLARO, alignment=TA_LEFT,  leading=11, spaceBefore=1)
    st_tipo     = E("Tipo",     fontSize=10, fontName="Helvetica-Bold",
                    textColor=DORADO,       alignment=TA_RIGHT, leading=13)
    st_folio_h  = E("FolioH",   fontSize=8,  fontName="Helvetica",
                    textColor=colors.HexColor("#a0b4cc"), alignment=TA_RIGHT, leading=11)

    # Secciones
    st_sec      = E("Sec",      fontSize=10, fontName="Helvetica-Bold",
                    textColor=MARINO,       alignment=TA_LEFT,  leading=14, spaceBefore=4)
    st_label    = E("Label",    fontSize=7,  fontName="Helvetica-Bold",
                    textColor=GRIS_LABEL,   alignment=TA_LEFT,  leading=10,
                    spaceBefore=3, spaceAfter=1)
    st_valor    = E("Valor",    fontSize=10, fontName="Helvetica",
                    textColor=MARINO,       alignment=TA_LEFT,  leading=14)
    st_cuerpo   = E("Cuerpo",   fontSize=10, fontName="Helvetica",
                    textColor=GRIS_TEXTO,   alignment=TA_JUSTIFY, leading=16, spaceAfter=4)
    st_legal    = E("Legal",    fontSize=8,  fontName="Helvetica",
                    textColor=GRIS_LABEL,   alignment=TA_JUSTIFY, leading=12)
    st_firma_n  = E("FirmaN",   fontSize=9,  fontName="Helvetica-Bold",
                    textColor=MARINO,       alignment=TA_CENTER, leading=12)
    st_firma_l  = E("FirmaL",   fontSize=7,  fontName="Helvetica",
                    textColor=GRIS_LABEL,   alignment=TA_CENTER, leading=10)
    st_badge    = E("Badge",    fontSize=8,  fontName="Helvetica-Bold",
                    textColor=VERDE_ESTADO, alignment=TA_CENTER, leading=11)
    st_qr_cap   = E("QRCap",   fontSize=6.5, fontName="Helvetica",
                    textColor=GRIS_LABEL,   alignment=TA_CENTER, leading=9)

    
    # QR CODE  (datos de verificación)
    
    qr_data = (
        f"FOLIO:{folio}|PACIENTE:{nombre_completo}|"
        f"DOCTOR:{resultado.doctor}|FECHA:{resultado.fecha}"
    )
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_flowable = Image(qr_buffer, width=22 * mm, height=22 * mm)

    
    # ENCABEZADO PREMIUM (3 columnas: logo · separador · meta)
    
    col_logo  = UW * 0.52
    col_sep   = UW * 0.03
    col_meta  = UW * 0.45

    header_izq = [
        Paragraph("Sistema Clínico", st_inst),
        Paragraph("Departamento Médico &nbsp;·&nbsp; Resultados Oficiales", st_dep),
    ]
    header_der = [
        Paragraph("RESULTADO MÉDICO", st_tipo),
        Spacer(1, 3),
        Paragraph(f"Folio: <b>{folio}</b>", st_folio_h),
        Paragraph(f"Emitido: {fecha_emision}", st_folio_h),
    ]

    tabla_header = Table(
        [[header_izq, "", header_der]],
        colWidths=[col_logo, col_sep, col_meta],
    )
    tabla_header.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MARINO),
        ("LINEAFTER",     (0, 0), (0, 0),   1.5, DORADO),
        ("LEFTPADDING",   (0, 0), (0, 0),   14),
        ("RIGHTPADDING",  (2, 0), (2, 0),   14),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))

    # Franja dorada inferior del header
    franja_dorada = Table(
        [[""]],
        colWidths=[UW],
        rowHeights=[2.5],
    )
    franja_dorada.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DORADO),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    
    # BADGE DE ESTADO
    
    badge_tabla = Table(
        [[Paragraph("✔  RESULTADO VERIFICADO", st_badge)]],
        colWidths=[UW],
    )
    badge_tabla.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), VERDE_FONDO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX",           (0, 0), (-1, -1), 0.8, VERDE_ESTADO),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))

    
    # TABLA DE DATOS DEL PACIENTE (estilizada, 2 col)
    
    # Tabla de 4 columnas: [etiqueta izq | valor izq | etiqueta der | valor der]
    # Anchos: label angosto, valor amplio, separador, label angosto, valor amplio
    C_LBL = UW * 0.20   # columna etiqueta
    C_VAL = UW * 0.28   # columna valor
    C_SEP = UW * 0.04   # espacio central
    # Total: (C_LBL + C_VAL) * 2 + C_SEP = UW ✓

    def lbl(texto):
        return Paragraph(texto.upper(), st_label)

    def val(texto):
        return Paragraph(str(texto) if texto else "—", st_valor)

    filas_paciente = [
        [lbl("Nombre del paciente"), val(nombre_completo),   "", lbl("Médico responsable"),  val(resultado.doctor)],
        [lbl("Teléfono"),            val(paciente.telefono), "", lbl("Fecha del resultado"),  val(resultado.fecha)],
        [lbl("Correo electrónico"),  val(paciente.correo),   "", lbl("Área / Especialidad"),  val(getattr(resultado, 'area', 'Medicina General'))],
    ]

    tabla_paciente = Table(
        filas_paciente,
        colWidths=[C_LBL, C_VAL, C_SEP, C_LBL, C_VAL],
        hAlign="LEFT",
    )
    tabla_paciente.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MARFIL),
        # Padding general
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        # Separador central (columna 2 es el espacio)
        ("BACKGROUND",    (2, 0), (2, -1), GRIS_LINEA),
        ("LEFTPADDING",   (2, 0), (2, -1), 0),
        ("RIGHTPADDING",  (2, 0), (2, -1), 0),
        # Líneas separadoras horizontales entre filas
        ("LINEBELOW",     (0, 0), (1, -2), 0.5, GRIS_LINEA),
        ("LINEBELOW",     (3, 0), (4, -2), 0.5, GRIS_LINEA),
        # Borde exterior
        ("BOX",           (0, 0), (-1, -1), 0.6, GRIS_LINEA),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))

    
    # SECCIÓN CLÍNICA (con word-wrap automático)
    
    def encabezado_seccion(titulo):
        linea = Table([["", ""]], colWidths=[3, UW - 3])
        linea.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), DORADO),
            ("BACKGROUND",    (1, 0), (1, 0), MARINO),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        return [linea, Spacer(1, 5), Paragraph(titulo, st_sec), Spacer(1, 6)]

    def seccion(titulo, texto):
        wrapped = Table(
            [[Paragraph(texto or "Sin información registrada.", st_cuerpo)]],
            colWidths=[UW],
        )
        wrapped.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), BLANCO),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
            ("LINEBEFORE",    (0, 0), (0, -1),  3,   AZUL),
        ]))
        return [*encabezado_seccion(titulo), wrapped]

    
    # FIRMA + QR  (lado a lado)
    
    col_firma_w = UW * 0.45
    col_qr_w    = UW * 0.25
    col_esp     = UW * 0.30

    firma_contenido = [
        HRFlowable(width=col_firma_w, thickness=0.8, color=MARINO, spaceAfter=5),
        Paragraph(str(resultado.doctor), st_firma_n),
        Paragraph("Médico Responsable", st_firma_l),
        Spacer(1, 3),
        Paragraph(f"Cédula Profesional: {getattr(resultado, 'cedula', 'N/D')}", st_firma_l),
    ]

    qr_contenido = [
        qr_flowable,
        Spacer(1, 3),
        Paragraph("Escanea para verificar", st_qr_cap),
        Paragraph(folio, E("FolioQR", fontSize=6, fontName="Helvetica-Bold",
                            textColor=MARINO, alignment=TA_CENTER, leading=8)),
    ]

    tabla_firma_qr = Table(
        [[firma_contenido, "", qr_contenido]],
        colWidths=[col_firma_w, col_esp, col_qr_w],
    )
    tabla_firma_qr.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "BOTTOM"),
        ("ALIGN",        (2, 0), (2, 0),   "CENTER"),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))

    
    # AVISO LEGAL
    
    legal_texto = (
        "Este documento es de carácter confidencial y de uso exclusivo del personal médico "
        "autorizado. La información aquí contenida forma parte del expediente clínico del "
        "paciente y ha sido generada por el Sistema Clínico. Su reproducción, divulgación "
        "o uso no autorizado está estrictamente prohibido y puede constituir una infracción "
        "legal. Para verificar la autenticidad de este documento, escanee el código QR."
    )
    tabla_legal = Table(
        [[Paragraph(legal_texto, st_legal)]],
        colWidths=[UW],
    )
    tabla_legal.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f0f3f8")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("LINEBEFORE",    (0, 0), (0, -1),  3,   DORADO),
    ]))

    
    # PIE DE PÁGINA (callback)
    
    def pie_pagina(c, d):
        c.saveState()

        # Franja marina inferior
        c.setFillColor(MARINO)
        c.rect(0, 0, W, 16 * mm, fill=1, stroke=0)

        # Línea dorada sobre la franja
        c.setStrokeColor(DORADO)
        c.setLineWidth(1)
        c.line(0, 16 * mm, W, 16 * mm)

        # Texto pie
        c.setFillColor(BLANCO)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(W / 2, 9 * mm,
            "Sistema Clínico  ·  Documento Médico Oficial  ·  Confidencial")

        c.setFillColor(colors.HexColor("#a0b4cc"))
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(W / 2, 5 * mm, "Proyecto escolar · Uso exclusivo del personal autorizado")

        # Folio y página (derecha)
        c.setFillColor(DORADO_CLARO)
        c.setFont("Helvetica-Bold", 7)
        c.drawRightString(W - d.rightMargin, 9 * mm, f"{folio}")
        c.setFillColor(colors.HexColor("#a0b4cc"))
        c.setFont("Helvetica", 6.5)
        c.drawRightString(W - d.rightMargin, 5 * mm, f"Página {d.page}")

        c.restoreState()

    
    # ENSAMBLE
    
    historia = [
        tabla_header,
        franja_dorada,
        Spacer(1, 8),
        badge_tabla,
        Spacer(1, 12),

        # — Paciente —
        *encabezado_seccion("Información del Paciente"),
        tabla_paciente,
        Spacer(1, 12),

        # — Diagnóstico —
        *seccion("Diagnóstico Médico", resultado.diagnostico),
        Spacer(1, 12),

        # — Observaciones —
        *seccion("Observaciones Clínicas", resultado.observaciones),
        Spacer(1, 20),

        # — Firma + QR —
        tabla_firma_qr,
        Spacer(1, 14),

        # — Legal —
        tabla_legal,
    ]

    doc.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)

    pdf = buffer.getvalue()
    buffer.close()

    
    import os, webbrowser

    ruta = os.path.join(
    os.path.expanduser("~"),
    "Downloads",
    f"resultado_{paciente.nombre}{paciente.apellido}{folio}.pdf"
    )

    with open(ruta, "wb") as f:
     f.write(pdf)

    webbrowser.open(ruta)

     
    response.write(pdf)
    return response