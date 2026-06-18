from django.conf import settings


def navbar_context(request):
    """Agrega variables globales al contexto de todas las templates."""
    return {
        'current_page': request.path, # Esto es para mostrar el menu activo
        'STRIPE_ENABLED': settings.STRIPE_ENABLED, # Para mostrar el botón de pagar con Stripe
    }