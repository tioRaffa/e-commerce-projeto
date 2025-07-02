from django.contrib import admin
from books.models import AuthorModel, BookModel, CategoryModel

@admin.register(AuthorModel)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('-id',)

@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('-id',)

@admin.register(BookModel)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'get_authors',
        'get_categories',
        'publisher',
        'is_active',
        'created_at',
    )
    list_display_links = ('id', 'title')
    search_fields = (
        'id',
        'google_books_id',
        'title',
        'authors__name',
        'categories__name',
        'publisher',
        'isbn_13',
        'isbn_10',
    )
    search_help_text = 'Search by ID, Google Books ID, title, author, category, publisher, or ISBN'
    list_filter = ('is_active', 'created_at', 'source')
    list_editable = ('is_active',)
    list_per_page = 15
    ordering = ('-created_at',)
    filter_horizontal = ('authors', 'categories')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('authors', 'categories')

    def get_authors(self, obj):
        return ", ".join([author.name for author in obj.authors.all()])
    get_authors.short_description = "Authors"

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.categories.all()])
    get_categories.short_description = "Categories"
    