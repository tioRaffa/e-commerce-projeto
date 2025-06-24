from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from courses.models import CourseModels # type: ignore
from courses.serializers import CourseSerializer, ReviewSerializer # type: ignore


IMPORTANTE = True
'''

def queryset() --------> DENTRO DA CLASSE model-view-set
    
    self.kwargs -- PARA BUSCAR \_ ID / PK _/ O OBJETO


'''

self.request.query_params   # PARA BUSCAR \ PARAMETROS DA URI /                   # type: ignore
        
        def get_queryset(self): # type: ignore
            qs = super().get_queryset()

            category_id = self.request.query_params.get('category_id', '')

            if category_id != '' and category_id.isnumeric():
                qs = qs.filter(category_id=category_id)

            return qs


class CoursesApiViewSets(viewsets.ModelViewSet): # type: ignore
    queryset = CourseModels.objects.all()
    serializer_class = CourseSerializer


    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):

        course = self.get_object()
        serializer = ReviewSerializer(course.reviews.all(), many=True)
        
        return Response(serializer.data)