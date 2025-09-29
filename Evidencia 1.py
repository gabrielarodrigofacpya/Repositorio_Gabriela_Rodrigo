#evidencia 1
#"reserva de salas para eventos el pollo feliz "  #es enserio que le pusiste ese nombre??
from datetime import datetime, date, timedelta
import itertools
import sys

clientes = {} #diccionario para el registro de clientes (revisar)
salas = {} #lo mismo de arriba 
reservaciones = {} #LMDA

cliente_id = itertools.count(1)  #Los ids (no comentes cada linea baboso)
sala_id = itertools.count(1)
reservacion_id = itertools.count(1)

def generar_cliente_id():
    return f"cliente {next(cliente_id):04d}"

def generar_sala_id():
    return f"sala {next(sala_id):04d}"

def generar_reservacion_id():
    return f"reserva {next(reservacion_id):04d}"

def fecha_reserva(fch) :
    return datetime.strptime(fch , "%Y-%m-%d").date()

def HOY():
    return date.today()

Turnos = ["Matutino", "Vespertino", "Nocturno"]  

def lista_clientes_orden():
    items = [ (cltid, info['apellidos'], info['nombre']) for cltid, info in clientes.items() ]
    items.sort(key = lambda x :
            (x[1].lower(), x[2].lower()))
    return items

def print_clientes_enlistado():
    registro_clt = lista_clientes_orden()

    if not registro_clt:
        print("NO TENEMOS CLIENTES REGISTRADOS. ")
        return
    
    print(f"{'Clave':<8} {'Apellidos':<25} {'Nombres':<25} ")
    print("-"*50) 

    for cltid, aplld, nmb in registro_clt:
        print(f"{cltid:<8} {aplld:<25} {nmb:<25} ")

def registrar_nv_cliente():                                               #pide SOLO los datos del Cliente
    print("\n --- REGISTRAR NUEVO CLIENTE --- ")

    nombres =  input("Nombre del cliente: ").strip()

    apellidos = input("Apellidos del cliente: ").strip()

    if not nombres or not apellidos: #validar datos
        print("LOS DATOS DEL CLIENTE SON OBLIGATORIOS \n OPERACION TERMINADA. ")
        return
    
    cltid = generar_cliente_id()

    clientes[cltid] = {'nombre': nombres, 'apellidos': apellidos} 
    print(f"EL CLIENTE FUE REGISTRADO. CLAVE DEL CLIENTE:{cltid}")

def registrar_nv_sala():                                                  #datos para el registro de la sala
    print("\n --- REGISTRAR NUEVO SALA --- ")

    nombre_sala = input("Nombre de la Sala: ").strip()

    cupo_sala = input("Cupo de la sala (Numero entero): ").strip()                                                        #obvio que es entero pero nunca falta el graciosito

    try:
        cupo = int(cupo_sala)
        if cupo <= 0: raise ValueError()

    except Exception:
        print("CUPO INVALIDO. OPERACION TERMINADA. ")
        return 
    
    rid = generar_sala_id()                                     
    salas[rid] = {'nombre': nombre_sala, 'cupo': cupo}             
    print(f"Sala registrada. Clave: {rid}")

def salas_disponibles(fecha_rsv, turno):
    ocupadas = set()     #set vacio se llena conforme reservamos las salas 
    for folio, r in reservaciones.items():                      
        if r['fecha'] == fecha_rsv and r['turno'].lower() == turno.lower():  
            ocupadas.add(r['room_id'])                         
    disponibles = [ (rid, info) for rid, info in salas.items() if rid not in ocupadas ]  
    return disponibles 

def registrar_reservacion():                                               #LO QUE AHI DICE
    print("\n--- Registrar reservación ---")                   
    if not clientes:                                            
        print("NO HAY CLIENTES REGISTRADOS, REGISTRE AL MENOS UN CLIENTE.")  
        return                                                 
    if not salas:                                              
        print("NO HAY SALAS REGISTRADAS, REGISTRE AL MENOS UNA SALA .")    
        return
                
    while True:                                                
        print_clientes_enlistado()                                
        cltid = input("Ingrese la clave del cliente (o 'C' para cancelar): ").strip()  
        if cltid.upper() == 'C':                                 
            print("OPERACION CANCELADA.")                      
            return                                            
        if cltid in clientes:                                     
            break                                              
        else:                                                 
            print("Clave inexistente. Intente de nuevo o C para cancelar.")
    
    fechas_min_rsv = HOY() + timedelta(days=2)                    
    while True:                                                
        fecha_a_reservar = input(f"Ingrese la fecha a reservar (YYYY-MM-DD) (>= {fechas_min_rsv}): ").strip()  
        try:                                                   
            d = fecha_reserva(fecha_a_reservar)                           
            if d < fechas_min_rsv:                                   
                print(f"La fecha debe ser al menos {fechas_min_rsv}.")  
                continue                                       
            break                                              
        except Exception:
            print("Formato de fecha inválido. Use DD-MM-AAAA.")

    print("Turnos disponibles:")                               
    for i, t in enumerate(Turnos, start=1):                     
        print(f"{i}. {t}")                                     
    while True:                                                
        turno_escogido = input("Seleccione turno (número): ").strip()  
        if not turno_escogido.isdigit() or not (1 <= int(turno_escogido) <= len(Turnos)):  
            print("Selección inválida.")                       
            continue                                           
        turno = Turnos[int(turno_escogido)-1]                         
        break 

    disponibles = salas_disponibles(d, turno)                
    if not disponibles:                                        
        print("No hay salas disponibles para esa fecha y turno.") 
        return                                                 
    print(f"\nSalas disponibles para {d} ({turno}):")           
    print(f"{'Clave':<8} {'Nombre':<25} {'Cupo':<5}")          
    print("-"*45)                                              
    for rid, info in disponibles:                              
        print(f"{rid:<8} {info['nombre']:<25} {info['cupo']:<5}")    

    while True:                                              
        rid = input("Ingrese la clave de la sala deseada (o 'C' para cancelar): ").strip()  
        if rid.upper() == 'C':                               
            print("Operación cancelada.")                      
            return                                             
        if any(rid == r for r, _ in disponibles):            
            break                                              
        print("Clave de sala inválida. Elija una de las mostradas.")    
        
    while True:
        nombre_del_evento = input ("Ingrese el nombre del evento: ").strip()
        if not nombre_del_evento:
            print("El nombre del evento no puede estar vacio.")
            continue
        break

    reservacion_id = generar_reservacion_id()

    reservaciones[reservacion_id] = { 'cliente_id': cltid, 'sala_id ': rid, 'fecha' : d , 'turno' : turno, 'nombre del evento' : nombre_del_evento, }
    print(f"Reservacion registrada. Folio: {reservacion_id}")

def reservaciones_por_fecha(d):
    print(f"\nReservaciones para {d}: ")
    rows = [(f,r) for f, r in reservaciones.items() if r['fecha'] == d ]        
    if not rows:
        print("No hay reservaciones para esa fecha.")
        return
    print(f"{'folio':<10} {'sala':<8} {'Cliente':<8} {'Turno':<10} {'Evento':<30}")
    print("-"*50)
    for folio, r in rows: 
        print(f"{folio:<10} {r['sala_id']:<8} {r['cliente_id']:<8} {r['turno']:<10} {r['nombre del evento']:<30}")

def consultar_reservaciones_fecha():                           
    fecha_s = input("Ingrese la fecha a consultar (YYYY-MM-DD): ").strip()  
    try:                                                       
        d = generar_reservacion_id(fecha_s)                                
    except Exception:                                          
        print("Formato de fecha inválido.")                  
        return                                                
    reservaciones_por_fecha(d)   

def editar_nombre_de_reservacion():                            
    print("\n--- Editar nombre de evento ---")                                                          
    while True:                                                
        desde_s = input("Fecha desde (YYYY-MM-DD): ").strip()  
        hasta_s = input("Fecha hasta (YYYY-MM-DD): ").strip() 
        try:                                                                                  
            desde = generar_reservacion_id(desde_s)                         
            hasta = generar_reservacion_id(hasta_s)                        
            if desde > hasta:                                  
                print("'Desde' no puede ser posterior a 'Hasta'.")  
                continue                                       
            break                                              
        except Exception:                                      
            print("Formato de fecha inválido. Intente de nuevo.")

    rows = [ (f, r) for f, r in reservaciones.items() if desde <= r['fecha'] <= hasta ] 
    if not rows:                                               
        print("No hay eventos en ese rango de fechas.")       
        return                                                 
    print(f"{'Folio':<10} {'Fecha':<12} {'Sala':<6} {'Turno':<10} {'Evento':<30}")  
    print("-"*80)                                              
    for folio, r in rows:                                     
        print(f"{folio:<10} {r['fecha']:<12} {r['sala_id']:<6} {r['turno']:<10} {r['nombre del evento']:<30}")

    ids_rsv_validos = {f for f, _ in rows}                        
    while True:                                                
        folio = input("Ingrese el folio a editar (o 'C' para cancelar): ").strip() 
        if folio.upper() == 'C':                              
            print("Operación cancelada.")                    
            return                                                                
        if folio not in ids_rsv_validos:                         
            print("Folio inválido o no pertenece al rango mostrado.")  
            continue                                           
        break

    while True:                                                
        nuevo = input("Nuevo nombre del evento: ").strip()     
        if not nuevo:                                         
            print("El nombre del evento no puede estar vacío.")  
            continue                                          
        reservaciones[folio]['nombre del evento'] = nuevo           
        print(f"Reservación {folio} actualizada.")           
        break

def main_menu():                                              
    while True:                                                
        print("\n=== Sistema de Reservaciones - Coworking ===")  
        print("1. Registrar reservación de una sala")          
        print("2. Editar nombre de evento de una reservación") 
        print("3. Consultar reservaciones para una fecha")     
        print("4. Registrar nuevo cliente")                    
        print("5. Registrar una sala")                         
        print("6. Listar clientes")                              
        print("7. Salir")                                      
        choice = input("Seleccione una opción: ").strip()     
        if choice == '1':                                      
            registrar_reservacion()                             
        elif choice == '2':                                   
            editar_nombre_de_reservacion()                      
        elif choice == '3':                                   
            consultar_reservaciones_fecha()                    
        elif choice == '4':                                    
            registrar_nv_cliente()                                  
        elif choice == '5':                                    
            registrar_nv_sala()                                    
        elif choice == '6':                                    
            print_clientes_enlistado()
        elif choice == '7':                                    
            print("Saliendo...")                               
            break                                              
        else:                                                  
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":                                    
    try:                                                      
        main_menu()                                            
    except KeyboardInterrupt:                                  
        print("\nInterrupción por teclado. Saliendo.")        
        sys.exit(0)