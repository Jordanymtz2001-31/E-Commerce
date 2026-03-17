import os
from pathlib import Path
from dotenv import load_dotenv

# ----------------------------------------------------
# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------
# Determinar el entorno: Desarrollo o Producción
# ----------------------------------------------------
## En PythonAnyWhere definir DJANGO_PRODUCTION = 1 en consola o WSGI
IS_PRODUCTION = os.environ.get('DJANGO_PRODUCTION') == '1'

# ----------------------------------------------------
# Cargar variables de entorno
# ----------------------------------------------------
# Cargar el archivo de entorno correspondiente dependiendo del entorno o caso, asi podemos estar en desarrollo o en produccion 
if not IS_PRODUCTION:
    ENV_FILE = Path(__file__).resolve().parent.parent / '.env.development'
    # Mostrar qué archivo .env se está cargando para depuración
    print(f"[Django settings] Cargando variables de entorno desde: {ENV_FILE}")
    load_dotenv(ENV_FILE) # Cargar el archivo de entorno

# ----------------------------------------------------
# Seguridad y depuración, les pasamos los valores de entorno
# ----------------------------------------------------
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'   
# ESTO NO EXPLOTA NUNCA
allowed_hosts_str = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',')]

# Validación para variables de base de datos obligatorias
if not os.getenv('DB_ENGINE'):
    raise Exception("La variable de entorno DB_ENGINE no está definida. Debe ser 'django.db.backends.mysql', 'django.db.backends.sqlite3', etc.")
if not os.getenv('DB_NAME'):
    raise Exception("La variable de entorno DB_NAME no está definida. Debe ser el nombre de la base de datos o el archivo para sqlite3.")

# CSRF para producción (Seenode)
CSRF_TRUSTED_ORIGINS = [
    'https://web-kzazb695kh3b.up-de-fra1-k8s-1.apps.run-on-seenode.com',
    'http://web-kzazb695kh3b.up-de-fra1-k8s-1.apps.run-on-seenode.com',
]

# ----------------------------------------------------
# Aplicaciones instaladas
# ----------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'widget_tweaks' # Libreria súper útil para estilizar formularios Django con Bootstrap sin escribir HTML manual
    
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' # Esto es para evitar un error

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', #WhiteNoise se integra con Django
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

# Para producción, usa PostgreSQL/MySQL. Ejemplo de PostgreSQL:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('POSTGRES_DB', 'nombre_db'),
#         'USER': os.getenv('POSTGRES_USER', 'usuario'),
#         'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'contraseña'),
#         'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
#         'PORT': os.getenv('POSTGRES_PORT', '5432'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER', ''),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', ''),
        'PORT': os.getenv('DB_PORT', ''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
STATIC_URL = 'static/'
#STATICFILES_DIRS = [BASE_DIR / 'static'] # Carpeta para archivos estaticos para desarrollo
STATIC_ROOT = BASE_DIR / 'staticfiles' # Carpeta para archivos estaticos para produccion, Django se encarga de crearla si no existe
                                        # Con py manage.py collectstatic se crean los archivos estaticos

# Configuracion para subir archivos
if IS_PRODUCTION:
    # Producción → Cloudflare R2
    MEDIA_URL = f"https://{os.environ.get('R2_PUBLIC_URL')}/"
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "access_key": os.environ.get("R2_ACCESS_KEY_ID"),
                "secret_key": os.environ.get("R2_SECRET_ACCESS_KEY"),
                "bucket_name": os.environ.get("R2_BUCKET_NAME"),
                "endpoint_url": os.environ.get("R2_ENDPOINT_URL"),
                "region_name": "auto",
                "default_acl": "public-read",
                "querystring_auth": False,
                "custom_domain": os.environ.get("R2_PUBLIC_URL"),
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
else:
    # Desarrollo → archivos locales
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {
                "location": MEDIA_ROOT,
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# Logging para producción
#Sirve para guardar errores y advertencias en un archivo (django.log). asi puedo verlos en produccion
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': True,
        },
    },
}

