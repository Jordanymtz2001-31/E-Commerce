def navbar_context(request):
    """Agrega la ruta actual al contexto para determinar enlaces activos en el navbar."""
    return {
        'current_page': request.path
    }