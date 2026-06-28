"""
Ejecutar: python run.py
Abre el navegador automáticamente en http://localhost:8000
"""
import os
import sys
import time
import threading
import webbrowser
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "smartgrid_project"))

try:
    from django.core.management import execute_from_command_line
except ImportError as exc:
    raise ImportError(
        "No se pudo importar Django. Asegúrate de instalarlo y activar el entorno virtual correcto."
    ) from exc

PORT = 8000
URL  = f"http://localhost:{PORT}"

def abrir_navegador():
    time.sleep(2)  # espera a que Django arranque
    webbrowser.open(URL)

if __name__ == "__main__":
    print("=" * 50)
    print("  Smart Grid Lima — Iniciando...")
    print(f"  URL: {URL}")
    print("  Presiona Ctrl+C para detener")
    print("=" * 50)

    threading.Thread(target=abrir_navegador, daemon=True).start()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartgrid_project.settings")

    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "runserver", str(PORT), "--noreload"])
