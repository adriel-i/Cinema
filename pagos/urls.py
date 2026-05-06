from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('procesar/<uuid:reserva_codigo>/', views.procesar_pago, name='procesar_pago'),
    path('mercadopago/<uuid:pago_codigo>/', views.procesar_mercadopago, name='procesar_mercadopago'),
    path('mercadopago/success/<uuid:pago_codigo>/', views.mercadopago_success, name='mercadopago_success'),
    path('mercadopago/failure/<uuid:pago_codigo>/', views.mercadopago_failure, name='mercadopago_failure'),
    path('mercadopago/pending/<uuid:pago_codigo>/', views.mercadopago_pending, name='mercadopago_pending'),
    path('transferencia/<uuid:pago_codigo>/', views.instrucciones_transferencia, name='instrucciones_transferencia'),
    path('confirmacion/<uuid:pago_codigo>/', views.confirmacion_pago, name='confirmacion'),
    path('detalle/<uuid:pago_codigo>/', views.detalle_pago, name='detalle'),
    path('webhook/mercadopago/', views.webhook_mercadopago, name='webhook_mercadopago'),
    path('verificar-cupon/', views.verificar_cupon, name='verificar_cupon'),
]
