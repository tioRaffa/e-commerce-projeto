from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from ..models import Recipe, Category, Tag # type: ignore
from ..serializer import RecipesSerializer, CategorySerializer, TagSerializer # type: ignore
from django.shortcuts import get_object_or_404



@api_view(http_method_names=['get', 'post'])
def recipe_api_list(request):

    if request.method == 'GET':

        recipe = Recipe.objects.select_related(
            'category', 'author'
            ).prefetch_related(
                'tags'
                ).all().order_by('id')

        serializer = RecipesSerializer(instance=recipe, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = RecipesSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        
        if request.user.is_authenticated:
            serializer.save(author=request.user)
        else:
            serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(http_method_names=['get', 'patch', 'delete'])
def recipe_api_detail(request, pk):

    recipe = Recipe.objects.select_related(
        'category', 'author'
    ).prefetch_related(
        'tags'
    ).filter(
        pk=pk
    ).first()

    if request.method == 'GET':
        serializer = RecipesSerializer(instance=recipe)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = RecipesSerializer(
            instance=recipe, 
            data=request.data, 
            partial=True, 
            )
        
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)

    elif request.method == 'DELETE':
        recipe.delete()
        return Response(status=status.HTTP_418_IM_A_TEAPOT)



@api_view(http_method_names=['get', 'post'])
def category_api_list(request):

    if request.method == 'GET':
        category = Category.objects.all()

        serializer = CategorySerializer(
            instance=category,
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
