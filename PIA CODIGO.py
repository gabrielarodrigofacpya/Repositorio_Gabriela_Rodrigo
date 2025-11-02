import datetime
import sys
import sqlite3
from sqlite3 import Error
import re

turnos = ("matutino","vespertino","nocturno")

try:
    with sqlite3.connect("sistema registro.db") as conn:
        mi_cursor = conn.cursor()

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_del_cliente TEXT NOT NULL, apellido_del_cliente TEXT NOT NULL); ")
        print ("Tabla cliente creada existosamente")

        mi_cursor.execute("CREATE TABLE IF NOT EXISTS salas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre_de_sala TEXT NOT NULL, cupo NUMBER NOT NULL); ")
        print ("Tabla salas creada existosamente")

        mi_cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_del_devento TEXT NOT NULL,
            clave_del_cliente NUMBER NOT NULL,
            turno TEXT NOT NULL,
            fecha_reservacion TIMESTAMP,
            clave_de_sala NUMBER NOT NULL,
            estado_reservacion TEXT DEFAULT 'activa',
            FOREIGN KEY (clave_del_cliente) REFERENCES clientes(id),
            FOREIGN KEY (clave_de_sala) REFERENCES salas(id)
        );
        """)
        print ("Tabla reservaciones creada existosamente")

except Error as e:
            print (e)

def registrar_nuevo_cliente():
    def es_nombre_valido(texto):
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
            mi_cursor.execute("INSERT INTO clientes (nombre_del_cliente, apellido_del_cliente) VALUES (?, ?)", (nombre, apellido) )
            print(f"La clave asignada fue {mi_cursor.lastrowid}")
            print("Registro agregado exitosamente.")
            conn.commit()

    except Error as e:
        print(e)

def registrar_nueva_sala():

    nombre_sala = input("ingrese el nombre de la nueva sala: ")
    while True:
        try:
            cupo_de_sala = int(input("ingrese el cupo de la sala: "))
            if cupo_de_sala <= 0:
                print("El cupo debe ser un número positivo.")
                continue
            break
        except ValueError:
            print("Entrada inválida. Por favor, ingrese un número para el cupo.")


    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("INSERT INTO salas (nombre_de_sala, cupo) VALUES (?,?)", (nombre_sala, cupo_de_sala) )
            print(f"La clave asignada fue {mi_cursor.lastrowid}")
            print ("Sala registrada existosamente")
            conn.commit()

    except Error as e:
            print (e)
def registrar_reservacion():
    listar_clientes()
    try:
        clave_del_cliente = int(input("Ingrese la clave del cliente: "))
    except ValueError:
        print("Debe ingresar un número válido para la clave del cliente.")
        return
        
    while True:
        fecha_reservacion_str = input("Ingrese la fecha de la reservación (MM-DD-AAAA): ").strip()
        try:
            fecha_reservacion = datetime.datetime.strptime(fecha_reservacion_str, "%m-%d-%Y").date()
        except ValueError:
            print("Formato de fecha inválido. Use MM-DD-AAAA.")
            continue

        hoy = datetime.date.today()
        diferencia = (fecha_reservacion - hoy).days
        dia_semana = fecha_reservacion.weekday()

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

    listar_salas()
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

    nombre_reservacion = input("Ingrese el nombre de la reservación o evento: ").strip()
    if not nombre_reservacion:
        print("El nombre del evento no puede estar vacío.")
        return

    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT id, estado_reservacion
                FROM reservaciones
                WHERE clave_de_sala = ? 
                AND turno = ?
                AND date(fecha_reservacion) = ?
            """, (clave_sala, turno, fecha_reservacion))
            existente = mi_cursor.fetchone()

            if existente:
                id_existente, estado = existente
                if estado and estado.lower().strip() != "cancelada":
                    print(f"La sala {clave_sala} ya está reservada para el turno '{turno}' en la fecha {fecha_reservacion}.")
                    return
                else:
                    mi_cursor.execute("""
                        UPDATE reservaciones
                        SET nombre_del_devento = ?, 
                            clave_del_cliente = ?, 
                            turno = ?, 
                            fecha_reservacion = ?, 
                            clave_de_sala = ?, 
                            estado_reservacion = 'activa'
                        WHERE id = ?
                    """, (nombre_reservacion, clave_del_cliente, turno, fecha_reservacion, clave_sala, id_existente))
                    conn.commit()
                    print(f"Reservación reactivada con ID {id_existente}.")
                    return

            mi_cursor.execute("""
                INSERT INTO reservaciones (nombre_del_devento, clave_del_cliente, turno, fecha_reservacion, clave_de_sala)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre_reservacion, clave_del_cliente, turno, fecha_reservacion, clave_sala))
            conn.commit()

            print(f"Nueva reservación creada exitosamente. Clave asignada: {mi_cursor.lastrowid}")

    except Error as e:
        print("Error al registrar la reservación:", e)

def listar_clientes():
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

def listar_reservaciones():
    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT r.id, 
                    r.nombre_del_devento, 
                    c.nombre_del_cliente || ' ' || c.apellido_del_cliente AS nombre_cliente,
                    s.nombre_de_sala,
                    r.turno, 
                    r.fecha_reservacion, 
                    r.estado_reservacion
                FROM reservaciones r
                JOIN clientes c ON r.clave_del_cliente = c.id
                JOIN salas s ON r.clave_de_sala = s.id
                ORDER BY date(r.fecha_reservacion) ASC, r.turno
            """)
            reservaciones = mi_cursor.fetchall()

            if reservaciones:
                print("\n=== Listado General de Reservaciones ===")
                print("ID\tEvento\t\tCliente\t\tSala\tTurno\tFecha\t\tEstado")
                print("--------------------------------------------------------------------------")
                for id_res, evento, cliente, sala, turno, fecha, estado in reservaciones:
                    try:
                        fecha_formateada = datetime.datetime.strptime(fecha, "%Y-%m-%d").strftime("%m-%d-%Y")
                    except Exception:
                        fecha_formateada = fecha
                    print(f"{id_res}\t{evento[:15]:15}\t{cliente[:15]:15}\t{sala[:10]:10}\t{turno:10}\t{fecha_formateada}\t{estado}")
                print("--------------------------------------------------------------------------\n")
            else:
                print("\nNo hay reservaciones registradas.\n")

    except Error as e:
        print("Error al listar reservaciones:", e)

def consultar_reservaciones():
    try:
        fecha_consulta_str = input("Ingrese la fecha a consultar (MM-DD-AAAA): ").strip()
        try:
            fecha_consulta = datetime.datetime.strptime(fecha_consulta_str, "%m-%d-%Y").date()
        except ValueError:
            print("Formato de fecha inválido. Use MM-DD-AAAA.")
            return

        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT r.id,
                    r.nombre_del_devento,
                    c.nombre_del_cliente || ' ' || c.apellido_del_cliente AS nombre_cliente,
                    s.nombre_de_sala,
                    r.turno,
                    r.fecha_reservacion,
                    r.estado_reservacion
                FROM reservaciones r
                JOIN clientes c ON r.clave_del_cliente = c.id
                JOIN salas s ON r.clave_de_sala = s.id
                WHERE date(r.fecha_reservacion) = ?
                AND r.estado_reservacion != 'cancelada'
                ORDER BY r.turno
            """, (fecha_consulta,))
            
            reservaciones = mi_cursor.fetchall()

            if reservaciones:
                print(f"\n=== Reservaciones activas para {fecha_consulta.strftime('%m-%d-%Y')} ===")
                print("ID\tEvento\t\tCliente\t\tSala\tTurno\tEstado")
                print("--------------------------------------------------------------------------")
                for id_res, evento, cliente, sala, turno, fecha, estado in reservaciones:
                    print(f"{id_res}\t{evento[:15]:15}\t{cliente[:15]:15}\t{sala[:10]:10}\t{turno:10}\t{estado}")
                print("--------------------------------------------------------------------------\n")
            else:
                print(f"\nNo hay reservaciones activas para la fecha {fecha_consulta.strftime('%m-%d-%Y')}.\n")

    except Error as e:
        print("Error al consultar reservaciones:", e)

def modificar_evento():
    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()

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
                    continue
                else:
                    nombre_actual = resultado[0]
                    print(f"\nReservación encontrada: {nombre_actual}")
                    break

            nuevo_nombre = input("Ingrese el nuevo nombre para el evento: ").strip()
            if not nuevo_nombre:
                print("El nombre no puede estar vacío. Operación cancelada.")
                return

            mi_cursor.execute("""
                UPDATE reservaciones
                SET nombre_del_devento = ?
                WHERE id = ?
            """, (nuevo_nombre, clave_reservacion))
            conn.commit()

            print(f"\n El nombre del evento ha sido actualizado exitosamente.\nDe: '{nombre_actual}' → A: '{nuevo_nombre}'")

    except Error as e:
        print("Error al modificar el evento:", e)

def cancelar_reservacion():
    listar_reservaciones()
    try:
        id_reservacion = int(input("Ingrese el ID de la reservación a cancelar: "))
    except ValueError:
        print("Debe ingresar un número válido para el ID.")
        return

    try:
        with sqlite3.connect("sistema registro.db") as conn:
            mi_cursor = conn.cursor()
            mi_cursor.execute("""
                SELECT fecha_reservacion, estado_reservacion 
                FROM reservaciones 
                WHERE id = ?
            """, (id_reservacion,))
            registro = mi_cursor.fetchone()

            if not registro:
                print("No existe una reservación con ese ID.")
                return

            fecha_reservacion_str, estado_actual = registro

            if estado_actual and estado_actual.lower().strip() == "cancelada":
                print("La reservación ya está cancelada.")
                return

            try:
                fecha_reservacion = datetime.datetime.strptime(fecha_reservacion_str, "%Y-%m-%d").date()
            except ValueError:
                try:
                    fecha_reservacion = datetime.datetime.strptime(fecha_reservacion_str, "%m-%d-%Y").date()
                except:
                    print("Error: formato de fecha no reconocido en la base de datos.")
                    return

            hoy = datetime.date.today()
            diferencia = (fecha_reservacion - hoy).days

            if diferencia < 2:
                print(f"No se puede cancelar la reservación. Debe hacerse con al menos 2 días de anticipación.\n"
                    f"Fecha del evento: {fecha_reservacion.strftime('%m-%d-%Y')}\nHoy: {hoy.strftime('%m-%d-%Y')}")
                return

            mi_cursor.execute("""
                UPDATE reservaciones
                SET estado_reservacion = 'cancelada'
                WHERE id = ?
            """, (id_reservacion,))
            conn.commit()

            print("Reservación cancelada exitosamente.")

    except Error as e:
        print("Error al cancelar reservación:", e)

def menu_de_opciones():
    while True:
        print("\n================ Sistema de Reservaciones ================")
        print("1. Registrar una reservacion de sala")
        print("2. Editar nombre de evento de una reservación")
        print("3. Consultar reservaciones para una fecha")
        print("4. Cancelar Reservacion")
        print("5. Registrar un nuevo cliente")
        print("6. Registrar una nueva sala")
        print("7. Salir")

        seleccion = input("Seleccione una opción: ").strip()
        if  seleccion == '1':
            registrar_reservacion()
        elif seleccion == '2':
            modificar_evento()
        elif seleccion == '3':
            consultar_reservaciones()
        elif seleccion == '4':
            cancelar_reservacion()
        elif seleccion == '5':
            registrar_nuevo_cliente()
        elif seleccion == '6':
            registrar_nueva_sala()
        elif seleccion == '7':
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    try:

        menu_de_opciones()
    except KeyboardInterrupt:
        print("\nInterrupción por teclado. Saliendo.")