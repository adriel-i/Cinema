from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from .models import Pago, MetodoPago, CuponDescuento
from reservas.models import Reserva
import mercadopago
import json
from django.conf import settings

@login_required
def procesar_pago(request, reserva_codigo):
    """Procesar pago de una reserva"""
    reserva = get_object_or_404(Reserva, codigo=reserva_codigo, usuario=request.user)
    
    # Verificar que la reserva esté temporal y no expirada
    if reserva.estado != 'temporal' or reserva.expirada:
        return redirect('index')
    
    # Obtener métodos de pago disponibles
    metodos_pago = MetodoPago.objects.filter(activo=True)
    
    # Obtener cupones disponibles
    cupones = CuponDescuento.objects.filter(
        activo=True,
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    )
    
    if request.method == 'POST':
        metodo_pago_id = request.POST.get('metodo_pago')
        cupon_codigo = request.POST.get('cupon_codigo', '')
        
        metodo_pago = get_object_or_404(MetodoPago, id=metodo_pago_id)
        
        # Calcular descuentos
        monto_final = reserva.precio_total
        descuento_aplicado = 0
        
        if cupon_codigo:
            try:
                cupon = CuponDescuento.objects.get(codigo=cupon_codigo.upper())
                if cupon.puede_usarse(monto_final):
                    descuento_aplicado = cupon.calcular_descuento(monto_final)
                    monto_final -= descuento_aplicado
            except CuponDescuento.DoesNotExist:
                pass
        
        # Crear pago
        pago = Pago.objects.create(
            reserva=reserva,
            metodo_pago=metodo_pago,
            monto=monto_final,
            estado='pendiente'
        )
        
        # Procesar según método de pago
        if metodo_pago.nombre.lower() == 'mercadopago':
            return redirect('pagos:procesar_mercadopago', pago.codigo)
        elif metodo_pago.nombre.lower() == 'transferencia':
            return redirect('pagos:instrucciones_transferencia', pago.codigo)
        else:
            # Simulación de pago exitoso
            pago.marcar_completado(transaccion_id=f"SIM-{pago.codigo}")
            return redirect('pagos:confirmacion', pago.codigo)
    
    return render(request, 'pagos/procesar_pago.html', {
        'reserva': reserva,
        'metodos_pago': metodos_pago,
        'cupones': cupones,
    })

@login_required
def procesar_mercadopago(request, pago_codigo):
    """Procesar pago con Mercado Pago"""
    pago = get_object_or_404(Pago, codigo=pago_codigo, reserva__usuario=request.user)
    
    # Configurar SDK de Mercado Pago
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    
    # Crear preferencia de pago
    preference_data = {
        "items": [
            {
                "title": f"Entradas Cine - {pago.reserva.funcion.pelicula.titulo}",
                "description": f"{pago.reserva.cantidad_entradas} entradas - Asientos: {pago.reserva.asientos}",
                "quantity": 1,
                "currency_id": "ARS",
                "unit_price": float(pago.monto)
            }
        ],
        "back_urls": {
            "success": request.build_absolute_uri(f'/pagos/mercadopago/success/{pago.codigo}/'),
            "failure": request.build_absolute_uri(f'/pagos/mercadopago/failure/{pago.codigo}/'),
            "pending": request.build_absolute_uri(f'/pagos/mercadopago/pending/{pago.codigo}/'),
        },
        "auto_return": "approved",
        "external_reference": str(pago.codigo)
    }
    
    preference = sdk.preference().create(preference_data)
    
    return render(request, 'pagos/mercadopago.html', {
        'pago': pago,
        'preference_id': preference['response']['id'],
        'public_key': settings.MERCADO_PAGO_PUBLIC_KEY,
    })

def mercadopago_success(request, pago_codigo):
    """Callback de éxito de Mercado Pago"""
    pago = get_object_or_404(Pago, codigo=pago_codigo)
    
    if pago.estado == 'pendiente':
        # Aquí deberías verificar el estado del pago con la API de Mercado Pago
        # Por ahora, lo marcamos como completado
        pago.marcar_completado(transaccion_id=request.GET.get('payment_id'))
    
    return redirect('pagos:confirmacion', pago.codigo)

def mercadopago_failure(request, pago_codigo):
    """Callback de fallo de Mercado Pago"""
    pago = get_object_or_404(Pago, codigo=pago_codigo)
    pago.marcar_fallido(respuesta={'status': 'failed', 'payment_id': request.GET.get('payment_id')})
    
    return render(request, 'pagos/error.html', {
        'pago': pago,
        'mensaje': 'El pago no pudo ser procesado. Por favor, intenta nuevamente.'
    })

def mercadopago_pending(request, pago_codigo):
    """Callback de pago pendiente de Mercado Pago"""
    pago = get_object_or_404(Pago, codigo=pago_codigo)
    pago.estado = 'procesando'
    pago.save()
    
    return render(request, 'pagos/pendiente.html', {'pago': pago})

@login_required
def instrucciones_transferencia(request, pago_codigo):
    """Mostrar instrucciones para transferencia bancaria"""
    pago = get_object_or_404(Pago, codigo=pago_codigo, reserva__usuario=request.user)
    
    return render(request, 'pagos/transferencia.html', {'pago': pago})

@login_required
def confirmacion_pago(request, pago_codigo):
    """Página de confirmación de pago"""
    pago = get_object_or_404(Pago, codigo=pago_codigo, reserva__usuario=request.user)
    
    return render(request, 'pagos/confirmacion.html', {'pago': pago})

@login_required
def detalle_pago(request, pago_codigo):
    """Ver detalles de un pago"""
    pago = get_object_or_404(Pago, codigo=pago_codigo, reserva__usuario=request.user)
    
    return render(request, 'pagos/detalle.html', {'pago': pago})

@csrf_exempt
@require_POST
def webhook_mercadopago(request):
    """Webhook para recibir notificaciones de Mercado Pago"""
    try:
        data = json.loads(request.body)
        
        # Procesar la notificación según la documentación de Mercado Pago
        if data.get('type') == 'payment':
            payment_id = data['data']['id']
            
            # Aquí deberías verificar el estado del pago con la API de Mercado Pago
            # y actualizar el estado del pago correspondiente
            
            return JsonResponse({'status': 'received'})
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'ok'})

@login_required
@require_POST
def verificar_cupon(request):
    """Verificar si un cupón es válido"""
    cupon_codigo = request.POST.get('cupon_codigo', '').upper()
    monto_compra = float(request.POST.get('monto_compra', 0))
    
    try:
        cupon = CuponDescuento.objects.get(codigo=cupon_codigo)
        
        if cupon.puede_usarse(monto_compra):
            descuento = cupon.calcular_descuento(monto_compra)
            return JsonResponse({
                'valid': True,
                'descuento': float(descuento),
                'monto_final': monto_compra - descuento,
                'mensaje': f'¡Cupón válido! Descuento de ${descuento:.2f}'
            })
        else:
            return JsonResponse({
                'valid': False,
                'mensaje': 'El cupón no es válido o no puede ser usado con esta compra.'
            })
            
    except CuponDescuento.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'mensaje': 'El cupón no existe.'
        })
