from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Categorie, Fournisseur, Produit, Client,
    Entrepot, StockEntrepot, MouvementStock, Vente,
    LigneDeVente, TransfertEntrepot, LigneTransfert, AuditLog
)
from django.utils.html import format_html


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'role', 'telephone', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'telephone', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {
         'fields': ('username', 'birthday', 'telephone', 'adresse')}),
        ('Rôle et permissions', {'fields': (
            'role', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active')}
         ),
    )


class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'created_by', 'created_at', 'nombre_produits')
    list_filter = ('created_at',)
    search_fields = ('nom', 'description')
    readonly_fields = ('created_at', 'nombre_produits')


class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'telephone',
                    'email', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('nom', 'contact', 'telephone', 'email')
    readonly_fields = ('created_at',)


class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'categorie', 'prix_vente',
                    'stock_actuel', 'stock_status')
    list_filter = ('categorie', 'fournisseur', 'created_at')
    search_fields = ('nom', 'code', 'description')
    readonly_fields = ('created_at', 'stock_actuel', 'stock_reserve')

    def stock_status(self, obj):
        stock = obj.stock_actuel()
        if stock <= 0:
            return format_html('<span style="color: red; font-weight: bold;">Rupture</span>')
        elif stock <= obj.stock_alerte:
            return format_html('<span style="color: orange; font-weight: bold;">Faible</span>')
        else:
            return format_html('<span style="color: green;">Normal</span>')
    stock_status.short_description = 'Statut Stock'


class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_client', 'telephone',
                    'email', 'created_by', 'created_at')
    list_filter = ('type_client', 'created_at')
    search_fields = ('nom', 'telephone', 'email')
    readonly_fields = ('created_at',)


class EntrepotAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'responsable', 'actif',
                    'produits_count', 'stock_total_valeur')
    list_filter = ('actif', 'created_at')
    search_fields = ('nom', 'adresse', 'telephone')
    readonly_fields = ('created_at', 'stock_total_valeur', 'produits_count')


class StockEntrepotInline(admin.TabularInline):
    model = StockEntrepot
    extra = 1
    readonly_fields = ('quantite_disponible', 'en_rupture', 'stock_faible')


class StockEntrepotAdmin(admin.ModelAdmin):
    list_display = ('produit', 'entrepot', 'quantite',
                    'quantite_reservee', 'quantite_disponible', 'stock_status')
    list_filter = ('entrepot', 'produit__categorie')
    search_fields = ('produit__nom', 'produit__code', 'emplacement')

    def stock_status(self, obj):
        if obj.en_rupture:
            return format_html('<span style="color: red; font-weight: bold;">Rupture</span>')
        elif obj.stock_faible:
            return format_html('<span style="color: orange; font-weight: bold;">Faible</span>')
        else:
            return format_html('<span style="color: green;">Normal</span>')
    stock_status.short_description = 'Statut'


class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'type_mouvement', 'quantite',
                    'entrepot', 'created_by', 'created_at')
    list_filter = ('type_mouvement', 'entrepot', 'created_at')
    search_fields = ('produit__nom', 'motif')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


class LigneDeVenteInline(admin.TabularInline):
    model = LigneDeVente
    extra = 1
    readonly_fields = ('sous_total', 'stock_preleve')


class VenteAdmin(admin.ModelAdmin):
    list_display = ('numero_vente', 'client', 'statut',
                    'montant_total', 'created_by', 'created_at')
    list_filter = ('statut', 'created_at')
    search_fields = ('numero_vente', 'client__nom')
    readonly_fields = ('created_at', 'montant_total')
    inlines = [LigneDeVenteInline]
    actions = ['confirmer_ventes', 'annuler_ventes']

    def confirmer_ventes(self, request, queryset):
        for vente in queryset.filter(statut='brouillon'):
            vente.confirmer_vente()
        self.message_user(request, f"{queryset.count()} ventes confirmées.")
    confirmer_ventes.short_description = "Confirmer les ventes sélectionnées"

    def annuler_ventes(self, request, queryset):
        updated = queryset.update(statut='annulee')
        self.message_user(request, f"{updated} ventes annulées.")
    annuler_ventes.short_description = "Annuler les ventes sélectionnées"


class LigneDeVenteAdmin(admin.ModelAdmin):
    list_display = ('vente', 'produit', 'entrepot', 'quantite',
                    'prix_unitaire', 'sous_total', 'stock_preleve')
    list_filter = ('entrepot', 'stock_preleve')
    search_fields = ('vente__numero_vente', 'produit__nom')
    readonly_fields = ('sous_total',)


class LigneTransfertInline(admin.TabularInline):
    model = LigneTransfert
    extra = 1


class TransfertEntrepotAdmin(admin.ModelAdmin):
    list_display = ('reference', 'entrepot_source',
                    'entrepot_destination', 'statut', 'created_by', 'created_at')
    list_filter = ('statut', 'created_at')
    search_fields = ('reference', 'motif')
    readonly_fields = ('created_at', 'confirme_at')
    inlines = [LigneTransfertInline]
    actions = ['confirmer_transferts', 'annuler_transferts']

    def confirmer_transferts(self, request, queryset):
        for transfert in queryset.filter(statut='brouillon'):
            transfert.confirmer_transfert()
        self.message_user(request, f"{queryset.count()} transferts confirmés.")
    confirmer_transferts.short_description = "Confirmer les transferts sélectionnés"

    def annuler_transferts(self, request, queryset):
        updated = queryset.update(statut='annule')
        self.message_user(request, f"{updated} transferts annulés.")
    annuler_transferts.short_description = "Annuler les transferts sélectionnés"


class LigneTransfertAdmin(admin.ModelAdmin):
    list_display = ('transfert', 'produit', 'quantite')
    list_filter = ('transfert__entrepot_source',
                   'transfert__entrepot_destination')
    search_fields = ('produit__nom', 'transfert__reference')


class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'modele', 'objet_id', 'created_at')
    list_filter = ('action', 'modele', 'created_at')
    search_fields = ('user__email', 'modele', 'details')
    readonly_fields = ('user', 'action', 'modele',
                       'objet_id', 'details', 'created_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Enregistrement des modèles dans l'admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Fournisseur, FournisseurAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Entrepot, EntrepotAdmin)
admin.site.register(StockEntrepot, StockEntrepotAdmin)
admin.site.register(MouvementStock, MouvementStockAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(LigneDeVente, LigneDeVenteAdmin)
admin.site.register(TransfertEntrepot, TransfertEntrepotAdmin)
admin.site.register(LigneTransfert, LigneTransfertAdmin)
admin.site.register(AuditLog, AuditLogAdmin)

# Configuration de l'admin
admin.site.site_header = "Administration du Système de Gestion de Stock"
admin.site.site_title = "Gestion de Stock"
admin.site.index_title = "Tableau de bord"
