from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Banque(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom de la banque")
    code = models.SlugField(max_length=50, unique=True, verbose_name="Code unique")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True, verbose_name="Logo")
    couleur_principale = models.CharField(max_length=7, default='#0066CC', verbose_name="Couleur principale")
    couleur_secondaire = models.CharField(max_length=7, default='#0056B3', verbose_name="Couleur secondaire")
    slogan = models.CharField(max_length=200, blank=True, verbose_name="Slogan")
    numero_enregistrement = models.CharField(max_length=100, blank=True, verbose_name="Numéro d'enregistrement")
    siege_social = models.CharField(max_length=200, blank=True, verbose_name="Siège social")
    actif = models.BooleanField(default=True, verbose_name="Banque active")

    class Meta:
        verbose_name = "Banque"
        verbose_name_plural = "Banques"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class ProfilUtilisateur(models.Model):
    TYPE_COMPTE_CHOICES = [
        ('standard', 'Standard (40 virements)'),
        ('premium', 'Premium (100 virements)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    type_compte = models.CharField(max_length=10, choices=TYPE_COMPTE_CHOICES, default='standard')
    quota_utilise = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_type_compte_display()}"
    
    @property
    def quota_maximum(self):
        return 100 if self.type_compte == 'premium' else 40
    
    @property
    def quota_restant(self):
        return self.quota_maximum - self.quota_utilise
    
    @property
    def quota_epuise(self):
        return self.quota_utilise >= self.quota_maximum
    
    @property
    def pourcentage_utilise(self):
        return (self.quota_utilise / self.quota_maximum) * 100

class Virement(models.Model):
    LANGUES_CHOICES = [
        ('fr', 'Français'),
        ('en', 'English'),
        ('es', 'Español'),
        ('it', 'Italiano'),
        ('de', 'Deutsch'),
        ('pl', 'Polski'),
        ('ru', 'Русский'),
        ('pt', 'Português'),
        ('ar', 'العربية'),
        ('zh', '中文'),
    ]
    
    DEVISES_CHOICES = [
        ('EUR', 'Euro (EUR)'),
        ('USD', 'Dollar américain (USD)'),
        ('CHF', 'Franc suisse (CHF)'),
        ('CAD', 'Dollar canadien (CAD)'),
        ('GBP', 'Livre sterling (GBP)'),
        ('PLN', 'Zloty polonais (PLN)'),
        ('RUB', 'Rouble russe (RUB)'),
    ]
    
    STATUT_CHOICES = [
        ('initie', 'Initié'),
        ('rejete', 'Rejeté'),
    ]
    
    # Champs système
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='virements')
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='initie')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Informations du bénéficiaire
    beneficiaire_nom = models.CharField(max_length=200, verbose_name="Nom du bénéficiaire")
    beneficiaire_prenom = models.CharField(max_length=200, verbose_name="Prénom du bénéficiaire")
    beneficiaire_email = models.EmailField(verbose_name="Email du bénéficiaire")
    beneficiaire_compte = models.CharField(max_length=50, verbose_name="Numéro de compte bénéficiaire")
    numero_bic = models.CharField(max_length=11, verbose_name="Numéro BIC")
    
    # Informations du donneur d'ordre
    donneur_ordre_nom = models.CharField(max_length=200, verbose_name="Nom du donneur d'ordre")
    donneur_ordre_prenom = models.CharField(max_length=200, verbose_name="Prénom du donneur d'ordre")
    donneur_ordre_compte = models.CharField(max_length=50, verbose_name="Numéro de compte donneur d'ordre")
    
    # Informations du virement
    montant = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant du virement"
    )
    devise = models.CharField(max_length=3, choices=DEVISES_CHOICES, default='EUR')
    
    # Configuration
    langue = models.CharField(max_length=2, choices=LANGUES_CHOICES, default='fr')
    banque_emettrice = models.ForeignKey(
        Banque,
        on_delete=models.PROTECT,
        verbose_name="Banque émettrice",
        related_name='virements',
    )
    
    # Fichiers générés
    pdf_initiation = models.FileField(upload_to='pdfs/initiations/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Virement"
        verbose_name_plural = "Virements"
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Virement {str(self.id)[:8]} - {self.beneficiaire_nom} {self.beneficiaire_prenom}"
    
    @property
    def beneficiaire_nom_complet(self):
        return f"{self.beneficiaire_nom} {self.beneficiaire_prenom}"
    
    @property
    def donneur_ordre_nom_complet(self):
        return f"{self.donneur_ordre_nom} {self.donneur_ordre_prenom}"
    
    @property
    def montant_formate(self):
        return f"{self.montant:,.2f} {self.devise}"
    
    @property
    def est_rejete(self):
        return self.statut == 'rejete'

class RejetVirement(models.Model):
    virement = models.OneToOneField(Virement, on_delete=models.CASCADE, related_name='rejet')
    frais_redirection = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Frais de redirection"
    )
    motif_rejet = models.TextField(verbose_name="Motif du rejet")
    date_rejet = models.DateTimeField(auto_now_add=True)
    
    # Fichier PDF généré
    pdf_rejet = models.FileField(upload_to='pdfs/rejets/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Rejet de virement"
        verbose_name_plural = "Rejets de virements"
        ordering = ['-date_rejet']
    
    def __str__(self):
        return f"Rejet - {self.virement}"
    
    @property
    def frais_formates(self):
        return f"{self.frais_redirection:,.2f} {self.virement.devise}"

# Signaux pour gérer automatiquement les profils utilisateurs
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def creer_profil_utilisateur(sender, instance, created, **kwargs):
    """Créer automatiquement un profil utilisateur lors de la création d'un User"""
    if created:
        ProfilUtilisateur.objects.create(user=instance)

@receiver(post_save, sender=User)
def sauvegarder_profil_utilisateur(sender, instance, **kwargs):
    """Sauvegarder le profil utilisateur lors de la sauvegarde d'un User"""
    if hasattr(instance, 'profil'):
        instance.profil.save()

@receiver(post_save, sender=Virement)
def incrementer_quota_utilisateur(sender, instance, created, **kwargs):
    """Incrémenter le quota utilisé lors de la création d'un virement"""
    if created:
        profil = instance.utilisateur.profil
        profil.quota_utilise += 1
        profil.save()

@receiver(post_save, sender=RejetVirement)
def marquer_virement_rejete(sender, instance, created, **kwargs):
    """Marquer le virement comme rejeté lors de la création d'un rejet"""
    if created:
        instance.virement.statut = 'rejete'
        instance.virement.save()