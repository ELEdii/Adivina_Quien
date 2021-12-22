import random
import socket
import time
import sys
import threading
import pickle
from Personaje import *

BUFFER_SIZE = 1024
JUEGO_TERMINADO = True
CABELLO = 0
OJOS = 1
PIEL = 2
ACCESORIO = 3
GENERO = 4
personajes = []
personaje = Personaje()
listaconexiones = []
identificadores = []
tiros_anteriores = []

def InicializarJuego():
    global JUEGO_TERMINADO
    JUEGO_TERMINADO = False
    global personaje
    personaje = random.choice( personajes )
    print("El personaje que eleji es:"+ str(personaje.nombre))

def CargarPersonajes():
    personajes.append( Personaje("Sora", "Negro", "Negros", "Blanca", "Espada", "Hombre") )
    personajes.append( Personaje("Cloud", "Rubio", "Azules", "Blanca", "Espada", "Hombre") )
    personajes.append( Personaje("Terry", "Rubio", "Azules", "Blanca", "Gorra", "Hombre") )
    personajes.append( Personaje("Samus", "Rubio", "Azules", "Blanca", "Cañon", "Mujer") )
    personajes.append( Personaje("Ken", "Rubio", "Azules", "Blanca", "Nada", "Hombre") )
    personajes.append( Personaje("Ryu", "Negro", "Negros", "Blanca", "Nada", "Hombre") )
    personajes.append( Personaje("Mario", "Negro", "Cafes", "Blanca", "Nada", "Hombre") )
    personajes.append( Personaje("Diddy Kong", "Cafe", "Negro", "Morena", "Banana", "Hombre") )
    personajes.append( Personaje("Pit", "Cafe", "Cafes", "Blanca", "Arco", "Hombre") )
    personajes.append( Personaje("Palutena", "Verde", "Negros", "Blanca", "Baston", "Mujer") )
    personajes.append( Personaje("Joker", "Negro", "Negros", "Blanca", "Antifaz", "Hombre") )


def ServirPorSiempre(socketTcp, numeroConexiones):
    try:
        condicionEsperarJugadores = threading.Condition()
        condicionTurnoActivo = threading.Condition()
        numero_cliente = 1
        while True:
            if( JUEGO_TERMINADO ):
                InicializarJuego() #Selección aleatoriamente de un nuevo personaje

            client_conn, client_addr = socketTcp.accept()
            print("Conectado a", client_addr)
            listaconexiones.append(client_conn)

            #client_conn.sendall(pickle.dumps(personajes)) #Enviando personajes al cliente
            
            #Ejecuta la función de recibir pregunta para el cliente conectado
            thread_read = threading.Thread(target=RecibirPregunta, args=[client_conn, client_addr, condicionEsperarJugadores, condicionTurnoActivo, numero_cliente, ])
            thread_read.start()

            with condicionEsperarJugadores:
                if( int(numeroConexiones) == len(listaconexiones) ):
                    print( "Se han conectado todos los jugadores" )                    
                    thread_read_tiros = threading.Thread(target=GestionarTiros, args=[condicionTurnoActivo, condicionEsperarJugadores, ])
                    thread_read_tiros.start()
                    numero_cliente = 0
                else:
                    print( "En espera de " + str(int(numeroConexiones) - len(listaconexiones)) + " conexiones" )
                condicionEsperarJugadores.notifyAll()            
            
            numero_cliente = numero_cliente + 1
            gestion_conexiones()
    except Exception as e:
        print(e)

def GestionarTiros(condicionTurnoActivo, condicionEsperarJugadores):    
    global JUEGO_TERMINADO
    global ID_TURNO
    
    turnos = 0
    
    while(not JUEGO_TERMINADO):
        time.sleep(0.5)
        #Determina que jugador puede tirar
        with condicionTurnoActivo:
            ID_TURNO = identificadores[turnos % len(identificadores)]
            print( "Turno del jugador: " + str(ID_TURNO) )
            #Notifica que ya se ha determinado al jugador que tiene el turno
            condicionTurnoActivo.notifyAll()

        #Espera a que el jugador notifique que termino su turno
        with condicionEsperarJugadores:
            condicionEsperarJugadores.wait()
        turnos = turnos + 1 
    
    with condicionTurnoActivo:
        condicionTurnoActivo.notifyAll()

    time.sleep(0.5)
    #Manda el resultado final a los clientes
    EnviarTirosAClientes(True, ID_TURNO)
    personaje = Personaje()
    listaconexiones.clear()
    tiros_anteriores.clear()
    print("hilos activos:", threading.active_count())

def gestion_conexiones():
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("hilos activos:", threading.active_count())
    print("conexiones: ", len(listaconexiones))

def EnviarTirosAClientes(JUEGO_TERMINADO = False, identificador = ""):
    i = 0
    for conn in listaconexiones:
        datoEnviar = []
        datoEnviar.append( identificadores[i] == ID_TURNO )
        datoEnviar.append( identificadores[i] )
        datoEnviar.append( tiros_anteriores )
        datoEnviar.append( JUEGO_TERMINADO )
        if( JUEGO_TERMINADO):
            if ( identificador == identificadores[i] ):
                resultado = "Has ganado"
            else:
                resultado = "Has perdido"
            nombre = personaje.nombre
        else:
            resultado = ""
            nombre = ""
        datoEnviar.append( resultado )
        datoEnviar.append( nombre )
        i += 1
        conn.sendall( pickle.dumps(datoEnviar) )
        
        if( JUEGO_TERMINADO ):
            print( "Cerrando conexión " + str(i) )
            conn.close()   

def CompararCaracteristica(caracteristica, valor):
    if ( caracteristica == "nombre" ):
        if(personaje.nombre.lower() == valor):
            global JUEGO_TERMINADO
            JUEGO_TERMINADO = True
        return personaje.nombre.lower() == valor
    elif ( caracteristica == "cabello" ):
        return personaje.caracteristicas[CABELLO].lower() == valor
    elif ( caracteristica == "ojos" ):
        return personaje.caracteristicas[OJOS].lower() == valor
    elif ( caracteristica == "piel" ):
        return personaje.caracteristicas[PIEL].lower() == valor
    elif ( caracteristica == "accesorio" ):
        return personaje.caracteristicas[ACCESORIO].lower() == valor
    elif ( caracteristica == "genero" ):
        return personaje.caracteristicas[GENERO].lower() == valor

def RecibirPregunta(conn, addr, condicionEsperarJugadores, condicionTurnoActivo, identificador):
    #Esperando el inicio del juego
    while True:
        with condicionEsperarJugadores:
            #Esperando notificación de un nuevo cliente conectado
            condicionEsperarJugadores.wait()
            conn.sendall( str(conexiones - len(listaconexiones)).encode() )
            if( conexiones == len(listaconexiones) ):
                print("Enviando inicio de juego")
                break
            #else: #Faltan str(conexiones - len(listaconexiones)).encode() jugadores 
    
    tiro_anterior = ""
    while not JUEGO_TERMINADO:        
        with condicionTurnoActivo:
            #Esperando a que gestión de tiros determine el siguiente turno
            condicionTurnoActivo.wait()            
            if( ID_TURNO == identificador and not JUEGO_TERMINADO):                
                #Espera el tiro del cliente
                with condicionEsperarJugadores:
                    EnviarTirosAClientes(JUEGO_TERMINADO, identificador)
                    print( "Esperando tiro del cliente: ", addr )
                    tiroCliente = pickle.loads( conn.recv(BUFFER_SIZE) )
                    comparacion = CompararCaracteristica( tiroCliente[0].lower(), tiroCliente[1].lower() )
                    if( comparacion ):
                        conn.sendall( str("Correcto, el personaje tiene : " + tiroCliente[0] + " " + tiroCliente[1] ).encode() )
                        tiroCliente.append("Si")
                    else:
                        conn.sendall( str("El personaje no tiene : " + tiroCliente[0] + " " + tiroCliente[1] ).encode() )
                        tiroCliente.append("No")
                    
                    tiros_anteriores.append(tiroCliente)
                    condicionEsperarJugadores.notify() #Notifica al gestor de tiros que el cliente ha tirado
            else:
                print ("No es turno del jugador: " + str(identificador) )

    print("SALIENDO jugador " + str(identificador)  +  " ... ")

def MostrarPersonajes():
    print("Personajes:")
    for personaje in personajes:
        personaje.DescripcionPersonaje()

host, port, numConn = sys.argv[1:4]

if len(sys.argv) != 4:
    print("usage:", sys.argv[0], "<host> <port> <numero jugadores>")
    sys.exit(1)

serveraddr = (host, int(port))
conexiones = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    TCPServerSocket.bind(serveraddr)
    TCPServerSocket.listen(int(numConn))
    conexiones = int(numConn)
    print( "El servidor TCP está disponible y en espera de solicitudes" )
    CargarPersonajes()

    for i in range(1, int(numConn) + 1):
        identificadores.append( i )
    
    ServirPorSiempre(TCPServerSocket, int(numConn))