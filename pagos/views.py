from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods
from .models import Pago
import json
from datetime import datetime
from django.shortcuts import get_object_or_404

def getPagosJson(request):
    # Obtener todos los pagos
    pagos = Pago.objects.all()
    
    # Crear una lista con los datos de cada pago en formato diccionario
    pagos_data = [
        {
            'id': pago.id,
            'valor': pago.valor,
            'causacion': pago.causacion,
            'fechaLimite': pago.fechaLimite.strftime('%Y-%m-%d'),
            'estado': pago.estadoPago,  # Usamos get_estado_display() para mostrar el valor legible
            'mes': pago.get_mes_display()  # Usamos get_mes_display() para mostrar el nombre del mes
        }
        for pago in pagos
    ]
    
    # Retornar los pagos como un JsonResponse
    return JsonResponse(pagos_data, safe=False)


@csrf_exempt  # Desactiva la protección CSRF solo para pruebas
@require_POST  # Asegura que la solicitud sea POST
def crear_pago(request):
    try:
        # Obtener los datos de la solicitud
        data = json.loads(request.body)
        
        # Extraer los datos necesarios
        valor = data.get('valor')
        causacion = data.get('causacion')
        fechaLimite_str = data.get('fechaLimite')  # Recibimos como cadena
        estadoPago = data.get('estadoPago', False)  # Por defecto, el estado es False (No Pagado)
        mes = data.get('mes', '01')  # Valor predeterminado '01' (Enero) si no se proporciona
        
        # Validaciones básicas
        if not valor or not causacion or not fechaLimite_str:
            return JsonResponse({"error": "Faltan datos requeridos."}, status=400)
        
        # Convertir fechaLimite a tipo date
        try:
            fechaLimite = datetime.strptime(fechaLimite_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({"error": "Fecha de límite inválida, debe tener el formato YYYY-MM-DD."}, status=400)
        
        # Crear el nuevo pago
        pago = Pago.objects.create(
            valor=valor,
            causacion=causacion,
            fechaLimite=fechaLimite,
            estadoPago=bool(estadoPago),
            mes=mes
        )
        
        # Respuesta con el pago creado
        return JsonResponse({
            'id': pago.id,
            'valor': pago.valor,
            'causacion': pago.causacion,
            'fechaLimite': pago.fechaLimite.strftime('%Y-%m-%d'),
            'estadoPago': pago.estadoPago,
            'mes': pago.get_mes_display()
        }, status=201)  # 201 es el código de estado para creación exitosa

    except json.JSONDecodeError:
        return JsonResponse({"error": "Datos JSON inválidos."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    
def get_pago_por_id(request, id):
    # Buscar el pago por id
    pago = get_object_or_404(Pago, id=id)

    # Retornar los detalles del pago como JSON
    return JsonResponse({
        'id': pago.id,
        'valor': pago.valor,
        'causacion': pago.causacion,
        'fechaLimite': pago.fechaLimite.strftime('%Y-%m-%d'),
        'estadoPago': pago.estadoPago,
        'mes': pago.get_mes_display()
    })
    
    
@csrf_exempt  # Desactiva la protección CSRF solo para pruebas
def modificar_pago(request, id):
    if request.method == 'PUT' or request.method == 'PATCH':
        # Obtener el pago a modificar
        pago = get_object_or_404(Pago, id=id)
        
        # Obtener los datos enviados en la solicitud
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos JSON inválidos."}, status=400)
        
        # Actualizar los campos que se proporcionen
        if 'valor' in data:
            pago.valor = data['valor']
        if 'causacion' in data:
            pago.causacion = data['causacion']
        if 'fechaLimite' in data:
            try:
                pago.fechaLimite = datetime.strptime(data['fechaLimite'], '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({"error": "Fecha de límite inválida, debe tener el formato YYYY-MM-DD."}, status=400)
        if 'estado' in data:
            pago.estadoPago = bool(data['estadoPago'])
        if 'mes' in data:
            pago.mes = data['mes']

        # Guardar el pago modificado
        pago.save()

        # Responder con el pago actualizado
        return JsonResponse({
            'id': pago.id,
            'valor': pago.valor,
            'causacion': pago.causacion,
            'fechaLimite': pago.fechaLimite.strftime('%Y-%m-%d'),
            'estadoPago': pago.estadoPago,
            'mes': pago.get_mes_display()
        })
    
    return JsonResponse({"error": "Método no permitido. Usa PUT o PATCH."}, status=405)

@csrf_exempt  # Desactiva la protección CSRF solo para pruebas
@require_http_methods(["DELETE"])
def borrar_pago(request, id):
    # Obtener el pago a eliminar
    pago = get_object_or_404(Pago, id=id)

    # Eliminar el pago
    pago.delete()

    # Responder con un mensaje de éxito
    return JsonResponse({"message": "Pago eliminado con éxito."}, status=200)