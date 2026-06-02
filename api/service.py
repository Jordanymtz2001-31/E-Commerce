from .models import Cliente, Resena
from django.contrib.auth.models import User
from django.db import transaction


class ClienteService:
    """
    Servicio para la lógica de negocio relacionada con Cliente.

    SRP: Separamos la lógica de negocio (creación de User + Cliente en una
    transacción) de la capa de presentación (vistas) y de persistencia (modelos).
    DIP: Las vistas dependen de esta abstracción en vez de llamar directamente
    a Cliente.objects.create(), facilitando cambios futuros en la lógica.
    """

    @staticmethod
    def registrar(datos: dict) -> Cliente:
        """
        Crea un User y su Cliente asociado en una sola transacción atómica.

        Por qué transaction.atomic(): si falla la creación del Cliente después
        de haber creado el User, se revierte todo para evitar un User huérfano
        sin perfil de Cliente.
        """
        with transaction.atomic():
            user = User.objects.create_user(
                username=datos['username'],
                password=datos['password1'],
                email=datos['email']
            )

            return Cliente.objects.create(
                usuario=user,
                telefono=datos['telefono'],
                direccion=datos['direccion']
            )


class ResenaService:
    """
    Servicio para la lógica de negocio relacionada con Reseñas.

    SRP: Aísla la validación y creación de reseñas, manteniendo las vistas
    delgadas y facilitando el testing unitario sin HTTP.
    """

    @staticmethod
    def crear(producto, usuario, estrellas: int, comentario: str) -> Resena:
        if estrellas < 1 or estrellas > 5:
            raise ValueError("Las estrellas deben estar entre 1 y 5")

        return Resena.objects.create(
            producto=producto,
            usuario=usuario,
            estrellas=estrellas,
            comentario=comentario.strip()
        )
