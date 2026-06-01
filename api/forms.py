#Esta clase hereda de UserCrearionForm que es un formulario que incluye todos los campos
# del sistema de usuarios de django y la usaremos para personalizar el formulario de registro.
# Es decir que seleccionaramos los campos del modelo se user y agregaremos nuestros campos de nuestro modelo Cliente
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Aqui registramos nuestro formulario (Dtos)
class RegistroForm(UserCreationForm):
    telefono = forms.CharField(max_length=15, required=True) 
    direccion = forms.CharField(widget = forms.Textarea, required=False)

    # Agregamos los campos al formulario
    class Meta:
        model = User
        
        # Solo oncluimos campos que No son contraseñas
        # UserCreationForm ya incluye los campos de contraseña en la interfaz, por lo que no es necesario incluirlos aquí
        fields = ['username', 'email']
        
    def save(self, commit=True):
        # Sobreescribimos el método para evitar que el formularcion guarde directamente el usuario en la base de datos
        # Ahora el control total de la persistencia lo tiene el Service, el cual se encargará de guardar el usuario y el cliente en la base de datos
        
        if not commit:
            raise ValueError("Para guardar, utliza ClienteService.registrar_cliente()")
        
    #Aqui me falta agregar estilos a los campos para que se se pasen al html o al formulario
    #Para que solo en el html solo ientrada sobre este formulario junto con sus estilos