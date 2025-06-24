from django.views.generic import FormView
from core.forms import ContactForm
from django.urls import reverse_lazy

from django.core.mail import send_mail
from django.contrib import messages

class ContactPage(FormView):
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy("places:contact")
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context.update({
            'form': self.get_form()
        })
        return context
    
    def form_valid(self, form, *args, **kwargs):
        form.send_mail()
        messages.success(self.request, 'Email enviado com Sucesso!')
        
        return super().form_valid(form, *args, **kwargs)
    
    def form_invalid(self, form, *args, **kwargs):
        response = super().form_invalid(form, *args, **kwargs)
        messages.error(self.request, 'Erro ao enviar Email!')
        
        return response
    