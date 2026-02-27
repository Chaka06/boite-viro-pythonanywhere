from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Virement, RejetVirement, ProfilUtilisateur
from .forms import InitiationVirementForm, RejetVirementForm, ProfilUtilisateurForm, RechercheVirementForm
from .utils import generer_pdf_initiation, generer_pdf_rejet
from .email_utils import envoyer_email_initiation, envoyer_email_rejet

@login_required
def dashboard(request):
    """Tableau de bord principal"""
    profil = request.user.profil
    
    # Statistiques de l'utilisateur
    virements_initie = Virement.objects.filter(utilisateur=request.user, statut='initie').count()
    virements_rejete = Virement.objects.filter(utilisateur=request.user, statut='rejete').count()
    total_virements = virements_initie + virements_rejete
    
    # Derniers virements
    derniers_virements = Virement.objects.filter(utilisateur=request.user).order_by('-date_creation')[:5]
    
    # Vérifier si le quota est proche de la limite
    pourcentage_quota = profil.pourcentage_utilise
    quota_warning = pourcentage_quota >= 80
    quota_danger = pourcentage_quota >= 95
    
    context = {
        'profil': profil,
        'virements_initie': virements_initie,
        'virements_rejete': virements_rejete,
        'total_virements': total_virements,
        'derniers_virements': derniers_virements,
        'quota_warning': quota_warning,
        'quota_danger': quota_danger,
        'pourcentage_quota': pourcentage_quota,
    }
    
    return render(request, 'virements/dashboard.html', context)

@login_required
def initiation_virement(request):
    """Formulaire d'initiation de virement"""
    profil = request.user.profil
    
    # Vérifier si le quota n'est pas épuisé
    if profil.quota_epuise:
        messages.error(
            request, 
            f'Votre quota de {profil.quota_maximum} virements est épuisé. '
            f'Contactez l\'administrateur via WhatsApp : +2250504001272'
        )
        return redirect('virements:dashboard')
    
    if request.method == 'POST':
        form = InitiationVirementForm(request.POST)
        if form.is_valid():
            # Vérifier à nouveau le quota avant de sauvegarder
            if profil.quota_epuise:
                messages.error(request, 'Quota épuisé pendant la soumission du formulaire.')
                return redirect('virements:dashboard')
            
            virement = form.save(commit=False)
            virement.utilisateur = request.user
            virement.save()
            
            # Générer le PDF d'initiation
            try:
                pdf_path = generer_pdf_initiation(virement)
                virement.pdf_initiation = pdf_path
                virement.save()
            except Exception as e:
                messages.warning(request, f'Virement créé mais erreur lors de la génération du PDF: {e}')
            
            # Envoyer l'email d'initiation via SMTP (une seule fois)
            try:
                email_envoye = envoyer_email_initiation(virement)
                if email_envoye:
                    messages.success(request, 'Virement initié avec succès! Un email de confirmation a été envoyé au bénéficiaire.')
                else:
                    messages.warning(request, 'Virement initié mais l\'email n\'a pas pu être envoyé.')
            except Exception as e:
                messages.warning(request, f'Virement initié mais erreur lors de l\'envoi de l\'email: {e}')
            
            # Redirection pour éviter le double envoi d'email lors du rafraîchissement
            return redirect('virements:initiation_success', virement_id=virement.id)
    else:
        form = InitiationVirementForm()
    
    context = {
        'form': form,
        'profil': profil,
        'quota_restant': profil.quota_restant
    }
    
    return render(request, 'virements/initiation.html', context)

@login_required
def rejet_virement(request, virement_id):
    """Formulaire de rejet de virement"""
    virement = get_object_or_404(Virement, id=virement_id, utilisateur=request.user)
    
    # Vérifier que le virement n'est pas déjà rejeté
    if virement.est_rejete:
        messages.warning(request, 'Ce virement est déjà rejeté.')
        return redirect('virements:historique')
    
    if request.method == 'POST':
        form = RejetVirementForm(request.POST)
        if form.is_valid():
            rejet = form.save(commit=False)
            rejet.virement = virement
            rejet.save()
            
            # Générer le PDF de rejet
            try:
                pdf_path = generer_pdf_rejet(rejet)
                rejet.pdf_rejet = pdf_path
                rejet.save()
            except Exception as e:
                messages.warning(request, f'Rejet créé mais erreur lors de la génération du PDF: {e}')
            
            # Envoyer l'email de rejet via SMTP (une seule fois)
            try:
                email_envoye = envoyer_email_rejet(virement, rejet)
                if email_envoye:
                    messages.success(request, 'Virement rejeté avec succès! Un email de notification a été envoyé au bénéficiaire.')
                else:
                    messages.warning(request, 'Rejet enregistré mais l\'email n\'a pas pu être envoyé.')
            except Exception as e:
                messages.warning(request, f'Rejet enregistré mais erreur lors de l\'envoi de l\'email: {e}')
            
            # Redirection pour éviter le double envoi d'email lors du rafraîchissement
            return redirect('virements:rejet_success', virement_id=virement.id)
    else:
        form = RejetVirementForm()
    
    context = {
        'form': form,
        'virement': virement
    }
    
    return render(request, 'virements/rejet.html', context)

@login_required
def historique(request):
    """Historique des virements avec recherche et pagination"""
    form = RechercheVirementForm(request.GET or None)
    virements = Virement.objects.filter(utilisateur=request.user).order_by('-date_creation')
    
    # Appliquer les filtres de recherche
    if form.is_valid():
        recherche = form.cleaned_data.get('recherche')
        if recherche:
            virements = virements.filter(
                Q(beneficiaire_nom__icontains=recherche) |
                Q(beneficiaire_prenom__icontains=recherche) |
                Q(beneficiaire_email__icontains=recherche) |
                Q(beneficiaire_compte__icontains=recherche) |
                Q(donneur_ordre_nom__icontains=recherche) |
                Q(donneur_ordre_prenom__icontains=recherche)
            )
        
        statut = form.cleaned_data.get('statut')
        if statut:
            virements = virements.filter(statut=statut)
        
        periode = form.cleaned_data.get('periode')
        if periode:
            date_limite = timezone.now() - timedelta(days=int(periode))
            virements = virements.filter(date_creation__gte=date_limite)
        
        banque = form.cleaned_data.get('banque')
        if banque:
            virements = virements.filter(banque_emettrice=banque)
        
        devise = form.cleaned_data.get('devise')
        if devise:
            virements = virements.filter(devise=devise)
    
    # Pagination
    paginator = Paginator(virements, 10)  # 10 virements par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'total_virements': virements.count()
    }
    
    return render(request, 'virements/historique.html', context)

@login_required
def initiation_success(request, virement_id):
    """Page de succès après initiation d'un virement (GET uniquement)"""
    virement = get_object_or_404(Virement, id=virement_id, utilisateur=request.user)
    return render(request, 'virements/initiation_success.html', {
        'virement': virement
    })

@login_required
def rejet_success(request, virement_id):
    """Page de succès après rejet d'un virement (GET uniquement)"""
    virement = get_object_or_404(Virement, id=virement_id, utilisateur=request.user)
    if not virement.est_rejete or not hasattr(virement, 'rejet'):
        messages.warning(request, 'Ce virement n\'a pas été rejeté.')
        return redirect('virements:historique')
    
    return render(request, 'virements/rejet_success.html', {
        'virement': virement,
        'rejet': virement.rejet
    })

@login_required
def profil_utilisateur(request):
    """Gestion du profil utilisateur"""
    profil = request.user.profil
    
    if request.method == 'POST':
        form = ProfilUtilisateurForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mot de passe modifié avec succès!')
            return redirect('virements:profil')
    else:
        form = ProfilUtilisateurForm(request.user)
    
    context = {
        'form': form,
        'profil': profil
    }
    
    return render(request, 'virements/profil.html', context)

@login_required
def download_pdf(request, virement_id):
    """Télécharger le PDF d'un virement"""
    virement = get_object_or_404(Virement, id=virement_id, utilisateur=request.user)
    
    # Déterminer quel PDF télécharger
    pdf_type = request.GET.get('type', 'initiation')
    
    if pdf_type == 'rejet' and hasattr(virement, 'rejet') and virement.rejet.pdf_rejet:
        pdf_file = virement.rejet.pdf_rejet
        filename = f'rejet_virement_{str(virement.id)[:8]}.pdf'
    elif virement.pdf_initiation:
        pdf_file = virement.pdf_initiation
        filename = f'virement_{str(virement.id)[:8]}.pdf'
    else:
        raise Http404("PDF non trouvé")
    
    try:
        with open(pdf_file.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    except FileNotFoundError:
        raise Http404("Fichier PDF non trouvé")