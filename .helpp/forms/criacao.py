# FORMS
class AuthorCreateRecipe(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._my_errors = defaultdict(list)
        
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
            'servings': forms.NumberInput(attrs={'min': 1, 'step': 1, 'class': 'form_input', 'placeholder': 'Serve Quantos?'}),
            'servings_unit': forms.TextInput(attrs={'type': 'text', 'class': 'form_input','id': 'nome', 'placeholder': 'Porcao', }),
            'preparation_steps': forms.Textarea(attrs={'name': 'mensagem', 'id': 'message', 'cols': '30', 'rows': '3', 'class': 'form_input message_input', 'style': 'background-color: rgb(149, 137, 137, 0.2);'}),
            'description': forms.Textarea(attrs={'name': 'mensagem', 'id': 'message', 'cols': '30', 'rows': '3', 'class': 'form_input message_input', 'style': 'background-color: rgb(149, 137, 137, 0.2);'}),
            'cover': forms.FileInput(),
            'preparation_time_unit': forms.Select(attrs={'type': 'text', 'class': 'form_input','id': 'nome'}, choices=(('Minutos', 'Minutos'), ('Horas', 'Horas'))),
        }
        
        category = forms.ModelChoiceField(
            queryset=Category.objects.all(),
            required=True,
            widget=forms.Select(attrs={'type': 'text', 'class': 'form_input','id': 'nome'})
        )
        

# VIEWS

def dashboard_create_recipe(request):
    form = AuthorCreateRecipe()
    
    if str(request.method) == 'POST':
        form = AuthorCreateRecipe(data=request.POST, files=request.FILES)
        
        if form.is_valid():
            recipe: RecipesModels = form.save(commit=False)
            recipe.author = request.user
            recipe.preparation_steps_is_html = False
            recipe.is_published = False
            recipe.slug = slugify(recipe.title)
            
            recipe.save()
            form = AuthorCreateRecipe()
            
            messages.success(request, 'Receita Criada com Sucesso!')
            return redirect(reverse('authors:CreateRecipeDashboard'))
            
        else:
            messages.error(request, 'Erro! Tente Novamente.')
            print(form.errors)
        
    context = {
        'forms': form,
    }    
    
    return render(request, 'authors/pages/dash_board_create.html', context=context)