class AuthorRecipeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_attr(self.fields.get('preparation_steps'), 'class', 'span-2')
        add_attr(self.fields.get('cover'), 'class', 'span-2')
        
        

class AuthorRecipeForm(forms.ModelForm):
    
    class Meta:
        model = RecipesModels
        fields = [
            'title', 'description', 'preparation_time',
            'preparation_time_unit', 'servings',
            'servings_unit', 'preparation_steps',
            'cover', 'category'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'type': 'text', 'class': 'form_input','id': 'nome', 'placeholder': 'Nome da Receita', }),
            'preparation_time': forms.NumberInput(attrs={'min': 1, 'step': 1, 'class': 'form_input', 'placeholder': 'Tempo de Preparação'}),
            'preparation_time_unit': forms.TextInput(attrs={'type': 'text', 'class': 'form_input','id': 'nome', 'placeholder': 'Minutos / Horas'}),
            'servings': forms.NumberInput(attrs={'min': 1, 'step': 1, 'class': 'form_input', 'placeholder': 'Serve Quantos?'}),
            'servings_unit': forms.TextInput(attrs={'type': 'text', 'class': 'form_input','id': 'nome', 'placeholder': 'Porcao', }),
            'preparation_steps': forms.Textarea(attrs={'name': 'mensagem', 'id': 'message', 'cols': '30', 'rows': '3', 'class': 'form_input message_input', 'style': 'background-color: rgb(149, 137, 137, 0.2);'}),
        }
        
        widgets = {
            'servings_unit': forms.Select(
                choices=(
                    ('Porções', 'Porções'),
                    ('Pedaços', 'Pedaços'),
                    ('Pessoas', 'Pessoas'),
                ),
            ),
            'preparation_time_unit': forms.Select(
                choices=(
                    ('Minutos', 'Minutos'),
                    ('Horas', 'Horas'),
                ),
            ),
        }