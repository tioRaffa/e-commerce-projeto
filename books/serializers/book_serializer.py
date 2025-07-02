from rest_framework import serializers
from books.models import AuthorModel, CategoryModel, BookModel
from django.core.exceptions import ValidationError 



class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorModel
        fields = [
            'id', 'name'
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = [
            'id', 'name'
        ]


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(read_only=True, many=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=AuthorModel.objects.all(),
        write_only=True,
        source='authors',
        many=True,
        help_text='ID do Autor'
    )

    categories = CategorySerializer(read_only=True, many=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=CategoryModel.objects.all(),
        write_only=True,
        source='categories',
        many=True,
        help_text='ID da categoria'
    )

    formatted_price = serializers.ReadOnlyField()
    is_ready_for_shipping = serializers.SerializerMethodField()

    class Meta:
        model = BookModel
        fields = [
            "id",
            "source",
            "google_books_id",
            "title",
            "slug",
            "authors",
            "author_ids",
            "publisher",
            "published_date",
            "description",
            "page_count",
            "categories",
            "category_ids",
            "isbn_13",
            "isbn_10",
            "thumbnail_url",
            "price",
            "formatted_price",
            "stock",
            "is_active",
            "weight_g",
            "height_cm",
            "width_cm",
            "length_cm",
            "is_ready_for_shipping",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            'slug', 'created_at', 'updated_at'
        ]

    def get_is_ready_for_shipping(self, obj: BookModel) -> bool:
        return obj.is_ready_for_shipping()

    def create(self, validated_data):
        author = validated_data.pop('authors', [])
        category = validated_data.pop('categories', [])
        book = BookModel.objects.create(**validated_data)
        
        try:
            book.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        if author:
            book.authors.set(author)
        if category:
            book.categories.set(category)
        return book
    
    def update(self, instance: BookModel, validated_data):
        author = validated_data.pop('authors', None)
        category = validated_data.pop('categories', None)

        instance = super().update(instance, validated_data)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        if author is not None:
            instance.authors.set(author)
        if category is not None:
            instance.categories.set(category)

        return instance