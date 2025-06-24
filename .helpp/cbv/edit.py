
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
class DashBoardRecipeEdit(View):
    def get_recipe(self, id=None):
        if id is not None:
            author = self.request.user
            recipe = get_object_or_404(RecipesModels, id=id, author=author)
        return recipe
            
            
    def render_recipe(self, form, recipe):
        context = {
            'recipes': recipe,
            'forms': form,
            'categorys': Category.objects.all()
        }
        
        return render(self.request, 'authors/pages/dash_board_editor.html', context=context)
    
    
    def get(self, request, id=None):
        recipe = self.get_recipe(id)
        form = AuthorRecipeForm(instance=recipe)
        
        return self.render_recipe(form=form, recipe=recipe)
        
    
    def post(self, request, id=None):
        recipe = self.get_recipe(id)
        
        form = AuthorRecipeForm(
            data=request.POST or None,
            files=request.FILES or None,
            instance=recipe
        )
            
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = self.request.user
            recipe.preparation_steps_is_html = False
            recipe.is_published = False
            recipe.category = Category.objects.get(id=recipe.category.id)

            recipe.save()
            messages.success(request, 'Alteração concluida com SUCESSO!')
            return redirect(reverse('authors:dashboard'))
                
        else:
            messages.error(request, f'ERRO, Tente novamente! ')
            print(form.errors)
            form = AuthorRecipeForm()
            
            
        return self.render_recipe(form=form, recipe=recipe)