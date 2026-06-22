from django.core.exceptions import ValidationError

#Metodo para validad el tamaño de la imagen
def validar_tamano_imagen(archivo):
    max_mb = 5
    if archivo.size > max_mb * 1024 * 1024:
        raise ValidationError(
            f'La imagen no puede superar los {max_mb} MB. '
            f'El archivo subido pesa {archivo.size / 1024 / 1024:.1f} MB.'
        )
