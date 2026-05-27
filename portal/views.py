from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.timezone import now

from pacientes.models import Paciente
from citas.models import Cita
from resultados.models import Resultado


@login_required
def portal_dashboard(request):

    paciente = Paciente.objects.filter(usuario=request.user).first()

   
    if not paciente:
        paciente = Paciente.objects.filter(
            correo=request.user.username
        ).first()

        if paciente:
            paciente.usuario = request.user
            paciente.save()

    citas = Cita.objects.filter(
        paciente=paciente,
        fecha__gte=now().date()
    ).order_by('fecha')

    resultados = Resultado.objects.filter(
        paciente=paciente
    ).order_by('-fecha')

    context = {
        'paciente': paciente,
        'citas': citas,
        'resultados': resultados,
    }

    return render(request, 'portal/dashboard.html', context)

@login_required
def descargar_pdf(request):
    """
    Genera el expediente médico en PDF premium para el paciente autenticado.
    Paleta: azul marino · dorado · blanco — misma identidad del sistema clínico.
    """
    import qrcode
    from io import BytesIO
    from datetime import datetime

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable, Image, Paragraph,
        SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    
    # PALETA
    
    MARINO       = colors.HexColor("#0a1628")
    AZUL         = colors.HexColor("#0d6efd")
    AZUL_SUAVE   = colors.HexColor("#eef4ff")
    DORADO       = colors.HexColor("#c9a84c")
    DORADO_CLARO = colors.HexColor("#f0d080")
    MARFIL       = colors.HexColor("#faf8f3")
    GRIS_LINEA   = colors.HexColor("#dde3ec")
    GRIS_TEXTO   = colors.HexColor("#4a5568")
    GRIS_LABEL   = colors.HexColor("#718096")
    VERDE_ESTADO = colors.HexColor("#1a7a4a")
    VERDE_FONDO  = colors.HexColor("#e6f4ed")
    BLANCO       = colors.white

    
    # DATOS
    
    paciente        = Paciente.objects.filter(usuario=request.user).first()
    nombre_completo = f"{paciente.nombre} {paciente.apellido}"
    folio           = f"PC-{paciente.id:06d}"
    fecha_emision   = datetime.now().strftime("%d de %B de %Y")

    citas = Cita.objects.filter(
        paciente=paciente,
        fecha__gte=now().date()
    ).order_by('fecha')

    resultados = Resultado.objects.filter(
        paciente=paciente
    ).order_by('-fecha')

   
    # RESPUESTA HTTP
   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="Expediente_{paciente.nombre}_{paciente.apellido}.pdf"'
    )

   
    # DOCUMENTO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=24 * mm,
        title=f"Expediente Médico – {nombre_completo}",
        author="Sistema Clínico",
    )

    W, H = letter
    UW = W - doc.leftMargin - doc.rightMargin

   
    # ESTILOS
    
    def E(nombre, **kw):
        return ParagraphStyle(nombre, **kw)

    st_inst         = E("Inst",    fontSize=19, fontName="Helvetica-Bold",
                        textColor=BLANCO,        alignment=TA_LEFT,   leading=23)
    st_dep          = E("Dep",     fontSize=8,  fontName="Helvetica",
                        textColor=DORADO_CLARO,  alignment=TA_LEFT,   leading=11, spaceBefore=1)
    st_tipo         = E("Tipo",    fontSize=10, fontName="Helvetica-Bold",
                        textColor=DORADO,         alignment=TA_RIGHT,  leading=13)
    st_folio_h      = E("FolioH",  fontSize=8,  fontName="Helvetica",
                        textColor=colors.HexColor("#a0b4cc"), alignment=TA_RIGHT, leading=11)
    st_sec          = E("Sec",     fontSize=10, fontName="Helvetica-Bold",
                        textColor=MARINO,         alignment=TA_LEFT,   leading=14, spaceBefore=4)
    st_label        = E("Label",   fontSize=7,  fontName="Helvetica-Bold",
                        textColor=GRIS_LABEL,     alignment=TA_LEFT,   leading=10,
                        spaceBefore=3, spaceAfter=1)
    st_valor        = E("Valor",   fontSize=10, fontName="Helvetica",
                        textColor=MARINO,         alignment=TA_LEFT,   leading=14)
    st_cuerpo       = E("Cuerpo",  fontSize=10, fontName="Helvetica",
                        textColor=GRIS_TEXTO,     alignment=TA_JUSTIFY, leading=16, spaceAfter=4)
    st_legal        = E("Legal",   fontSize=8,  fontName="Helvetica",
                        textColor=GRIS_LABEL,     alignment=TA_JUSTIFY, leading=12)
    st_badge        = E("Badge",   fontSize=8,  fontName="Helvetica-Bold",
                        textColor=VERDE_ESTADO,   alignment=TA_CENTER,  leading=11)
    st_qr_cap       = E("QRCap",   fontSize=6.5, fontName="Helvetica",
                        textColor=GRIS_LABEL,     alignment=TA_CENTER,  leading=9)
    st_bienvenida   = E("Bienvenida", fontSize=11, fontName="Helvetica-Bold",
                        textColor=MARINO,         alignment=TA_LEFT,   leading=15)
    st_bienvenida_p = E("BienvenidaP", fontSize=9, fontName="Helvetica",
                        textColor=GRIS_TEXTO,     alignment=TA_LEFT,   leading=13, spaceAfter=4)
    st_sin_datos    = E("SinDatos", fontSize=9, fontName="Helvetica",
                        textColor=GRIS_LABEL,     alignment=TA_CENTER,  leading=13)
    st_num_tarjeta  = E("NumTarjeta", fontSize=8, fontName="Helvetica-Bold",
                        textColor=BLANCO,         alignment=TA_LEFT,   leading=11)

 
    # QR CODE
   
    qr_img = qrcode.make(
        f"FOLIO:{folio}|PACIENTE:{nombre_completo}|EMITIDO:{fecha_emision}"
    )
    qr_buf = BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_flowable = Image(qr_buf, width=22 * mm, height=22 * mm)

   
    # HELPERS REUTILIZABLES
   
    def lbl(texto):
        return Paragraph(texto.upper(), st_label)

    def val(texto):
        return Paragraph(str(texto) if texto else "—", st_valor)

    def encabezado_seccion(titulo):
        barra = Table([["", ""]], colWidths=[3, UW - 3])
        barra.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0),   DORADO),
            ("BACKGROUND",    (1, 0), (1, 0),   MARINO),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        return [barra, Spacer(1, 5), Paragraph(titulo, st_sec), Spacer(1, 6)]

    def caja_sin_datos(texto):
        t = Table([[Paragraph(texto, st_sin_datos)]], colWidths=[UW])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), MARFIL),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        return t

    def tarjeta(encabezado_color, titulo, filas_datos, acento_izq=None):
        """
        Construye una tarjeta con encabezado de color y filas [label, valor].
        filas_datos: lista de (texto_label, texto_valor)
        """
        enc = Table([[Paragraph(titulo, st_num_tarjeta)]], colWidths=[UW])
        enc.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), encabezado_color),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        C_L = UW * 0.30
        C_V = UW * 0.70
        filas = [[lbl(l), val(v)] for l, v in filas_datos]
        cuerpo_inner = Table(filas, colWidths=[C_L, C_V])
        cuerpo_inner.setStyle(TableStyle([
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.4, GRIS_LINEA),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))

        estilo_cuerpo = [
            ("BACKGROUND",    (0, 0), (-1, -1), MARFIL),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ]
        if acento_izq:
            estilo_cuerpo.append(("LINEBEFORE", (0, 0), (0, -1), 3, acento_izq))

        cuerpo = Table([[cuerpo_inner]], colWidths=[UW])
        cuerpo.setStyle(TableStyle(estilo_cuerpo))

        return [enc, cuerpo, Spacer(1, 8)]

  
    # ENCABEZADO PREMIUM
   
    tabla_header = Table(
        [[
            [
                Paragraph("Sistema Clínico", st_inst),
                Paragraph("Departamento Médico &nbsp;·&nbsp; Atención al Paciente", st_dep),
            ],
            "",
            [
                Paragraph("EXPEDIENTE MÉDICO", st_tipo),
                Spacer(1, 3),
                Paragraph(f"Folio: <b>{folio}</b>", st_folio_h),
                Paragraph(f"Emitido: {fecha_emision}", st_folio_h),
            ],
        ]],
        colWidths=[UW * 0.52, UW * 0.03, UW * 0.45],
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

    franja_dorada = Table([[""]],  colWidths=[UW], rowHeights=[2.5])
    franja_dorada.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DORADO),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    
    # BADGE
  
    badge = Table(
        [[Paragraph("✔  DOCUMENTO OFICIAL PARA EL PACIENTE", st_badge)]],
        colWidths=[UW],
    )
    badge.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), VERDE_FONDO),
        ("BOX",           (0, 0), (-1, -1), 0.8, VERDE_ESTADO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))

   
    # BIENVENIDA
    
    bienvenida = Table(
        [[
            Paragraph(f"Hola, {paciente.nombre} \U0001f44b", st_bienvenida),
            Paragraph(
                "Este documento contiene tu expediente médico personal: "
                "tus datos, tus próximas citas y tus resultados registrados. "
                "Guárdalo en un lugar seguro.",
                st_bienvenida_p,
            ),
        ]],
        colWidths=[UW],
    )
    bienvenida.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_SUAVE),
        ("BOX",           (0, 0), (-1, -1), 0.6, AZUL),
        ("LINEBEFORE",    (0, 0), (0, -1),  4,   AZUL),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("SPAN",          (0, 0), (-1, -1)),
    ]))

    
    # DATOS DEL PACIENTE
  
    C_LBL = UW * 0.20
    C_VAL = UW * 0.28
    C_SEP = UW * 0.04

    tabla_paciente = Table(
        [
            [lbl("Tu nombre"),  val(nombre_completo),   "", lbl("Tu teléfono"), val(paciente.telefono)],
            [lbl("Tu correo"),  val(paciente.correo),   "", lbl(""),            val("")                ],
        ],
        colWidths=[C_LBL, C_VAL, C_SEP, C_LBL, C_VAL],
    )
    tabla_paciente.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MARFIL),
        ("BACKGROUND",    (2, 0), (2, -1),  GRIS_LINEA),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (2, 0), (2, -1),  0),
        ("RIGHTPADDING",  (2, 0), (2, -1),  0),
        ("LINEBELOW",     (0, 0), (1, -2),  0.5, GRIS_LINEA),
        ("LINEBELOW",     (3, 0), (4, -2),  0.5, GRIS_LINEA),
        ("BOX",           (0, 0), (-1, -1), 0.6, GRIS_LINEA),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))

    
    # CITAS
    
    elementos_citas = []
    if citas.exists():
        for i, cita in enumerate(citas, 1):
            elementos_citas += tarjeta(
                encabezado_color=AZUL,
                titulo=f"Cita #{i}",
                filas_datos=[
                    ("¿Cuándo?",    cita.fecha),
                    ("¿A qué hora?", cita.hora),
                    ("Tu médico",    cita.doctor),
                ],
                acento_izq=None,
            )
    else:
        elementos_citas.append(
            caja_sin_datos("No tienes citas próximas registradas.")
        )

    
    # RESULTADOS
  
    elementos_resultados = []
    if resultados.exists():
        for i, r in enumerate(resultados, 1):
            filas = [("¿Cuándo?", r.fecha), ("Tu médico", r.doctor)]
            if r.diagnostico:
                filas.append(("Lo que encontró", r.diagnostico))
            if r.observaciones:
                filas.append(("Recomendación", r.observaciones))
            elementos_resultados += tarjeta(
                encabezado_color=MARINO,
                titulo=f"Resultado #{i}",
                filas_datos=filas,
                acento_izq=DORADO,
            )
    else:
        elementos_resultados.append(
            caja_sin_datos("No tienes resultados médicos registrados.")
        )

    
    # MENSAJE FINAL + QR
    
    col_msg = UW * 0.75
    col_qr  = UW * 0.25

    tabla_final = Table(
        [[
            [
                Paragraph("¿Tienes dudas sobre este documento?", E(
                    "MsgT", fontSize=9, fontName="Helvetica-Bold",
                    textColor=MARINO, alignment=TA_LEFT, leading=13,
                )),
                Spacer(1, 4),
                Paragraph(
                    "Puedes acercarte a tu médico o a la recepción de la clínica "
                    "para aclarar cualquier información. El código QR te permite "
                    "verificar la autenticidad de este documento.",
                    E("MsgP", fontSize=8, fontName="Helvetica",
                      textColor=GRIS_TEXTO, alignment=TA_JUSTIFY, leading=12),
                ),
            ],
            [
                qr_flowable,
                Spacer(1, 3),
                Paragraph("Verificar", st_qr_cap),
                Paragraph(folio, E("FolioQR", fontSize=6, fontName="Helvetica-Bold",
                                    textColor=MARINO, alignment=TA_CENTER, leading=8)),
            ],
        ]],
        colWidths=[col_msg, col_qr],
    )
    tabla_final.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_SUAVE),
        ("BOX",           (0, 0), (-1, -1), 0.6, AZUL),
        ("LEFTPADDING",   (0, 0), (0, 0),   14),
        ("RIGHTPADDING",  (0, 0), (0, 0),   8),
        ("LEFTPADDING",   (1, 0), (1, 0),   6),
        ("RIGHTPADDING",  (1, 0), (1, 0),   10),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "CENTER"),
    ]))

    
    # AVISO LEGAL
   
    tabla_legal = Table(
        [[Paragraph(
            "Este documento ha sido generado por el Sistema Clínico exclusivamente para "
            "uso personal del paciente. La información aquí contenida es confidencial. "
            "No compartas este documento con terceros sin autorización de tu médico.",
            st_legal,
        )]],
        colWidths=[UW],
    )
    tabla_legal.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f0f3f8")),
        ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("LINEBEFORE",    (0, 0), (0, -1),  3,   DORADO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    
    # PIE DE PÁGINA
   
    def pie_pagina(c, d):
        c.saveState()
        c.setFillColor(MARINO)
        c.rect(0, 0, W, 16 * mm, fill=1, stroke=0)
        c.setStrokeColor(DORADO)
        c.setLineWidth(1)
        c.line(0, 16 * mm, W, 16 * mm)
        c.setFillColor(BLANCO)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(
            W / 2, 9 * mm,
            "Sistema Clínico  ·  Tu documento médico personal  ·  Confidencial"
        )
        c.setFillColor(colors.HexColor("#a0b4cc"))
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(W / 2, 5 * mm, "Proyecto escolar · Guárdalo en un lugar seguro")
        c.setFillColor(DORADO_CLARO)
        c.setFont("Helvetica-Bold", 7)
        c.drawRightString(W - d.rightMargin, 9 * mm, folio)
        c.setFillColor(colors.HexColor("#a0b4cc"))
        c.setFont("Helvetica", 6.5)
        c.drawRightString(W - d.rightMargin, 5 * mm, f"Página {d.page}")
        c.restoreState()

    
    # ENSAMBLE
   
    historia = [
        tabla_header,
        franja_dorada,
        Spacer(1, 8),
        badge,
        Spacer(1, 10),
        bienvenida,
        Spacer(1, 14),

        *encabezado_seccion("Tus Datos Personales"),
        tabla_paciente,
        Spacer(1, 14),

        *encabezado_seccion("Tus Próximas Citas"),
        *elementos_citas,
        Spacer(1, 6),

        *encabezado_seccion("Tus Resultados Médicos"),
        *elementos_resultados,
        Spacer(1, 14),

        tabla_final,
        Spacer(1, 10),
        tabla_legal,
    ]

    doc.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

@login_required
def exportar_citas_pdf(request):
    """
    Genera el historial de citas en PDF premium para el paciente autenticado.
    Paleta: azul marino · dorado · blanco — misma identidad del sistema clínico.
    """
    import qrcode
    from io import BytesIO
    from datetime import datetime

    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable, Image, Paragraph,
        SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    
    # PALETA
   
    MARINO       = colors.HexColor("#0a1628")
    AZUL         = colors.HexColor("#0d6efd")
    AZUL_SUAVE   = colors.HexColor("#eef4ff")
    DORADO       = colors.HexColor("#c9a84c")
    DORADO_CLARO = colors.HexColor("#f0d080")
    MARFIL       = colors.HexColor("#faf8f3")
    GRIS_LINEA   = colors.HexColor("#dde3ec")
    GRIS_TEXTO   = colors.HexColor("#4a5568")
    GRIS_LABEL   = colors.HexColor("#718096")
    VERDE_ESTADO = colors.HexColor("#1a7a4a")
    VERDE_FONDO  = colors.HexColor("#e6f4ed")
    BLANCO       = colors.white

    
    # DATOS
    
    paciente = Paciente.objects.filter(usuario=request.user).first()
    if not paciente:
        paciente = Paciente.objects.filter(correo=request.user.username).first()

    nombre_completo = f"{paciente.nombre} {paciente.apellido}"
    folio           = f"CA-{paciente.id:06d}"
    fecha_emision   = datetime.now().strftime("%d de %B de %Y")

    # Todas las citas (pasadas y futuras), más recientes primero
    citas = Cita.objects.filter(paciente=paciente).order_by('-fecha')

    
    # RESPUESTA HTTP
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="Citas_{paciente.nombre}_{paciente.apellido}.pdf"'
    )

    
    # DOCUMENTO
   
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=20 * mm,
        bottomMargin=24 * mm,
        title=f"Historial de Citas – {nombre_completo}",
        author="Sistema Clínico",
    )

    W, H = letter
    UW = W - doc.leftMargin - doc.rightMargin

    
    # ESTILOS
   
    def E(nombre, **kw):
        return ParagraphStyle(nombre, **kw)

    st_inst         = E("Inst",    fontSize=19, fontName="Helvetica-Bold",
                        textColor=BLANCO,        alignment=TA_LEFT,   leading=23)
    st_dep          = E("Dep",     fontSize=8,  fontName="Helvetica",
                        textColor=DORADO_CLARO,  alignment=TA_LEFT,   leading=11, spaceBefore=1)
    st_tipo         = E("Tipo",    fontSize=10, fontName="Helvetica-Bold",
                        textColor=DORADO,         alignment=TA_RIGHT,  leading=13)
    st_folio_h      = E("FolioH",  fontSize=8,  fontName="Helvetica",
                        textColor=colors.HexColor("#a0b4cc"), alignment=TA_RIGHT, leading=11)
    st_sec          = E("Sec",     fontSize=10, fontName="Helvetica-Bold",
                        textColor=MARINO,         alignment=TA_LEFT,   leading=14, spaceBefore=4)
    st_label        = E("Label",   fontSize=7,  fontName="Helvetica-Bold",
                        textColor=GRIS_LABEL,     alignment=TA_LEFT,   leading=10,
                        spaceBefore=3, spaceAfter=1)
    st_valor        = E("Valor",   fontSize=10, fontName="Helvetica",
                        textColor=MARINO,         alignment=TA_LEFT,   leading=14)
    st_sin_datos    = E("SinDatos", fontSize=9, fontName="Helvetica",
                        textColor=GRIS_LABEL,     alignment=TA_CENTER,  leading=13)
    st_badge        = E("Badge",   fontSize=8,  fontName="Helvetica-Bold",
                        textColor=VERDE_ESTADO,   alignment=TA_CENTER,  leading=11)
    st_qr_cap       = E("QRCap",   fontSize=6.5, fontName="Helvetica",
                        textColor=GRIS_LABEL,     alignment=TA_CENTER,  leading=9)
    st_bienvenida   = E("Bienvenida", fontSize=11, fontName="Helvetica-Bold",
                        textColor=MARINO,         alignment=TA_LEFT,   leading=15)
    st_bienvenida_p = E("BienvenidaP", fontSize=9, fontName="Helvetica",
                        textColor=GRIS_TEXTO,     alignment=TA_LEFT,   leading=13, spaceAfter=4)
    st_num_tarjeta  = E("NumTarjeta", fontSize=8, fontName="Helvetica-Bold",
                        textColor=BLANCO,         alignment=TA_LEFT,   leading=11)

    
    # QR CODE
    
    qr_img = qrcode.make(
        f"FOLIO:{folio}|PACIENTE:{nombre_completo}|EMITIDO:{fecha_emision}"
    )
    qr_buf = BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_flowable = Image(qr_buf, width=22 * mm, height=22 * mm)

    
    # HELPERS REUTILIZABLES
    
    def lbl(texto):
        return Paragraph(texto.upper(), st_label)

    def val(texto):
        return Paragraph(str(texto) if texto else "—", st_valor)

    def encabezado_seccion(titulo):
        barra = Table([["", ""]], colWidths=[3, UW - 3])
        barra.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0),   DORADO),
            ("BACKGROUND",    (1, 0), (1, 0),   MARINO),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        return [barra, Spacer(1, 5), Paragraph(titulo, st_sec), Spacer(1, 6)]

    def caja_sin_datos(texto):
        t = Table([[Paragraph(texto, st_sin_datos)]], colWidths=[UW])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), MARFIL),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        return t

    def tarjeta(encabezado_color, titulo, filas_datos, acento_izq=None):
        enc = Table([[Paragraph(titulo, st_num_tarjeta)]], colWidths=[UW])
        enc.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), encabezado_color),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))

        C_L = UW * 0.30
        C_V = UW * 0.70
        filas = [[lbl(l), val(v)] for l, v in filas_datos]
        cuerpo_inner = Table(filas, colWidths=[C_L, C_V])
        cuerpo_inner.setStyle(TableStyle([
            ("TOPPADDING",    (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("LINEBELOW",     (0, 0), (-1, -2), 0.4, GRIS_LINEA),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))

        estilo_cuerpo = [
            ("BACKGROUND",    (0, 0), (-1, -1), MARFIL),
            ("LEFTPADDING",   (0, 0), (-1, -1), 12),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ]
        if acento_izq:
            estilo_cuerpo.append(("LINEBEFORE", (0, 0), (0, -1), 3, acento_izq))

        cuerpo = Table([[cuerpo_inner]], colWidths=[UW])
        cuerpo.setStyle(TableStyle(estilo_cuerpo))

        return [enc, cuerpo, Spacer(1, 8)]

    
    # ENCABEZADO PREMIUM
    
    tabla_header = Table(
        [[
            [
                Paragraph("Sistema Clínico", st_inst),
                Paragraph("Departamento Médico &nbsp;·&nbsp; Atención al Paciente", st_dep),
            ],
            "",
            [
                Paragraph("HISTORIAL DE CITAS", st_tipo),
                Spacer(1, 3),
                Paragraph(f"Folio: <b>{folio}</b>", st_folio_h),
                Paragraph(f"Emitido: {fecha_emision}", st_folio_h),
            ],
        ]],
        colWidths=[UW * 0.52, UW * 0.03, UW * 0.45],
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

    franja_dorada = Table([[""]], colWidths=[UW], rowHeights=[2.5])
    franja_dorada.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), DORADO),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    
    # BADGE
    
    badge = Table(
        [[Paragraph("✔  DOCUMENTO OFICIAL PARA EL PACIENTE", st_badge)]],
        colWidths=[UW],
    )
    badge.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), VERDE_FONDO),
        ("BOX",           (0, 0), (-1, -1), 0.8, VERDE_ESTADO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
    ]))

    
    # BIENVENIDA
    
    total_citas = citas.count()
    bienvenida = Table(
        [[
            Paragraph(f"Hola, {paciente.nombre} \U0001f4c5", st_bienvenida),
            Paragraph(
                f"Este documento contiene tu historial completo de citas médicas "
                f"({total_citas} cita{'s' if total_citas != 1 else ''} registrada{'s' if total_citas != 1 else ''}). "
                "Guárdalo en un lugar seguro.",
                st_bienvenida_p,
            ),
        ]],
        colWidths=[UW],
    )
    bienvenida.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_SUAVE),
        ("BOX",           (0, 0), (-1, -1), 0.6, AZUL),
        ("LINEBEFORE",    (0, 0), (0, -1),  4,   AZUL),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("SPAN",          (0, 0), (-1, -1)),
    ]))

    
    # DATOS DEL PACIENTE
    
    C_LBL = UW * 0.20
    C_VAL = UW * 0.28
    C_SEP = UW * 0.04

    tabla_paciente = Table(
        [
            [lbl("Tu nombre"),  val(nombre_completo),   "", lbl("Tu teléfono"), val(paciente.telefono)],
            [lbl("Tu correo"),  val(paciente.correo),   "", lbl(""),            val("")                ],
        ],
        colWidths=[C_LBL, C_VAL, C_SEP, C_LBL, C_VAL],
    )
    tabla_paciente.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), MARFIL),
        ("BACKGROUND",    (2, 0), (2, -1),  GRIS_LINEA),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (2, 0), (2, -1),  0),
        ("RIGHTPADDING",  (2, 0), (2, -1),  0),
        ("LINEBELOW",     (0, 0), (1, -2),  0.5, GRIS_LINEA),
        ("LINEBELOW",     (3, 0), (4, -2),  0.5, GRIS_LINEA),
        ("BOX",           (0, 0), (-1, -1), 0.6, GRIS_LINEA),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))

    
    # CITAS
    
    today = now().date()
    elementos_citas = []

    if citas.exists():
        for i, cita in enumerate(citas, 1):
            es_futura = cita.fecha >= today
            color_enc  = AZUL if es_futura else MARINO
            acento     = None if es_futura else DORADO
            estado     = "Próxima" if es_futura else "Realizada"

            elementos_citas += tarjeta(
                encabezado_color=color_enc,
                titulo=f"Cita #{i}  ·  {estado}",
                filas_datos=[
                    ("¿Cuándo?",     cita.fecha),
                    ("¿A qué hora?", cita.hora),
                    ("Tu médico",    cita.doctor),
                ],
                acento_izq=acento,
            )
    else:
        elementos_citas.append(
            caja_sin_datos("No tienes citas registradas.")
        )

    
    # MENSAJE FINAL + QR
    
    col_msg = UW * 0.75
    col_qr  = UW * 0.25

    tabla_final = Table(
        [[
            [
                Paragraph("¿Tienes dudas sobre este documento?", E(
                    "MsgT", fontSize=9, fontName="Helvetica-Bold",
                    textColor=MARINO, alignment=TA_LEFT, leading=13,
                )),
                Spacer(1, 4),
                Paragraph(
                    "Puedes acercarte a tu médico o a la recepción de la clínica "
                    "para aclarar cualquier información. El código QR te permite "
                    "verificar la autenticidad de este documento.",
                    E("MsgP", fontSize=8, fontName="Helvetica",
                      textColor=GRIS_TEXTO, alignment=TA_JUSTIFY, leading=12),
                ),
            ],
            [
                qr_flowable,
                Spacer(1, 3),
                Paragraph("Verificar", st_qr_cap),
                Paragraph(folio, E("FolioQR", fontSize=6, fontName="Helvetica-Bold",
                                    textColor=MARINO, alignment=TA_CENTER, leading=8)),
            ],
        ]],
        colWidths=[col_msg, col_qr],
    )
    tabla_final.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_SUAVE),
        ("BOX",           (0, 0), (-1, -1), 0.6, AZUL),
        ("LEFTPADDING",   (0, 0), (0, 0),   14),
        ("RIGHTPADDING",  (0, 0), (0, 0),   8),
        ("LEFTPADDING",   (1, 0), (1, 0),   6),
        ("RIGHTPADDING",  (1, 0), (1, 0),   10),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (1, 0),   "CENTER"),
    ]))

    
    # AVISO LEGAL
    
    tabla_legal = Table(
        [[Paragraph(
            "Este documento ha sido generado por el Sistema Clínico exclusivamente para "
            "uso personal del paciente. La información aquí contenida es confidencial. "
            "No compartas este documento con terceros sin autorización de tu médico.",
            E("Legal", fontSize=8, fontName="Helvetica",
              textColor=GRIS_LABEL, alignment=TA_JUSTIFY, leading=12),
        )]],
        colWidths=[UW],
    )
    tabla_legal.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#f0f3f8")),
        ("BOX",           (0, 0), (-1, -1), 0.5, GRIS_LINEA),
        ("LINEBEFORE",    (0, 0), (0, -1),  3,   DORADO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    
    # PIE DE PÁGINA
    
    def pie_pagina(c, d):
        c.saveState()
        c.setFillColor(MARINO)
        c.rect(0, 0, W, 16 * mm, fill=1, stroke=0)
        c.setStrokeColor(DORADO)
        c.setLineWidth(1)
        c.line(0, 16 * mm, W, 16 * mm)
        c.setFillColor(BLANCO)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(
            W / 2, 9 * mm,
            "Sistema Clínico  ·  Tu historial de citas  ·  Confidencial"
        )
        c.setFillColor(colors.HexColor("#a0b4cc"))
        c.setFont("Helvetica", 6.5)
        c.drawCentredString(W / 2, 5 * mm, "Proyecto escolar · Guárdalo en un lugar seguro")
        c.setFillColor(DORADO_CLARO)
        c.setFont("Helvetica-Bold", 7)
        c.drawRightString(W - d.rightMargin, 9 * mm, folio)
        c.setFillColor(colors.HexColor("#a0b4cc"))
        c.setFont("Helvetica", 6.5)
        c.drawRightString(W - d.rightMargin, 5 * mm, f"Página {d.page}")
        c.restoreState()

    
    # ENSAMBLE
    
    historia = [
        tabla_header,
        franja_dorada,
        Spacer(1, 8),
        badge,
        Spacer(1, 10),
        bienvenida,
        Spacer(1, 14),

        *encabezado_seccion("Tus Datos Personales"),
        tabla_paciente,
        Spacer(1, 14),

        *encabezado_seccion("Tu Historial de Citas"),
        *elementos_citas,
        Spacer(1, 14),

        tabla_final,
        Spacer(1, 10),
        tabla_legal,
    ]

    doc.build(historia, onFirstPage=pie_pagina, onLaterPages=pie_pagina)

    pdf = buffer.getvalue()
    buffer.close()

    # 🔥 GUARDAR EN DESCARGAS Y ABRIR (para .exe)
    import os, webbrowser

    ruta = os.path.join(
     os.path.expanduser("~"),
     "Downloads",
       f"Expediente_{paciente.nombre}_{paciente.apellido}.pdf"
    )

    with open(ruta, "wb") as f:
       f.write(pdf)

    webbrowser.open(ruta)

     # 🔥 seguir devolviendo el response (para navegador normal)
    response.write(pdf)
    return response