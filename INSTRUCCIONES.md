# Agenda universitaria — Meta 2.3

Aplicación de consola desarrollada en Python para administrar eventos universitarios mediante MySQL y `mysql-connector-python`.

## Funciones

- Consultar el catálogo completo.
- Buscar eventos por parte del nombre.
- Consultar eventos con capacidad para una cantidad solicitada de asistentes.
- Registrar asistentes con validación de cupo.
- Cancelar registros sin permitir cantidades negativas.
- Crear eventos nuevos.
- Modificar fecha, hora, lugar y cupo, validando los registros existentes.
- Consultar próximos eventos que aún tengan lugares disponibles.

## Requisitos

- Python 3.10 o posterior.
- MySQL 8.
- Paquete `mysql-connector-python`.

## Instalación y ejecución

1. Abre MySQL Workbench y ejecuta el archivo `estructura_universitaria.sql`.
2. Instala el conector desde una terminal:

   ```bash
   pip install mysql-connector-python
   ```

3. Abre `conexion_eventos.py` y cambia `TU_CONTRASENA` por la contraseña de tu usuario MySQL.
4. Ejecuta el programa:

   ```bash
   python conexion_eventos.py
   ```

## Archivos

- `estructura_universitaria.sql`: crea la base de datos, la tabla y datos de prueba.
- `conexion_eventos.py`: contiene el menú y las operaciones de gestión.
- `INSTRUCCIONES.md`: documentación de instalación y uso.

> Nota: los datos de conexión son locales. No publiques contraseñas reales en GitHub.
