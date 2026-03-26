from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegistroForm
from .models import Categoria, Cliente, Producto, Resena, StockTalla, PuntoVenta, Evento, FotoEvento, ImagenProducto
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone  # Importamos timezone para obtener la fecha actual

# Metodo de registro
def registro_view(request): # request = peticion

    #Carcamos las categorias para mostras en el footer
    categorias = Categoria.objects.all()

    if request.method == 'POST': # Si la peticion es POST entonces
        #Obtenemos los datos del formulario que el usuario ingreso en la plantilla
        formulario = RegistroForm(request.POST)
        if formulario.is_valid(): #Validamos si los datos son correctos
            user = formulario.save() #Guardamos en la bd

            #Creamos el cliente el cual el objeto del cliente se relaciona con el usuario 
            Cliente.objects.create(
                usuario = user,
                telefono = formulario.cleaned_data['telefono'],
                direccion = formulario.cleaned_data['direccion']
                )
            
            messages.success(request, 'Usuario registrado correctamente!') # Mensaje de exito
            return redirect('login') # Redireccionamos al login
    else:
        formulario = RegistroForm() # Si el formulario no es valido lo volvemos a inicializar
    return render(request, 'registro.html', {'form': formulario, 'categorias': categorias})
        
#Metodo para entrar al sistema
def login_view(request):

    #Carcamos las categorias para mostras en el footer
    categorias = Categoria.objects.all()

    if request.method == 'POST':
        #Obtenemos los valores desde el formulario
        username = request.POST['username']
        password = request.POST['password']

        #Verificamos si el usuario y la contraseña son correctos
        user = authenticate(request, username=username, password=password)
        if user is not None: # Si el usuario existe
            login(request, user) # Iniciamos sesion

            # DEBUG: confirma que funciona
            #print(f"LOGIN EXITOSO: {user.username} - ID: {user.id}")
            #print(f"request.user.is_authenticated: {request.user.is_authenticated}")

            messages.success(request, 'Inicio de sesion exitoso!')
            return redirect('tienda') # Redireccionamos al dashboard
        else: 
            messages.error(request, 'Credenciales incorrectas.') # Mensaje de error

    return render(request, 'login.html', {'categorias': categorias}) # Si no es POST entonces renderizamos el login

#Metodo para salir de la sesion
def logout_view(request):
    #Borramos toda la informacion de la session, es decir cerramos la sesion
    logout(request)
    #Una vez que cerramos la sesion, regresamos al login
    return redirect('tienda')

#Metodo para mostrar la tienda sin acceso
def tienda_view(request):
    categorias = Categoria.objects.all() # Obtenemos todas las categorias 

    return render(request, 'tienda.html', {'categorias': categorias}) # Y aqui lo renderizamos junto con las categorias 

#Metodo para mostrar los productos junto con las categorias
def productos_view(request):
    productos = Producto.objects.prefetch_related( #El prefetch_related nos permite obtener los objetos relacionados
        'imagenes', 
        'categoria', 
        'tallaDisponible', 
        'tipoMateria', 
        'instruccionesCuidado',
        'stocktalla_set__talla'
    )
    categorias = Categoria.objects.all()
    
    categoria_id = request.GET.get('categoria')
    if categoria_id:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        productos = productos.filter(categoria=categoria)
        categoria_seleccionada = categoria
    else:
        categoria_seleccionada = None

    for producto in productos:
        stock = producto.stocktalla_set.filter(talla_stock__gt=0)
        producto.stock_por_talla = [
            {'talla': s.talla.nombreTalla, 'stock': s.talla_stock}
            for s in stock
        ]
    
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
    productos = Producto.objects.prefetch_related('imagenes', 'categoria', 'tallaDisponible', 'tipoMateria', 'instruccionesCuidado').all()
    categoria = Categoria.objects.all() # Obtenemos todas las categorias

    context = {
        'productos': productos, #PASAMOS LOS PRODUCTOS PARA QUE SE VEAN
        'categoria': categoria, #PASAMOS LA CATEGORIA PARA QUE SE VEAN
        'categoria_seleccionada' : categoria_seleccionada # PARA RESALTAR EL BOTON ACTIVO
    }

    return render(request, 'productos.html', context)


#Metodo para crear una reseña
@login_required
def crear_resena(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        try:
            #cliente = Cliente.objects.get(usuario=request.user) # Obtenemos el cliente
            cliente = get_object_or_404(Cliente, usuario=request.user) # Obtenemos el cliente por su id, pero para el admin se puede usar el get_object_or_404
            estrellas = int(request.POST.get('estrellas', 5))
            if estrellas < 1 or estrellas > 5:
                raise ValueError("Estrellas fuera de rango")
            comentario = request.POST.get('comentario', '').strip()
            
            Resena.objects.create(
                producto=producto,
                usuario=cliente,
                estrellas=estrellas,
                comentario=comentario
            )
            messages.success(request, '¡Gracias por tu reseña!')
        except (ValueError, Cliente.DoesNotExist):
            messages.error(request, 'Error en los datos enviados. Intentalo de nuevo')
    
    return redirect('productList')

#Metodo para mostrar los puntos de venta
def punto_venta_view(request):
    categoria = Categoria.objects.all() # Obtenemos todas las categorias
    puntos_venta = PuntoVenta.objects.filter(activo=True) # Obtenemos todos los puntos de venta activos
    context = {
        'categorias': categoria,
        'puntos_venta': puntos_venta,
    }
    return render(request, 'puntos_venta.html', context)

#Metodo para mostrar los eventos
def eventos_view(request):
    categorias = Categoria.objects.all() # Obtenemos todas las categorias

    hoy = timezone.now().date() # Obtenemos la fecha actual
    proximos = Evento.objects.filter(activo=True, fecha__gte=hoy).prefetch_related('fotos', 'colaboradores').order_by('fecha') # Obtenemos los eventos proximos que esten activos 
    pasados = Evento.objects.filter(activo=True, fecha__lt=hoy).prefetch_related('fotos', 'colaboradores').order_by('-fecha') # Obtenemos los eventos pasados que esten activos

    context = {
        'categorias': categorias,
        'proximos': proximos,
        'pasados': pasados,
    }
    return render(request, 'eventos.html', context)