from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsViewSet, SourceViewSet

router = DefaultRouter()
router.register(r'news', NewsViewSet)
router.register(r'sources', SourceViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]