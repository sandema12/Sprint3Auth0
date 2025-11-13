import time

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from monitoring.auth0backend import getRole
from .models import Order

# Roles que SÍ pueden modificar pedidos
ALLOWED_ROLES_UPDATE = [
    "Jefe Logística y Operaciones",
    "Gerente",
    "Operario Alistador",
]


@login_required
def orders_list(request):
    """
    Muestra la lista de pedidos.
    Todos los usuarios autenticados la pueden ver.
    Si venimos de una edición exitosa, el tiempo de respuesta
    del POST se encuentra en request.session["last_update_time_ms"].
    """
    orders = Order.objects.all().order_by("id")
    last_update_time_ms = request.session.pop("last_update_time_ms", None)

    return render(
        request,
        "orders/orders_list.html",
        {
            "orders": orders,
            "last_update_time_ms": last_update_time_ms,
        },
    )


@login_required
def order_edit(request, order_id):
    """
    Vista para editar un pedido.
    - Si el usuario NO tiene uno de los roles permitidos, se muestra
      una página de "Acceso no autorizado" con el tiempo de respuesta.
    - Si tiene el rol apropiado y hace POST, se actualiza el pedido,
      se mide el tiempo y se redirige a la lista.
    """
    start = time.perf_counter()
    role = getRole(request)
    order = get_object_or_404(Order, pk=order_id)

    # Usuario autenticado pero sin rol permitido -> acceso no autorizado
    if role not in ALLOWED_ROLES_UPDATE:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return render(
            request,
            "orders/unauthorized.html",
            {
                "role": role,
                "order": order,
                "response_time_ms": elapsed_ms,
            },
        )

    if request.method == "POST":
        order.quantity = int(request.POST.get("quantity", order.quantity))
        order.products_list = request.POST.get("products_list", order.products_list)
        order.picker_name = request.POST.get("picker_name", order.picker_name)
        order.status = request.POST.get("status", order.status)
        order.save()

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        request.session["last_update_time_ms"] = elapsed_ms

        return redirect("orders:list")

    # Si es GET y el usuario está autorizado, solo mostramos el formulario
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return render(
        request,
        "orders/order_edit.html",
        {
            "order": order,
            "role": role,
            "response_time_ms": elapsed_ms,
        },
    )
