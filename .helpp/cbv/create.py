from django.views.generic import View
from core.models import RecipesModels, Category

from authors.forms import RegisterForm, LoginForms, AuthorRecipeForm, AuthorCreateRecipe

from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, reverse, get_object_or_404

from django.contrib import messages
from django.utils.text import slugify
import time


@method_decorator(
    login_required(
        login_url='authors:login',
        redirect_field_name='next',
    ),
    name='dispatch'
)
class DashBoardCreate(View):
    def render_page(self, request, form):
        context = {'forms': form}  
        return render(request, 'authors/pages/dash_board_create.html', context)

    def get(self, request):
        form = AuthorCreateRecipe()
        return self.render_page(request, form)

    def post(self, request):
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

        messages.error(request, 'Erro! Tente Novamente.')
        print(form.errors)

        return self.render_page(request, form)
    
    
class DashBoardDelete(View):
    def get_recipe(self, request, id):
        return get_object_or_404(RecipesModels, id=id, author=request.user)

    def redirect_dashboard(self):
        return redirect(reverse('authors:dashboard'))
    
    def post(self, request, id):
        recipe = self.get_recipe(request, id)
        recipe.delete()
        messages.success(request, 'Receita Apagada com Sucesso')
        
        return self.redirect_dashboard()