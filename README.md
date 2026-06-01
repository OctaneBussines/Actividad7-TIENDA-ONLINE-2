# Tienda Online Profesional

Proyecto de tienda online construido en Python con Flask. El sistema incluye:

- Inicio de sesión con usuario administrador y cliente.
- Vista de productos filtrados por categoría.
- Carrito de compras con visualización dinámica.
- Descarga de factura en PDF al finalizar compra.
- Módulo MVC para agregar, editar y eliminar productos.
- Interfaz responsive para escritorio y móvil.

## Requisitos

- Python 3.10+
- Instalación de dependencias con `pip install -r requirements.txt`

## Ejecutar la aplicación

1. Abrir una terminal en `TiendaOnline`.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Iniciar la aplicación:
   ```bash
   python run.py
   ```
4. Abrir el navegador en `http://127.0.0.1:5000`

## Credenciales iniciales

- Administrador:
  - Usuario: `admin`
  - Contraseña: `admin123`
- Cliente:
  - Usuario: `cliente`
  - Contraseña: `cliente123`

## Calidad y diseño

Este proyecto aplica principios de calidad ISO 25000 en:

- Funcionalidad: rutas y operaciones completas para gestión de productos y carrito.
- Usabilidad: interfaz web clara, mensajes de usuario y flujo de compra.
- Fiabilidad: almacenamiento en SQLite local y manejo de sesiones.
- Mantenibilidad: separaciones MVC entre `app.py`, `controllers.py`, `models.py` y `database.py`.
- Portabilidad: ejecutable en cualquier entorno con Python y Flask.
- Documentación de calidad: informe y bitácora de ISO 25000 en `ISO25000.md`.
