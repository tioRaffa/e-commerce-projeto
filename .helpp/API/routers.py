

# URL APP
    from rest_framework.routers import SimpleRouter                             # type: ignore
   
    router = SimpleRouter()
    router.register('courses', CoursesApiViewSets)                              # type: ignore


# URL PRINCIPAL
    from 'NOME DO APP'.urls import router                                       # type: ignore

    urlpatterns = [
        path('auth/', include('rest_framework.urls')),                          # type: ignore
        path('api/v1/', include(router.urls)),                                  # type: ignore
    ]                                                                           # type: ignore