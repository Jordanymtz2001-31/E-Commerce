"""
Configuración de pruebas para Django.
Usa SQLite en memoria para mayor velocidad.
"""
from ecommerce.settings import *

# Sobrescribir base de datos para tests (SQLite en memoria)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}