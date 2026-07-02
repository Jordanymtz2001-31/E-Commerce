from django import template

register = template.Library()


@register.filter
def safe_url(image_field, default=''):
    """
    Filtro para usar en templates al obtener la URL de un ImageField.
    
    Django lanza ValueError cuando el archivo físico no existe en el disco aunque
    la base de datos tenga la ruta. Esto ocurre comúnmente al desplegar a producción
    (Seenode) donde las imágenes locales pueden no estar presentes.
    
    En lugar de que el template explote con un error 500, este filtro captura la
    excepción y retorna el string vacío (o un valor por defecto), permitiendo que
    la página se renderice sin imágenes o con una imagen placeholder.
    
    Uso en template:
        {{ field|safe_url }} --> Si no hay archivo, retorna string vacío ''
        {{ field|safe_url:'https://ejemplo.com/placeholder.jpg' }} --> Si no hay archivo, retorna placeholder
    
    -- SI la imagen existe --> retorna la URL de la imagen
    -- SI no existe --> captura la excepción y retorna default(string vacío)
    -- SI el campo está vacío --> retorna default
    """
    try:
        return image_field.url
    except (ValueError, AttributeError):
        return default

