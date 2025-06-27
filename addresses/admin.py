from django.contrib import admin
from addresses.models import AddressModel
# Register your models here.

@admin.register(AddressModel)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'zip_code', 'street', 'neighborhood', 'city', 'state', 'is_primary'
    ]
    list_display_links = [
        'id', 'user', 'zip_code', 'street', 'neighborhood', 'city', 'state', 'is_primary'
    ]
    search_fields = [
        'id', 'user__username', 'user__email', 'user__first_name', 'zip_code', 'street', 'neighborhood',
        'city', 'state'
    ]
    search_help_text = "Busque por Username, Email ou Primeiro Nome do Usuário, CEP, Rua e Bairro, Cidade e Estado."

    list_filter = ['is_primary']
    list_per_page = 20
    ordering = ['-id']
    autocomplete_fields = ['user']
    list_select_related = ['user']