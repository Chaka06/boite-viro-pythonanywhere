from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import RegexValidator
from .models import Banque, Virement, RejetVirement

class InitiationVirementForm(forms.ModelForm):
    # Validation pour les numéros de compte/IBAN internationaux (très flexible)
    compte_validator = RegexValidator(
        regex=r'^[A-Z0-9\s\-]{8,50}$',
        message='Le numéro de compte doit contenir entre 8 et 50 caractères (lettres, chiffres, espaces et tirets autorisés).'
    )
    
    # Validation pour le BIC international
    bic_validator = RegexValidator(
        regex=r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$',
        message='Le code BIC doit contenir 8 ou 11 caractères (format standard BIC/SWIFT).'
    )
    
    class Meta:
        model = Virement
        fields = [
            'beneficiaire_nom', 'beneficiaire_prenom', 'beneficiaire_email',
            'beneficiaire_compte', 'numero_bic', 'montant', 'devise',
            'donneur_ordre_nom', 'donneur_ordre_prenom', 'donneur_ordre_compte',
            'langue', 'fuseau_horaire', 'banque_emettrice'
        ]
        
        widgets = {
            'beneficiaire_nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du bénéficiaire',
                'required': True
            }),
            'beneficiaire_prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom du bénéficiaire',
                'required': True
            }),
            'beneficiaire_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@exemple.com',
                'required': True
            }),
            'beneficiaire_compte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IBAN ou numéro de compte (tout pays accepté)',
                'required': True
            }),
            'numero_bic': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'BNPAFRPP, CHASUS33, DEUTDEFF, etc.',
                'style': 'text-transform: uppercase;',
                'required': True
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1000.00',
                'step': '0.01',
                'min': '0.01',
                'required': True
            }),
            'devise': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'donneur_ordre_nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du donneur d\'ordre',
                'required': True
            }),
            'donneur_ordre_prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom du donneur d\'ordre',
                'required': True
            }),
            'donneur_ordre_compte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'IBAN ou numéro de compte (tout pays accepté)',
                'required': True
            }),
            'langue': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'fuseau_horaire': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'banque_emettrice': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limiter aux banques actives uniquement
        self.fields['banque_emettrice'].queryset = Banque.objects.filter(actif=True).order_by('nom')

        # Appliquer les validateurs personnalisés
        self.fields['beneficiaire_compte'].validators.append(self.compte_validator)
        self.fields['donneur_ordre_compte'].validators.append(self.compte_validator)
        self.fields['numero_bic'].validators.append(self.bic_validator)
        
        # Personnaliser les labels
        self.fields['beneficiaire_nom'].label = "Nom du bénéficiaire *"
        self.fields['beneficiaire_prenom'].label = "Prénom du bénéficiaire *"
        self.fields['beneficiaire_email'].label = "Email du bénéficiaire *"
        self.fields['beneficiaire_compte'].label = "Numéro de compte / IBAN bénéficiaire *"
        self.fields['numero_bic'].label = "Code BIC/SWIFT *"
        self.fields['montant'].label = "Montant du virement *"
        self.fields['devise'].label = "Devise *"
        self.fields['donneur_ordre_nom'].label = "Nom du donneur d'ordre *"
        self.fields['donneur_ordre_prenom'].label = "Prénom du donneur d'ordre *"
        self.fields['donneur_ordre_compte'].label = "Numéro de compte / IBAN donneur d'ordre *"
        self.fields['langue'].label = "Langue du document *"
        self.fields['fuseau_horaire'].label = "Fuseau horaire *"
        self.fields['banque_emettrice'].label = "Banque émettrice *"
        
        # Textes d'aide
        self.fields['beneficiaire_compte'].help_text = "IBAN de n'importe quel pays ou numéro de compte bancaire (ex: FR76..., DE89..., US12345678901234567890, etc.)"
        self.fields['donneur_ordre_compte'].help_text = "IBAN de n'importe quel pays ou numéro de compte bancaire (ex: FR76..., DE89..., US12345678901234567890, etc.)"
        self.fields['numero_bic'].help_text = "Code BIC/SWIFT de n'importe quelle banque mondiale (8 ou 11 caractères)"
        self.fields['montant'].help_text = "Montant en décimales (ex: 1250.75) - Aucune limite de montant"
        self.fields['langue'].help_text = "Langue utilisée pour l'email et le PDF"
        self.fields['fuseau_horaire'].help_text = "Fuseau horaire affiché dans le document (ex : Europe/Paris pour la France)"
        
    def clean_numero_bic(self):
        """Nettoyer et valider le code BIC"""
        bic = self.cleaned_data.get('numero_bic', '').replace(' ', '').upper()
        return bic
    
    def clean_beneficiaire_compte(self):
        """Nettoyer le numéro de compte bénéficiaire"""
        compte = self.cleaned_data.get('beneficiaire_compte', '').replace(' ', '').upper()
        return compte
    
    def clean_donneur_ordre_compte(self):
        """Nettoyer le numéro de compte donneur d'ordre"""
        compte = self.cleaned_data.get('donneur_ordre_compte', '').replace(' ', '').upper()
        return compte
    
    def clean(self):
        """Validation croisée des champs"""
        cleaned_data = super().clean()
        beneficiaire_compte = cleaned_data.get('beneficiaire_compte')
        donneur_ordre_compte = cleaned_data.get('donneur_ordre_compte')
        
        # Vérifier que les comptes ne sont pas identiques
        if beneficiaire_compte and donneur_ordre_compte and beneficiaire_compte == donneur_ordre_compte:
            raise forms.ValidationError(
                "Le compte bénéficiaire et le compte donneur d'ordre ne peuvent pas être identiques."
            )
        
        return cleaned_data

class RejetVirementForm(forms.ModelForm):
    class Meta:
        model = RejetVirement
        fields = ['frais_redirection', 'motif_rejet']
        
        widgets = {
            'frais_redirection': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '25.00',
                'step': '0.01',
                'min': '0.00',
                'required': True
            }),
            'motif_rejet': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Précisez le motif du rejet du virement...',
                'rows': 4,
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les labels
        self.fields['frais_redirection'].label = "Frais de redirection *"
        self.fields['motif_rejet'].label = "Motif du rejet *"
        
        # Textes d'aide
        self.fields['frais_redirection'].help_text = "Montant des frais en décimales (ex: 25.50) - Aucune limite de montant"
        self.fields['motif_rejet'].help_text = "Expliquez clairement la raison du rejet"
        
    def clean_motif_rejet(self):
        """Valider le motif de rejet"""
        motif = self.cleaned_data.get('motif_rejet', '').strip()
        
        if len(motif) < 10:
            raise forms.ValidationError(
                "Le motif du rejet doit contenir au moins 10 caractères."
            )
        
        if len(motif) > 1000:
            raise forms.ValidationError(
                "Le motif du rejet ne peut pas dépasser 1000 caractères."
            )
        
        return motif

class ProfilUtilisateurForm(PasswordChangeForm):
    """Formulaire pour modifier le mot de passe utilisateur"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personnaliser les widgets
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mot de passe actuel'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nouveau mot de passe'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmer le nouveau mot de passe'
        })
        
        # Personnaliser les labels
        self.fields['old_password'].label = "Mot de passe actuel *"
        self.fields['new_password1'].label = "Nouveau mot de passe *"
        self.fields['new_password2'].label = "Confirmer le nouveau mot de passe *"
        
        # Textes d'aide
        self.fields['new_password1'].help_text = "Minimum 8 caractères, avec lettres et chiffres"

class RechercheVirementForm(forms.Form):
    """Formulaire de recherche pour l'historique des virements"""
    
    STATUT_CHOICES = [
        ('', 'Tous les statuts'),
        ('initie', 'Initiés'),
        ('rejete', 'Rejetés'),
    ]
    
    PERIODE_CHOICES = [
        ('', 'Toute période'),
        ('7', 'Les 7 derniers jours'),
        ('30', 'Les 30 derniers jours'),
        ('90', 'Les 3 derniers mois'),
        ('365', 'La dernière année'),
    ]
    
    recherche = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, email, compte...'
        }),
        label="Recherche"
    )
    
    statut = forms.ChoiceField(
        choices=STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Statut"
    )
    
    periode = forms.ChoiceField(
        choices=PERIODE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Période"
    )
    
    banque = forms.ModelChoiceField(
        queryset=Banque.objects.filter(actif=True).order_by('nom'),
        required=False,
        empty_label='Toutes les banques',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Banque émettrice"
    )
    
    devise = forms.ChoiceField(
        choices=[('', 'Toutes les devises')] + Virement.DEVISES_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label="Devise"
    )