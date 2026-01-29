#Esta clase hereda de UserCrearionForm que es un formulario que incluye todos los campos
# del sistema de usuarios de django y la usaremos para personalizar el formulario de registro.
# Es decir que seleccionaramos los campos del modelo se user y agregaremos nuestros campos de nuestro modelo Cliente
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Aqui registramos nuestro formulario
class RegistroForm(UserCreationForm):
    telefono = forms.CharField(max_length=15) 
    direccion = forms.CharField(widget = forms.Textarea)

    # Agregamos los campos al formulario
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'telefono', 'direccion']