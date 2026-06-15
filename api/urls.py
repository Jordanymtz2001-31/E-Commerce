from django.urls import path
from . import views
  #Estas rutas te direccinan a la pagina web
urlpatterns = [
  
    path('', views.tienda_view, name='tienda'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('productList/', views.productos_view, name='productList'),
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('producto/<int:pk>/resena/', views.crear_resena, name='crear_resena'),
    path('punto_venta/', views.punto_venta_view, name='punto_venta'),
    path('eventos/', views.eventos_view, name='eventos'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('pedido/<int:pk>/pago-exitoso/', views.pago_exitoso_view, name='pago_exitoso'),
    path('pedido/<int:pk>/confirmacion/', views.pedido_confirmado_view, name='pedido_confirmado'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),
]
