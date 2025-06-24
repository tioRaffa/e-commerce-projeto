

def MyView(request):
    recipes = get_list_or_404(RecipesModels.objects.filter(
        is_published=True).order_by('-id'))

    __________________________________
    
    page_obj, pagination_range = make_pagination(request, recipes, 9, 4)
    ___________________________________
    
    context = {
        'dados': page_obj,
        'is_detail_page': False,
        'pagination_range': pagination_range
    }

    return render(request, 'receitas/pages/home.html', context)