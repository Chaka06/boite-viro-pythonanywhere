from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from datetime import datetime
import os
import requests
from PIL import Image as PILImage
from io import BytesIO
from .email_utils import get_bank_info

def hex_to_color(hex_color):
    """Convertir une couleur hexadécimale en colors.Color"""
    try:
        # Essayer HexColor si disponible
        return colors.HexColor(hex_color)
    except:
        # Fallback: convertir manuellement
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return colors.Color(r, g, b)
        return colors.Color(0, 0.4, 0.8)  # Couleur par défaut bleue

def get_logo_path(banque_code):
    """Télécharger et retourner le chemin du logo de la banque depuis l'URL"""
    # Créer le dossier des logos s'il n'existe pas
    logos_dir = os.path.join(settings.MEDIA_ROOT, 'logos', 'banques')
    os.makedirs(logos_dir, exist_ok=True)
    
    logo_path = os.path.join(logos_dir, f'{banque_code}.png')
    
    # Si le logo n'existe pas, le télécharger depuis l'URL
    if not os.path.exists(logo_path):
        try:
            # Récupérer l'URL du logo depuis get_bank_info
            bank_info = get_bank_info(banque_code)
            logo_url = bank_info.get('logo_url', '')
            
            if logo_url:
                # Télécharger le logo
                response = requests.get(logo_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    # Sauvegarder l'image
                    img = PILImage.open(BytesIO(response.content))
                    # Convertir en RGB si nécessaire (pour les PNG avec transparence)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        background = PILImage.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    # Redimensionner si trop grand (max 300px de largeur)
                    if img.width > 300:
                        ratio = 300 / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((300, new_height), PILImage.Resampling.LANCZOS)
                    img.save(logo_path, 'PNG', quality=95)
                    print(f"Logo téléchargé pour {banque_code} : {logo_path}")
                else:
                    print(f"Impossible de télécharger le logo pour {banque_code}, création d'un logo générique")
                    create_generic_logo(logo_path, banque_code)
            else:
                create_generic_logo(logo_path, banque_code)
        except Exception as e:
            print(f"Erreur lors du téléchargement du logo pour {banque_code}: {e}")
            # Créer un logo générique en cas d'erreur
            if not os.path.exists(logo_path):
                create_generic_logo(logo_path, banque_code)
    
    return logo_path

def create_generic_logo(logo_path, banque_code):
    """Créer un logo générique pour une banque"""
    try:
        # Couleurs par banque
        bank_colors = {
            'bnp_paribas': (0, 150, 82),
            'credit_agricole': (0, 150, 130),
            'bnp_paribas_fortis': (0, 100, 180),
            'credit_mutuel': (0, 80, 150),
            'credit_suisse': (200, 16, 46),
            'credit_lyonnais': (0, 60, 120),
            'banque_populaire': (200, 50, 50),
            'societe_generale': (200, 0, 50),
            'intesa_sanpaolo': (0, 80, 150),
            'deutsche_bank': (0, 25, 80),
            'hsbc': (218, 41, 28),
            'barclays': (0, 120, 215),
            'citibank': (0, 120, 215),
            'ubs': (0, 0, 0),
            'ing_bank': (255, 120, 0)
        }
        
        color = bank_colors.get(banque_code, (70, 130, 180))
        
        # Créer une image 200x150 avec PIL
        img = PILImage.new('RGB', (200, 150), color)
        from PIL import ImageDraw, ImageFont
        
        draw = ImageDraw.Draw(img)
        
        # Dessiner un cercle blanc
        draw.ellipse([50, 25, 150, 125], fill='white', outline=color, width=3)
        
        # Ajouter du texte (initiales de la banque)
        try:
            # Linux (PythonAnywhere, Ubuntu/Debian)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        except:
            try:
                # macOS (développement local)
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                font = ImageFont.load_default()
        
        # Extraire les initiales
        bank_names = {
            'bnp_paribas': 'BNP',
            'credit_agricole': 'CA',
            'bnp_paribas_fortis': 'BPF',
            'credit_mutuel': 'CM',
            'credit_suisse': 'CS',
            'credit_lyonnais': 'CL',
            'banque_populaire': 'BP',
            'societe_generale': 'SG',
            'intesa_sanpaolo': 'ISP',
            'deutsche_bank': 'DB',
            'hsbc': 'HSBC',
            'barclays': 'BAR',
            'citibank': 'CITI',
            'ubs': 'UBS',
            'ing_bank': 'ING'
        }
        
        text = bank_names.get(banque_code, 'BK')
        
        # Centrer le texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (200 - text_width) // 2
        y = (150 - text_height) // 2
        
        draw.text((x, y), text, fill=color, font=font)
        
        img.save(logo_path, 'PNG', quality=95)
        print(f"Logo générique créé pour {banque_code} : {logo_path}")
        
    except Exception as e:
        print(f"Erreur lors de la création du logo générique: {e}")

def get_translations(langue):
    """Retourner les traductions complètes selon la langue"""
    translations = {
        'fr': {
            'titre_initiation': 'ORDRE DE VIREMENT INTERNATIONAL',
            'titre_rejet': 'AVIS DE REJET DE VIREMENT',
            'beneficiaire': 'BÉNÉFICIAIRE',
            'donneur_ordre': 'DONNEUR D\'ORDRE',
            'compte': 'Numéro de compte',
            'bic': 'Code BIC/SWIFT',
            'montant': 'Montant',
            'devise': 'Devise',
            'date': 'Date d\'exécution',
            'numero': 'Référence',
            'banque': 'Établissement émetteur',
            'frais': 'Frais de redirection',
            'motif': 'Motif du rejet',
            'signature': 'Service des Opérations',
            'reference': 'Référence de l\'opération',
            'statut': 'Statut',
            'details_operation': 'DÉTAILS DE L\'OPÉRATION',
            'informations_parties': 'INFORMATIONS DES PARTIES',
            'avis_important': 'AVIS IMPORTANT',
            'msg_rejet': 'Le présent virement a été rejeté pour le motif indiqué ci-dessous.',
            'email': 'Email',
            'en_lettres': 'En lettres',
            'a_transferer': 'à transférer',
            'montant_initial': 'Montant initial',
            'date_rejet': 'Date de rejet',
            'beneficiaire_concerne': 'Bénéficiaire concerné',
            'compte_beneficiaire': 'Compte bénéficiaire',
            'signature_cachet': 'Signature autorisée & Cachet',
            'rejete': 'REJETÉ',
            'dept_operations': 'DÉPARTEMENT DES OPÉRATIONS INTERNATIONALES',
            'systeme_gestion': 'Système de Gestion des Virements',
            'document_confidentiel': 'Ce document est confidentiel et destiné exclusivement au bénéficiaire mentionné.',
            'reproduction_interdite': 'Toute reproduction, distribution ou utilisation non autorisée est strictement interdite.',
            'document_genere': 'Document généré automatiquement par BOITE-VIRO le',
            'page': 'Page'
        },
        'en': {
            'titre_initiation': 'INTERNATIONAL WIRE TRANSFER ORDER',
            'titre_rejet': 'WIRE TRANSFER REJECTION NOTICE',
            'beneficiaire': 'BENEFICIARY',
            'donneur_ordre': 'ORDERING PARTY',
            'compte': 'Account number',
            'bic': 'BIC/SWIFT Code',
            'montant': 'Amount',
            'devise': 'Currency',
            'date': 'Execution date',
            'numero': 'Reference',
            'banque': 'Issuing institution',
            'frais': 'Redirection fees',
            'motif': 'Rejection reason',
            'signature': 'Operations Department',
            'reference': 'Transaction reference',
            'statut': 'Status',
            'details_operation': 'TRANSACTION DETAILS',
            'informations_parties': 'PARTY INFORMATION',
            'avis_important': 'IMPORTANT NOTICE',
            'msg_rejet': 'This wire transfer has been rejected for the reason indicated below.',
            'email': 'Email',
            'en_lettres': 'In words',
            'a_transferer': 'to transfer',
            'montant_initial': 'Initial amount',
            'date_rejet': 'Rejection date',
            'beneficiaire_concerne': 'Concerned beneficiary',
            'compte_beneficiaire': 'Beneficiary account',
            'signature_cachet': 'Authorized signature & Stamp',
            'rejete': 'REJECTED',
            'dept_operations': 'INTERNATIONAL OPERATIONS DEPARTMENT',
            'systeme_gestion': 'Wire Transfer Management System',
            'document_confidentiel': 'This document is confidential and intended exclusively for the mentioned beneficiary.',
            'reproduction_interdite': 'Any reproduction, distribution or unauthorized use is strictly prohibited.',
            'document_genere': 'Document automatically generated by BOITE-VIRO on',
            'page': 'Page'
        },
        'es': {
            'titre_initiation': 'ORDEN DE TRANSFERENCIA INTERNACIONAL',
            'titre_rejet': 'AVISO DE RECHAZO DE TRANSFERENCIA',
            'beneficiaire': 'BENEFICIARIO',
            'donneur_ordre': 'ORDENANTE',
            'compte': 'Número de cuenta',
            'bic': 'Código BIC/SWIFT',
            'montant': 'Importe',
            'devise': 'Divisa',
            'date': 'Fecha de ejecución',
            'numero': 'Referencia',
            'banque': 'Institución emisora',
            'frais': 'Gastos de redirección',
            'motif': 'Motivo del rechazo',
            'signature': 'Departamento de Operaciones',
            'reference': 'Referencia de la operación',
            'statut': 'Estado',
            'details_operation': 'DETALLES DE LA OPERACIÓN',
            'informations_parties': 'INFORMACIÓN DE LAS PARTES',
            'avis_important': 'AVISO IMPORTANTE',
            'msg_rejet': 'Esta transferencia ha sido rechazada por el motivo indicado a continuación.',
            'email': 'Email',
            'en_lettres': 'En letras',
            'a_transferer': 'a transferir',
            'montant_initial': 'Importe inicial',
            'date_rejet': 'Fecha de rechazo',
            'beneficiaire_concerne': 'Beneficiario concernido',
            'compte_beneficiaire': 'Cuenta del beneficiario',
            'signature_cachet': 'Firma autorizada y Sello',
            'rejete': 'RECHAZADO',
            'dept_operations': 'DEPARTAMENTO DE OPERACIONES INTERNACIONALES',
            'systeme_gestion': 'Sistema de Gestión de Transferencias',
            'document_confidentiel': 'Este documento es confidencial y destinado exclusivamente al beneficiario mencionado.',
            'reproduction_interdite': 'Cualquier reproducción, distribución o uso no autorizado está estrictamente prohibido.',
            'document_genere': 'Documento generado automáticamente por BOITE-VIRO el',
            'page': 'Página'
        },
        'it': {
            'titre_initiation': 'ORDINE DI BONIFICO INTERNAZIONALE',
            'titre_rejet': 'AVVISO DI RIFIUTO BONIFICO',
            'beneficiaire': 'BENEFICIARIO',
            'donneur_ordre': 'ORDINANTE',
            'compte': 'Numero di conto',
            'bic': 'Codice BIC/SWIFT',
            'montant': 'Importo',
            'devise': 'Valuta',
            'date': 'Data di esecuzione',
            'numero': 'Riferimento',
            'banque': 'Istituzione emittente',
            'frais': 'Commissioni di reindirizzamento',
            'motif': 'Motivo del rifiuto',
            'signature': 'Dipartimento Operazioni',
            'reference': 'Riferimento dell\'operazione',
            'statut': 'Stato',
            'details_operation': 'DETTAGLI DELL\'OPERAZIONE',
            'informations_parties': 'INFORMAZIONI DELLE PARTI',
            'avis_important': 'AVVISO IMPORTANTE',
            'msg_rejet': 'Questo bonifico è stato rifiutato per il motivo indicato di seguito.',
            'email': 'Email',
            'en_lettres': 'A lettere',
            'a_transferer': 'da trasferire',
            'montant_initial': 'Importo iniziale',
            'date_rejet': 'Data di rifiuto',
            'beneficiaire_concerne': 'Beneficiario interessato',
            'compte_beneficiaire': 'Conto del beneficiario',
            'signature_cachet': 'Firma autorizzata e Timbro',
            'rejete': 'RIFIUTATO',
            'dept_operations': 'DIPARTIMENTO OPERAZIONI INTERNAZIONALI',
            'systeme_gestion': 'Sistema di Gestione Bonifici',
            'document_confidentiel': 'Questo documento è confidenziale e destinato esclusivamente al beneficiario menzionato.',
            'reproduction_interdite': 'Qualsiasi riproduzione, distribuzione o uso non autorizzato è severamente vietato.',
            'document_genere': 'Documento generato automaticamente da BOITE-VIRO il',
            'page': 'Pagina'
        },
        'de': {
            'titre_initiation': 'INTERNATIONALE ÜBERWEISUNGSANWEISUNG',
            'titre_rejet': 'ÜBERWEISUNGS-ABLEHNUNGSBENACHRICHTIGUNG',
            'beneficiaire': 'BEGÜNSTIGTER',
            'donneur_ordre': 'AUFTRAGGEBER',
            'compte': 'Kontonummer',
            'bic': 'BIC/SWIFT-Code',
            'montant': 'Betrag',
            'devise': 'Währung',
            'date': 'Ausführungsdatum',
            'numero': 'Referenz',
            'banque': 'Ausstellende Institution',
            'frais': 'Umleitungsgebühren',
            'motif': 'Ablehnungsgrund',
            'signature': 'Abteilung Operationen',
            'reference': 'Transaktionsreferenz',
            'statut': 'Status',
            'details_operation': 'TRANSAKTIONSDETAILS',
            'informations_parties': 'PARTEIENINFORMATIONEN',
            'avis_important': 'WICHTIGER HINWEIS',
            'msg_rejet': 'Diese Überweisung wurde aus dem unten angegebenen Grund abgelehnt.',
            'email': 'Email',
            'en_lettres': 'In Worten',
            'a_transferer': 'zu überweisen',
            'montant_initial': 'Ursprünglicher Betrag',
            'date_rejet': 'Ablehnungsdatum',
            'beneficiaire_concerne': 'Betroffener Begünstigter',
            'compte_beneficiaire': 'Begünstigtenkonto',
            'signature_cachet': 'Autorisierte Unterschrift & Stempel',
            'rejete': 'ABGELEHNT',
            'dept_operations': 'ABTEILUNG INTERNATIONALE OPERATIONEN',
            'systeme_gestion': 'Überweisungs-Managementsystem',
            'document_confidentiel': 'Dieses Dokument ist vertraulich und ausschließlich für den genannten Begünstigten bestimmt.',
            'reproduction_interdite': 'Jede Reproduktion, Verteilung oder unbefugte Verwendung ist strengstens untersagt.',
            'document_genere': 'Dokument automatisch generiert von BOITE-VIRO am',
            'page': 'Seite'
        },
        'pl': {
            'titre_initiation': 'MIĘDZYNARODOWE ZLECENIE PRZELEWU',
            'titre_rejet': 'POWIADOMIENIE O ODRZUCENIU PRZELEWU',
            'beneficiaire': 'BENEFICJENT',
            'donneur_ordre': 'ZLECENIODAWCA',
            'compte': 'Numer konta',
            'bic': 'Kod BIC/SWIFT',
            'montant': 'Kwota',
            'devise': 'Waluta',
            'date': 'Data wykonania',
            'numero': 'Referencja',
            'banque': 'Instytucja wydająca',
            'frais': 'Opłaty przekierowania',
            'motif': 'Powód odrzucenia',
            'signature': 'Dział Operacji',
            'reference': 'Referencja transakcji',
            'statut': 'Status',
            'details_operation': 'SZCZEGÓŁY TRANSAKCJI',
            'informations_parties': 'INFORMACJE O STRONACH',
            'avis_important': 'WAŻNA UWAGA',
            'msg_rejet': 'Ten przelew został odrzucony z powodu wskazanego poniżej.',
            'email': 'Email',
            'en_lettres': 'Słownie',
            'a_transferer': 'do przelewu',
            'montant_initial': 'Kwota początkowa',
            'date_rejet': 'Data odrzucenia',
            'beneficiaire_concerne': 'Dotyczy beneficjenta',
            'compte_beneficiaire': 'Konto beneficjenta',
            'signature_cachet': 'Podpis upoważniony i Pieczęć',
            'rejete': 'ODRZUCONY',
            'dept_operations': 'DZIAŁ OPERACJI MIĘDZYNARODOWYCH',
            'systeme_gestion': 'System Zarządzania Przelewami',
            'document_confidentiel': 'Ten dokument jest poufny i przeznaczony wyłącznie dla wymienionego beneficjenta.',
            'reproduction_interdite': 'Jakiekolwiek powielanie, dystrybucja lub nieautoryzowane użycie jest surowo zabronione.',
            'document_genere': 'Dokument automatycznie wygenerowany przez BOITE-VIRO dnia',
            'page': 'Strona'
        },
        'ru': {
            'titre_initiation': 'МЕЖДУНАРОДНОЕ РАСПОРЯЖЕНИЕ О ПЕРЕВОДЕ',
            'titre_rejet': 'УВЕДОМЛЕНИЕ ОБ ОТКЛОНЕНИИ ПЕРЕВОДА',
            'beneficiaire': 'БЕНЕФИЦИАР',
            'donneur_ordre': 'ПЛАТЕЛЬЩИК',
            'compte': 'Номер счета',
            'bic': 'БИК/SWIFT код',
            'montant': 'Сумма',
            'devise': 'Валюта',
            'date': 'Дата исполнения',
            'numero': 'Справка',
            'banque': 'Банк-эмитент',
            'frais': 'Комиссия за перенаправление',
            'motif': 'Причина отклонения',
            'signature': 'Отдел операций',
            'reference': 'Ссылка на транзакцию',
            'statut': 'Статус',
            'details_operation': 'ДЕТАЛИ ОПЕРАЦИИ',
            'informations_parties': 'ИНФОРМАЦИЯ О СТОРОНАХ',
            'avis_important': 'ВАЖНОЕ УВЕДОМЛЕНИЕ',
            'msg_rejet': 'Этот перевод был отклонен по причине, указанной ниже.',
            'email': 'Email',
            'en_lettres': 'Прописью',
            'a_transferer': 'к переводу',
            'montant_initial': 'Первоначальная сумма',
            'date_rejet': 'Дата отклонения',
            'beneficiaire_concerne': 'Касается бенефициара',
            'compte_beneficiaire': 'Счет бенефициара',
            'signature_cachet': 'Авторизованная подпись и Печать',
            'rejete': 'ОТКЛОНЕНО',
            'dept_operations': 'ОТДЕЛ МЕЖДУНАРОДНЫХ ОПЕРАЦИЙ',
            'systeme_gestion': 'Система Управления Переводами',
            'document_confidentiel': 'Этот документ является конфиденциальным и предназначен исключительно для указанного бенефициара.',
            'reproduction_interdite': 'Любое воспроизведение, распространение или несанкционированное использование строго запрещено.',
            'document_genere': 'Документ автоматически сгенерирован BOITE-VIRO',
            'page': 'Страница'
        },
        'pt': {
            'titre_initiation': 'ORDEM DE TRANSFERÊNCIA INTERNACIONAL',
            'titre_rejet': 'AVISO DE REJEIÇÃO DE TRANSFERÊNCIA',
            'beneficiaire': 'BENEFICIÁRIO',
            'donneur_ordre': 'ORDENANTE',
            'compte': 'Número da conta',
            'bic': 'Código BIC/SWIFT',
            'montant': 'Valor',
            'devise': 'Moeda',
            'date': 'Data de execução',
            'numero': 'Referência',
            'banque': 'Instituição emissora',
            'frais': 'Taxas de redirecionamento',
            'motif': 'Motivo da rejeição',
            'signature': 'Departamento de Operações',
            'reference': 'Referência da transação',
            'statut': 'Status',
            'details_operation': 'DETALHES DA OPERAÇÃO',
            'informations_parties': 'INFORMAÇÕES DAS PARTES',
            'avis_important': 'AVISO IMPORTANTE',
            'msg_rejet': 'Esta transferência foi rejeitada pelo motivo indicado abaixo.',
            'email': 'Email',
            'en_lettres': 'Por extenso',
            'a_transferer': 'a transferir',
            'montant_initial': 'Valor inicial',
            'date_rejet': 'Data de rejeição',
            'beneficiaire_concerne': 'Beneficiário em questão',
            'compte_beneficiaire': 'Conta do beneficiário',
            'signature_cachet': 'Assinatura autorizada e Carimbo',
            'rejete': 'REJEITADO',
            'dept_operations': 'DEPARTAMENTO DE OPERAÇÕES INTERNACIONAIS',
            'systeme_gestion': 'Sistema de Gestão de Transferências',
            'document_confidentiel': 'Este documento é confidencial e destinado exclusivamente ao beneficiário mencionado.',
            'reproduction_interdite': 'Qualquer reprodução, distribuição ou uso não autorizado é estritamente proibido.',
            'document_genere': 'Documento gerado automaticamente por BOITE-VIRO em',
            'page': 'Página'
        },
        'ar': {
            'titre_initiation': 'أمر التحويل الدولي',
            'titre_rejet': 'إشعار رفض التحويل',
            'beneficiaire': 'المستفيد',
            'donneur_ordre': 'آمر الدفع',
            'compte': 'رقم الحساب',
            'bic': 'رمز BIC/SWIFT',
            'montant': 'المبلغ',
            'devise': 'العملة',
            'date': 'تاريخ التنفيذ',
            'numero': 'المرجع',
            'banque': 'المؤسسة المصدرة',
            'frais': 'رسوم إعادة التوجيه',
            'motif': 'سبب الرفض',
            'signature': 'قسم العمليات',
            'reference': 'مرجع المعاملة',
            'statut': 'الحالة',
            'details_operation': 'تفاصيل العملية',
            'informations_parties': 'معلومات الأطراف',
            'avis_important': 'إشعار مهم',
            'msg_rejet': 'تم رفض هذا التحويل للسبب المذكور أدناه.',
            'email': 'البريد الإلكتروني',
            'en_lettres': 'بالأحرف',
            'a_transferer': 'للتحويل',
            'montant_initial': 'المبلغ الأولي',
            'date_rejet': 'تاريخ الرفض',
            'beneficiaire_concerne': 'المستفيد المعني',
            'compte_beneficiaire': 'حساب المستفيد',
            'signature_cachet': 'التوقيع المصرح به والختم',
            'rejete': 'مرفوض',
            'dept_operations': 'قسم العمليات الدولية',
            'systeme_gestion': 'نظام إدارة التحويلات',
            'document_confidentiel': 'هذا المستند سري ومخصص حصرياً للمستفيد المذكور.',
            'reproduction_interdite': 'أي نسخ أو توزيع أو استخدام غير مصرح به محظور تماماً.',
            'document_genere': 'تم إنشاء هذا المستند تلقائياً بواسطة BOITE-VIRO في',
            'page': 'صفحة'
        },
        'zh': {
            'titre_initiation': '国际转账指令',
            'titre_rejet': '转账拒绝通知',
            'beneficiaire': '收款人',
            'donneur_ordre': '付款人',
            'compte': '账户号码',
            'bic': 'BIC/SWIFT代码',
            'montant': '金额',
            'devise': '货币',
            'date': '执行日期',
            'numero': '参考号',
            'banque': '发卡机构',
            'frais': '重定向费用',
            'motif': '拒绝原因',
            'signature': '运营部门',
            'reference': '交易参考',
            'statut': '状态',
            'details_operation': '交易详情',
            'informations_parties': '各方信息',
            'avis_important': '重要通知',
            'msg_rejet': '此转账因以下原因被拒绝。',
            'email': '电子邮件',
            'en_lettres': '大写金额',
            'a_transferer': '待转账',
            'montant_initial': '初始金额',
            'date_rejet': '拒绝日期',
            'beneficiaire_concerne': '相关收款人',
            'compte_beneficiaire': '收款人账户',
            'signature_cachet': '授权签名和印章',
            'rejete': '已拒绝',
            'dept_operations': '国际运营部',
            'systeme_gestion': '转账管理系统',
            'document_confidentiel': '本文档为机密文件，仅供指定收款人使用。',
            'reproduction_interdite': '严禁任何未经授权的复制、分发或使用。',
            'document_genere': '本文档由BOITE-VIRO系统自动生成于',
            'page': '页'
        }
    }
    
    return translations.get(langue, translations['fr'])

def number_to_words(number, langue='fr'):
    """Convertir un nombre en lettres selon la langue"""
    try:
        # Import conditionnel de num2words
        from num2words import num2words
        
        lang_map = {
            'fr': 'fr',
            'en': 'en',
            'es': 'es', 
            'it': 'it',
            'de': 'de',
            'pl': 'pl',
            'ru': 'ru',
            'pt': 'pt',
            'ar': 'ar',
            'zh': 'zh'
        }
        
        lang_code = lang_map.get(langue, 'fr')
        return num2words(number, lang=lang_code).upper()
        
    except ImportError:
        # Fallback simple en français si num2words n'est pas installé
        if number == 0:
            return "ZÉRO"
        elif number < 20:
            units = ["", "UN", "DEUX", "TROIS", "QUATRE", "CINQ", "SIX", "SEPT", "HUIT", "NEUF",
                    "DIX", "ONZE", "DOUZE", "TREIZE", "QUATORZE", "QUINZE", "SEIZE", 
                    "DIX-SEPT", "DIX-HUIT", "DIX-NEUF"]
            return units[int(number)]
        else:
            return f"({number:,.2f})"
    except:
        return f"({number:,.2f})"

# Enregistrer les polices Unicode au démarrage
def register_unicode_fonts():
    """Enregistrer les polices Unicode pour supporter toutes les langues"""
    try:
        # Essayer de charger DejaVu Sans (support Unicode complet)
        font_paths = [
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
            '/Library/Fonts/Arial Unicode.ttf',
            'C:/Windows/Fonts/arial.ttf',  # Windows
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
                    pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_path.replace('Sans.ttf', 'Sans-Bold.ttf').replace('Arial Unicode.ttf', 'Arial Unicode.ttf')))
                    print(f"Police Unicode chargée: {font_path}")
                    return True
                except:
                    continue
        
        # Si aucune police Unicode trouvée, utiliser Helvetica (limité)
        print("Aucune police Unicode trouvée, utilisation de Helvetica (limité)")
        return False
    except Exception as e:
        print(f"Erreur lors du chargement des polices Unicode: {e}")
        return False

# Enregistrer les polices au chargement du module
_UNICODE_FONTS_LOADED = register_unicode_fonts()
_UNICODE_FONT_NAME = 'DejaVu' if _UNICODE_FONTS_LOADED else 'Helvetica'

class BankDocumentCanvas(canvas.Canvas):
    """Canvas personnalisé pour les documents bancaires"""
    
    def __init__(self, *args, **kwargs):
        self.logo_path = kwargs.pop('logo_path', None)
        self.banque_name = kwargs.pop('banque_name', '')
        self.bank_info = kwargs.pop('bank_info', {})
        self.langue = kwargs.pop('langue', 'fr')
        super().__init__(*args, **kwargs)
    
    def draw_watermark(self):
        """Ajouter un filigrane discret"""
        self.saveState()
        self.setFillColor(colors.lightgrey, alpha=0.05)
        self.setFont(f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else "Helvetica-Bold", 80)
        self.rotate(45)
        self.drawCentredText(300, -200, "CONFIDENTIEL")
        self.restoreState()
    
    def draw_header(self):
        """Dessiner l'en-tête professionnel de la banque"""
        t = get_translations(self.langue)
        
        # Couleur de la banque depuis bank_info
        bank_color = hex_to_color(self.bank_info.get('primary_color', '#0066CC'))
        
        # Bandeau supérieur avec couleur de la banque
        self.setFillColor(bank_color)
        self.rect(0, A4[1] - 50, A4[0], 50, fill=1, stroke=0)
        
        # Logo de la banque (sur fond blanc dans le bandeau)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                # Logo blanc sur fond coloré
                self.drawImage(self.logo_path, 40, A4[1] - 45, width=100, height=40, mask='auto', preserveAspectRatio=True)
            except Exception as e:
                print(f"Erreur lors du chargement du logo: {e}")
        
        # Nom de la banque (blanc sur fond coloré)
        self.setFillColor(colors.white)
        font_name = f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else "Helvetica-Bold"
        self.setFont(font_name, 18)
        self.drawString(160, A4[1] - 35, self.banque_name.upper())
        
        # Sous-titre traduit (blanc sur fond coloré)
        self.setFont(_UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else "Helvetica", 9)
        self.setFillColor(colors.Color(0.95, 0.95, 0.95))
        self.drawString(160, A4[1] - 50, t['dept_operations'])
        
        # Date et référence à droite
        self.setFont(_UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else "Helvetica", 8)
        self.drawRightString(A4[0] - 40, A4[1] - 35, datetime.now().strftime('%d/%m/%Y'))
        self.drawRightString(A4[0] - 40, A4[1] - 50, t['systeme_gestion'])
    
    def draw_footer(self):
        """Dessiner le pied de page professionnel"""
        t = get_translations(self.langue)
        
        # Ligne de séparation
        self.setStrokeColor(colors.Color(0.8, 0.8, 0.8))
        self.setLineWidth(1)
        self.line(30, 80, A4[0] - 30, 80)
        
        # Informations de confidentialité traduites
        self.setFillColor(colors.Color(0.4, 0.4, 0.4))
        font_name = _UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else "Helvetica"
        self.setFont(font_name, 7)
        confidentiality_text = [
            t['document_confidentiel'],
            t['reproduction_interdite'],
        ]
        
        y_pos = 65
        for line in confidentiality_text:
            self.drawCentredText(A4[0] / 2, y_pos, line)
            y_pos -= 9
        
        # Numéro de page traduit
        self.setFont(f"{font_name}-Bold" if _UNICODE_FONTS_LOADED else "Helvetica-Bold", 8)
        bank_color = hex_to_color(self.bank_info.get('primary_color', '#0066CC'))
        self.setFillColor(bank_color)
        self.drawRightString(A4[0] - 40, 25, f"{t['page']} {self._pageNumber}")

def draw_first_page(canvas, doc):
    """Dessiner la première page"""
    if hasattr(canvas, 'draw_watermark'):
        canvas.draw_watermark()
        canvas.draw_header()
        canvas.draw_footer()

def draw_later_pages(canvas, doc):
    """Dessiner les pages suivantes"""
    if hasattr(canvas, 'draw_watermark'):
        canvas.draw_watermark()
        canvas.draw_header()
        canvas.draw_footer()

def generer_pdf_initiation(virement):
    """Générer le PDF professionnel d'initiation de virement"""
    # Créer le dossier s'il n'existe pas
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'initiations')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Nom du fichier
    filename = f'ordre_virement_{str(virement.id)[:8]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    filepath = os.path.join(pdf_dir, filename)
    
    # Récupérer les informations de la banque
    bank_info = get_bank_info(virement.banque_emettrice)
    logo_path = get_logo_path(virement.banque_emettrice)
    banque_name = bank_info['name']
    
    # Créer le document PDF avec canvas personnalisé
    def make_canvas(*args, **kwargs):
        return BankDocumentCanvas(*args, **kwargs, logo_path=logo_path, banque_name=banque_name, bank_info=bank_info, langue=virement.langue)
    
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=A4,
        topMargin=120,
        bottomMargin=100,
        leftMargin=40,
        rightMargin=40,
        canvasmaker=make_canvas
    )
    
    # Styles professionnels avec polices Unicode
    styles = getSampleStyleSheet()
    bank_color = hex_to_color(bank_info.get('primary_color', '#0066CC'))
    
    # Style de titre professionnel
    title_style = ParagraphStyle(
        'BankTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=bank_color,
        spaceAfter=30,
        spaceBefore=15,
        alignment=TA_CENTER,
        fontName=f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold',
        borderWidth=3,
        borderColor=bank_color,
        borderPadding=20,
        backColor=colors.Color(0.98, 0.99, 1.0),
        leading=24
    )
    
    # Style de section
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=bank_color,
        spaceAfter=18,
        spaceBefore=25,
        alignment=TA_LEFT,
        fontName=f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold',
        backColor=colors.Color(0.97, 0.98, 1.0),
        borderWidth=2,
        borderColor=bank_color,
        leftIndent=12,
        borderPadding=10,
        leading=16
    )
    
    # Style normal avec Unicode
    normal_style = ParagraphStyle(
        'BankNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.Color(0.1, 0.1, 0.1),
        spaceAfter=8,
        fontName=_UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else 'Helvetica',
        leading=15
    )
    
    story = []
    
    # Récupérer les traductions
    t = get_translations(virement.langue)
    
    # Titre principal
    story.append(Paragraph(t['titre_initiation'], title_style))
    story.append(Spacer(1, 20))
    
    # Numéro de référence en évidence
    ref_data = [
        ['', ''],
        [Paragraph(f"<b>{t['reference']} :</b>", normal_style), 
         Paragraph(f"<b>{str(virement.id)[:8].upper()}</b>", normal_style)],
        [Paragraph(f"<b>{t['date']} :</b>", normal_style), 
         Paragraph(f"<b>{virement.date_creation.strftime('%d/%m/%Y - %H:%M')}</b>", normal_style)],
        [Paragraph(f"<b>{t['banque']} :</b>", normal_style), 
         Paragraph(f"<b>{banque_name}</b>", normal_style)],
        ['', '']
    ]
    
    ref_table = Table(ref_data, colWidths=[6*cm, 10*cm])
    ref_font = f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold'
    ref_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 1), (-1, 3), colors.Color(0.97, 0.99, 1.0)),
        ('GRID', (0, 1), (-1, 3), 1.5, bank_color),
        ('LINEBELOW', (0, 0), (-1, 0), 0, colors.white),
        ('LINEABOVE', (0, -1), (-1, -1), 0, colors.white),
        ('FONTNAME', (0, 1), (-1, 3), ref_font),
        ('FONTSIZE', (0, 1), (-1, 3), 12),
        ('ALIGN', (0, 1), (-1, 3), 'LEFT'),
        ('VALIGN', (0, 1), (-1, 3), 'MIDDLE'),
        ('LEFTPADDING', (0, 1), (-1, 3), 18),
        ('RIGHTPADDING', (0, 1), (-1, 3), 18),
        ('TOPPADDING', (0, 1), (-1, 3), 12),
        ('BOTTOMPADDING', (0, 1), (-1, 3), 12),
        ('TEXTCOLOR', (0, 1), (0, 3), bank_color),
    ]))
    
    story.append(ref_table)
    story.append(Spacer(1, 25))
    
    # Section informations des parties
    story.append(Paragraph(t['informations_parties'], section_style))
    
    # Tableau des parties
    parties_data = [
        [Paragraph(f"<b>{t['beneficiaire']}</b>", normal_style), 
         Paragraph(f"<b>{t['donneur_ordre']}</b>", normal_style)],
        [Paragraph(f"{virement.beneficiaire_nom_complet}", normal_style),
         Paragraph(f"{virement.donneur_ordre_nom_complet}", normal_style)],
        [Paragraph(f"<i>{t['compte']} :</i><br/>{virement.beneficiaire_compte}", normal_style),
         Paragraph(f"<i>{t['compte']} :</i><br/>{virement.donneur_ordre_compte}", normal_style)],
        [Paragraph(f"<i>{t['bic']} :</i><br/>{virement.numero_bic}", normal_style),
         Paragraph(f"<i>{t['email']} :</i><br/>{virement.beneficiaire_email}", normal_style)]
    ]
    
    parties_table = Table(parties_data, colWidths=[8*cm, 8*cm])
    parties_font = f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold'
    parties_font_normal = _UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else 'Helvetica'
    parties_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), bank_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), parties_font),
        ('FONTSIZE', (0, 0), (-1, 0), 13),
        ('BACKGROUND', (0, 1), (-1, -1), colors.Color(0.99, 0.99, 1.0)),
        ('GRID', (0, 0), (-1, -1), 1.5, bank_color),
        ('FONTNAME', (0, 1), (-1, -1), parties_font_normal),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.98, 0.99, 1.0)]),
    ]))
    
    story.append(parties_table)
    story.append(Spacer(1, 25))
    
    # Section détails de l'opération
    story.append(Paragraph(t['details_operation'], section_style))
    
    # Montant en évidence
    montant_data = [
        [Paragraph(f"<b>{t['montant']} {t['a_transferer']}</b>", normal_style), 
         Paragraph(f"<font size=16><b>{virement.montant:,.2f} {virement.devise}</b></font>", normal_style)],
        [Paragraph(f"<i>{t['en_lettres']} :</i>", normal_style),
         Paragraph(f"<i>{number_to_words(float(virement.montant), virement.langue)} {dict(virement.DEVISES_CHOICES)[virement.devise]}</i>", normal_style)]
    ]
    
    montant_table = Table(montant_data, colWidths=[6*cm, 10*cm])
    montant_font = f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold'
    montant_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.95, 1.0, 0.95)),
        ('GRID', (0, 0), (-1, -1), 2.5, colors.Color(0.0, 0.7, 0.0)),
        ('FONTNAME', (0, 0), (0, -1), montant_font),
        ('FONTNAME', (1, 0), (1, 0), montant_font),
        ('FONTSIZE', (1, 0), (1, 0), 18),
        ('TEXTCOLOR', (1, 0), (1, 0), colors.Color(0.0, 0.5, 0.0)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ('RIGHTPADDING', (0, 0), (-1, -1), 18),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    story.append(montant_table)
    story.append(Spacer(1, 30))
    
    # Construire le PDF
    doc.build(story, onFirstPage=draw_first_page, onLaterPages=draw_later_pages)
    
    return f'pdfs/initiations/{filename}'

def generer_pdf_rejet(rejet):
    """Générer le PDF professionnel de rejet de virement"""
    virement = rejet.virement
    
    # Créer le dossier s'il n'existe pas
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'rejets')
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Nom du fichier
    filename = f'avis_rejet_{str(virement.id)[:8]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    filepath = os.path.join(pdf_dir, filename)
    
    # Récupérer les informations de la banque
    bank_info = get_bank_info(virement.banque_emettrice)
    logo_path = get_logo_path(virement.banque_emettrice)
    banque_name = bank_info['name']
    
    # Créer le document PDF avec canvas personnalisé
    def make_canvas(*args, **kwargs):
        return BankDocumentCanvas(*args, **kwargs, logo_path=logo_path, banque_name=banque_name, bank_info=bank_info, langue=virement.langue)
    
    doc = SimpleDocTemplate(
        filepath, 
        pagesize=A4,
        topMargin=120,
        bottomMargin=100,
        leftMargin=40,
        rightMargin=40,
        canvasmaker=make_canvas
    )
    
    # Styles (couleurs différentes pour le rejet)
    styles = getSampleStyleSheet()
    reject_color = colors.Color(0.8, 0.2, 0.2)
    
    title_style = ParagraphStyle(
        'RejectTitle',
        parent=styles['Title'],
        fontSize=20,
        textColor=reject_color,
        spaceAfter=30,
        spaceBefore=15,
        alignment=TA_CENTER,
        fontName=f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold',
        borderWidth=3,
        borderColor=reject_color,
        borderPadding=20,
        backColor=colors.Color(1.0, 0.97, 0.97),
        leading=24
    )
    
    section_style = ParagraphStyle(
        'RejectSection',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=reject_color,
        spaceAfter=18,
        spaceBefore=25,
        alignment=TA_LEFT,
        fontName=f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold',
        backColor=colors.Color(1.0, 0.99, 0.99),
        borderWidth=2,
        borderColor=reject_color,
        leftIndent=12,
        borderPadding=10,
        leading=16
    )
    
    normal_style = ParagraphStyle(
        'BankNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.Color(0.1, 0.1, 0.1),
        spaceAfter=8,
        fontName=_UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else 'Helvetica',
        leading=15
    )
    
    story = []
    
    # Récupérer les traductions
    t = get_translations(virement.langue)
    
    # Titre principal
    story.append(Paragraph(t['titre_rejet'], title_style))
    story.append(Spacer(1, 20))
    
    # Informations de base
    ref_data = [
        ['', ''],
        [Paragraph(f"<b>{t['reference']} :</b>", normal_style), 
         Paragraph(f"<b>{str(virement.id)[:8].upper()}</b>", normal_style)],
        [Paragraph(f"<b>{t['date_rejet']} :</b>", normal_style), 
         Paragraph(f"<b>{rejet.date_rejet.strftime('%d/%m/%Y - %H:%M')}</b>", normal_style)],
        [Paragraph(f"<b>{t['statut']} :</b>", normal_style), 
         Paragraph(f"<b><font color='red'>{t['rejete']}</font></b>", normal_style)],
        ['', '']
    ]
    
    ref_table = Table(ref_data, colWidths=[6*cm, 10*cm])
    ref_font = f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold'
    ref_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 1), (-1, 3), colors.Color(1.0, 0.97, 0.97)),
        ('GRID', (0, 1), (-1, 3), 1.5, reject_color),
        ('FONTNAME', (0, 1), (-1, 3), ref_font),
        ('FONTSIZE', (0, 1), (-1, 3), 12),
        ('ALIGN', (0, 1), (-1, 3), 'LEFT'),
        ('VALIGN', (0, 1), (-1, 3), 'MIDDLE'),
        ('LEFTPADDING', (0, 1), (-1, 3), 18),
        ('RIGHTPADDING', (0, 1), (-1, 3), 18),
        ('TOPPADDING', (0, 1), (-1, 3), 12),
        ('BOTTOMPADDING', (0, 1), (-1, 3), 12),
        ('TEXTCOLOR', (0, 1), (0, 3), reject_color),
    ]))
    
    story.append(ref_table)
    story.append(Spacer(1, 20))
    
    # Message d'avis important
    story.append(Paragraph(t['avis_important'], section_style))
    story.append(Paragraph(t['msg_rejet'], normal_style))
    story.append(Spacer(1, 20))
    
    # Détails du rejet
    rejet_data = [
        [Paragraph(f"<b>{t['montant_initial']} :</b>", normal_style), 
         Paragraph(f"{virement.montant:,.2f} {virement.devise}", normal_style)],
        [Paragraph(f"<b>{t['frais']} :</b>", normal_style),
         Paragraph(f"<font color='red'><b>{rejet.frais_redirection:,.2f} {virement.devise}</b></font>", normal_style)],
        [Paragraph(f"<b>{t['motif']} :</b>", normal_style),
         Paragraph(f"{rejet.motif_rejet}", normal_style)]
    ]
    
    rejet_table = Table(rejet_data, colWidths=[6*cm, 10*cm])
    rejet_font = f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold'
    rejet_font_normal = _UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else 'Helvetica'
    rejet_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(1.0, 0.99, 0.98)),
        ('GRID', (0, 0), (-1, -1), 1.5, reject_color),
        ('FONTNAME', (0, 0), (0, -1), rejet_font),
        ('FONTNAME', (1, 0), (-1, -1), rejet_font_normal),
        ('FONTSIZE', (0, 0), (0, -1), 12),
        ('FONTSIZE', (1, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), reject_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 18),
        ('RIGHTPADDING', (0, 0), (-1, -1), 18),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(rejet_table)
    story.append(Spacer(1, 30))
    
    # Informations des parties (version condensée pour le rejet)
    parties_data = [
        [Paragraph(f"<b>{t['beneficiaire_concerne']} :</b>", normal_style), 
         Paragraph(f"{virement.beneficiaire_nom_complet}", normal_style)],
        [Paragraph(f"<b>{t['compte_beneficiaire']} :</b>", normal_style),
         Paragraph(f"{virement.beneficiaire_compte}", normal_style)],
        [Paragraph(f"<b>{t['donneur_ordre']} :</b>", normal_style),
         Paragraph(f"{virement.donneur_ordre_nom_complet}", normal_style)]
    ]
    
    parties_table = Table(parties_data, colWidths=[6*cm, 10*cm])
    parties_font = f"{_UNICODE_FONT_NAME}-Bold" if _UNICODE_FONTS_LOADED else 'Helvetica-Bold'
    parties_font_normal = _UNICODE_FONT_NAME if _UNICODE_FONTS_LOADED else 'Helvetica'
    parties_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.99, 0.99, 0.99)),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.Color(0.9, 0.9, 0.9)),
        ('FONTNAME', (0, 0), (0, -1), parties_font),
        ('FONTNAME', (1, 0), (-1, -1), parties_font_normal),
        ('FONTSIZE', (0, 0), (0, -1), 12),
        ('FONTSIZE', (1, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), reject_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    
    story.append(parties_table)
    story.append(Spacer(1, 30))
    
    # Construire le PDF
    doc.build(story, onFirstPage=draw_first_page, onLaterPages=draw_later_pages)
    
    return f'pdfs/rejets/{filename}'