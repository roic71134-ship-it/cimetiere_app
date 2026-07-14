"""Génération automatique de factures PDF avec ReportLab."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils import timezone
import datetime


def generer_numero_facture(reservation_id: int) -> str:
    annee = datetime.datetime.now().year
    return f"FACT-{annee}-{reservation_id:05d}"


def generer_facture(reservation):
    """Génère une facture PDF et l'envoie par email."""
    from apps.finances.models import Facture
    from apps.terrain.models import Configuration
    from django.core.mail import EmailMessage
    from django.conf import settings

    # Récupérer la configuration pour les prix
    config, _ = Configuration.objects.get_or_create(
        id=1,
        defaults={"superficie_totale": 10000, "longueur_tombeau": 2.0, "largeur_tombeau": 1.0}
    )

    if reservation.type_concession == 'perpetuelle':
        montant = config.prix_concession_perpetuelle
    else:
        montant = config.prix_concession_temporaire

    numero = generer_numero_facture(reservation.id)

    # Créer la facture en base
    facture, created = Facture.objects.get_or_create(
        reservation=reservation,
        defaults={
            "numero": numero,
            "montant_total": montant,
        }
    )
    if not created:
        return facture

    # Générer le PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    story = []

    # En-tête
    titre_style = ParagraphStyle('titre', parent=styles['Title'],
                                  fontSize=18, textColor=colors.HexColor('#1e3a5f'),
                                  spaceAfter=6)
    sous_titre_style = ParagraphStyle('sous_titre', parent=styles['Normal'],
                                       fontSize=11, textColor=colors.HexColor('#555555'))
    label_style = ParagraphStyle('label', parent=styles['Normal'],
                                  fontSize=10, textColor=colors.HexColor('#333333'))
    value_style = ParagraphStyle('value', parent=styles['Normal'],
                                  fontSize=10, fontName='Helvetica-Bold')

    story.append(Paragraph("ADMINISTRATION DU CIMETIÈRE", titre_style))
    story.append(Paragraph("Service de Gestion Funéraire", sous_titre_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1e3a5f')))
    story.append(Spacer(1, 0.5*cm))

    # Numéro et date
    info_data = [
        ["FACTURE", numero],
        ["Date d'émission", timezone.now().strftime("%d/%m/%Y")],
        ["Référence réservation", f"#{reservation.id}"],
    ]
    info_table = Table(info_data, colWidths=[8*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 14),
        ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#1e3a5f')),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.3*cm))

    # Informations client
    story.append(Paragraph("FACTURER À :", label_style))
    client = reservation.client
    story.append(Paragraph(f"{client.prenom} {client.nom}", value_style))
    story.append(Paragraph(client.email, styles['Normal']))
    if client.telephone:
        story.append(Paragraph(client.telephone, styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Informations défunt
    if reservation.defunt:
        story.append(Paragraph("DÉFUNT :", label_style))
        d = reservation.defunt
        story.append(Paragraph(f"{d.prenom} {d.nom}", value_style))
        story.append(Paragraph(f"Date de décès : {d.date_deces.strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 0.5*cm))

    # Tableau de facturation
    story.append(Paragraph("DÉTAIL DE LA FACTURATION", label_style))
    story.append(Spacer(1, 0.2*cm))

    type_label = "Concession perpétuelle" if reservation.type_concession == 'perpetuelle' else "Concession temporaire (15 ans)"
    echeance = reservation.date_echeance.strftime('%d/%m/%Y') if reservation.date_echeance else "Sans échéance"

    table_data = [
        ["Description", "Caveau", "Échéance", "Montant (FCFA)"],
        [type_label, reservation.caveau.reference, echeance, f"{montant:,.0f}"],
        ["", "", "TOTAL", f"{montant:,.0f}"],
    ]

    table = Table(table_data, colWidths=[7*cm, 3*cm, 3*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
        ('ALIGN', (2, 2), (2, 2), 'RIGHT'),
        ('FONTNAME', (2, 2), (3, 2), 'Helvetica-Bold'),
        ('BACKGROUND', (2, 2), (3, 2), colors.HexColor('#f0f4f8')),
        ('GRID', (0, 0), (-1, 1), 0.5, colors.grey),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.HexColor('#1e3a5f')),
        ('ROWBACKGROUNDS', (0, 1), (-1, 1), [colors.HexColor('#f9f9f9')]),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 1*cm))

    # Modes de paiement
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("MODES DE PAIEMENT ACCEPTÉS", label_style))
    story.append(Paragraph("Mobile Money • Airtel Money • Espèces • Virement bancaire", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Ce document fait foi de contrat entre l'Administration du Cimetière et le bénéficiaire.",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
    ))

    doc.build(story)
    buffer.seek(0)

    # Sauvegarder le PDF
    nom_fichier = f"facture_{numero}.pdf"
    facture.fichier_pdf.save(nom_fichier, ContentFile(buffer.read()), save=True)

    # Envoyer par email
    try:
        email = EmailMessage(
            subject=f"[Cimetière] Votre facture {numero}",
            body=f"""
Bonjour {client.prenom},

Veuillez trouver ci-joint votre facture {numero} d'un montant de {montant:,.0f} FCFA.

Modes de paiement : Mobile Money, Airtel Money, Espèces, Virement bancaire.

Cordialement,
Administration du Cimetière
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[client.email],
        )
        facture.fichier_pdf.open()
        email.attach(nom_fichier, facture.fichier_pdf.read(), 'application/pdf')
        email.send(fail_silently=True)
        facture.fichier_pdf.close()
    except Exception:
        pass

    return facture
