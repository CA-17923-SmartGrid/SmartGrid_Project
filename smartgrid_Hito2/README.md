# Smart Grid Lima — Aplicación Django

Red eléctrica inteligente · Miraflores / San Isidro, Lima, Perú

## Instalación

```bash
pip install django numpy pandas scipy geopy networkx
```

## Ejecución

```bash
cd smartgrid_project
python manage.py runserver
```

Abre tu navegador en: **http://localhost:8000**

## Estructura

```
smartgrid_project/
├── manage.py
├── smartgrid_project/
│   ├── settings.py
│   └── urls.py
└── grid/
    ├── services.py      ← lógica de red (numpy, scipy, geopy, networkx)
    ├── views.py         ← vistas Django (landing, app, api_red, api_exportar)
    ├── urls.py
    └── templates/grid/
        ├── base.html
        ├── landing.html
        └── app.html
```

## Endpoints

| Ruta | Descripción |
|------|-------------|
| `/` | Landing page |
| `/app/` | Dashboard principal |
| `/api/red/?n=1500&umbral=0.003&seed=42` | JSON con nodos, conexiones y stats |
| `/api/exportar/?tipo=nodos` | Descarga dataset_nodos.csv |
| `/api/exportar/?tipo=conexiones` | Descarga dataset_conexiones.csv |
