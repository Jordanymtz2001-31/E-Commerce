from .models import Cliente, User
from django.db import transaction
from .models import Cliente

# Creamos el servicio para manejar la logica de negocio relacionada con el cliente, en este caso el registro del cliente, el cual se encargará de crear el usuario y el cliente en la base de datos
class CLienteService:
    
    #Creamos un metodo estatico por que no necesitamos instanciar la clase para usarlo, ademas recibe un diccionario con los datos del formulario y devuelve un objeto cliente
    @staticmethod
    def registrar_cliente(datos: dict) -> Cliente:
        
        """ 
        Iniciamos la transaccion en caso de que ocurra un error en alguna de las operaciones, se revierta todo lo realizado hasta el momento
        Esto es importante para mantener la integridad de la base de datos, ya que si ocurre un error al crear el cliente, no queremos que se cree el usuario sin el cliente asociado o viceversa
        Es decir que si se vrea el User correctamente pero ocurre un error al crear el Cliente, se revierta la creacion del User para evitar tener un usuario sin cliente asociado
        """
        
        with transaction.atomic():
        
            # Creamos el usuario
            user = User.objects.create_user(
                username=datos['username'],
                password=datos['password1'],
                email=datos['email']
            )
            
            # Creamos el cliente asociado al usuario
            return Cliente.objects.create(
                usuario=user,
                telefono=datos['telefono'],
                direccion=datos['direccion']
            )