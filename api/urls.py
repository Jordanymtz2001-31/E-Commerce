from django.urls import path
from . import views

urlpatterns = [
    path('', views.tienda_view, name='tienda'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('productList/', views.productos_view, name='productList'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('producto/<int:pk>/resena/', views.crear_resena, name='crear_resena'),
]
