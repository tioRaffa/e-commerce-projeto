from rest_framework import serializers
from books.models import AuthorModel, CategoryModel, BookModel


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
    categories = CategorySerializer(read_only=True, many=True)

    