from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import ProfilUtilisateur, Virement, RejetVirement

class ProfilUtilisateurInline(admin.StackedInline):
    model = ProfilUtilisateur
    can_delete = False
    verbose_name_plural = 'Profil utilisateur'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfilUtilisateurInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_type_compte', 'get_quota_utilise')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profil__type_compte')
    
    def get_type_compte(self, obj):
        return obj.profil.get_type_compte_display() if hasattr(obj, 'profil') else 'Aucun profil'
    get_type_compte.short_description = 'Type de compte'
    
    def get_quota_utilise(self, obj):
        if hasattr(obj, 'profil'):
            return f"{obj.profil.quota_utilise}/{obj.profil.quota_maximum}"
        return 'Aucun profil'
    get_quota_utilise.short_description = 'Quota (utilisé/max)'

@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_compte', 'quota_utilise', 'quota_maximum', 'quota_restant', 'date_creation')
    list_filter = ('type_compte', 'date_creation')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('date_creation', 'date_modification')
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Configuration du compte', {
            'fields': ('type_compte', 'quota_utilise')
        }),
        ('Informations système', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['reinitialiser_quota', 'passer_en_premium', 'passer_en_standard']
    
    def reinitialiser_quota(self, request, queryset):
        updated = queryset.update(quota_utilise=0)
        self.message_user(request, f'{updated} quota(s) réinitialisé(s) avec succès.')
    reinitialiser_quota.short_description = "Réinitialiser le quota des utilisateurs sélectionnés"
    
    def passer_en_premium(self, request, queryset):
        updated = queryset.update(type_compte='premium')
        self.message_user(request, f'{updated} utilisateur(s) passé(s) en Premium.')
    passer_en_premium.short_description = "Passer en compte Premium"
    
    def passer_en_standard(self, request, queryset):
        updated = queryset.update(type_compte='standard')
        self.message_user(request, f'{updated} utilisateur(s) passé(s) en Standard.')
    passer_en_standard.short_description = "Passer en compte Standard"

@admin.register(Virement)
class VirementAdmin(admin.ModelAdmin):
    list_display = ('id', 'beneficiaire_nom_complet', 'donneur_ordre_nom_complet', 'montant_formate', 'statut', 'banque_emettrice', 'date_creation')
    list_filter = ('statut', 'banque_emettrice', 'devise', 'langue', 'date_creation')
    search_fields = ('beneficiaire_nom', 'beneficiaire_prenom', 'donneur_ordre_nom', 'donneur_ordre_prenom', 'beneficiaire_email')
    readonly_fields = ('id', 'date_creation', 'date_modification')
    
    fieldsets = (
        ('Informations système', {
            'fields': ('id', 'utilisateur', 'statut', 'date_creation', 'date_modification')
        }),
        ('Bénéficiaire', {
            'fields': ('beneficiaire_nom', 'beneficiaire_prenom', 'beneficiaire_email', 'beneficiaire_compte', 'numero_bic')
        }),
        ('Donneur d\'ordre', {
            'fields': ('donneur_ordre_nom', 'donneur_ordre_prenom', 'donneur_ordre_compte')
        }),
        ('Virement', {
            'fields': ('montant', 'devise', 'banque_emettrice', 'langue')
        }),
        ('Fichiers', {
            'fields': ('pdf_initiation',),
            'classes': ('collapse',)
        }),
    )

@admin.register(RejetVirement)
class RejetVirementAdmin(admin.ModelAdmin):
    list_display = ('virement', 'frais_formates', 'date_rejet')
    list_filter = ('date_rejet', 'virement__devise', 'virement__banque_emettrice')
    search_fields = ('virement__beneficiaire_nom', 'virement__beneficiaire_prenom', 'motif_rejet')
    readonly_fields = ('date_rejet',)
    
    fieldsets = (
        ('Virement concerné', {
            'fields': ('virement',)
        }),
        ('Détails du rejet', {
            'fields': ('frais_redirection', 'motif_rejet', 'date_rejet')
        }),
        ('Fichiers', {
            'fields': ('pdf_rejet',),
            'classes': ('collapse',)
        }),
    )

# Re-registration de User avec le nouveau admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Configuration du site admin
admin.site.site_header = "Administration BOITE-VIRO"
admin.site.site_title = "BOITE-VIRO Admin"
admin.site.index_title = "Gestion des virements bancaires"