# grid/views.py
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from .services import generar_red, optimizar_red_kruskal
import json


def app_view(request):
    """
    Vista principal de la aplicación.
    Genera la red eléctrica, calcula el MST y envía los datos al frontend.
    """
    # 1. Generamos la red inicial con los 1500 nodos 
    n_nodos = 1500
    datos_red = generar_red(n_nodos=n_nodos)
    
    # 2. Aplicamos Kruskal para encontrar la red de cableado óptima 
    mst_aristas, costo_mst = optimizar_red_kruskal(n_nodos, datos_red['conexiones'])
    
    # 3. Preparamos el contexto (los datos que viajarán al HTML)
    # Convertimos los datos a formato JSON para que JavaScript pueda leerlos fácilmente y dibujar el grafo.
    context = {
        # Datos del dataset original
        'nodos_json': json.dumps(datos_red['nodos']),
        
        # Solo enviamos las aristas del MST para no sobrecargar el navegador 
        # (mostrar todas las conexiones posibles colapsaría la página)
        'mst_aristas_json': json.dumps(mst_aristas),
        
        # Estadísticas para el panel lateral de la web
        'stats': datos_red['stats'],
        'costo_mst': costo_mst,
    }
    
    return render(request, 'grid/app.html', context)

def landing_view(request):
    """
    Vista para la página de inicio (Landing Page).
    """
    return render(request, 'grid/landing.html')




def api_red(request):
    n = int(request.GET.get('n', 1500))
    umbral = float(request.GET.get('umbral', 0.003))
    seed = int(request.GET.get('seed', 42))
    
    # Generar datos 
    datos_red = generar_red(n_nodos=n, umbral=umbral, seed=seed)
    
    # Calcular MST 
    mst_aristas, costo_mst = optimizar_red_kruskal(n, datos_red['conexiones'])
    
    # Unir todo en el JSON que espera tu app.html
    datos_red['mst_aristas'] = mst_aristas
    datos_red['costo_mst'] = costo_mst
    
    return JsonResponse(datos_red)



def api_exportar(request):
    tipo = request.GET.get('tipo', 'nodos')
    n = int(request.GET.get('n', 1500))
    umbral = float(request.GET.get('umbral', 0.003))
    seed = int(request.GET.get('seed', 42))
    
    # Regeneramos la red para obtener los datos
    datos_red = generar_red(n_nodos=n, umbral=umbral, seed=seed)
    
    # Seleccionamos qué CSV enviar
    if tipo == 'nodos':
        csv_content = datos_red['csv_nodos']
        filename = "dataset_nodos.csv"
    else:
        csv_content = datos_red['csv_conn']
        filename = "dataset_conexiones.csv"
    
    # Preparamos la respuesta como archivo descargable
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response