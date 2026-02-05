from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegistroForm
from .models import Categoria, Cliente, Producto, Resena
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
            return redirect('tienda') # Redireccionamos al login
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

            # 👇 DEBUG: confirma que funciona
            print(f"LOGIN EXITOSO: {user.username} - ID: {user.id}")
            print(f"request.user.is_authenticated: {request.user.is_authenticated}")

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

#Metodo para mostrar los productos junto con las categorias
def productos_view(request):
    productos = Producto.objects.all() # Obtenemos todos los productos
    categorias = Categoria.objects.all() # Obtenemos todas las categorias
    
    # Detecta categoría desde URL param (opcional)
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        productos = productos.filter(categoria=categoria)
        categoria_seleccionada = categoria
    else:
        categoria_seleccionada = None
    
    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada
    }
    return render(request, 'productos.html', context)

#Metodo para mostrar productos por categoria
def productos_por_categoria(request, categoria_id):
    #El get_object_or_404 nos permite obtener un objeto por su id
    categoria_seleccionada  = get_object_or_404(Categoria, id=categoria_id) # Obtenemos la categoria por id
    productos = Producto.objects.filter(categoria=categoria) # Obtenemos los productos por categoria mediante el id
    categoria = Categoria.objects.all() # Obtenemos todas las categorias

    context = {
        'productos': productos, #PASAMOS LOS PRODUCTOS PARA QUE SE VEAN
        'categoria': categoria, #PASAMOS LA CATEGORIA PARA QUE SE VEAN
        'categoria_seleccionada' : categoria_seleccionada # PARA RESALTAR EL BOTON ACTIVO
    }

    #Y si no esta vacia mostramos los productos
    return render(request, 'productos.html', context)



#Metodo para crear una reseña
@login_required
def crear_resena(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        try:
            cliente = Cliente.objects.get(usuario=request.user)
            estrellas = int(request.POST.get('estrellas', 5))
            comentario = request.POST.get('comentario', '').strip()
            
            Resena.objects.create(
                producto=producto,
                usuario=cliente,
                estrellas=estrellas,
                comentario=comentario
            )
            messages.success(request, '¡Gracias por tu reseña!')
        except Cliente.DoesNotExist:
            messages.error(request, 'Error: No tienes un perfil de cliente completo.')
        except ValueError:
            messages.error(request, 'Error en los datos enviados.')
    
    return redirect('productList')
