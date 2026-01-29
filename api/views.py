from django.shortcuts import render, redirect
from .forms import RegistroForm
from .models import Cliente, Producto
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Metodo de registro
def registro_view(request): # request = peticion
    if request.method == 'POST': # Si la peticion es POST entonces
        #Inicializamos el formulario con todos los valores de los input
        form = RegistroForm(request.POST)
        if form.is_valid(): #Validamos si los datos son correctos
            user = form.save() #Guardamos en la bd

            #Creamos el cliente el cual el objeto del cliente se relaciona con el usuario 
            Cliente.objects.create(
                usuario = user,
                telefono = form.cleaned_data['telefono'],
                direccion = form.cleaned_data['direccion']
                )
            
            messages.success(request, 'Usuario registrado correctamente!') # Mensaje de exito
            return redirect('dashboard') # Redireccionamos al login
    else:
        form = RegistroForm() # Si el formulario no es valido lo volvemos a inicializar
    return render(request, 'registro.html', {'form': form})
        
#Metodo para entrar al sistema
def login_view(request):
    if request.method == 'POST':
        #Obtenemos los valores desde el formulario
        username = request.POST['username']
        password = request.POST['password']

        #Verificamos si el usuario y la contraseña son correctos
        user = authenticate(request, username=username, password=password)
        if user is not None: # Si el usuario existe
            login(request, user) # Iniciamos sesion
            return redirect('tienda') # Redireccionamos al dashboard
        else: 
            messages.error(request, 'Credenciales incorrectas.') # Mensaje de error

    return render(request, 'login.html') # Si no es POST entonces renderizamos el login

#Metodo para salir de la sesion
def logout_view(request):
    #Borramos toda la informacion de la session, es decir cerramos la sesion
    logout(request)
    #Una vez que cerramos la sesion, regresamos al login
    return redirect('tienda')

#Metodo para mostrar la tienda sin acceso
def tienda_view(request):
    return render(request, 'tienda.html', {}) 

def productos_view(request):
    productos = Producto.objects.all() # Obtenemos todos los productos

    #Validamos si la lista de productos esta vacia
    if not productos:
        messages.error(request, '😔 No hay productos disponibles')
    #Y si no esta vacia mostramos los productos    
    return render(request, 'productos.html', {'productos': productos})
    
