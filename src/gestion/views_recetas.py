# ==================== VISTAS DE RECETAS ====================
"""
Módulo de vistas para la gestión de recetas.
Funcionalidades:
- Crear, editar, eliminar y listar recetas
- Gestionar ingredientes de recetas
- Ver detalles de recetas con costos
"""

# ==================== IMPORTS ====================
import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import RecetaForm
from .models import MateriaPrima, Producto, Receta, RecetaMateriaPrima


# ==================== CREAR RECETA ====================
@login_required
def crear_receta(request):
    """Vista para crear una nueva receta."""
    if request.method == 'POST':
        form = RecetaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    receta = form.save(commit=False)
                    receta.creador = request.user
                    receta.save()
                    form.save_m2m()  # Guardar relaciones ManyToMany para productos

                    # Procesar ingredientes dinámicos
                    procesar_ingredientes_receta(request.POST, receta)

                    messages.success(request, f'Receta "{receta.nombre}" creada exitosamente.')
                    return redirect('gestion:lista_recetas')
            except Exception as e:
                messages.error(request, f'Error al crear la receta: {str(e)}')
    else:
        form = RecetaForm()

    # Obtener todas las materias primas para el JavaScript
    materias_primas = MateriaPrima.objects.all().order_by('nombre')

    context = {
        'form': form,
        'materias_primas': materias_primas,
    }
    return render(request, 'modules/recetas/form.html', context)


# ==================== PROCESAR INGREDIENTES ====================
def procesar_ingredientes_receta(post_data, receta):
    """Procesa los ingredientes dinámicos del formulario de receta."""
    # Limpiar ingredientes existentes
    RecetaMateriaPrima.objects.filter(receta=receta).delete()

    # Procesar nuevos ingredientes
    index = 0
    while f'materia_prima_{index}' in post_data:
        materia_prima_id = post_data.get(f'materia_prima_{index}')
        cantidad = post_data.get(f'cantidad_{index}')

        if materia_prima_id and cantidad:
            try:
                materia_prima = MateriaPrima.objects.get(id=materia_prima_id)
                cantidad_decimal = Decimal(cantidad)

                RecetaMateriaPrima.objects.create(
                    receta=receta,
                    materia_prima=materia_prima,
                    cantidad=cantidad_decimal,
                    unidad=materia_prima.unidad_medida  # Usar la unidad de la materia prima
                )
            except (MateriaPrima.DoesNotExist, ValueError, TypeError) as e:
                raise Exception(f'Error al procesar ingrediente {index + 1}: {str(e)}')

        index += 1


# ==================== EDITAR RECETA ====================
@login_required
def editar_receta(request, pk):
    """Vista para editar una receta existente."""
    receta = get_object_or_404(Receta, pk=pk)

    if not request.user.has_perm('gestion.change_receta'):
        messages.error(request, 'No tienes permiso para editar recetas.')
        return redirect('gestion:lista_recetas')

    if request.method == 'POST':
        form = RecetaForm(request.POST, instance=receta)
        if form.is_valid():
            try:
                with transaction.atomic():
                    receta = form.save(commit=False)
                    receta.save()

                    # Eliminar ingredientes existentes
                    RecetaMateriaPrima.objects.filter(receta=receta).delete()

                    # Procesar nuevos ingredientes
                    procesar_ingredientes_receta(request.POST, receta)

                    messages.success(request, 'Receta actualizada exitosamente.')
                    return redirect('gestion:lista_recetas')
            except Exception as e:
                messages.error(request, f'Error al actualizar la receta: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{form.fields[field].label}: {error}')
    else:
        form = RecetaForm(instance=receta)

    # Obtener ingredientes actuales para mostrar en el formulario
    ingredientes_actuales = []
    for ingrediente in receta.recetamateriaprima_set.all():
        ingredientes_actuales.append({
            'materia_prima_id': ingrediente.materia_prima.id,
            'materia_prima_nombre': ingrediente.materia_prima.nombre,
            'cantidad': float(ingrediente.cantidad),
            'unidad': ingrediente.unidad,
            'costo': float(ingrediente.costo_ingrediente())
        })

    context = {
        'form': form,
        'receta': receta,
        'materias_primas': MateriaPrima.objects.filter(activo=True),
        'ingredientes_actuales': json.dumps(ingredientes_actuales),
        'es_edicion': True
    }
    return render(request, 'modules/recetas/form.html', context)


# ==================== ELIMINAR RECETA ====================
@login_required
def eliminar_receta(request, pk):
    """Vista para eliminar una receta."""
    receta = get_object_or_404(Receta, pk=pk)

    if not request.user.has_perm('gestion.delete_receta'):
        messages.error(request, 'No tienes permiso para eliminar recetas.')
        return redirect('gestion:lista_recetas')

    if request.method == 'POST':
        try:
            # Verificar si la receta está siendo usada por productos
            productos_usando = receta.productos.all()
            if productos_usando.exists():
                productos_nombres = ', '.join([p.nombre for p in productos_usando[:3]])
                if productos_usando.count() > 3:
                    productos_nombres += f" y {productos_usando.count() - 3} más"
                messages.error(
                    request,
                    f'No se puede eliminar la receta porque está siendo usada por los productos: {productos_nombres}'
                )
                return redirect('gestion:lista_recetas')

            nombre_receta = receta.nombre
            receta.delete()
            messages.success(request, f'Receta "{nombre_receta}" eliminada exitosamente.')

        except Exception as e:
            messages.error(request, f'Error al eliminar la receta: {str(e)}')

        return redirect('gestion:lista_recetas')

    # Para GET, mostrar página de confirmación
    context = {
        'receta': receta,
        'productos_usando': receta.productos.all(),
        'ingredientes_count': receta.recetamateriaprima_set.count()
    }
    return render(request, 'modules/recetas/confirmar_eliminar_receta.html', context)


# ==================== DETALLE RECETA ====================
@login_required
def detalle_receta(request, pk):
    """Vista para ver el detalle de una receta."""
    receta = get_object_or_404(Receta, pk=pk)

    # Calcular información adicional
    total_ingredientes = receta.recetamateriaprima_set.count()
    costo_total = receta.costo_total()
    productos_usando = receta.productos.all()

    # Obtener ingredientes con información detallada
    ingredientes = []
    for ingrediente in receta.recetamateriaprima_set.all():
        ingredientes.append({
            'materia_prima': ingrediente.materia_prima,
            'cantidad': ingrediente.cantidad,
            'unidad': ingrediente.unidad,
            'costo_unitario': ingrediente.materia_prima.costo_unitario,
            'costo_total': ingrediente.costo_ingrediente(),
            'porcentaje_costo': (ingrediente.costo_ingrediente() / costo_total * 100) if costo_total > 0 else 0
        })

    # Preparar subtitle con estado e ingredientes
    estado_text = "Receta Activa" if receta.activa else "Receta Inactiva"
    subtitle_text = f"{estado_text} • {total_ingredientes} ingrediente(s)"

    context = {
        'receta': receta,
        'ingredientes': ingredientes,
        'total_ingredientes': total_ingredientes,
        'costo_total': costo_total,
        'productos_usando': productos_usando,
        'puede_editar': request.user.has_perm('gestion.change_receta'),
        'puede_eliminar': request.user.has_perm('gestion.delete_receta'),
        'subtitle_text': subtitle_text,
    }
    return render(request, 'modules/recetas/detalle.html', context)


# ==================== LISTA RECETAS ====================
@login_required
def lista_recetas(request):
    """Vista para listar recetas con KPIs LINO V3"""
    from django.core.paginator import Paginator

    from gestion.utils.kpi_builder import prepare_recetas_kpis

    recetas = Receta.objects.all().prefetch_related('productos', 'materias_primas')

    # Preparar KPIs
    kpis = prepare_recetas_kpis(recetas)

    # Paginación
    paginator = Paginator(recetas, 25)
    page_number = request.GET.get('page', 1)
    recetas_paginadas = paginator.get_page(page_number)

    context = {
        'recetas': recetas_paginadas,
        'kpis': kpis,
        'productos_en_recetas': Producto.objects.filter(recetas_producto__isnull=False).distinct(),
        'materias_en_recetas': MateriaPrima.objects.filter(recetas_materia__isnull=False).distinct(),
        'title': 'Recetas',
        'subtitle': 'Gestión de recetas y costos de producción',
        'icon': 'book',
        'create_url': reverse('gestion:crear_receta'),
    }
    return render(request, 'modules/recetas/lista.html', context)
