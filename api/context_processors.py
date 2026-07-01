from django.conf import settings


def navbar_context(request):
    """Agrega variables globales al contexto de todas las templates."""
    return {
        'current_page': request.path, # Esto es para mostrar el active en la navbar
        'STRIPE_ENABLED': settings.STRIPE_ENABLED, # Esto es para mostrar el boton de pagar con stripe
        'APP_VERSION': settings.VERSION, # Esto es para mostrar la version
    }