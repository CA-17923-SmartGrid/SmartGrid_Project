"""
Lógica de negocio: generación, análisis de la red eléctrica y optimización MST.
"""
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from geopy.distance import geodesic


# 1. GENERACIÓN DE LA RED Y VALIDACIÓN (BFS)

def generar_red(n_nodos: int = 1500, umbral: float = 0.003, seed: int = 42) -> dict:
    np.random.seed(seed)

    LAT = (-12.12, -12.09)
    LON = (-77.05, -77.02)

    lats  = np.random.uniform(*LAT, n_nodos)
    lons  = np.random.uniform(*LON, n_nodos)
    tipos = np.random.choice(
        ['Poste', 'Subestación', 'Punto_Carga'],
        n_nodos, p=[0.80, 0.05, 0.15]
    )

    df_nodos = pd.DataFrame({'id': range(n_nodos), 'lat': lats, 'lon': lons, 'tipo': tipos})

    # KDTree para búsqueda de vecinos
    coords = list(zip(lats, lons))
    tree   = KDTree(coords)

    conexiones = []
    vistos     = set()
    for i, punto in enumerate(coords):
        vecinos = tree.query_ball_point(punto, umbral)
        for j in vecinos:
            if i == j:
                continue
            par = (min(i, j), max(i, j))
            if par in vistos:
                continue
            vistos.add(par)
            dist_m = geodesic(coords[i], coords[j]).meters
            conexiones.append({'origen': i, 'destino': j, 'distancia_metros': round(dist_m, 1)})

    df_conn = pd.DataFrame(conexiones) if conexiones else pd.DataFrame(columns=['origen','destino','distancia_metros'])

    # BFS conectividad
    n   = len(df_nodos)
    adj = [[] for _ in range(n)]
    for _, row in df_conn.iterrows():
        a, b = int(row['origen']), int(row['destino'])
        adj[a].append(b); adj[b].append(a)

    vis = [False] * n
    cola = [0]; vis[0] = True; alcanzados = 1
    while cola:
        u = cola.pop(0)
        for v in adj[u]:
            if not vis[v]:
                vis[v] = True; alcanzados += 1; cola.append(v)

    cobertura = round(alcanzados / n * 100, 2)
    conteo    = df_nodos['tipo'].value_counts().to_dict()

    return {
        'nodos':       df_nodos.to_dict('records'),
        # Quitamos el límite de 10000 aquí para que Kruskal reciba todas las aristas posibles
        'conexiones':  df_conn.to_dict('records'), 
        'csv_nodos':   df_nodos.to_csv(index=False, sep=';'),
        'csv_conn':    df_conn.to_csv(index=False, sep=';'),
        'stats': {
            'total_nodos':    n,
            'total_conn':     len(df_conn),
            'alcanzados':     alcanzados,
            'cobertura':      cobertura,
            'densidad':       round(len(df_conn) / n, 2),
            'postes':         int(conteo.get('Poste', 0)),
            'subestaciones':  int(conteo.get('Subestación', 0)),
            'puntos_carga':   int(conteo.get('Punto_Carga', 0)),
            'conexo':         cobertura >= 95,
        }
    }



# 2. OPTIMIZACIÓN DE CABLEADO (MST - KRUSKAL CON UFDS)

class UnionFind:
    """
    Estructura de datos UFDS (Union-Find Disjoint Set).
    """
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                self.parent[root_i] = root_j
            elif self.rank[root_i] > self.rank[root_j]:
                self.parent[root_j] = root_i
            else:
                self.parent[root_j] = root_i
                self.rank[root_i] += 1
            return True
        return False


def optimizar_red_kruskal(n_nodos_total, conexiones):
    """
    Aplica el algoritmo de Kruskal para encontrar el Árbol de Expansión Mínima (MST).
    """
    uf = UnionFind(n_nodos_total)
    
    # Ordenar todas las aristas de menor a mayor peso (distancia)
    conexiones_ordenadas = sorted(conexiones, key=lambda x: x['distancia_metros'])
    
    mst_edges = []
    costo_total_metros = 0.0
    
    for arista in conexiones_ordenadas:
        u = arista['origen']
        v = arista['destino']
        peso = arista['distancia_metros']
        
        # Si no forma un ciclo, lo agregamos al cableado final
        if uf.union(u, v):
            mst_edges.append(arista)
            costo_total_metros += peso
            
            # Optimización: Un MST siempre tiene (V - 1) aristas
            if len(mst_edges) == n_nodos_total - 1:
                break
                
    return mst_edges, round(costo_total_metros, 2)