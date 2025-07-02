from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter

from users.views import UserViewSet
from addresses.views import AddressViewset
from books.views import BookViewSetAPI

router = SimpleRouter()
router.register('users', UserViewSet, basename='user-api')
router.register('addresses', AddressViewset, basename='address-api')
router.register('books', BookViewSetAPI, basename='book-api')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)