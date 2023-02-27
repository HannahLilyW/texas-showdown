from django.urls import include, path
from rest_framework import routers
from texas_api import views


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls))
]
