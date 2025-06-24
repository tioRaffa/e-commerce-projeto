class Search(RecipeListViewBase):
    template_name = 'receitas/pages/search.html'
    
    
    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        
        search_term = self.request.GET.get('q', '').strip()
        queryset = queryset.filter(
            Q(
            Q(title__icontains=search_term) | 
            Q(category__name__icontains=search_term),
        ),
        is_published=True
        )
        
        return queryset
    
    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        page_obj, pagination_range = make_pagination(self.request, ctx.get('dados'), PER_PAGE, 4)
        search_term = self.request.GET.get('q', '').strip()
        
        ctx.update({
            'page_title': f'Search for "{search_term}"',
            'search_term': search_term,
            'dados': page_obj,
            'pagination_range': pagination_range,
            'add_url_query': f'&q={search_term}',
        })
        
        return ctx