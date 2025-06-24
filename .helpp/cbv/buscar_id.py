class RecipeListViewBase(ListView):
    model = RecipesModels
    template_name = 'receitas/pages/home.html'
    context_object_name = 'dados'
    paginate_by = None
    ordering = '-id'
    
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(is_published=True)

        return queryset
        
    
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        page_obj, pagination_range = make_pagination(self.request, ctx.get('dados'), PER_PAGE, 4)
        
        ctx.update({
            'dados': page_obj,
            'pagination_range': pagination_range,
            'is_detail_page': False
        })
                
        
        return ctx


class Category(RecipeListViewBase):
    template_name = 'receitas/pages/category.html'
    
    # -----------------------------
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        queryset = queryset.filter(
            category__id=self.kwargs.get('id')# !!!!!!!!!!!!!!!!!!!!
        )
        return queryset
    # -----------------------------


    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        page_obj, pagination_range = make_pagination(request, ctx.get('dados'), PER_PAGE, 4)
        title = self.get_queryset(*args, **kwargs)
        
        ctx.update({
            'dados': page_obj,
            'pagination_range': pagination_range,
            'is_category_page': True,
            'is_detail_page': False,
            'title': f'{title[0].category.name}'
            })        
        
        return ctx
    
    
# fuction view
def category(request, id):
    receitas = get_list_or_404(RecipesModels.objects.filter(
        category__id=id, is_published=True).order_by('-id'))

    page_obj, pagination_range = make_pagination(request, receitas, PER_PAGE, 4)

    context = {
        'dados': page_obj,
        'pagination_range': pagination_range,
        'is_category_page': True,
        'is_detail_page': False,
        'title': f'{receitas[0].category.name}'
    }

    return render(request, 'receitas/pages/category.html', context)