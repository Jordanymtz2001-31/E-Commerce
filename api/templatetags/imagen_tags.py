from django import template

register = template.Library()


@register.filter
def safe_url(image_field, default=''):
    try:
        return image_field.url
    except (ValueError, AttributeError):
        return default
