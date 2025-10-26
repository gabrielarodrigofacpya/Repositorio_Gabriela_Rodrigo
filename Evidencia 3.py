#ev 3 version "4.6"    VERSION "ACTUAL" (TRABAJADA)
import datetime
import sys
import sqlite3
from sqlite3 import Error
import re 

turnos = ("matutino","vespertino","nocturno")

#tablas de registros
try:
    with sqlite3.connect("sistema registro.db") as conn:
        mi_cursor = conn.cursor()

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_del_cliente TEXT NOT NULL, apellido_del_cliente TEXT NOT NULL); ")    #TABLA DE CLIENTES
        print ("Tabla cliente creada existosamente")   #si no aparece esta algo mal

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS salas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_de_sala TEXT NOT NULL, cupo NUMBER NOT NULL); ")  # TABLA DE SALAS 
        print ("Tabla salas creada existosamente")

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS reservaciones (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_del_devento TEXT NOT NULL, clave_del_cliente NUMBER NOT NULL, turno TEXT NOT NULL, fecha_reservacion timestamp, clave_de_sala NUMBER NOT NULL); ")   #TABLA DE RESERVACIONES
        print ("Tabla reservaciones creada existosamente")

except Error as e:
            print (e)
#####################################################################################################################################
def registrar_nuevo_cliente():
    def es_nombre_valido(texto):  #VALIDACION DE LOS DATOS
        return bool(re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ ]+", texto))

    while True:
        nombre = input("Nombre del cliente: ").strip()
        if not nombre:
            print("El nombre es obligatorio.")
            continue
        if not es_nombre_valido(nombre):
            print("El nombre solo puede contener letras y espacios.")
            continue
        break

    while True:
        apellido = input("Apellidos del cliente: ").strip()
        if not apellido:
            print("Los apellidos son obligatorios.")
            continue
        if not es_nombre_valido(apellido):
            print("Los apellidos solo pueden contener letras y espacios.")
            continue
        break
    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("INSERT INTO clientes (nombre_del_cliente, apellido_del_cliente) VALUES (?, ?)", (nombre, apellido) ) #INSERTAR DATOS EN LA TABLA 
            print(f"La clave asignada fue {mi_cursor.lastrowid}")  # ARROJA LAS CLAVES
            print("Registro agregado exitosamente.")
            conn.commit()

    except Error as e:
        print(e)

#####################################################################################################################################
#LISTAR CLIENTE LISTAR SALAS (DATOS A USAR PARA LOS REGISTROS)
#####################################################################################################################################

def listar_clientes():
    """Muestra un listado de todos los clientes registrados"""
    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT id, nombre_del_cliente, apellido_del_cliente FROM clientes ORDER BY id")
            clientes = mi_cursor.fetchall()

            if clientes:
                print("\n=== Listado de Clientes ===")
                print("ID\tNombre Completo")
                print("---------------------------")
                for id_cliente, nombre, apellido in clientes:
                    print(f"{id_cliente}\t{nombre} {apellido}")
                print("---------------------------\n")
            else:
                print("No hay clientes registrados.\n")

    except Error as e:
        print("Error al listar clientes:", e)

def listar_salas():
    """Muestra las salas registradas"""
    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("SELECT id, nombre_de_sala, cupo FROM salas ORDER BY id")
            salas = mi_cursor.fetchall()

            if salas:
                print("\n=== Listado de Salas ===")
                print("ID\tNombre de Sala\tCupo")
                print("---------------------------")
                for id_sala, nombre, cupo in salas:
                    print(f"{id_sala}\t{nombre}\t{cupo}")
                print("---------------------------\n")
            else:
                print("No hay salas registradas.\n")

    except Error as e:
        print("Error al listar salas:", e)

######################################################################################################################################################################################
######################################################################################################################################################################################

def registrar_nueva_sala():

    nombre_sala = input("ingrese el nombre de la nueva sala: ") 
    while True:
        try:
            cupo_de_sala = int(input("ingrese el cupo de la sala: ")) # 
            if cupo_de_sala <= 0:                                     #EVITA QUE EL CUPO SE 0 
                print("El cupo debe ser un número positivo.")
                continue
            break
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número para el cupo.")


    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("INSERT INTO salas (nombre_de_sala, cupo) VALUES (?,?)", (nombre_sala, cupo_de_sala) )    # Inserta los datos 
            print(f"La clave asignada fue {mi_cursor.lastrowid}")           #ARROJA LAS CLAVES
            print ("Sala registrada existosamente")
            conn.commit() 

    except Error as e:
            print (e)
#######################################################################################################################################
def registrar_reservacion():
    listar_clientes()
    listar_salas()

    try:
        clave_del_cliente = int(input("Ingrese la clave del cliente: "))
    except ValueError:
        print("Debe ingresar un número válido para la clave del cliente.")
        return

    # Validar fecha
    while True:
        fecha_reservacion_str = input("Ingrese la fecha de la reservación (MM-DD-AAAA): ").strip()
        try:
            fecha_reservacion = datetime.datetime.strptime(fecha_reservacion_str, "%m-%d-%Y").date()
        except ValueError:
            print("Formato de fecha inválido. Use MM-DD-AAAA .")
            continue

        hoy = datetime.date.today()
        diferencia = (fecha_reservacion - hoy).days
        dia_semana = fecha_reservacion.weekday()  # lunes=0, domingo=6

        if fecha_reservacion < hoy:
            print("No se puede registrar una reservación en una fecha pasada.")
            continue
        if diferencia < 2:
            print("La reservación debe hacerse con al menos 2 días de anticipación.")
            continue
        if dia_semana == 6:
            print("No se pueden hacer reservaciones en domingo.")
            continue
        break

    try:
        clave_sala = int(input("Ingrese la clave de la sala: "))
    except ValueError:
        print("Debe ingresar un número válido para la clave de la sala.")
        return

    while True:
        turno = input("Ingrese el turno (matutino, vespertino, nocturno): ").lower()
        if turno not in turnos:
            print("Turno inválido. Por favor, ingrese matutino, vespertino o nocturno.")
            continue
        break

    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT COUNT(*) 
                FROM reservaciones 
                WHERE clave_de_sala = ? AND turno = ? AND date(fecha_reservacion) = ?
            """, (clave_sala, turno, fecha_reservacion))
            existe = mi_cursor.fetchone()[0]

            if existe > 0:
                print(f"La sala {clave_sala} ya está reservada para el turno '{turno}' en la fecha {fecha_reservacion}.")
                return
    except Error as e:
        print("Error al verificar disponibilidad de sala:", e)
        return

    nombre_reservacion = input("Ingrese el nombre de la reservación o evento: ")

    datos_reservacion = (nombre_reservacion, clave_del_cliente, turno, fecha_reservacion, clave_sala)

    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                INSERT INTO reservaciones (nombre_del_devento, clave_del_cliente, turno, fecha_reservacion, clave_de_sala)
                VALUES (?,?,?,?,?)
            """, datos_reservacion)
            print(f"La clave asignada fue {mi_cursor.lastrowid}")
            print("Registro agregado exitosamente")
            conn.commit()
    except Error as e:
        print(e)

################################################################################################################################################################################

def consultar_reservaciones():                                                                      #
    fecha_consulta_str = input("Ingrese la fecha para consultar reservaciones (MM-DD-AAAA): ").strip()
    try:
        fecha_consulta = datetime.datetime.strptime(fecha_consulta_str, "%m-%d-%Y").date()
    except ValueError:
        print("Formato de fecha inválido. Use MM-DD-AAAA (por ejemplo, 10-30-2025).")
        return
    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()                                      #fetchall como se indico
            mi_cursor.execute("SELECT id, nombre_del_devento, clave_del_cliente, turno, clave_de_sala FROM reservaciones WHERE date(fecha_reservacion) = ? ORDER BY nombre_del_devento", (fecha_consulta,)) # Select specific columns and filter by date
            registros = mi_cursor.fetchall()

            if registros:
                print(f"\nReservaciones para la fecha {fecha_consulta.strftime('%m-%d-%Y')}:")
                print("ID\tEvento\tCliente ID\tTurno\tSala ID")
                print("*" * 50)
                for id, evento, cliente_id, turno, sala_id in registros:
                    print(f"{id}\t{evento}\t{cliente_id}\t{turno}\t{sala_id}")

            else:
                print(f"No se encontraron reservaciones para la fecha {fecha_consulta}")

    except Error as e:
            print (e)
################################################################################################################################################################################
####################################################################################################################################
def modificar_evento():
    """Permite modificar el nombre del evento de una reservación existente"""
    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            
            # Mostrar todas las reservaciones actuales
            mi_cursor.execute("""
                SELECT id, nombre_del_devento, clave_del_cliente, turno, clave_de_sala, fecha_reservacion 
                FROM reservaciones
                ORDER BY fecha_reservacion
            """)
            reservaciones = mi_cursor.fetchall()

            if not reservaciones:
                print("\nNo hay reservaciones registradas para modificar.\n")
                return

            print("\n=== LISTADO DE RESERVACIONES ===")
            print("ID\tEvento\t\tCliente\tTurno\tSala\tFecha")
            print("-----------------------------------------------------------")
            for id_res, evento, cliente, turno, sala, fecha in reservaciones:
                try:
                    fecha_formateada = datetime.datetime.strptime(fecha, "%Y-%m-%d").strftime("%m-%d-%Y")
                except Exception:
                    fecha_formateada = fecha
                print(f"{id_res}\t{evento[:15]:15}\t{cliente}\t{turno}\t{sala}\t{fecha_formateada}")
            print("-----------------------------------------------------------")

            while True:
                try:
                    clave_reservacion = int(input("\nIngrese la clave (ID) de la reservación que desea modificar: "))
                except ValueError:
                    print("Entrada inválida. Ingrese un número de ID.")
                    continue

                mi_cursor.execute("SELECT nombre_del_devento FROM reservaciones WHERE id = ?", (clave_reservacion,))
                resultado = mi_cursor.fetchone()

                if not resultado:
                    print("Clave no válida, ingrese una valida.")
                    continue  # vuelve a pedir la clave
                else:
                    nombre_actual = resultado[0]
                    print(f"\nReservación encontrada: {nombre_actual}")
                    break
###########################################################################################################################
            # Pedir nuevo nombre del evento #(aqui se pide y pone simple)
            nuevo_nombre = input("Ingrese el nuevo nombre para el evento: ").strip()
            if not nuevo_nombre:
                print("El nombre no puede estar vacío. Operación cancelada.")
                return

            # cambia la reservacion en la base de datos       ###########################################################
            mi_cursor.execute("""
                UPDATE reservaciones
                SET nombre_del_devento = ?
                WHERE id = ?
            """, (nuevo_nombre, clave_reservacion))
            conn.commit()

            print(f"\n El nombre del evento ha sido actualizado exitosamente.\nDe: '{nombre_actual}' → A: '{nuevo_nombre}'")

    except Error as e:
        print("Error al modificar el evento:", e)

################################################################################################################################################################################
def menu_de_opciones():
    while True:
        print("\n================ Sistema de Reservaciones ================")
        print("1. Registrar reservación de una sala")
        print("2. Editar nombre de evento de una reservación")
        print("3. Consultar reservaciones para una fecha")
        print("4. Registrar nuevo cliente")
        print("5. Registrar una sala")
        print("6. Salir")

        seleccion = input("Seleccione una opción: ").strip()
        if  seleccion == '1':
            registrar_reservacion()
        elif seleccion == '2':
            modificar_evento()
        elif seleccion == '3':
            consultar_reservaciones()
        elif seleccion == '4':
            registrar_nuevo_cliente()
        elif seleccion == '5':
            registrar_nueva_sala()
        elif seleccion == '6':
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__": 
    try:

        menu_de_opciones()
    except KeyboardInterrupt:
        print("\nInterrupción por teclado. Saliendo.")
