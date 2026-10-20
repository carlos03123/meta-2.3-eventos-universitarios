# Meta 2.3: Sistema de gestión de eventos universitarios

**Estudiante:** Carlos René López Cervantes  
**Grupo:** 952  
**Fecha:** 20/10/2026

## Descripción

Aplicación de consola desarrollada en Python que utiliza MySQL para administrar actividades y eventos universitarios. El sistema permite consultar información, controlar la capacidad de cada evento y mantener actualizado el número de asistentes registrados.

### Funciones del sistema

1. Consultar el catálogo completo de eventos.
2. Buscar eventos por nombre o parte del nombre.
3. Revisar qué eventos tienen espacio para una cantidad específica de asistentes.
4. Registrar asistentes, comprobando que exista el evento y que haya cupo suficiente.
5. Cancelar registros sin permitir que el total sea negativo.
6. Crear eventos nuevos con fecha, hora, ubicación y capacidad.
7. Modificar la fecha, hora, ubicación y cupo de un evento existente.
8. Consultar próximos eventos que todavía tengan lugares disponibles.
9. Salir del programa.

Las consultas que reciben información utilizan parámetros SQL para evitar concatenar directamente los datos ingresados. Las operaciones de actualización guardan los cambios en MySQL y manejan errores de conexión y de ejecución.

## Archivos del proyecto

- **`estructura_universitaria.sql`**: crea la base de datos `eventos_universitarios`, la tabla `eventos` y agrega registros de ejemplo.
- **`conexion_eventos.py`**: contiene la conexión con MySQL, las funciones para administrar eventos y el menú principal.

## Requisitos

- Python 3.10 o posterior.
- MySQL 8.
- Biblioteca `mysql-connector-python`.
- MySQL Workbench, o una herramienta equivalente para ejecutar el script SQL.

## Cómo ejecutar

### 1. Crear la base de datos

Abre MySQL Workbench y ejecuta el contenido de `estructura_universitaria.sql`.

También puedes importar el archivo desde una terminal con MySQL configurado:

```bash
mysql -u root -p < estructura_universitaria.sql
```

### 2. Instalar el conector de Python

Abre una terminal y ejecuta:

```bash
pip install mysql-connector-python
```

### 3. Configurar la conexión

Abre `conexion_eventos.py` y localiza el bloque `DB_CONFIG`. Cambia `TU_CONTRASENA` por la contraseña de tu usuario local de MySQL. Si tu servidor usa otro usuario, host o base de datos, actualiza esos valores.

**No publiques contraseñas reales en GitHub.**

### 4. Iniciar el programa

En la terminal, entra a la carpeta donde guardaste el archivo y ejecuta:

```bash
python conexion_eventos.py
```

### 5. Usar el menú

Selecciona una opción del 1 al 9 y sigue las indicaciones que aparecen en pantalla. Para comprobar el funcionamiento, puedes consultar el catálogo, buscar un evento y revisar la disponibilidad antes de registrar asistentes.

## Nota

Los eventos incluidos en el script SQL son datos de prueba y pueden modificarse según las necesidades de la práctica.
