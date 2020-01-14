#!/usr/bin/env python
# -*- coding= UTF-8 -*-
# Fad

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# setup the empty canvas
from io import FileIO as file
# from Common.pyPdf import PdfFileWriter, PdfFileReader
from PyPDF2 import PdfFileWriter, PdfFileReader
from models import InvoiceItem
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
# from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from num2words import num2words
# from configuration import Config
from Common.ui.util import formatted_number
from Common.ui.util import get_temp_filename


def pdFview(filename, invoice):
    """
        cette views est cree pour la generation du PDF
    """

    if not filename:
        filename = get_temp_filename('pdf')
        # print(filename)
    # on recupere les items de la facture
    items_invoice = InvoiceItem.filter(invoices=invoice)

    style_sheet = getSampleStyleSheet()

    style_n = ParagraphStyle(style_sheet['Normal'])
    # Static source pdf to be overlayed
    PDFSOURCE = 'fact_source.pdf'
    TMP_FILE = 'tmp.pdf'
    DATE_FORMAT = u"%d/%m/%Y"

    # FONT = 'Courier-Bold'
    # A simple function to return a leading 0 on any single digit int.
    # PDF en entrée
    input1 = PdfFileReader(file(PDFSOURCE, "rb"))

    # PDF en sortie
    output = PdfFileWriter()
    # Récupération du nombre de pages
    n_pages = input1.getNumPages()
    # Pour chaque page

    y = 620
    x = 40

    for i in range(n_pages):
        # Récupération de la page du doc initial (input1)
        page = input1.getPage(i)
        p = canvas.Canvas(TMP_FILE, pagesize=A4)
        # p.setFont(FONT, DEFAULT_FONT_SIZE)
        p.drawString(x, y, "N° : " + str(invoice.number))
        p.drawString(x + 350, y, "Date : " + str(invoice.date.strftime(DATE_FORMAT)))
        p.drawString(x, y - 15, "Doit : " + str(invoice.client))

        hdata = ['Quantité', 'Désigantion', 'P. Unitaire', 'Montant']

        ldata = []
        ldata.append(hdata)
        ht = 0
        cp = 0
        for e, r in enumerate(items_invoice):
            montant = r.price * r.quantity
            ht += montant
            nb_cart = len(r.description.name)
            cp += round(nb_cart / 80)
            ldata.append([
                formatted_number(r.quantity),
                Paragraph('{}'.format(r.description), style_n),
                formatted_number(r.price), formatted_number(montant)])
        for i in range(e, 20 - cp):
            ldata.append(["", "", ""])

        ldata.append(["", "", "Total", str(formatted_number(ht))])
        btable = Table(ldata, colWidths=[1 * inch, 3 * inch, 1.5 * inch, 1.5 * inch])
        btable.setStyle(
            TableStyle([("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                       ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                       ('ALIGN', (0, 0), (-1, -1), "RIGHT"),
                       ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                       ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                       ('FONTSIZE', (0, 0), (-1, 0), 12),
                       ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                       ('BACKGROUND', (1, 1), (1, 1), colors.black),
                       ('ALIGN', (1, 0), (1, -1), 'LEFT')])
        )
        data_len = len(ldata)
        for each in range(1, data_len):
            if each % 2 == 0:
                bg_color = colors.whitesmoke
            else:
                bg_color = colors.lightgrey
            btable.setStyle(TableStyle([('BACKGROUND', (0, each), (-1, each), bg_color)]))

        a_w = 500
        a_h = 180

        w, h = btable.wrap(a_w, a_h)
        btable.drawOn(p, 40, a_h)

        ht_en_lettre = num2words(ht, lang='fr')
        y = a_h - 15
        ht_en_lettre1, ht_en_lettre2 = controle_caratere(ht_en_lettre + " franc CFA", 55, 40)
        p.drawString(x, y - 30, "Arrêté la présente facture à la somme de : {}".format(ht_en_lettre1.title()))
        # p.drawString(x + 155, y - 30, (ht_en_lettre1.title()))
        p.drawString(x, y - 45, (ht_en_lettre2))
        y -= 80
        p.drawString(x, y, "Pour Acquit")
        p.drawString(x + 440, y, "Fournisseur")
        p.showPage()
        # Sauvegarde de la page
        p.save()
        # Création du watermark
        watermark = PdfFileReader(file(TMP_FILE, "rb"))
        # Création page_initiale+watermark
        page.mergePage(watermark.getPage(0))
        # Création de la nouvelle page
        output.addPage(page)
    # Nouveau pdf
    file_dest = filename + ".pdf"
    output_stream = file(file_dest, u"wb")
    output.write(output_stream)
    output_stream.close()

    return file_dest


def controle_caratere(lettre, nb_controle, nb_limite):
    """
        cette fonction decoupe une chaine de caratere en fonction
        du nombre de caratere donnée et conduit le reste à la ligne
    """
    lettre = lettre
    if len(lettre) <= nb_controle:
        ch = lettre
        ch2 = u""
        return ch, ch2
    else:
        ch = ch2 = u""
        for n in lettre.split(u" "):
            if len(ch) <= nb_limite:
                ch = ch + u" " + n
            else:
                ch2 = ch2 + u" " + n
        return ch, ch2
