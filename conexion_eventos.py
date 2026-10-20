"""
Sistema de gestión de eventos universitarios
Meta 2.3 - Programación en Python con MySQL

Instalación:
    pip install mysql-connector-python

Antes de ejecutar:
1. Ejecuta estructura_universitaria.sql en MySQL Workbench.
2. Actualiza DB_CONFIG con tu usuario y contraseña de MySQL.
3. Ejecuta: python conexion_eventos.py
"""

from datetime import date, datetime
import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "TU_CONTRASENA",
    "database": "eventos_universitarios",
}


def abrir_conexion():
    """Abre y devuelve una conexión a la base de datos."""
    return mysql.connector.connect(**DB_CONFIG)


def listar_eventos():
    """Muestra el catálogo completo de eventos."""
    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, nombre, fecha, hora, lugar, cupo, registrados
            FROM eventos
            ORDER BY fecha, hora
        """)
        filas = cursor.fetchall()

        if not filas:
            print("\nNo hay eventos registrados.")
            return

        print("\n--- CATÁLOGO DE EVENTOS ---")
        for evento in filas:
            print(
                f"[{evento['id']}] {evento['nombre']} | "
                f"{evento['fecha']} {evento['hora']} | {evento['lugar']} | "
                f"Cupo: {evento['registrados']}/{evento['cupo']}"
            )
    except Error as error:
        print(f"No se pudieron consultar los eventos: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def localizar_evento():
    """Busca eventos cuyo nombre contenga el texto indicado."""
    texto = input("Escribe parte del nombre del evento: ").strip()
    if not texto:
        print("Debes escribir un nombre para realizar la búsqueda.")
        return

    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, nombre, fecha, hora, lugar, cupo, registrados
               FROM eventos
               WHERE nombre LIKE %s
               ORDER BY fecha""",
            (f"%{texto}%",),
        )
        resultados = cursor.fetchall()
        if resultados:
            for evento in resultados:
                print(
                    f"{evento['id']}. {evento['nombre']} — {evento['fecha']} "
                    f"{evento['hora']} — {evento['lugar']} — "
                    f"Disponibles: {evento['cupo'] - evento['registrados']}"
                )
        else:
            print("No se encontraron coincidencias.")
    except Error as error:
        print(f"Error al buscar: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def consultar_cupos():
    """Lista los eventos que pueden recibir la cantidad solicitada."""
    try:
        cantidad = int(input("¿Cuántas personas asistirán?: "))
        if cantidad < 1:
            print("La cantidad debe ser mayor que cero.")
            return
    except ValueError:
        print("Introduce un número entero válido.")
        return

    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, nombre, fecha, hora, lugar, cupo, registrados
               FROM eventos
               WHERE (cupo - registrados) >= %s
                 AND fecha >= CURDATE()
               ORDER BY fecha, hora""",
            (cantidad,),
        )
        eventos = cursor.fetchall()
        if not eventos:
            print("No hay eventos futuros con suficientes lugares disponibles.")
            return
        print("\nEventos con cupo suficiente:")
        for evento in eventos:
            disponibles = evento["cupo"] - evento["registrados"]
            print(
                f"{evento['id']}. {evento['nombre']} | {evento['fecha']} "
                f"{evento['hora']} | {evento['lugar']} | "
                f"{disponibles} lugares disponibles"
            )
    except Error as error:
        print(f"No se pudo revisar la disponibilidad: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def registrar_asistentes():
    """Incrementa el registro si el evento existe y hay capacidad."""
    try:
        evento_id = int(input("ID del evento: "))
        cantidad = int(input("Número de asistentes por registrar: "))
        if evento_id < 1 or cantidad < 1:
            print("El ID y la cantidad deben ser positivos.")
            return
    except ValueError:
        print("Introduce valores numéricos enteros.")
        return

    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        conexion.start_transaction()
        cursor.execute(
            "SELECT cupo, registrados FROM eventos WHERE id = %s FOR UPDATE",
            (evento_id,),
        )
        evento = cursor.fetchone()
        if evento is None:
            print("No existe un evento con ese ID.")
            conexion.rollback()
            return

        cupo, registrados = evento
        if registrados + cantidad > cupo:
            print(f"Cupo insuficiente. Lugares disponibles: {cupo - registrados}.")
            conexion.rollback()
            return

        cursor.execute(
            "UPDATE eventos SET registrados = registrados + %s WHERE id = %s",
            (cantidad, evento_id),
        )
        conexion.commit()
        print("Registro de asistentes actualizado.")
    except Error as error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        print(f"No se pudo completar el registro: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def retirar_asistentes():
    """Resta asistentes sin permitir que el contador sea negativo."""
    try:
        evento_id = int(input("ID del evento: "))
        cantidad = int(input("Número de registros que deseas cancelar: "))
        if evento_id < 1 or cantidad < 1:
            print("El ID y la cantidad deben ser positivos.")
            return
    except ValueError:
        print("Introduce valores numéricos enteros.")
        return

    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        conexion.start_transaction()
        cursor.execute(
            "SELECT registrados FROM eventos WHERE id = %s FOR UPDATE",
            (evento_id,),
        )
        fila = cursor.fetchone()
        if fila is None:
            print("No existe un evento con ese ID.")
            conexion.rollback()
            return

        registrados = fila[0]
        if cantidad > registrados:
            print(f"Solo hay {registrados} registros que se pueden cancelar.")
            conexion.rollback()
            return

        cursor.execute(
            "UPDATE eventos SET registrados = registrados - %s WHERE id = %s",
            (cantidad, evento_id),
        )
        conexion.commit()
        print("Cancelación realizada correctamente.")
    except Error as error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        print(f"No se pudo cancelar: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def crear_evento():
    """Inserta un evento nuevo con cero asistentes iniciales."""
    nombre = input("Nombre del evento: ").strip()
    fecha_texto = input("Fecha (AAAA-MM-DD): ").strip()
    hora_texto = input("Hora (HH:MM): ").strip()
    lugar = input("Lugar: ").strip()

    try:
        cupo = int(input("Cupo máximo: "))
        fecha_valida = date.fromisoformat(fecha_texto)
        hora_valida = datetime.strptime(hora_texto, "%H:%M").time()
        if not nombre or not lugar or cupo < 1:
            print("Completa el nombre y lugar; el cupo debe ser mayor que cero.")
            return
        if fecha_valida < date.today():
            print("La fecha no puede estar en el pasado.")
            return
    except ValueError:
        print("Revisa la fecha, la hora o el cupo introducido.")
        return

    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        cursor.execute(
            """INSERT INTO eventos (nombre, fecha, hora, lugar, cupo, registrados)
               VALUES (%s, %s, %s, %s, %s, 0)""",
            (nombre, fecha_valida, hora_valida, lugar, cupo),
        )
        conexion.commit()
        print(f"Evento creado. ID asignado: {cursor.lastrowid}")
    except Error as error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        print(f"No se pudo crear el evento: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def editar_evento():
    """Actualiza fecha, hora, lugar o cupo de un evento existente."""
    try:
        evento_id = int(input("ID del evento que deseas modificar: "))
        nuevo_cupo = int(input("Nuevo cupo máximo: "))
        fecha_texto = input("Nueva fecha (AAAA-MM-DD): ").strip()
        hora_texto = input("Nueva hora (HH:MM): ").strip()
        nuevo_lugar = input("Nuevo lugar: ").strip()

        fecha_valida = date.fromisoformat(fecha_texto)
        hora_valida = datetime.strptime(hora_texto, "%H:%M").time()
        if evento_id < 1 or nuevo_cupo < 1 or not nuevo_lugar:
            print("Verifica el ID, el cupo y el lugar.")
            return
        if fecha_valida < date.today():
            print("La fecha no puede estar en el pasado.")
            return
    except ValueError:
        print("Alguno de los datos no tiene el formato correcto.")
        return

    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT registrados FROM eventos WHERE id = %s", (evento_id,))
        fila = cursor.fetchone()
        if fila is None:
            print("No existe un evento con ese ID.")
            return
        if nuevo_cupo < fila[0]:
            print(f"El nuevo cupo no puede ser menor que los {fila[0]} registros actuales.")
            return

        cursor.execute(
            """UPDATE eventos
               SET fecha = %s, hora = %s, lugar = %s, cupo = %s
               WHERE id = %s""",
            (fecha_valida, hora_valida, nuevo_lugar, nuevo_cupo, evento_id),
        )
        conexion.commit()
        print("Datos del evento modificados.")
    except Error as error:
        if conexion and conexion.is_connected():
            conexion.rollback()
        print(f"No se pudo modificar el evento: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def eventos_proximos():
    """Muestra eventos futuros que todavía tienen lugares libres."""
    conexion = None
    cursor = None
    try:
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, nombre, fecha, hora, lugar,
                      (cupo - registrados) AS lugares_libres
               FROM eventos
               WHERE fecha >= CURDATE() AND registrados < cupo
               ORDER BY fecha, hora"""
        )
        filas = cursor.fetchall()
        if not filas:
            print("No hay próximos eventos con lugares disponibles.")
            return
        print("\n--- PRÓXIMOS EVENTOS DISPONIBLES ---")
        for evento in filas:
            print(
                f"{evento['id']}. {evento['nombre']} | {evento['fecha']} "
                f"{evento['hora']} | {evento['lugar']} | "
                f"Lugares libres: {evento['lugares_libres']}"
            )
    except Error as error:
        print(f"No se pudieron consultar los próximos eventos: {error}")
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def mostrar_menu():
    print("""
========== AGENDA UNIVERSITARIA ==========
1. Ver catálogo de eventos
2. Localizar evento por nombre
3. Consultar disponibilidad por cantidad
4. Registrar asistentes
5. Cancelar registros de asistentes
6. Crear un evento
7. Editar fecha, hora, lugar y cupo
8. Ver próximos eventos disponibles
9. Salir
""")


def ejecutar():
    acciones = {
        "1": listar_eventos,
        "2": localizar_evento,
        "3": consultar_cupos,
        "4": registrar_asistentes,
        "5": retirar_asistentes,
        "6": crear_evento,
        "7": editar_evento,
        "8": eventos_proximos,
    }

    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-9): ").strip()
        if opcion == "9":
            print("Programa finalizado.")
            break
        accion = acciones.get(opcion)
        if accion is None:
            print("Opción no válida. Elige una opción del 1 al 9.")
            continue
        accion()
        input("\nPresiona Enter para volver al menú...")


if __name__ == "__main__":
    try:
        ejecutar()
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario.")
    except Error as error:
        print(f"Error de conexión con MySQL: {error}")
