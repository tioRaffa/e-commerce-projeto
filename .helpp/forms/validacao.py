from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib import messages
import re


def strong_password(password):
    regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$')
    
    if not regex.match(password):
        raise ValidationError('erro', code='invalide')

txt = 'ex: Ab12345678'
class RegisterForm(forms.ModelForm):
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-box', 'placeholder': f'{txt}', 'required': 'True'}),
        validators=[strong_password]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-box', 'placeholder': 'Confirme sua Senha', 'required': 'True'}),
    )
    username = forms.CharField(
        max_length=50,
        min_length=2,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'input-box',
            'placeholder': 'Digite seu Nome de Usuário',
        })
    )
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-box', 'placeholder': 'Digite seu Nome', 'required': 'True'}),
            'last_name': forms.TextInput(attrs={'class': 'input-box', 'placeholder': 'Digite seu Último Nome','required': 'True'}),
            'email': forms.EmailInput(attrs={'class': 'input-box', 'placeholder': 'ex: exemploemail@gmail.com','required': 'True'}),
        }
        
    
    def clean_first_name(self):
        data = self.cleaned_data.get('first_name')
        
        if data[0].islower():
            raise ValidationError('A primeira letra deve ser Maiscula')

        return data
       
    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        
        
        if password != password2:
            raise ValidationError('Erro na confirmaçao, Digite Novamente!')