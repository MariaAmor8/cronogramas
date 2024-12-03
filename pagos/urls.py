from django.urls import path
from . import views

urlpatterns = [
    # Otras rutas
    path('get_pagos_json/', views.getPagosJson, name='get_pagos_json'),
    path('crear_pago/', views.crear_pago, name='crear_pago'),
    path('get_pagos_json/<int:id>/', views.get_pago_por_id, name='get_pago_por_id'),
    path('get_pagos_json/modificar/<int:id>/', views.modificar_pago, name='modificar_pago'),
    path('borrar_pago/<int:id>/', views.borrar_pago, name='borrar_pago'),
]