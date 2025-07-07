from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .author_model import AuthorModel
from .category_model import CategoryModel

class BookModel(models.Model):

    # cadastro via API ou manual
    SOURCE_CHOICES = [
        ('manual', 'MANUAL'),
        ('google_bookS', 'GOOGLE_BOOKS')
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='manual', verbose_name='fonte')

    # API do Google
    google_books_id = models.CharField(max_length=20, unique=True, verbose_name='ID Google Books', null=True, blank=True)
    title = models.CharField(max_length=150, verbose_name='Titulo do Livro')
    authors = models.ManyToManyField(AuthorModel, related_name='author_books', verbose_name='Autores')
    categories = models.ManyToManyField(CategoryModel, related_name='category_books', verbose_name='Categorias')
    publisher = models.CharField(max_length=500, verbose_name='Editora', null=True, blank=True)
    published_date = models.CharField(max_length=20, verbose_name='Data de Publicação', blank=True, null=True)
    description = models.TextField(null=True, blank=True, verbose_name='Descrição')
    page_count = models.PositiveIntegerField(verbose_name='Numeros de Paginas', null=True, blank=True)

    isbn_13 = models.CharField(max_length=13, null=True, blank=True, unique=True, verbose_name="ISBN-13")
    isbn_10 = models.CharField(max_length=10, null=True, blank=True, unique=True, verbose_name="ISBN-10")
    thumbnail_url = models.URLField(max_length=300, null=True, blank=True, verbose_name="URL da Capa")


    slug = models.SlugField(max_length=250, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Preço - R$', validators=[MinValueValidator(0)],)
    stock = models.PositiveIntegerField(default=0, verbose_name='Quantidade em Estoque')
    is_active = models.BooleanField(default=False, verbose_name='Ativo na Loja')

    # FRETE
    weight_g = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Peso (g)")
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Altura (cm)")
    width_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Largura (cm)")
    length_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Comprimento (cm)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["isbn_13"]),
            models.Index(fields=["google_books_id"]),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    def is_ready_for_shipping(self):
        return all([
            self.weight_g is not None and self.weight_g > 0,
            self.height_cm is not None and self.height_cm > 0,
            self.width_cm is not None and self.width_cm > 0,
            self.length_cm is not None and self.length_cm > 0,
        ])
    
    def clean(self):
        if self.price is not None and self.price <= 0:
            raise ValidationError({
                "price": "O preço se definido, deve ser maior que zero!"
            })
        
        if self.is_active and self.price is not None and not self.is_ready_for_shipping():
            raise ValidationError(
                "Um livro ativo e com preço deve ter todas as informações de peso e dimensões para o cálculo do frete!"
            )
        
    @property
    def formatted_price(self):
        return f"R$ {self.price:.2f}" if self.price else "Preço ainda não definido"