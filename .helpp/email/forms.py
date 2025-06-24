from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from django.core.mail import EmailMessage
from django import forms

def validate_custom_mail(value):
    if not value.endswith('@gmail.com'):
        raise ValidationError(
            'Use um email validos, ex:. seuemail@gmail.com'
        )


class ContactForm(forms.Form):
    name = forms.CharField(
        label='name',
        max_length=100,
        widget=forms.TextInput()
    )
    
    email = forms.EmailField(
        label='email',
        max_length=100,
        validators=[EmailValidator(), validate_custom_mail],
        widget=forms.EmailInput(),
        error_messages={'required': 'Informe um e-mail válido.'}
        
    )
    
    subject = forms.CharField(
        label='subject',
        max_length=200,
        widget=forms.TextInput()
    )
    
    message = forms.CharField(
        label='message',
        widget=forms.Textarea()
    )


    def send_mail(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        
        content = f'Nome: {name}\nEmail: {email}\nAssunto: {subject}\nMensagem: {message}'
        
        try:
            mail = EmailMessage(
                subject=subject,
                body=content,
                from_email=email,
                to=['rafaelmuniz200@gmail.com', ],
                headers={'Reply-To': email},
            )
            
            mail.send()
        except Exception as e:
            print(f'Erro ->, {e}')
            raise ValidationError(
                'Erro ao enviar o Email'
            )