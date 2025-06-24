# urls
path('dashboard/delete/<int:id>', views.DashBoardDelete.as_view(), name='dashboard_delete')

# views
class DashBoardDelete(View):#  -----------------------------------------------------APAGAR
    def get_recipe(self, request, id):
        return get_object_or_404(RecipesModels, id=id, author=request.user)

    def redirect_dashboard(self):
        return redirect(reverse('authors:dashboard'))
    
    def post(self, request, id):
        recipe = self.get_recipe(request, id)
        recipe.delete()
        messages.success(request, 'Receita Apagada com Sucesso')
        
        return self.redirect_dashboard()
    
    
# html
'''

<form action="{% url 'authors:dashboard_delete' recipe.id %}" method="POST" style="display: inline-block;">
{% csrf_token %}
<button type="submit" style="background: none; border: none;">
<i class="fa-solid fa-trash" style="color: #db0f0f;"></i>
</button>
</form>

'''