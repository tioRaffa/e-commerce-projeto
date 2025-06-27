from django.contrib import admin
from .models import ProfileModel
# Register your models here.

@admin.register(ProfileModel)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'cpf', 'birth_date', 'email_verified']
    list_display_links = ['id', 'user', 'cpf']
    
    search_fields = ['id', 'user__username', 'user__email', 'user__first_name','cpf', ]
    search_help_text = "Busque por CPF, username, email ou primeiro nome do usuário."
   
    list_filter = ['birth_date', 'email_verified']
    list_per_page = 15
    ordering = ['-id']
    autocomplete_fields = ['user']
    list_select_related = ['user']