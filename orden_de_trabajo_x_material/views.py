from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import OTM

def orden_de_trabajo_material_crud(request):
    if request.user.is_authenticated:
        search_query = request.GET.get('search')
        if search_query:
            # Filtrar las órdenes de trabajo por número de orden que contenga el término de búsqueda
            ordenes = OTM.objects.filter(nro_orden__icontains=search_query)
        else:
            # Obtener todas las órdenes de trabajo
            ordenes = OTM.objects.all()

        # Paginar las órdenes de trabajo para mostrar en la página
        paginator = Paginator(ordenes, 15)  # Divide las órdenes en páginas de 15 elementos por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {"page_obj": page_obj}
        return render(request, 'orden_de_trabajo/orden_de_trabajo.html', context)
    else:
        return redirect('login')