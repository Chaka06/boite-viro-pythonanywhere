from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from datetime import datetime
import os
from .email_utils import get_bank_info

# ── Palette strictement noir / blanc / gris ──────────────────────────
C_BLACK  = colors.Color(0.08, 0.08, 0.08)   # texte principal
C_DARK   = colors.Color(0.20, 0.20, 0.20)   # en-têtes de section
C_MED    = colors.Color(0.45, 0.45, 0.45)   # labels, pieds de page
C_BORDER = colors.Color(0.70, 0.70, 0.70)   # bordures de tableaux
C_LIGHT  = colors.Color(0.94, 0.94, 0.94)   # fond alternance lignes
C_WHITE  = colors.white

PAGE_W, PAGE_H = A4        # 595 × 842 pt
ML = 45                    # marge gauche
MR = 45                    # marge droite
CW = PAGE_W - ML - MR      # largeur utile ≈ 505 pt


# ─────────────────────────────────────────────────────────────────────
# Traductions
# ─────────────────────────────────────────────────────────────────────
def get_translations(langue):
    translations = {
        'fr': {
            'titre_initiation': 'ORDRE DE VIREMENT INTERNATIONAL',
            'titre_rejet': 'AVIS DE REJET DE VIREMENT',
            'beneficiaire': 'BÉNÉFICIAIRE',
            'donneur_ordre': "DONNEUR D'ORDRE",
            'compte': 'Numéro de compte',
            'bic': 'Code BIC/SWIFT',
            'montant': 'Montant',
            'devise': 'Devise',
            'date': "Date d'exécution",
            'numero': 'Référence',
            'banque': 'Établissement émetteur',
            'frais': 'Frais de redirection',
            'motif': 'Motif du rejet',
            'signature': 'Service des Opérations',
            'reference': "Référence de l'opération",
            'statut': 'Statut',
            'details_operation': "DÉTAILS DE L'OPÉRATION",
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
            'reproduction_interdite': 'Toute reproduction ou distribution non autorisée est strictement interdite.',
            'document_genere': 'Document généré automatiquement le',
            'page': 'Page',
            'statut_traitement': 'EN TRAITEMENT',
            'donneur_ordre_label': 'Le donneur d\'ordre',
            'visa_banque': 'Visa de la banque émettrice',
            'montant_virement': 'MONTANT DU VIREMENT',
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
            'reproduction_interdite': 'Any reproduction or unauthorized use is strictly prohibited.',
            'document_genere': 'Document automatically generated on',
            'page': 'Page',
            'statut_traitement': 'PROCESSING',
            'donneur_ordre_label': 'The ordering party',
            'visa_banque': 'Bank visa',
            'montant_virement': 'TRANSFER AMOUNT',
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
            'reproduction_interdite': 'Cualquier reproducción o uso no autorizado está estrictamente prohibido.',
            'document_genere': 'Documento generado automáticamente el',
            'page': 'Página',
            'statut_traitement': 'EN PROCESO',
            'donneur_ordre_label': 'El ordenante',
            'visa_banque': 'Visado del banco',
            'montant_virement': 'IMPORTE DE LA TRANSFERENCIA',
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
            'reference': "Riferimento dell'operazione",
            'statut': 'Stato',
            'details_operation': "DETTAGLI DELL'OPERAZIONE",
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
            'reproduction_interdite': 'Qualsiasi riproduzione o uso non autorizzato è severamente vietato.',
            'document_genere': 'Documento generato automaticamente il',
            'page': 'Pagina',
            'statut_traitement': 'IN ELABORAZIONE',
            'donneur_ordre_label': "L'ordinante",
            'visa_banque': 'Visto della banca',
            'montant_virement': 'IMPORTO DEL BONIFICO',
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
            'reproduction_interdite': 'Jede Reproduktion oder unbefugte Verwendung ist strengstens untersagt.',
            'document_genere': 'Dokument automatisch generiert am',
            'page': 'Seite',
            'statut_traitement': 'IN BEARBEITUNG',
            'donneur_ordre_label': 'Der Auftraggeber',
            'visa_banque': 'Bankvisum',
            'montant_virement': 'ÜBERWEISUNGSBETRAG',
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
            'reproduction_interdite': 'Jakiekolwiek powielanie lub nieautoryzowane użycie jest surowo zabronione.',
            'document_genere': 'Dokument automatycznie wygenerowany dnia',
            'page': 'Strona',
            'statut_traitement': 'W TRAKCIE PRZETWARZANIA',
            'donneur_ordre_label': 'Zleceniodawca',
            'visa_banque': 'Wiza bankowa',
            'montant_virement': 'KWOTA PRZELEWU',
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
            'reproduction_interdite': 'Любое воспроизведение или несанкционированное использование строго запрещено.',
            'document_genere': 'Документ автоматически сгенерирован',
            'page': 'Страница',
            'statut_traitement': 'В ОБРАБОТКЕ',
            'donneur_ordre_label': 'Плательщик',
            'visa_banque': 'Виза банка',
            'montant_virement': 'СУММА ПЕРЕВОДА',
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
            'reproduction_interdite': 'Qualquer reprodução ou uso não autorizado é estritamente proibido.',
            'document_genere': 'Documento gerado automaticamente em',
            'page': 'Página',
            'statut_traitement': 'EM PROCESSAMENTO',
            'donneur_ordre_label': 'O ordenante',
            'visa_banque': 'Visto do banco',
            'montant_virement': 'VALOR DA TRANSFERÊNCIA',
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
            'document_confidentiel': 'هذا المستند سري ومخصص حصراً للمستفيد المذكور.',
            'reproduction_interdite': 'أي نسخ أو استخدام غير مصرح به محظور تماماً.',
            'document_genere': 'تم إنشاء هذا المستند تلقائياً في',
            'page': 'صفحة',
            'statut_traitement': 'قيد المعالجة',
            'donneur_ordre_label': 'آمر الدفع',
            'visa_banque': 'تأشيرة البنك',
            'montant_virement': 'مبلغ التحويل',
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
            'reproduction_interdite': '严禁任何未经授权的复制或使用。',
            'document_genere': '本文档由系统自动生成于',
            'page': '页',
            'statut_traitement': '处理中',
            'donneur_ordre_label': '付款人',
            'visa_banque': '银行签证',
            'montant_virement': '转账金额',
        },
    }
    return translations.get(langue, translations['fr'])


# ─────────────────────────────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────────────────────────────
def number_to_words(number, langue='fr'):
    try:
        from num2words import num2words
        lang_map = {'fr':'fr','en':'en','es':'es','it':'it','de':'de',
                    'pl':'pl','ru':'ru','pt':'pt','ar':'ar','zh':'zh'}
        return num2words(number, lang=lang_map.get(langue, 'fr')).upper()
    except Exception:
        return f"({number:,.2f})"


def get_logo_path(banque_code):
    """Retourne le chemin du logo depuis media/logos/<banque>.png"""
    path = os.path.join(settings.MEDIA_ROOT, 'logos', f'{banque_code}.png')
    return path if os.path.exists(path) else None


def register_unicode_fonts():
    font_paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
        '/Library/Fonts/Arial Unicode.ttf',
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont('DejaVu', fp))
                bold_fp = fp.replace('Sans.ttf', 'Sans-Bold.ttf')
                if os.path.exists(bold_fp):
                    pdfmetrics.registerFont(TTFont('DejaVu-Bold', bold_fp))
                else:
                    pdfmetrics.registerFont(TTFont('DejaVu-Bold', fp))
                return True
            except Exception:
                continue
    return False


_FONTS_OK  = register_unicode_fonts()
FONT       = 'DejaVu'      if _FONTS_OK else 'Helvetica'
FONT_BOLD  = 'DejaVu-Bold' if _FONTS_OK else 'Helvetica-Bold'


# ─────────────────────────────────────────────────────────────────────
# Canvas personnalisé — en-tête & pied de page
# ─────────────────────────────────────────────────────────────────────
class BankCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        self.logo_path   = kwargs.pop('logo_path',   None)
        self.bank_info   = kwargs.pop('bank_info',   {})
        self.doc_title   = kwargs.pop('doc_title',   '')
        self.ref_num     = kwargs.pop('ref_num',     '')
        self.doc_date    = kwargs.pop('doc_date',    '')
        self.langue      = kwargs.pop('langue',      'fr')
        self.bank_numero = kwargs.pop('bank_numero', '')
        self.bank_siege  = kwargs.pop('bank_siege',  '')
        super().__init__(*args, **kwargs)

    def showPage(self):
        """Dessine header/footer sur chaque page avant de la valider."""
        self._draw_header()
        self._draw_footer()
        super().showPage()

    # ── Appelé par showPage ───────────────────────────────────────────
    def draw_page_decorations(self):
        self._draw_header()
        self._draw_footer()

    # ── En-tête ──────────────────────────────────────────────────────
    def _draw_header(self):
        t = get_translations(self.langue)

        # ── Filet noir 3pt tout en haut
        self.setStrokeColor(C_BLACK)
        self.setLineWidth(3)
        self.line(0, PAGE_H - 2, PAGE_W, PAGE_H - 2)

        # ── Fond gris clair zone logo (y = PAGE_H-3 → PAGE_H-82)
        self.setFillColor(C_LIGHT)
        self.rect(0, PAGE_H - 82, PAGE_W, 79, fill=1, stroke=0)

        # ── Logo — colonne gauche
        LOGO_X = ML
        LOGO_Y = PAGE_H - 76
        LOGO_W = 130
        LOGO_H = 52
        logo_drawn = False
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                self.drawImage(
                    self.logo_path, LOGO_X, LOGO_Y,
                    width=LOGO_W, height=LOGO_H,
                    preserveAspectRatio=True,
                )
                logo_drawn = True
            except Exception:
                pass
        if not logo_drawn:
            # Fallback : nom de la banque en texte
            self.setFillColor(C_DARK)
            self.setFont(FONT_BOLD, 12)
            self.drawString(LOGO_X, LOGO_Y + 18, self.bank_info.get('name', 'BANK'))

        # ── Infos banque — colonne droite (alignées à droite)
        RIGHT_X = PAGE_W - MR
        # Nom de la banque
        self.setFillColor(C_BLACK)
        self.setFont(FONT_BOLD, 10)
        self.drawRightString(RIGHT_X, PAGE_H - 26, self.bank_info.get('name', ''))

        # Numéro d'enregistrement
        if self.bank_numero:
            self.setFillColor(C_MED)
            self.setFont(FONT, 7.5)
            self.drawRightString(RIGHT_X, PAGE_H - 37, self.bank_numero)

        # Siège social
        if self.bank_siege:
            self.setFont(FONT, 7.5)
            self.drawRightString(RIGHT_X, PAGE_H - 47, self.bank_siege)

        # Type de document (en italique via gris foncé)
        self.setFillColor(C_DARK)
        self.setFont(FONT_BOLD, 7.5)
        self.drawRightString(RIGHT_X, PAGE_H - 60, self.doc_title)

        # ── Filet séparateur header / bande méta
        self.setStrokeColor(C_BORDER)
        self.setLineWidth(0.6)
        self.line(ML, PAGE_H - 84, PAGE_W - MR, PAGE_H - 84)

        # ── Bande méta : référence gauche, date droite
        self.setFillColor(C_MED)
        self.setFont(FONT, 7.5)
        self.drawString(ML, PAGE_H - 97,
                        f"{t['reference']} :  {self.ref_num}")
        self.drawRightString(PAGE_W - MR, PAGE_H - 97,
                             f"{t['date']} :  {self.doc_date}")

        # ── Filet fin sous bande méta
        self.setLineWidth(0.4)
        self.line(ML, PAGE_H - 104, PAGE_W - MR, PAGE_H - 104)

    def _text_logo(self, x, y):
        """Fallback texte si le logo est absent"""
        self.setFillColor(C_DARK)
        self.setFont(FONT_BOLD, 13)
        self.drawString(x, y, self.bank_info.get('name', 'BANK'))

    # ── Pied de page ─────────────────────────────────────────────────
    def _draw_footer(self):
        t = get_translations(self.langue)

        self.setStrokeColor(C_BORDER)
        self.setLineWidth(0.5)
        self.line(ML, 58, PAGE_W - MR, 58)

        self.setFont(FONT, 6.5)
        self.setFillColor(C_MED)
        self.drawCentredText(PAGE_W / 2, 47, t['document_confidentiel'])
        self.drawCentredText(PAGE_W / 2, 37, t['reproduction_interdite'])

        gen = datetime.now().strftime('%d/%m/%Y %H:%M')
        self.drawString(ML, 24, f"{t['document_genere']} {gen}")

        self.setFont(FONT_BOLD, 7)
        self.setFillColor(C_DARK)
        self.drawRightString(PAGE_W - MR, 24,
                             f"{t['page']} {self._pageNumber}")


# ─────────────────────────────────────────────────────────────────────
# Helpers de mise en page
# ─────────────────────────────────────────────────────────────────────
def _section_title(text):
    """Titre de section : fond gris foncé, texte blanc, majuscules"""
    st = ParagraphStyle(
        '_ST',
        fontName=FONT_BOLD, fontSize=8,
        textColor=C_WHITE, backColor=C_DARK,
        spaceBefore=12, spaceAfter=0,
        leftIndent=0, borderPadding=(5, 8, 5, 8),
        leading=11,
    )
    return Paragraph(f'<b>{text.upper()}</b>', st)


def _p(text, bold=False, size=9, color=None, align=TA_LEFT):
    st = ParagraphStyle(
        '_P',
        fontName=FONT_BOLD if bold else FONT,
        fontSize=size,
        textColor=color or C_BLACK,
        leading=size + 3,
        alignment=align,
    )
    return Paragraph(str(text), st)


def _table(data, col_widths, header_row=False):
    """Tableau sobre : fond blanc, lignes alternées gris clair, bordures grises."""
    tbl = Table(data, colWidths=col_widths, repeatRows=1 if header_row else 0)
    style = [
        ('FONTNAME',       (0, 0), (-1, -1),  FONT),
        ('FONTSIZE',       (0, 0), (-1, -1),  9),
        ('TEXTCOLOR',      (0, 0), (-1, -1),  C_BLACK),
        ('ALIGN',          (0, 0), (-1, -1),  'LEFT'),
        ('VALIGN',         (0, 0), (-1, -1),  'MIDDLE'),
        ('LEFTPADDING',    (0, 0), (-1, -1),  8),
        ('RIGHTPADDING',   (0, 0), (-1, -1),  8),
        ('TOPPADDING',     (0, 0), (-1, -1),  6),
        ('BOTTOMPADDING',  (0, 0), (-1, -1),  6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1),  [C_WHITE, C_LIGHT]),
        ('GRID',           (0, 0), (-1, -1),  0.5, C_BORDER),
    ]
    if header_row:
        style += [
            ('BACKGROUND', (0, 0), (-1, 0), C_DARK),
            ('TEXTCOLOR',  (0, 0), (-1, 0), C_WHITE),
            ('FONTNAME',   (0, 0), (-1, 0), FONT_BOLD),
            ('FONTSIZE',   (0, 0), (-1, 0), 8.5),
        ]
    tbl.setStyle(TableStyle(style))
    return tbl


# ─────────────────────────────────────────────────────────────────────
# PDF — Initiation de virement
# ─────────────────────────────────────────────────────────────────────
def generer_pdf_initiation(virement):
    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'initiations')
    os.makedirs(pdf_dir, exist_ok=True)
    filename = (f'ordre_virement_{str(virement.id)[:8]}_'
                f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    filepath = os.path.join(pdf_dir, filename)

    bank_info = get_bank_info(virement.banque_emettrice)
    logo_path = get_logo_path(virement.banque_emettrice)
    t         = get_translations(virement.langue)
    ref       = str(virement.id)[:8].upper()
    date_str  = virement.date_creation.strftime('%d/%m/%Y')

    def make_canvas(*args, **kwargs):
        return BankCanvas(
            *args, **kwargs,
            logo_path=logo_path, bank_info=bank_info,
            doc_title=t['titre_initiation'],
            ref_num=ref, doc_date=date_str,
            langue=virement.langue,
            bank_numero=bank_info.get('numero', ''),
            bank_siege=bank_info.get('siege_social', ''),
        )

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=118, bottomMargin=72,
        leftMargin=ML, rightMargin=MR,
        canvasmaker=make_canvas,
    )

    # ── Montant en lettres ─────────────────────────────────────────
    try:
        montant_lettres = number_to_words(float(virement.montant), virement.langue)
        devise_label = dict(virement.DEVISES_CHOICES).get(virement.devise, virement.devise)
        montant_lettres = f"{montant_lettres} {devise_label}"
    except Exception:
        montant_lettres = ''

    story = []

    # ── Section 1 : Établissement & référence ─────────────────────
    story.append(_section_title(t['details_operation']))
    story.append(_table(
        [
            [_p(t['banque'] + ' :', bold=True), _p(bank_info['name']),
             _p(t['reference'] + ' :', bold=True), _p(ref)],
            [_p(t['date'] + ' :', bold=True),
             _p(virement.date_creation.strftime('%d/%m/%Y — %H:%M')),
             _p(t['statut'] + ' :', bold=True),
             _p(t['statut_traitement'])],
        ],
        col_widths=[3.8*cm, 6.5*cm, 3.8*cm, 5.4*cm],
    ))
    story.append(Spacer(1, 10))

    # ── Section 2 : Parties ────────────────────────────────────────
    story.append(_section_title(t['informations_parties']))

    half = CW / 2 - 3
    parties = _table(
        [
            # En-têtes
            [_p(t['donneur_ordre'], bold=True, color=C_WHITE),
             _p(t['beneficiaire'],  bold=True, color=C_WHITE)],
            # Noms
            [_p(virement.donneur_ordre_nom_complet, bold=True),
             _p(virement.beneficiaire_nom_complet,  bold=True)],
            # Comptes
            [_p(t['compte'] + ' :'),
             _p(t['compte'] + ' :')],
            [_p(virement.donneur_ordre_compte, size=8.5),
             _p(virement.beneficiaire_compte,  size=8.5)],
            # BIC / Email
            [_p(t['email'] + ' :'),
             _p(t['bic']   + ' :')],
            [_p(virement.beneficiaire_email, size=8.5),
             _p(virement.numero_bic,         size=8.5)],
        ],
        col_widths=[half, half],
        header_row=True,
    )
    story.append(parties)
    story.append(Spacer(1, 10))

    # ── Section 3 : Montant ────────────────────────────────────────
    story.append(_section_title(t['montant_virement']))

    montant_fmt = f"{virement.montant:,.2f} {virement.devise}"
    amount_style = ParagraphStyle(
        '_AMT',
        fontName=FONT_BOLD, fontSize=18,
        textColor=C_BLACK, alignment=TA_CENTER, leading=22,
    )
    words_style = ParagraphStyle(
        '_WRD',
        fontName=FONT, fontSize=8,
        textColor=C_MED, alignment=TA_CENTER, leading=11,
        spaceBefore=2,
    )

    tbl_amount = Table(
        [[Paragraph(montant_fmt, amount_style)],
         [Paragraph(montant_lettres, words_style)]],
        colWidths=[CW],
    )
    tbl_amount.setStyle(TableStyle([
        ('ALIGN',          (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',         (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',     (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 10),
        ('LEFTPADDING',    (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 10),
        ('BOX',            (0, 0), (-1, -1), 1, C_BORDER),
        ('BACKGROUND',     (0, 0), (-1, -1), C_WHITE),
        ('LINEBELOW',      (0, 0), (-1, 0),  0.4, C_BORDER),
    ]))
    story.append(tbl_amount)
    story.append(Spacer(1, 14))

    # ── Section 4 : Signatures ─────────────────────────────────────
    story.append(_section_title(t['signature_cachet']))

    sig_label_style = ParagraphStyle(
        '_SL', fontName=FONT, fontSize=8,
        textColor=C_MED, leading=11,
    )
    sig_line_style = ParagraphStyle(
        '_SLN', fontName=FONT, fontSize=9,
        textColor=C_LIGHT, leading=20,
    )
    half_sig = CW / 2 - 3

    def sig_cell(label):
        return [
            Paragraph(label, sig_label_style),
            Spacer(1, 22),
            Paragraph('_' * 42, sig_line_style),
        ]

    sig_tbl = Table(
        [[sig_cell(t['donneur_ordre_label']),
          sig_cell(t['visa_banque'])]],
        colWidths=[half_sig, half_sig],
    )
    sig_tbl.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX',           (0, 0), (-1, -1), 0.5, C_BORDER),
        ('LINEBEFORE',    (1, 0), (1, -1),  0.5, C_BORDER),
        ('BACKGROUND',    (0, 0), (-1, -1), C_WHITE),
    ]))
    story.append(sig_tbl)

    doc.build(story)
    return f'pdfs/initiations/{filename}'


# ─────────────────────────────────────────────────────────────────────
# PDF — Rejet de virement
# ─────────────────────────────────────────────────────────────────────
def generer_pdf_rejet(rejet):
    virement = rejet.virement

    pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs', 'rejets')
    os.makedirs(pdf_dir, exist_ok=True)
    filename = (f'avis_rejet_{str(virement.id)[:8]}_'
                f'{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    filepath = os.path.join(pdf_dir, filename)

    bank_info = get_bank_info(virement.banque_emettrice)
    logo_path = get_logo_path(virement.banque_emettrice)
    t         = get_translations(virement.langue)
    ref       = str(virement.id)[:8].upper()
    date_str  = rejet.date_rejet.strftime('%d/%m/%Y')

    def make_canvas(*args, **kwargs):
        return BankCanvas(
            *args, **kwargs,
            logo_path=logo_path, bank_info=bank_info,
            doc_title=t['titre_rejet'],
            ref_num=ref, doc_date=date_str,
            langue=virement.langue,
            bank_numero=bank_info.get('numero', ''),
            bank_siege=bank_info.get('siege_social', ''),
        )

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=118, bottomMargin=72,
        leftMargin=ML, rightMargin=MR,
        canvasmaker=make_canvas,
    )

    story = []

    # ── Section 1 : Références ─────────────────────────────────────
    story.append(_section_title(t['details_operation']))
    story.append(_table(
        [
            [_p(t['banque']      + ' :', bold=True), _p(bank_info['name']),
             _p(t['reference']   + ' :', bold=True), _p(ref)],
            [_p(t['date_rejet']  + ' :', bold=True),
             _p(rejet.date_rejet.strftime('%d/%m/%Y — %H:%M')),
             _p(t['statut']      + ' :', bold=True),
             _p(t['rejete'], bold=True)],
        ],
        col_widths=[3.8*cm, 6.5*cm, 3.8*cm, 5.4*cm],
    ))
    story.append(Spacer(1, 10))

    # ── Section 2 : Avis important ────────────────────────────────
    story.append(_section_title(t['avis_important']))
    story.append(_table(
        [[_p(t['msg_rejet'], size=9)]],
        col_widths=[CW],
    ))
    story.append(Spacer(1, 10))

    # ── Section 3 : Détails du rejet ──────────────────────────────
    story.append(_section_title(t['informations_parties']))
    story.append(_table(
        [
            [_p(t['beneficiaire_concerne'] + ' :', bold=True),
             _p(virement.beneficiaire_nom_complet, bold=True)],
            [_p(t['compte_beneficiaire']   + ' :', bold=True),
             _p(virement.beneficiaire_compte)],
            [_p(t['donneur_ordre']         + ' :', bold=True),
             _p(virement.donneur_ordre_nom_complet)],
        ],
        col_widths=[5.5*cm, CW - 5.5*cm],
    ))
    story.append(Spacer(1, 10))

    # ── Section 4 : Montant & frais ───────────────────────────────
    story.append(_section_title(t['details_operation'] + ' — ' + t['frais']))
    story.append(_table(
        [
            [_p(t['montant_initial'] + ' :', bold=True),
             _p(f"{virement.montant:,.2f} {virement.devise}", bold=True)],
            [_p(t['frais']           + ' :', bold=True),
             _p(f"{rejet.frais_redirection:,.2f} {virement.devise}", bold=True)],
            [_p(t['motif']           + ' :', bold=True),
             _p(rejet.motif_rejet)],
        ],
        col_widths=[5.5*cm, CW - 5.5*cm],
    ))
    story.append(Spacer(1, 14))

    # ── Section 5 : Signatures ────────────────────────────────────
    story.append(_section_title(t['signature_cachet']))

    sig_label_style = ParagraphStyle(
        '_SL2', fontName=FONT, fontSize=8,
        textColor=C_MED, leading=11,
    )
    sig_line_style = ParagraphStyle(
        '_SLN2', fontName=FONT, fontSize=9,
        textColor=C_LIGHT, leading=20,
    )
    half_sig = CW / 2 - 3

    def sig_cell(label):
        return [
            Paragraph(label, sig_label_style),
            Spacer(1, 22),
            Paragraph('_' * 42, sig_line_style),
        ]

    sig_tbl = Table(
        [[sig_cell(t['donneur_ordre_label']),
          sig_cell(t['visa_banque'])]],
        colWidths=[half_sig, half_sig],
    )
    sig_tbl.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BOX',           (0, 0), (-1, -1), 0.5, C_BORDER),
        ('LINEBEFORE',    (1, 0), (1, -1),  0.5, C_BORDER),
        ('BACKGROUND',    (0, 0), (-1, -1), C_WHITE),
    ]))
    story.append(sig_tbl)

    doc.build(story)
    return f'pdfs/rejets/{filename}'
