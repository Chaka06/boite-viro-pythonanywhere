"""
Module pour l'envoi d'emails SMTP pour les virements
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import os


def get_bank_info(banque_code):
    """
    Retourner les informations de la banque (logo URL, couleurs, slogan, etc.)
    Les logos doivent être des URLs publiques pour garantir l'affichage dans les emails
    """
    BASE = 'https://www.virement.net/media/logos'
    bank_info = {
        'bnp_paribas': {
            'name': 'BNP PARIBAS',
            'logo_url': f'{BASE}/bnp_paribas.png',
            'primary_color': '#009652',
            'secondary_color': '#0066CC',
            'slogan': "La banque d'un monde qui change",
            'text_color': '#FFFFFF',
            'numero': 'RCS Paris 662 042 449',
            'siege_social': '16, boulevard des Italiens — 75009 Paris',
        },
        'credit_agricole': {
            'name': 'CRÉDIT AGRICOLE S.A.',
            'logo_url': f'{BASE}/credit_agricole.png',
            'primary_color': '#009682',
            'secondary_color': '#0066CC',
            'slogan': "La banque qui a du sens",
            'text_color': '#FFFFFF',
            'numero': 'RCS Paris 784 608 416',
            'siege_social': '12, place des États-Unis — 92127 Montrouge Cedex',
        },
        'bnp_paribas_fortis': {
            'name': 'BNP PARIBAS FORTIS',
            'logo_url': f'{BASE}/bnp_paribas_fortis.png',
            'primary_color': '#0064B4',
            'secondary_color': '#004D8A',
            'slogan': "La banque d'un monde qui change",
            'text_color': '#FFFFFF',
            'numero': 'RCS Bruxelles 403 199 702',
            'siege_social': 'Montagne du Parc 3 — 1000 Bruxelles, Belgique',
        },
        'credit_mutuel': {
            'name': 'CRÉDIT MUTUEL',
            'logo_url': f'{BASE}/credit_mutuel.png',
            'primary_color': '#0050A0',
            'secondary_color': '#003D7D',
            'slogan': "La banque qui vous ressemble",
            'text_color': '#FFFFFF',
            'numero': 'RCS Strasbourg 588 505 354',
            'siege_social': '34, rue du Wacken — 67000 Strasbourg',
        },
        'credit_suisse': {
            'name': 'CREDIT SUISSE AG',
            'logo_url': f'{BASE}/credit_suisse.png',
            'primary_color': '#C8102E',
            'secondary_color': '#A00D24',
            'slogan': "Banking on Switzerland",
            'text_color': '#FFFFFF',
            'numero': 'CHE-106.831.974',
            'siege_social': 'Paradeplatz 8 — 8070 Zürich, Suisse',
        },
        'credit_lyonnais': {
            'name': 'CRÉDIT LYONNAIS (LCL)',
            'logo_url': f'{BASE}/credit_lyonnais.png',
            'primary_color': '#003C78',
            'secondary_color': '#002D5A',
            'slogan': "La banque qui vous ressemble",
            'text_color': '#FFFFFF',
            'numero': 'RCS Paris 954 509 741',
            'siege_social': '20, avenue de Paris — 94811 Villejuif Cedex',
        },
        'banque_populaire': {
            'name': 'BANQUE POPULAIRE',
            'logo_url': f'{BASE}/banque_populaire.png',
            'primary_color': '#C83232',
            'secondary_color': '#A02828',
            'slogan': "La banque coopérative",
            'text_color': '#FFFFFF',
            'numero': 'RCS Paris 552 002 313',
            'siege_social': '50, avenue Pierre Mendès France — 75013 Paris',
        },
        'societe_generale': {
            'name': 'SOCIÉTÉ GÉNÉRALE',
            'logo_url': f'{BASE}/societe_generale.png',
            'primary_color': '#C80000',
            'secondary_color': '#A00000',
            'slogan': "La banque qui vous accompagne",
            'text_color': '#FFFFFF',
            'numero': 'RCS Paris 552 120 222',
            'siege_social': '29, boulevard Haussmann — 75009 Paris',
        },
        'intesa_sanpaolo': {
            'name': 'INTESA SANPAOLO S.P.A.',
            'logo_url': f'{BASE}/intesa_sanpaolo.png',
            'primary_color': '#003D82',
            'secondary_color': '#002D5F',
            'slogan': "La banca che ti ascolta",
            'text_color': '#FFFFFF',
            'numero': 'REA MI-1584927',
            'siege_social': 'Piazza San Carlo 156 — 10121 Torino, Italia',
        },
        'deutsche_bank': {
            'name': 'DEUTSCHE BANK AG',
            'logo_url': f'{BASE}/deutsche_bank.png',
            'primary_color': '#0018A8',
            'secondary_color': '#001066',
            'slogan': "Leading to a better future",
            'text_color': '#FFFFFF',
            'numero': 'HRB 71118 — Amtsgericht Frankfurt',
            'siege_social': 'Taunusanlage 12 — 60325 Frankfurt am Main',
        },
        'hsbc': {
            'name': 'HSBC BANK PLC',
            'logo_url': f'{BASE}/hsbc.png',
            'primary_color': '#DB0011',
            'secondary_color': '#B0000E',
            'slogan': "The world's local bank",
            'text_color': '#FFFFFF',
            'numero': 'Company No. 14259',
            'siege_social': '8 Canada Square — London E14 5HQ, United Kingdom',
        },
        'barclays': {
            'name': 'BARCLAYS BANK PLC',
            'logo_url': f'{BASE}/barclays.png',
            'primary_color': '#00AEEF',
            'secondary_color': '#0088CC',
            'slogan': "Now there's a thought",
            'text_color': '#FFFFFF',
            'numero': 'Company No. 1026167',
            'siege_social': '1 Churchill Place — London E14 5HP, United Kingdom',
        },
        'citibank': {
            'name': 'CITIBANK N.A.',
            'logo_url': f'{BASE}/citibank.png',
            'primary_color': '#1B4F9B',
            'secondary_color': '#0F3A6B',
            'slogan': "Citi never sleeps",
            'text_color': '#FFFFFF',
            'numero': 'FDIC # 7213',
            'siege_social': '388 Greenwich Street — New York, NY 10013, USA',
        },
        'ubs': {
            'name': 'UBS AG',
            'logo_url': f'{BASE}/ubs.png',
            'primary_color': '#E0001B',
            'secondary_color': '#B00015',
            'slogan': "Your world. Your ambitions. Our commitment.",
            'text_color': '#FFFFFF',
            'numero': 'CHE-101.329.561',
            'siege_social': 'Bahnhofstrasse 45 — 8098 Zürich, Suisse',
        },
        'ing_bank': {
            'name': 'ING BANK N.V.',
            'logo_url': f'{BASE}/ing_bank.png',
            'primary_color': '#FF6200',
            'secondary_color': '#CC4E00',
            'slogan': "Do your thing",
            'text_color': '#FFFFFF',
            'numero': 'KvK 33031431',
            'siege_social': 'Bijlmerplein 888 — 1102 MG Amsterdam, Pays-Bas',
        },
    }

    return bank_info.get(banque_code, {
        'name': banque_code.upper().replace('_', ' '),
        'logo_url': f'{BASE}/default.png',
        'primary_color': '#0066CC',
        'secondary_color': '#0056B3',
        'slogan': 'Banking services',
        'text_color': '#FFFFFF',
        'numero': '',
        'siege_social': '',
    })


def get_email_translations(langue):
    """Retourner les traductions complètes selon la langue"""
    translations = {
        'fr': {
            'subject_initiation': 'Confirmation de virement',
            'subject_rejet': 'Avis de rejet de virement',
            'dept_operations': 'DÉPARTEMENT DES OPÉRATIONS INTERNATIONALES',
            'securite_msg': 'Communication sécurisée',
            'titre_principal_initiation': 'Ordre de virement initié',
            'titre_principal_rejet': 'Virement rejeté',
            'reference_label': 'Référence',
            'salutation': 'Cher/Chère',
            'message_principal_initiation': 'Nous vous informons qu\'un virement bancaire international a été initié en votre faveur et est actuellement en cours de traitement selon nos protocoles de sécurité.',
            'message_principal_rejet': 'Nous avons le regret de vous informer que le virement de <strong>{{montant}} {{devise}}</strong> que vous deviez recevoir de la part de <strong>{{donneur_ordre}}</strong> n\'a pas pu être traité en raison d\'un blocage sur le compte de l\'émetteur. Pour débloquer la situation et permettre la réception des fonds, des frais de déblocage sont nécessaires. Vous trouverez les détails ci-dessous.',
            'rejete': 'BLOQUÉ / ÉCHOUÉ',
            'montant_label': 'MONTANT DU VIREMENT',
            'montant_rejete_label': 'MONTANT REJETÉ',
            'details_operation': 'Détails de l\'opération',
            'details_rejet': 'Détails du rejet',
            'beneficiaire_label': 'Bénéficiaire',
            'donneur_ordre_label': 'Donneur d\'ordre',
            'banque_label': 'Banque émettrice',
            'date_label': 'Date d\'initiation',
            'date_rejet_label': 'Date de rejet',
            'statut_label': 'Statut',
            'statut_traitement': 'EN TRAITEMENT',
            'info_importante': 'Information importante',
            'message_info': 'Ce virement sera traité dans les plus brefs délais. Vous recevrez une notification dès que les fonds seront disponibles sur votre compte.',
            'temps_traitement_label': 'Temps de traitement estimé',
            'temps_traitement': '1-3 jours ouvrables',
            'frais_label': 'Frais de redirection applicables',
            'motif_label': 'Motif du rejet',
            'que_faire': 'Que faire maintenant ?',
            'instructions': 'Veuillez contacter le donneur d\'ordre afin qu\'il paye les frais de rejet pour relancer la transaction.',
            'contact_label': 'Pour toute question',
            'contact_info': 'Veuillez contacter le donneur d\'ordre.',
            'message_automatique': 'Ce message est automatique. Merci de ne pas y répondre.',
            'droits_reserves': 'Tous droits réservés',
            'footer_msg': 'Document généré automatiquement',
            'systeme_gestion': 'Système de gestion des virements bancaires internationaux',
        },
        'en': {
            'subject_initiation': 'Wire Transfer Confirmation',
            'subject_rejet': 'Wire Transfer Rejection Notice',
            'dept_operations': 'INTERNATIONAL OPERATIONS DEPARTMENT',
            'securite_msg': 'Secure Communication',
            'titre_principal_initiation': 'Wire Transfer Initiated',
            'titre_principal_rejet': 'Transfer Rejected',
            'reference_label': 'Reference',
            'salutation': 'Dear',
            'message_principal_initiation': 'We inform you that an international wire transfer has been initiated in your favor and is currently being processed according to our security protocols.',
            'message_principal_rejet': 'We regret to inform you that the transfer of <strong>{{montant}} {{devise}}</strong> that you were supposed to receive from <strong>{{donneur_ordre}}</strong> could not be processed due to a block on the sender\'s account. To unblock the situation and allow the reception of funds, unblocking fees are necessary. You will find the details below.',
            'rejete': 'BLOCKED / FAILED',
            'montant_label': 'TRANSFER AMOUNT',
            'montant_rejete_label': 'REJECTED AMOUNT',
            'details_operation': 'Transaction Details',
            'details_rejet': 'Rejection Details',
            'beneficiaire_label': 'Beneficiary',
            'donneur_ordre_label': 'Ordering Party',
            'banque_label': 'Issuing Bank',
            'date_label': 'Initiation Date',
            'date_rejet_label': 'Rejection Date',
            'statut_label': 'Status',
            'statut_traitement': 'PROCESSING',
            'info_importante': 'Important Information',
            'message_info': 'This transfer will be processed as soon as possible. You will receive a notification once the funds are available in your account.',
            'temps_traitement_label': 'Estimated processing time',
            'temps_traitement': '1-3 business days',
            'frais_label': 'Applicable redirection fees',
            'motif_label': 'Rejection reason',
            'que_faire': 'What to do now?',
            'instructions': 'Please contact the ordering party so that they pay the rejection fees to restart the transaction.',
            'contact_label': 'For any questions',
            'contact_info': 'Please contact ordering party.',
            'message_automatique': 'This is an automated message. Please do not reply.',
            'droits_reserves': 'All rights reserved',
            'footer_msg': 'Document automatically generated',
            'systeme_gestion': 'International wire transfer management system',
        },
        'es': {
            'subject_initiation': 'Confirmación de transferencia',
            'subject_rejet': 'Aviso de rechazo de transferencia',
            'dept_operations': 'DEPARTAMENTO DE OPERACIONES INTERNACIONALES',
            'securite_msg': 'Comunicación segura',
            'titre_principal_initiation': 'Transferencia iniciada',
            'titre_principal_rejet': 'Transferencia rechazada',
            'reference_label': 'Referencia',
            'salutation': 'Estimado/a',
            'message_principal_initiation': 'Le informamos que se ha iniciado una transferencia bancaria internacional a su favor y está siendo procesada según nuestros protocolos de seguridad.',
            'message_principal_rejet': 'Lamentamos informarle que la transferencia de <strong>{{montant}} {{devise}}</strong> que debía recibir de <strong>{{donneur_ordre}}</strong> no ha podido ser procesada debido a un bloqueo en la cuenta del emisor. Para desbloquear la situación y permitir la recepción de fondos, se requieren tarifas de desbloqueo. Encontrará los detalles a continuación.',
            'rejete': 'BLOQUEADO / FALLIDO',
            'montant_label': 'IMPORTE DE LA TRANSFERENCIA',
            'montant_rejete_label': 'IMPORTE RECHAZADO',
            'details_operation': 'Detalles de la operación',
            'details_rejet': 'Detalles del rechazo',
            'beneficiaire_label': 'Beneficiario',
            'donneur_ordre_label': 'Ordenante',
            'banque_label': 'Banco emisor',
            'date_label': 'Fecha de iniciación',
            'date_rejet_label': 'Fecha de rechazo',
            'statut_label': 'Estado',
            'statut_traitement': 'EN PROCESO',
            'info_importante': 'Información importante',
            'message_info': 'Esta transferencia será procesada lo antes posible. Recibirá una notificación una vez que los fondos estén disponibles en su cuenta.',
            'temps_traitement_label': 'Tiempo de procesamiento estimado',
            'temps_traitement': '1-3 días hábiles',
            'frais_label': 'Gastos de redirección aplicables',
            'motif_label': 'Motivo del rechazo',
            'que_faire': '¿Qué hacer ahora?',
            'instructions': 'Por favor, contacte al ordenante para que pague las tasas de rechazo y reinicie la transacción.',
            'contact_label': 'Para cualquier pregunta',
            'contact_info': 'Póngase en contacto el ordenante.',
            'message_automatique': 'Este es un mensaje automático. Por favor, no responda.',
            'droits_reserves': 'Todos los derechos reservados',
            'footer_msg': 'Documento generado automáticamente',
            'systeme_gestion': 'Sistema de gestión de transferencias bancarias internacionales',
        },
        'it': {
            'subject_initiation': 'Conferma bonifico',
            'subject_rejet': 'Avviso di rifiuto bonifico',
            'dept_operations': 'DIPARTIMENTO OPERAZIONI INTERNAZIONALI',
            'securite_msg': 'Comunicazione sicura',
            'titre_principal_initiation': 'Bonifico avviato',
            'titre_principal_rejet': 'Bonifico rifiutato',
            'reference_label': 'Riferimento',
            'salutation': 'Gentile',
            'message_principal_initiation': 'La informiamo che è stato avviato un bonifico bancario internazionale a suo favore ed è attualmente in elaborazione secondo i nostri protocolli di sicurezza.',
            'message_principal_rejet': 'Ci dispiace informarla che il bonifico di <strong>{{montant}} {{devise}}</strong> che avrebbe dovuto ricevere da <strong>{{donneur_ordre}}</strong> non ha potuto essere elaborato a causa di un blocco sul conto del mittente. Per sbloccare la situazione e consentire la ricezione dei fondi, sono necessarie commissioni di sblocco. Troverà i dettagli di seguito.',
            'rejete': 'BLOCCATO / FALLITO',
            'montant_label': 'IMPORTO DEL BONIFICO',
            'montant_rejete_label': 'IMPORTO RIFIUTATO',
            'details_operation': 'Dettagli dell\'operazione',
            'details_rejet': 'Dettagli del rifiuto',
            'beneficiaire_label': 'Beneficiario',
            'donneur_ordre_label': 'Ordinante',
            'banque_label': 'Banca emittente',
            'date_label': 'Data di avvio',
            'date_rejet_label': 'Data di rifiuto',
            'statut_label': 'Stato',
            'statut_traitement': 'IN ELABORAZIONE',
            'info_importante': 'Informazione importante',
            'message_info': 'Questo bonifico sarà elaborato il prima possibile. Riceverà una notifica non appena i fondi saranno disponibili sul suo conto.',
            'temps_traitement_label': 'Tempo di elaborazione stimato',
            'temps_traitement': '1-3 giorni lavorativi',
            'frais_label': 'Commissioni di reindirizzamento applicabili',
            'motif_label': 'Motivo del rifiuto',
            'que_faire': 'Cosa fare ora?',
            'instructions': 'Si prega di contattare l\'ordinante affinché paghi le commissioni di rifiuto per riavviare la transazione.',
            'contact_label': 'Per qualsiasi domanda',
            'contact_info': 'Si prega di contattare l\'ordinante.',
            'message_automatique': 'Questo è un messaggio automatico. Si prega di non rispondere.',
            'droits_reserves': 'Tutti i diritti riservati',
            'footer_msg': 'Documento generato automaticamente',
            'systeme_gestion': 'Sistema di gestione bonifici bancari internazionali',
        },
        'de': {
            'subject_initiation': 'Überweisungsbestätigung',
            'subject_rejet': 'Überweisungs-Ablehnungsbenachrichtigung',
            'dept_operations': 'ABTEILUNG INTERNATIONALE OPERATIONEN',
            'securite_msg': 'Sichere Kommunikation',
            'titre_principal_initiation': 'Überweisung eingeleitet',
            'titre_principal_rejet': 'Überweisung abgelehnt',
            'reference_label': 'Referenz',
            'salutation': 'Liebe/r',
            'message_principal_initiation': 'Wir informieren Sie, dass eine internationale Banküberweisung zu Ihren Gunsten eingeleitet wurde und derzeit gemäß unseren Sicherheitsprotokollen bearbeitet wird.',
            'message_principal_rejet': 'Wir bedauern, Ihnen mitteilen zu müssen, dass die Überweisung von <strong>{{montant}} {{devise}}</strong>, die Sie von <strong>{{donneur_ordre}}</strong> erhalten sollten, aufgrund einer Sperre auf dem Konto des Absenders nicht verarbeitet werden konnte. Um die Situation zu entsperren und den Empfang der Mittel zu ermöglichen, sind Entsperrungsgebühren erforderlich. Sie finden die Details unten.',
            'rejete': 'GESPERRT / FEHLGESCHLAGEN',
            'montant_label': 'ÜBERWEISUNGSBETRAG',
            'montant_rejete_label': 'ABGELEHNTER BETRAG',
            'details_operation': 'Transaktionsdetails',
            'details_rejet': 'Ablehnungsdetails',
            'beneficiaire_label': 'Begünstigter',
            'donneur_ordre_label': 'Auftraggeber',
            'banque_label': 'Ausstellende Bank',
            'date_label': 'Initiierungsdatum',
            'date_rejet_label': 'Ablehnungsdatum',
            'statut_label': 'Status',
            'statut_traitement': 'IN BEARBEITUNG',
            'info_importante': 'Wichtige Information',
            'message_info': 'Diese Überweisung wird so schnell wie möglich bearbeitet. Sie erhalten eine Benachrichtigung, sobald die Mittel auf Ihrem Konto verfügbar sind.',
            'temps_traitement_label': 'Geschätzte Bearbeitungszeit',
            'temps_traitement': '1-3 Werktage',
            'frais_label': 'Anfallende Umleitungsgebühren',
            'motif_label': 'Ablehnungsgrund',
            'que_faire': 'Was ist jetzt zu tun?',
            'instructions': 'Bitte kontaktieren Sie den Auftraggeber, damit er die Ablehnungsgebühren zahlt, um die Transaktion neu zu starten.',
            'contact_label': 'Bei Fragen',
            'contact_info': 'Bitte wenden Sie sich an den Besteller.',
            'message_automatique': 'Dies ist eine automatische Nachricht. Bitte nicht antworten.',
            'droits_reserves': 'Alle Rechte vorbehalten',
            'footer_msg': 'Dokument automatisch generiert',
            'systeme_gestion': 'Verwaltungssystem für internationale Banküberweisungen',
        },
        'pl': {
            'subject_initiation': 'Potwierdzenie przelewu',
            'subject_rejet': 'Powiadomienie o odrzuceniu przelewu',
            'dept_operations': 'DZIAŁ OPERACJI MIĘDZYNARODOWYCH',
            'securite_msg': 'Bezpieczna komunikacja',
            'titre_principal_initiation': 'Przelew zainicjowany',
            'titre_principal_rejet': 'Przelew odrzucony',
            'reference_label': 'Referencja',
            'salutation': 'Szanowny/a',
            'message_principal_initiation': 'Informujemy, że został zainicjowany międzynarodowy przelew bankowy na Pańską korzyść i jest obecnie przetwarzany zgodnie z naszymi protokołami bezpieczeństwa.',
            'message_principal_rejet': 'Z przykrością informujemy, że przelew w wysokości <strong>{{montant}} {{devise}}</strong>, który miał Pan/Pani otrzymać od <strong>{{donneur_ordre}}</strong>, nie mógł zostać przetworzony z powodu blokady na koncie nadawcy. Aby odblokować sytuację i umożliwić otrzymanie środków, wymagane są opłaty za odblokowanie. Szczegóły znajdzie Pan/Pani poniżej.',
            'rejete': 'ZABLOKOWANY / NIEPOWODZENIE',
            'montant_label': 'KWOTA PRZELEWU',
            'montant_rejete_label': 'KWOTA ODRZUCONA',
            'details_operation': 'Szczegóły transakcji',
            'details_rejet': 'Szczegóły odrzucenia',
            'beneficiaire_label': 'Beneficjent',
            'donneur_ordre_label': 'Zleceniodawca',
            'banque_label': 'Bank wydający',
            'date_label': 'Data inicjacji',
            'date_rejet_label': 'Data odrzucenia',
            'statut_label': 'Status',
            'statut_traitement': 'W TRAKCIE PRZETWARZANIA',
            'info_importante': 'Ważna informacja',
            'message_info': 'Ten przelew zostanie przetworzony tak szybko, jak to możliwe. Otrzyma Pan/Pani powiadomienie, gdy środki będą dostępne na koncie.',
            'temps_traitement_label': 'Szacowany czas przetwarzania',
            'temps_traitement': '1-3 dni robocze',
            'frais_label': 'Obowiązujące opłaty przekierowania',
            'motif_label': 'Powód odrzucenia',
            'que_faire': 'Co teraz robić?',
            'instructions': 'Proszę skontaktować się ze zleceniodawcą, aby zapłacił opłaty za odrzucenie i ponownie uruchomił transakcję.',
            'contact_label': 'W przypadku pytań',
            'contact_info': 'Skontaktuj się z dyrektorem.',
            'message_automatique': 'To jest automatyczna wiadomość. Prosimy nie odpowiadać.',
            'droits_reserves': 'Wszelkie prawa zastrzeżone',
            'footer_msg': 'Dokument automatycznie wygenerowany',
            'systeme_gestion': 'System zarządzania międzynarodowymi przelewami bankowymi',
        },
        'ru': {
            'subject_initiation': 'Подтверждение перевода',
            'subject_rejet': 'Уведомление об отклонении перевода',
            'dept_operations': 'ОТДЕЛ МЕЖДУНАРОДНЫХ ОПЕРАЦИЙ',
            'securite_msg': 'Безопасная связь',
            'titre_principal_initiation': 'Перевод инициирован',
            'titre_principal_rejet': 'Перевод отклонен',
            'reference_label': 'Ссылка',
            'salutation': 'Уважаемый/ая',
            'message_principal_initiation': 'Информируем Вас о том, что международный банковский перевод в Вашу пользу был инициирован и в настоящее время обрабатывается в соответствии с нашими протоколами безопасности.',
            'message_principal_rejet': 'С сожалением сообщаем Вам, что перевод на сумму <strong>{{montant}} {{devise}}</strong>, который Вы должны были получить от <strong>{{donneur_ordre}}</strong>, не мог быть обработан из-за блокировки на счете отправителя. Для разблокировки ситуации и получения средств необходимы комиссии за разблокировку. Детали Вы найдете ниже.',
            'rejete': 'ЗАБЛОКИРОВАН / ОТКЛОНЕН',
            'montant_label': 'СУММА ПЕРЕВОДА',
            'montant_rejete_label': 'ОТКЛОНЕННАЯ СУММА',
            'details_operation': 'Детали операции',
            'details_rejet': 'Детали отклонения',
            'beneficiaire_label': 'Бенефициар',
            'donneur_ordre_label': 'Плательщик',
            'banque_label': 'Банк-эмитент',
            'date_label': 'Дата инициации',
            'date_rejet_label': 'Дата отклонения',
            'statut_label': 'Статус',
            'statut_traitement': 'В ОБРАБОТКЕ',
            'info_importante': 'Важная информация',
            'message_info': 'Этот перевод будет обработан как можно скорее. Вы получите уведомление, как только средства станут доступны на Вашем счете.',
            'temps_traitement_label': 'Предполагаемое время обработки',
            'temps_traitement': '1-3 рабочих дня',
            'frais_label': 'Применимые комиссии за перенаправление',
            'motif_label': 'Причина отклонения',
            'que_faire': 'Что делать сейчас?',
            'instructions': 'Пожалуйста, свяжитесь с плательщиком, чтобы он оплатил комиссию за отклонение и перезапустил транзакцию.',
            'contact_label': 'По любым вопросам',
            'contact_info': 'Свяжитесь со своим плательщиком.',
            'message_automatique': 'Это автоматическое сообщение. Пожалуйста, не отвечайте.',
            'droits_reserves': 'Все права защищены',
            'footer_msg': 'Документ автоматически сгенерирован',
            'systeme_gestion': 'Система управления международными банковскими переводами',
        },
        'pt': {
            'subject_initiation': 'Confirmação de Transferência',
            'subject_rejet': 'Aviso de Rejeição de Transferência',
            'dept_operations': 'DEPARTAMENTO DE OPERAÇÕES INTERNACIONAIS',
            'securite_msg': 'Comunicação Segura',
            'titre_principal_initiation': 'Transferência Iniciada',
            'titre_principal_rejet': 'Transferência Rejeitada',
            'reference_label': 'Referência',
            'salutation': 'Caro/Cara',
            'message_principal_initiation': 'Informamos que uma transferência bancária internacional foi iniciada em seu favor e está atualmente sendo processada de acordo com nossos protocolos de segurança.',
            'message_principal_rejet': 'Lamentamos informar que a transferência de <strong>{{montant}} {{devise}}</strong> que você deveria receber de <strong>{{donneur_ordre}}</strong> não pôde ser processada devido a um bloqueio na conta do remetente. Para desbloquear a situação e permitir o recebimento dos fundos, são necessárias taxas de desbloqueio. Você encontrará os detalhes abaixo.',
            'rejete': 'BLOQUEADO / FALHADO',
            'montant_label': 'VALOR DA TRANSFERÊNCIA',
            'montant_rejete_label': 'VALOR REJEITADO',
            'details_operation': 'Detalhes da Operação',
            'details_rejet': 'Detalhes da Rejeição',
            'beneficiaire_label': 'Beneficiário',
            'donneur_ordre_label': 'Ordenante',
            'banque_label': 'Banco Emissor',
            'date_label': 'Data de Iniciação',
            'date_rejet_label': 'Data de Rejeição',
            'statut_label': 'Status',
            'statut_traitement': 'EM PROCESSAMENTO',
            'info_importante': 'Informação Importante',
            'message_info': 'Esta transferência será processada o mais breve possível. Você receberá uma notificação assim que os fundos estiverem disponíveis em sua conta.',
            'temps_traitement_label': 'Tempo de processamento estimado',
            'temps_traitement': '1-3 dias úteis',
            'frais_label': 'Taxas de redirecionamento aplicáveis',
            'motif_label': 'Motivo da rejeição',
            'que_faire': 'O que fazer agora?',
            'instructions': 'Por favor, entre em contato com o ordenante para que ele pague as taxas de rejeição e reinicie a transação.',
            'contact_label': 'Para qualquer dúvida',
            'contact_info': 'Por favor, entre em contato com o ordenante.',
            'message_automatique': 'Esta é uma mensagem automática. Por favor, não responda.',
            'droits_reserves': 'Todos os direitos reservados',
            'footer_msg': 'Documento gerado automaticamente',
            'systeme_gestion': 'Sistema de gestão de transferências bancárias internacionais',
        },
        'ar': {
            'subject_initiation': 'تأكيد التحويل',
            'subject_rejet': 'إشعار رفض التحويل',
            'dept_operations': 'قسم العمليات الدولية',
            'securite_msg': 'اتصال آمن',
            'titre_principal_initiation': 'تم بدء التحويل',
            'titre_principal_rejet': 'تم رفض التحويل',
            'reference_label': 'المرجع',
            'salutation': 'عزيزي/عزيزتي',
            'message_principal_initiation': 'نود إعلامكم بأنه تم بدء تحويل مصرفي دولي لصالحكم وهو قيد المعالجة حالياً وفقاً لبروتوكولات الأمان الخاصة بنا.',
            'message_principal_rejet': 'نأسف لإعلامكم بأن التحويل بقيمة <strong>{{montant}} {{devise}}</strong> الذي كان من المفترض أن تتلقوه من <strong>{{donneur_ordre}}</strong> لم يتمكن من المعالجة بسبب حظر على حساب المرسل. لفتح الحظر والسماح باستلام الأموال، هناك حاجة لرسوم فتح الحظر. ستجدون التفاصيل أدناه.',
            'rejete': 'محظور / فشل',
            'montant_label': 'مبلغ التحويل',
            'montant_rejete_label': 'المبلغ المرفوض',
            'details_operation': 'تفاصيل العملية',
            'details_rejet': 'تفاصيل الرفض',
            'beneficiaire_label': 'المستفيد',
            'donneur_ordre_label': 'آمر الدفع',
            'banque_label': 'المصرف المصدر',
            'date_label': 'تاريخ البدء',
            'date_rejet_label': 'تاريخ الرفض',
            'statut_label': 'الحالة',
            'statut_traitement': 'قيد المعالجة',
            'info_importante': 'معلومة مهمة',
            'message_info': 'سيتم معالجة هذا التحويل في أقرب وقت ممكن. ستتلقى إشعاراً بمجرد توفر الأموال في حسابك.',
            'temps_traitement_label': 'الوقت المتوقع للمعالجة',
            'temps_traitement': '1-3 أيام عمل',
            'frais_label': 'رسوم إعادة التوجيه المطبقة',
            'motif_label': 'سبب الرفض',
            'que_faire': 'ماذا تفعل الآن؟',
            'instructions': 'يرجى الاتصال بآمر الدفع لدفع رسوم الرفض وإعادة تشغيل المعاملة.',
            'contact_label': 'لأي استفسار',
            'contact_info': 'يرجى الاتصال بآمر الدفع.',
            'message_automatique': 'هذه رسالة تلقائية. يرجى عدم الرد.',
            'droits_reserves': 'جميع الحقوق محفوظة',
            'footer_msg': 'تم إنشاء هذا المستند تلقائياً',
            'systeme_gestion': 'نظام إدارة التحويلات المصرفية الدولية',
        },
        'zh': {
            'subject_initiation': '转账确认',
            'subject_rejet': '转账拒绝通知',
            'dept_operations': '国际运营部',
            'securite_msg': '安全通信',
            'titre_principal_initiation': '转账已启动',
            'titre_principal_rejet': '转账已拒绝',
            'reference_label': '参考号',
            'salutation': '尊敬的',
            'message_principal_initiation': '我们通知您，已为您启动了一笔国际银行转账，目前正在根据我们的安全协议进行处理。',
            'message_principal_rejet': '我们遗憾地通知您，您本应从<strong>{{donneur_ordre}}</strong>收到的<strong>{{montant}} {{devise}}</strong>转账由于发送方账户被冻结而无法处理。要解除冻结并允许接收资金，需要支付解冻费用。您将在下面找到详细信息。',
            'rejete': '已冻结 / 失败',
            'montant_label': '转账金额',
            'montant_rejete_label': '被拒绝金额',
            'details_operation': '交易详情',
            'details_rejet': '拒绝详情',
            'beneficiaire_label': '收款人',
            'donneur_ordre_label': '付款人',
            'banque_label': '发卡银行',
            'date_label': '启动日期',
            'date_rejet_label': '拒绝日期',
            'statut_label': '状态',
            'statut_traitement': '处理中',
            'info_importante': '重要信息',
            'message_info': '此转账将尽快处理。一旦资金在您的账户中可用，您将收到通知。',
            'temps_traitement_label': '预计处理时间',
            'temps_traitement': '1-3个工作日',
            'frais_label': '适用的重定向费用',
            'motif_label': '拒绝原因',
            'que_faire': '现在该怎么办？',
            'instructions': '请联系付款人支付拒绝费用以重新启动交易。',
            'contact_label': '如有任何疑问',
            'contact_info': '请联系付款人。',
            'message_automatique': '这是一条自动消息。请勿回复。',
            'droits_reserves': '版权所有',
            'footer_msg': '本文档自动生成',
            'systeme_gestion': '国际银行转账管理系统',
        }
    }
    
    return translations.get(langue, translations['fr'])


def envoyer_email_initiation(virement):
    """
    Envoyer un email d'initiation de virement via SMTP
    """
    try:
        langue = virement.langue
        translations = get_email_translations(langue)
        
        # Récupérer les informations de la banque
        bank_info = get_bank_info(virement.banque_emettrice)
        
        # Préparer le contexte pour le template
        context = {
            'virement': virement,
            't': translations,
            'numero_virement': str(virement.id)[:8].upper(),
            'banque_name': virement.get_banque_emettrice_display(),
            'bank_info': bank_info,
        }
        
        # Rendre le template HTML
        html_message = render_to_string('virements/emails/initiation.html', context)
        
        # Créer le message email
        subject = f"{translations['subject_initiation']} - {context['banque_name']}"
        
        # Utiliser le nom de la banque comme expéditeur
        from_email = f"{bank_info['name']} <{settings.EMAIL_HOST_USER}>"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_message),  # Version texte pour les clients qui ne supportent pas HTML
            from_email=from_email,
            to=[virement.beneficiaire_email],
        )
        
        # Attacher la version HTML
        email.attach_alternative(html_message, "text/html")

        # Attacher le PDF d'initiation si disponible
        if virement.pdf_initiation:
            pdf_full_path = os.path.join(settings.MEDIA_ROOT, str(virement.pdf_initiation))
            if os.path.exists(pdf_full_path):
                email.attach_file(pdf_full_path)

        # Envoyer l'email
        email.send()

        return True

    except Exception as e:
        import logging
        logger = logging.getLogger('virements')
        logger.error(f"Erreur envoi email initiation (bénéficiaire={virement.beneficiaire_email}): {type(e).__name__}: {e}")
        raise


def envoyer_email_rejet(virement, rejet):
    """
    Envoyer un email de rejet de virement via SMTP
    """
    try:
        langue = virement.langue
        translations = get_email_translations(langue)
        
        # Récupérer les informations de la banque
        bank_info = get_bank_info(virement.banque_emettrice)
        
        # Préparer le contexte pour le template
        context = {
            'virement': virement,
            'rejet': rejet,
            't': translations,
            'numero_virement': str(virement.id)[:8].upper(),
            'banque_name': virement.get_banque_emettrice_display(),
            'bank_info': bank_info,
        }
        
        # Remplacer les placeholders dans le message principal de rejet
        message_rejet = translations['message_principal_rejet']
        message_rejet = message_rejet.replace('{{montant}}', str(virement.montant))
        message_rejet = message_rejet.replace('{{devise}}', virement.devise)
        message_rejet = message_rejet.replace('{{donneur_ordre}}', virement.donneur_ordre_nom_complet)
        context['message_principal_rejet_formatted'] = message_rejet
        
        # Rendre le template HTML
        html_message = render_to_string('virements/emails/rejet.html', context)
        
        # Créer le message email
        subject = f"{translations['subject_rejet']} - {context['banque_name']}"
        
        # Utiliser le nom de la banque comme expéditeur
        from_email = f"{bank_info['name']} <{settings.EMAIL_HOST_USER}>"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=strip_tags(html_message),  # Version texte
            from_email=from_email,
            to=[virement.beneficiaire_email],
        )
        
        # Attacher la version HTML
        email.attach_alternative(html_message, "text/html")

        # Attacher le PDF de rejet si disponible
        if rejet.pdf_rejet:
            pdf_full_path = os.path.join(settings.MEDIA_ROOT, str(rejet.pdf_rejet))
            if os.path.exists(pdf_full_path):
                email.attach_file(pdf_full_path)

        # Envoyer l'email
        email.send()

        return True

    except Exception as e:
        import logging
        logger = logging.getLogger('virements')
        logger.error(f"Erreur envoi email rejet (bénéficiaire={virement.beneficiaire_email}): {type(e).__name__}: {e}")
        raise

