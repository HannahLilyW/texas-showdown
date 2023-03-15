from django.urls import include, path
from rest_framework import routers
from texas_api import views
from texas.obtain_expiring_auth_token import ObtainExpiringAuthToken


router = routers.DefaultRouter()
router.register(r'games', views.GameViewSet)

urlpatterns = [
    path('create_account/', views.CreateAccountView.as_view()),
    path('login/', ObtainExpiringAuthToken.as_view()),
    path('logout/', views.LogOutView.as_view()),
    path('', include(router.urls)),
]
