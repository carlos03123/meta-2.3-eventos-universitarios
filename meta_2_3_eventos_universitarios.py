"""
Meta 2.3 - Sistema de Eventos Universitarios
Python + MySQL usando mysql-connector-python.

Antes de ejecutar:
1. Instala el conector: pip install mysql-connector-python
2. Cambia USUARIO y CONTRASENA por tus datos locales de MySQL.
3. Ejecuta primero el archivo crear_base_datos.sql en MySQL Workbench.
"""

import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

# Configuracion de conexion: modifica estos valores segun tu instalacion.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "TU_CONTRASENA",
    "database": "eventos_universitarios"
}


def conectar():
    """Abre y devuelve una conexion a la base de datos."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as error:
        print(f"Error al conectar con MySQL: {error}")
        return None


def mostrar_eventos():
    """Muestra todos los eventos almacenados."""
    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, fecha, hora, lugar, cupo, registrados
            FROM eventos
            ORDER BY fecha, hora
        """)
        filas = cursor.fetchall()
        if not filas:
            print("\nNo hay eventos registrados.")
            return

        print("\n{:<4} {:<32} {:<12} {:<8} {:<25} {:>7} {:>11}".format(
            "ID", "NOMBRE", "FECHA", "HORA", "LUGAR", "CUPO", "REGISTRADOS"))
        print("-" * 105)
        for evento in filas:
            print("{:<4} {:<32} {:<12} {:<8} {:<25} {:>7} {:>11}".format(
                evento[0], evento[1][:31], str(evento[2]),
                str(evento[3]), evento[4][:24], evento[5], evento[6]))
    except Error as error:
        print(f"Error al consultar eventos: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def buscar_evento():
    """Busca eventos por una parte del nombre usando parametros SQL."""
    texto = input("Escribe el nombre o parte del nombre: ").strip()
    if not texto:
        print("Debes escribir un texto para buscar.")
        return

    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, fecha, hora, lugar, cupo, registrados
            FROM eventos
            WHERE nombre LIKE %s
            ORDER BY fecha
        """, (f"%{texto}%",))
        filas = cursor.fetchall()
        if filas:
            for e in filas:
                print(f"ID: {e[0]} | {e[1]} | Fecha: {e[2]} | Hora: {e[3]} | "
                      f"Lugar: {e[4]} | Cupo: {e[5]} | Registrados: {e[6]}")
        else:
            print("No se encontraron eventos con ese nombre.")
    except Error as error:
        print(f"Error al buscar eventos: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def consultar_disponibilidad():
    """Lista eventos con suficientes lugares para la cantidad solicitada."""
    try:
        cantidad = int(input("¿Cuántas personas deseas registrar?: "))
        if cantidad <= 0:
            print("La cantidad debe ser mayor que cero.")
            return
    except ValueError:
        print("Ingresa una cantidad entera válida.")
        return

    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, fecha, hora, lugar, cupo - registrados AS disponibles
            FROM eventos
            WHERE cupo - registrados >= %s
            ORDER BY fecha, hora
        """, (cantidad,))
        filas = cursor.fetchall()
        if not filas:
            print("No hay eventos con esa capacidad disponible.")
            return
        for e in filas:
            print(f"ID: {e[0]} | {e[1]} | {e[2]} {e[3]} | {e[4]} "
                  f"| Lugares disponibles: {e[5]}")
    except Error as error:
        print(f"Error al consultar disponibilidad: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def registrar_asistentes():
    """Registra asistentes si el evento existe y cuenta con cupo suficiente."""
    try:
        evento_id = int(input("ID del evento: "))
        cantidad = int(input("Número de asistentes a registrar: "))
        if evento_id <= 0 or cantidad <= 0:
            print("El ID y la cantidad deben ser mayores que cero.")
            return
    except ValueError:
        print("Debes ingresar números enteros válidos.")
        return

    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        conexion.start_transaction()
        cursor = conexion.cursor()
        # FOR UPDATE evita que dos registros simultáneos excedan el cupo.
        cursor.execute(
            "SELECT cupo, registrados FROM eventos WHERE id = %s FOR UPDATE",
            (evento_id,))
        evento = cursor.fetchone()
        if not evento:
            print("El evento no existe.")
            conexion.rollback()
            return

        cupo, registrados = evento
        if cantidad > cupo - registrados:
            print(f"Cupo insuficiente. Lugares disponibles: {cupo - registrados}.")
            conexion.rollback()
            return

        cursor.execute(
            "UPDATE eventos SET registrados = registrados + %s WHERE id = %s",
            (cantidad, evento_id))
        conexion.commit()
        print(f"Registro exitoso. Total de personas registradas: {registrados + cantidad}.")
    except Error as error:
        conexion.rollback()
        print(f"Error al registrar asistentes: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def cancelar_registros():
    """Cancela registros sin permitir que el total sea negativo."""
    try:
        evento_id = int(input("ID del evento: "))
        cantidad = int(input("Número de registros que deseas cancelar: "))
        if evento_id <= 0 or cantidad <= 0:
            print("El ID y la cantidad deben ser mayores que cero.")
            return
    except ValueError:
        print("Debes ingresar números enteros válidos.")
        return

    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        conexion.start_transaction()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT registrados FROM eventos WHERE id = %s FOR UPDATE",
            (evento_id,))
        fila = cursor.fetchone()
        if not fila:
            print("El evento no existe.")
            conexion.rollback()
            return
        registrados = fila[0]
        if cantidad > registrados:
            print(f"No se pueden cancelar {cantidad}; actualmente hay {registrados} registrados.")
            conexion.rollback()
            return

        cursor.execute(
            "UPDATE eventos SET registrados = registrados - %s WHERE id = %s",
            (cantidad, evento_id))
        conexion.commit()
        print(f"Cancelación exitosa. Registros restantes: {registrados - cantidad}.")
    except Error as error:
        conexion.rollback()
        print(f"Error al cancelar registros: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def agregar_evento():
    """Solicita datos y agrega un evento con cero personas registradas."""
    nombre = input("Nombre del evento: ").strip()
    fecha_texto = input("Fecha (AAAA-MM-DD): ").strip()
    hora_texto = input("Hora (HH:MM): ").strip()
    lugar = input("Lugar: ").strip()

    try:
        fecha_valida = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        hora_valida = datetime.strptime(hora_texto, "%H:%M").time()
        cupo = int(input("Cupo máximo: "))
        if not nombre or not lugar:
            print("El nombre y el lugar son obligatorios.")
            return
        if fecha_valida < date.today():
            print("La fecha no puede estar en el pasado.")
            return
        if cupo <= 0:
            print("El cupo debe ser mayor que cero.")
            return
    except ValueError:
        print("Datos inválidos. Usa AAAA-MM-DD, HH:MM y un cupo entero.")
        return

    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO eventos (nombre, fecha, hora, lugar, cupo, registrados)
            VALUES (%s, %s, %s, %s, %s, 0)
        """, (nombre, fecha_valida, hora_valida, lugar, cupo))
        conexion.commit()
        print(f"Evento agregado correctamente. ID asignado: {cursor.lastrowid}")
    except Error as error:
        conexion.rollback()
        print(f"Error al agregar evento: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def modificar_evento():
    """Permite modificar fecha, hora, lugar o cupo de un evento."""
    try:
        evento_id = int(input("ID del evento que deseas modificar: "))
        if evento_id <= 0:
            print("El ID debe ser mayor que cero.")
            return
    except ValueError:
        print("El ID debe ser un número entero.")
        return

    print("¿Qué dato deseas modificar?")
    print("1. Fecha")
    print("2. Hora")
    print("3. Lugar")
    print("4. Cupo")
    opcion = input("Selecciona una opción: ").strip()

    columnas = {
        "1": ("fecha", "Fecha nueva (AAAA-MM-DD): "),
        "2": ("hora", "Hora nueva (HH:MM): "),
        "3": ("lugar", "Lugar nuevo: "),
        "4": ("cupo", "Cupo nuevo: ")
    }
    if opcion not in columnas:
        print("Opción no válida.")
        return

    columna, mensaje = columnas[opcion]
    valor = input(mensaje).strip()
    try:
        if columna == "fecha":
            valor = datetime.strptime(valor, "%Y-%m-%d").date()
            if valor < date.today():
                print("La fecha no puede estar en el pasado.")
                return
        elif columna == "hora":
            valor = datetime.strptime(valor, "%H:%M").time()
        elif columna == "lugar":
            if not valor:
                print("El lugar no puede estar vacío.")
                return
        elif columna == "cupo":
            valor = int(valor)
            if valor <= 0:
                print("El cupo debe ser mayor que cero.")
                return
    except ValueError:
        print("El valor ingresado no tiene el formato correcto.")
        return

    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        cursor = conexion.cursor()
        if columna == "cupo":
            cursor.execute("SELECT registrados FROM eventos WHERE id = %s", (evento_id,))
            fila = cursor.fetchone()
            if not fila:
                print("El evento no existe.")
                return
            if valor < fila[0]:
                print(f"El cupo no puede ser menor que los registrados ({fila[0]}).")
                return

        # El nombre de columna proviene del diccionario fijo, no del usuario.
        consulta = f"UPDATE eventos SET {columna} = %s WHERE id = %s"
        cursor.execute(consulta, (valor, evento_id))
        if cursor.rowcount == 0:
            print("No se encontró el evento o el dato no cambió.")
            conexion.rollback()
            return
        conexion.commit()
        print("Evento actualizado correctamente.")
    except Error as error:
        conexion.rollback()
        print(f"Error al modificar el evento: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def mostrar_eventos_proximos():
    """Muestra eventos de hoy en adelante que aún tengan lugares disponibles."""
    conexion = conectar()
    if not conexion:
        return
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id, nombre, fecha, hora, lugar, cupo - registrados AS disponibles
            FROM eventos
            WHERE fecha >= %s AND registrados < cupo
            ORDER BY fecha, hora
        """, (date.today(),))
        filas = cursor.fetchall()
        if not filas:
            print("No hay eventos próximos con lugares disponibles.")
            return
        print("\nEVENTOS PRÓXIMOS CON DISPONIBILIDAD")
        for e in filas:
            print(f"ID: {e[0]} | {e[1]} | {e[2]} a las {e[3]} | Lugar: {e[4]} "
                  f"| Lugares disponibles: {e[5]}")
    except Error as error:
        print(f"Error al consultar eventos próximos: {error}")
    finally:
        if cursor:
            cursor.close()
        conexion.close()


def menu():
    """Mantiene activo el menú hasta que el usuario elija salir."""
    while True:
        print("\n===== SISTEMA DE EVENTOS UNIVERSITARIOS =====")
        print("1. Mostrar eventos")
        print("2. Buscar evento")
        print("3. Consultar eventos con disponibilidad")
        print("4. Registrar asistentes")
        print("5. Cancelar registros")
        print("6. Agregar evento")
        print("7. Modificar evento")
        print("8. Mostrar eventos próximos")
        print("9. Salir")
        opcion = input("Selecciona una opción: ").strip()

        if opcion == "1":
            mostrar_eventos()
        elif opcion == "2":
            buscar_evento()
        elif opcion == "3":
            consultar_disponibilidad()
        elif opcion == "4":
            registrar_asistentes()
        elif opcion == "5":
            cancelar_registros()
        elif opcion == "6":
            agregar_evento()
        elif opcion == "7":
            modificar_evento()
        elif opcion == "8":
            mostrar_eventos_proximos()
        elif opcion == "9":
            print("Gracias por utilizar el sistema.")
            break
        else:
            print("Opción no válida. Selecciona un número del 1 al 9.")


if __name__ == "__main__":
    menu()
