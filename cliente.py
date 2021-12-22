import socket
import pickle
import os
import datetime
import threading
import sys
import speech_recognition as sr
from Personaje import *

personajes = []
BUFFER_SIZE = 1024
HOST, PORT = sys.argv[1:3]

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

def MostrarPersonajes():
    for personaje in personajes:
        personaje.DescripcionPersonaje()

def ObtenerMensajeVoz():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        os.system( "cls" )
        MostrarPersonajes()
        MostrarTiros(tiros_anteriores)
        print( "Es tu turno de adivinar el personaje\nEscuchando ... ")
        audio = r.listen(source)

        try:    
            return r.recognize_google(audio)	
        except Exception as e:
            return ""

def ObtenerCaracteristica( texto ):
    texto = texto.lower()
    accesorios = ["Nada", "Espada", "Gorra", "Banana", "Baston", "Cañon","Arco"] # "tu personaje tiene <accesorio>"
    nombres = ["Sora","Cloud","Terry","Samus","Ken","Ryu","Mario","Diddy Kong","Pit", "Palutena", "Joker"] #"tu personaje es <genero_nombre>"
    generos = ["Mujer", "Hombre"]
    caracteristicas = [" ojo", " cabello", " piel", " genero"]
    
    i = 0
    for caracteristica in caracteristicas:
        if( caracteristica in texto):
            t = texto.split( caracteristica )
            color = t[1].split(" ")
            if( i == 0):
                caracteristica = caracteristica + "s"
            response = [caracteristica.replace(" ",""), color[1]]
            return response

        i = i + 1
    
    if( "tiene" in texto):
        t = texto.split("tiene")
        acc = t[1]
        for accesorio in accesorios:           
            if( accesorio in acc):
             return ["accesorio", accesorio]             
        return ["accesorio", "nada"]
    else:
        for genero in generos:
            if( genero in texto):
                return ["genero", genero]
        
        for nombre in nombres:
            if( nombre.lower() in texto):
                return ["nombre", nombre]
    return ""

def MostrarTiros(tiros):
    if(len(tiros) > 0):
        print( "\tTiros hasta el momento: ")
        for tiro in tiros:
            print( "\t\t" + tiro[0] + " " + tiro[1] + ": " + tiro[2] )

if len(sys.argv) != 3:
    print( "usage:", sys.argv[0], "<host> <port>" )
    sys.exit(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:    
    TCPClientSocket.connect((HOST, int(PORT) ))

    CargarPersonajes()

    while(True):
        jugadoresFaltantes = TCPClientSocket.recv(100)
        os.system( "cls" )
        if(  jugadoresFaltantes.decode() == "0"):
            print( "Todos los jugadores se han unido ..." )
            break
        else:
            print( "Esperando a " + jugadoresFaltantes.decode() + " jugadores ..." )
    
    tiros_anteriores = []
    
    while(True):
        print( "Esperando datos del servidor" )
        dato = pickle.loads( TCPClientSocket.recv(BUFFER_SIZE) ) # [MI_TURNO?, QUIEN_TIENE_TURNO, TIRO_ANTERIOR, JUEGO_TERMINADO, RESULTADO, PERSONAJE]

        if ( dato[3] ):
            break
        
        if( dato[2] != ""):
            tiros_anteriores = dato[2]
        
        if( dato[0] ):            
            while(True):
                texto = ObtenerMensajeVoz()
                if (texto != ""):
                    tiroCliente = ObtenerCaracteristica( texto )
                    if( tiroCliente != ""):
                        TCPClientSocket.sendall( pickle.dumps(tiroCliente) )
                        resultado = TCPClientSocket.recv(BUFFER_SIZE)
                        break
                print(texto)
                input( "Intentalo de nuevo. Pulsa enter para continuar ..." )
        else:
            os.system( "cls" )
            MostrarPersonajes()
            MostrarTiros(tiros_anteriores)
            print( "Esperando a que el jugador " + str(dato[1]) + " termine su turno." )
    os.system( "cls" )
    MostrarPersonajes()
    print( "El personaje era: " + dato[5] )
    print( dato[4] )
