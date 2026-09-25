"""
==============================================================================
 SIMULADOR INTERACTIVO DEL MODELO OSI
 Comunicación de Datos - UNEMI
 Objetivo: Visualizar el proceso de encapsulamiento y desencapsulamiento
 de datos a través de las 7 capas del Modelo OSI, desde un emisor (PC-A)
 hasta un receptor (PC-B).
==============================================================================
"""

import base64   # Librería estándar para codificar/decodificar en Base64
                 # (simula la conversión de datos a "bits" transmisibles)
import time      # Librería estándar usada para dar pequeñas pausas y que
                 # la simulación se vea paso a paso en pantalla

# ------------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------------------------------------------------

# Lista con el nombre de las 7 capas OSI en el orden en que se ENCAPSULAN
# los datos: desde la capa más cercana al usuario (Aplicación) hasta la
# más cercana al medio físico (Física).
CAPAS_ENCAPSULAMIENTO = [
    "Aplicación",       # Capa 7
    "Presentación",      # Capa 6
    "Sesión",             # Capa 5
    "Transporte",         # Capa 4
    "Red",                # Capa 3
    "Enlace de Datos",    # Capa 2
    "Física",             # Capa 1
]

# Lista con el orden inverso, usada para el DESENCAPSULAMIENTO en PC-B:
# se procesa primero la capa Física y se termina en Aplicación.
CAPAS_DESENCAPSULAMIENTO = list(reversed(CAPAS_ENCAPSULAMIENTO))


# ------------------------------------------------------------------------
# FUNCIONES DE ENCAPSULAMIENTO
# Cada función simula lo que "agrega" cada capa al mensaje original,
# siguiendo el proceso PDU (Protocol Data Unit) del modelo OSI.
# ------------------------------------------------------------------------

def capa_aplicacion(mensaje):
    """
    Nombre: capa_aplicacion
    Objetivo: Representa el punto de partida del mensaje generado por el
              usuario (Capa 7 - Aplicación).
    Parámetros: mensaje (str) -> texto ingresado por el usuario en PC-A.
    Resultado: El mismo mensaje, marcado como dato de la capa de Aplicación.
    Parte del proceso OSI: Capa 7 - Aplicación (inicio del encapsulamiento).
    """
    # Se antepone la etiqueta [APP-DATA] para identificar que este dato
    # nació en la capa de Aplicación. Esta etiqueta luego servirá para
    # que la función des_capa_aplicacion() la reconozca y la retire.
    return f"[APP-DATA]{mensaje}"


def capa_presentacion(pdu):
    """
    Objetivo: Simula la traducción/formato de los datos (Capa 6).
              Aquí se codifica el mensaje en Base64 para representar
              la transformación de formato (cifrado/compresión simulados).
    Parámetros: pdu (str) -> PDU recibida de la capa de Aplicación.
    Resultado: PDU codificada en Base64 con encabezado de Presentación.
    Parte del proceso OSI: Capa 6 - Presentación.
    """
    # 1) Se convierte el texto (pdu) a bytes con encode("utf-8"),
    #    porque base64 solo trabaja con bytes, no con texto directo.
    # 2) b64encode() codifica esos bytes en Base64.
    # 3) decode("utf-8") vuelve a convertir el resultado en texto (str)
    #    para poder seguir concatenando cadenas normalmente.
    codificado = base64.b64encode(pdu.encode("utf-8")).decode("utf-8")

    # Se agrega un encabezado [PRES-HDR|...] que indica qué formato se
    # aplicó, simulando el encabezado que agregaría la capa de Presentación.
    return f"[PRES-HDR|Formato:UTF8->Base64]{codificado}"


def capa_sesion(pdu):
    """
    Objetivo: Simula el establecimiento de una sesión de comunicación
              entre PC-A y PC-B (Capa 5), agregando un identificador
              de sesión a la PDU.
    Parámetros: pdu (str) -> PDU recibida de la capa de Presentación.
    Resultado: PDU con encabezado de sesión (ID de sesión simulado).
    Parte del proceso OSI: Capa 5 - Sesión.
    """
    # Se define un identificador fijo de sesión (en un caso real, este
    # ID sería único y negociado dinámicamente entre PC-A y PC-B).
    id_sesion = "SESSION-ID:0001"

    # Se agrega el encabezado de sesión ANTES de la PDU recibida,
    # tal como ocurre en el encapsulamiento real (cada capa "envuelve"
    # a la anterior).
    return f"[SES-HDR|{id_sesion}]{pdu}"


def capa_transporte(pdu, puerto_origen=5050, puerto_destino=8080):
    """
    Objetivo: Simula la segmentación y el direccionamiento por puertos
              (Capa 4), agregando puertos de origen y destino como
              lo haría TCP/UDP.
    Parámetros: pdu (str), puerto_origen (int), puerto_destino (int).
    Resultado: PDU (segmento) con encabezado de puertos.
    Parte del proceso OSI: Capa 4 - Transporte.
    """
    # Se construye el encabezado de Transporte con los puertos de
    # origen y destino (por defecto 5050 y 8080, pero se pueden pasar
    # otros valores al llamar la función).
    encabezado = f"[TRANS-HDR|Puerto_Origen:{puerto_origen}|Puerto_Destino:{puerto_destino}]"

    # Se concatena el encabezado antes de la PDU recibida, formando
    # el "segmento" de la capa de Transporte.
    return f"{encabezado}{pdu}"


def capa_red(pdu, ip_origen="192.168.1.10", ip_destino="192.168.1.20"):
    """
    Objetivo: Simula el direccionamiento lógico (Capa 3), agregando
              las direcciones IP de origen (PC-A) y destino (PC-B),
              generando así el "paquete".
    Parámetros: pdu (str), ip_origen (str), ip_destino (str).
    Resultado: PDU (paquete) con encabezado de direccionamiento IP.
    Parte del proceso OSI: Capa 3 - Red.
    """
    # Se arma el encabezado de Red con las direcciones IP simuladas
    # de PC-A (origen) y PC-B (destino).
    encabezado = f"[RED-HDR|IP_Origen:{ip_origen}|IP_Destino:{ip_destino}]"

    # Se agrega el encabezado de Red antes del segmento recibido,
    # formando el "paquete" (PDU de la capa de Red).
    return f"{encabezado}{pdu}"


def capa_enlace(pdu, mac_origen="AA:BB:CC:00:11:22", mac_destino="AA:BB:CC:33:44:55"):
    """
    Objetivo: Simula el direccionamiento físico local (Capa 2), agregando
              las direcciones MAC de origen y destino, generando la "trama".
    Parámetros: pdu (str), mac_origen (str), mac_destino (str).
    Resultado: PDU (trama) con encabezado y cola (trailer) de enlace.
    Parte del proceso OSI: Capa 2 - Enlace de Datos.
    """
    # Encabezado de Enlace de Datos con las direcciones MAC simuladas.
    encabezado = f"[ENLACE-HDR|MAC_Origen:{mac_origen}|MAC_Destino:{mac_destino}]"

    # La capa de Enlace de Datos también agrega una "cola" (trailer)
    # llamada FCS (Frame Check Sequence), que en redes reales sirve
    # para detectar errores de transmisión. Aquí se simula como "OK".
    cola = "[FCS-OK]"

    # Se arma la trama completa: encabezado + datos + cola.
    return f"{encabezado}{pdu}{cola}"


def capa_fisica(pdu):
    """
    Objetivo: Simula la conversión final de la trama en una secuencia de
              "bits" transmisibles (Capa 1), aquí representada como una
              cadena Base64 que viaja por el medio de transmisión.
    Parámetros: pdu (str) -> trama completa proveniente de Enlace de Datos.
    Resultado: Cadena en Base64 que representa la señal/bits transmitidos.
    Parte del proceso OSI: Capa 1 - Física.
    """
    # Se codifica TODA la trama (encabezados + datos + cola) en Base64,
    # simbolizando la transformación final a una señal de "bits" que
    # viaja físicamente por el medio de transmisión (cable, wifi, etc.).
    bits_simulados = base64.b64encode(pdu.encode("utf-8")).decode("utf-8")
    return bits_simulados


# ------------------------------------------------------------------------
# FUNCIONES DE DESENCAPSULAMIENTO
# Realizan el proceso inverso, quitando encabezados capa por capa hasta
# recuperar el mensaje original en PC-B.
# ------------------------------------------------------------------------

def des_capa_fisica(bits):
    """
    Objetivo: Convierte la señal de bits (Base64) recibida nuevamente en
              la trama de datos original.
    Parámetros: bits (str) -> cadena Base64 recibida del medio de transmisión.
    Resultado: Trama de Enlace de Datos reconstruida.
    Parte del proceso OSI: Capa 1 - Física (desencapsulamiento).
    """
    # b64decode() revierte la codificación Base64 hecha en capa_fisica().
    # encode/decode se usan igual que antes, para pasar entre bytes y texto.
    return base64.b64decode(bits.encode("utf-8")).decode("utf-8")


def des_capa_enlace(trama):
    """
    Objetivo: Retira el encabezado y la cola (FCS) agregados por Enlace
              de Datos, verificando la integridad simulada de la trama.
    Parámetros: trama (str).
    Resultado: PDU de la capa de Red (paquete).
    Parte del proceso OSI: Capa 2 - Enlace de Datos (desencapsulamiento).
    """
    # Se elimina la cola [FCS-OK] que se agregó al final de la trama.
    sin_cola = trama.replace("[FCS-OK]", "")

    # split("]", 1) divide la cadena en la PRIMERA aparición de "]",
    # separando así el encabezado [ENLACE-HDR|...] del contenido real.
    # [1] toma la segunda parte (todo lo que viene después del encabezado).
    contenido = sin_cola.split("]", 1)[1]
    return contenido


def des_capa_red(paquete):
    """
    Objetivo: Retira el encabezado de direccionamiento IP.
    Parámetros: paquete (str).
    Resultado: PDU de la capa de Transporte (segmento).
    Parte del proceso OSI: Capa 3 - Red (desencapsulamiento).
    """
    # Se descarta el encabezado [RED-HDR|...] de la misma forma que en
    # la función anterior: se corta en el primer "]" y se toma el resto.
    return paquete.split("]", 1)[1]


def des_capa_transporte(segmento):
    """
    Objetivo: Retira el encabezado de puertos origen/destino.
    Parámetros: segmento (str).
    Resultado: PDU de la capa de Sesión.
    Parte del proceso OSI: Capa 4 - Transporte (desencapsulamiento).
    """
    # Se elimina el encabezado [TRANS-HDR|...] agregado en capa_transporte().
    return segmento.split("]", 1)[1]


def des_capa_sesion(pdu):
    """
    Objetivo: Retira el identificador de sesión.
    Parámetros: pdu (str).
    Resultado: PDU de la capa de Presentación.
    Parte del proceso OSI: Capa 5 - Sesión (desencapsulamiento).
    """
    # Se elimina el encabezado [SES-HDR|...] agregado en capa_sesion().
    return pdu.split("]", 1)[1]


def des_capa_presentacion(pdu):
    """
    Objetivo: Decodifica de Base64 a texto plano, revirtiendo la
              transformación de formato.
    Parámetros: pdu (str).
    Resultado: PDU de la capa de Aplicación (texto original con marca APP-DATA).
    Parte del proceso OSI: Capa 6 - Presentación (desencapsulamiento).
    """
    # Primero se retira el encabezado [PRES-HDR|...], quedando solo el
    # contenido codificado en Base64.
    contenido_codificado = pdu.split("]", 1)[1]

    # Luego se decodifica ese contenido de Base64 a texto plano,
    # revirtiendo exactamente lo que hizo capa_presentacion().
    return base64.b64decode(contenido_codificado.encode("utf-8")).decode("utf-8")


def des_capa_aplicacion(pdu):
    """
    Objetivo: Retira la marca [APP-DATA] y entrega el mensaje original
              tal como fue escrito por el usuario en PC-A.
    Parámetros: pdu (str).
    Resultado: Mensaje original (str).
    Parte del proceso OSI: Capa 7 - Aplicación (fin del desencapsulamiento).
    """
    # replace() reemplaza la etiqueta [APP-DATA] por una cadena vacía,
    # dejando únicamente el mensaje original que el usuario escribió.
    return pdu.replace("[APP-DATA]", "")


# ------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE TRANSMISIÓN
# ------------------------------------------------------------------------

def transmitir(mensaje):
    """
    Nombre: transmitir
    Objetivo: Orquesta todo el proceso: toma el mensaje escrito en PC-A,
              lo encapsula a través de las 7 capas, simula el envío por
              el medio físico, y lo desencapsula en PC-B hasta recuperar
              el mensaje original.
    Parámetros: mensaje (str) -> texto ingresado por el usuario.
    Resultado: Imprime en pantalla cada etapa del proceso y retorna el
               mensaje final recuperado en PC-B.
    Parte del proceso OSI: Todas (es la función que coordina las 7 capas
              de encapsulamiento y las 7 de desencapsulamiento).
    """
    # Encabezado visual para identificar el inicio de la simulación.
    print("=" * 70)
    print(" INICIO DE TRANSMISIÓN — PC-A ➜ PC-B")
    print("=" * 70)

    # ---------------- ENCAPSULAMIENTO EN PC-A ----------------
    # A partir de aquí, la variable "pdu" va cambiando en cada paso:
    # cada función de capa recibe la PDU de la capa anterior y le
    # agrega su propio encabezado, simulando el encapsulamiento real.
    print("\n--- PROCESO DE ENCAPSULAMIENTO (PC-A) ---\n")

    # Capa 7 - Aplicación: se genera la PDU inicial con el mensaje del usuario.
    pdu = capa_aplicacion(mensaje)
    print(f"[Capa 7 - Aplicación]      -> {pdu}")
    time.sleep(0.2)  # Pequeña pausa solo para efecto visual en consola

    # Capa 6 - Presentación: se codifica la PDU en Base64.
    pdu = capa_presentacion(pdu)
    print(f"[Capa 6 - Presentación]    -> {pdu}")
    time.sleep(0.2)

    # Capa 5 - Sesión: se agrega el identificador de sesión.
    pdu = capa_sesion(pdu)
    print(f"[Capa 5 - Sesión]          -> {pdu}")
    time.sleep(0.2)

    # Capa 4 - Transporte: se agregan los puertos de origen/destino.
    pdu = capa_transporte(pdu)
    print(f"[Capa 4 - Transporte]      -> {pdu}")
    time.sleep(0.2)

    # Capa 3 - Red: se agregan las direcciones IP de origen/destino.
    pdu = capa_red(pdu)
    print(f"[Capa 3 - Red]             -> {pdu}")
    time.sleep(0.2)

    # Capa 2 - Enlace de Datos: se agregan direcciones MAC y el FCS.
    pdu = capa_enlace(pdu)
    print(f"[Capa 2 - Enlace de Datos] -> {pdu}")
    time.sleep(0.2)

    # Capa 1 - Física: se convierte la trama completa en "bits" (Base64).
    # Nota: aquí la variable cambia de nombre a "bits" porque ya no es
    # una PDU con encabezados legibles, sino la señal final a transmitir.
    bits = capa_fisica(pdu)
    print(f"[Capa 1 - Física]          -> {bits}")
    time.sleep(0.2)

    # ---------------- TRANSMISIÓN POR EL MEDIO ----------------
    # Esta sección solo representa visualmente el "viaje" de los bits
    # desde PC-A hasta PC-B por el medio de transmisión (cable/aire).
    print("\n--- TRANSMISIÓN POR EL MEDIO FÍSICO ---")
    print(f"Bits enviados a PC-B: {bits}\n")
    time.sleep(0.3)

    # ---------------- DESENCAPSULAMIENTO EN PC-B ----------------
    # A partir de aquí se reutiliza la variable "pdu" para ir
    # reconstruyendo el mensaje, quitando un encabezado por capa,
    # en el orden EXACTAMENTE inverso al encapsulamiento.
    print("--- PROCESO DE DESENCAPSULAMIENTO (PC-B) ---\n")

    # Capa 1 - Física: se decodifica la señal de bits recibida.
    pdu = des_capa_fisica(bits)
    print(f"[Capa 1 - Física]          -> {pdu}")
    time.sleep(0.2)

    # Capa 2 - Enlace de Datos: se retira encabezado MAC y cola FCS.
    pdu = des_capa_enlace(pdu)
    print(f"[Capa 2 - Enlace de Datos] -> {pdu}")
    time.sleep(0.2)

    # Capa 3 - Red: se retira encabezado de direcciones IP.
    pdu = des_capa_red(pdu)
    print(f"[Capa 3 - Red]             -> {pdu}")
    time.sleep(0.2)

    # Capa 4 - Transporte: se retira encabezado de puertos.
    pdu = des_capa_transporte(pdu)
    print(f"[Capa 4 - Transporte]      -> {pdu}")
    time.sleep(0.2)

    # Capa 5 - Sesión: se retira el identificador de sesión.
    pdu = des_capa_sesion(pdu)
    print(f"[Capa 5 - Sesión]          -> {pdu}")
    time.sleep(0.2)

    # Capa 6 - Presentación: se decodifica de Base64 a texto plano.
    pdu = des_capa_presentacion(pdu)
    print(f"[Capa 6 - Presentación]    -> {pdu}")
    time.sleep(0.2)

    # Capa 7 - Aplicación: se retira la marca [APP-DATA] y se obtiene
    # finalmente el mensaje original, tal como se escribió en PC-A.
    mensaje_final = des_capa_aplicacion(pdu)
    print(f"[Capa 7 - Aplicación]      -> {mensaje_final}")
    time.sleep(0.2)

    # Resumen final de la transmisión.
    print("\n" + "=" * 70)
    print(" FIN DE TRANSMISIÓN")
    print("=" * 70)
    print(f"\nMensaje original enviado desde PC-A : {mensaje}")
    print(f"Mensaje recibido y recuperado en PC-B: {mensaje_final}")

    # Se compara el mensaje original con el mensaje recuperado para
    # confirmar que todo el proceso de encapsulamiento/desencapsulamiento
    # funcionó correctamente (esto sirve como "prueba" para el informe).
    if mensaje == mensaje_final:
        print("\n✅ El mensaje fue recuperado CORRECTAMENTE en PC-B.")
    else:
        print("\n❌ Hubo un error: el mensaje recuperado no coincide con el original.")

    # Se retorna el mensaje final por si se quiere usar en otra parte
    # del programa (por ejemplo, para pruebas automáticas).
    return mensaje_final


# ------------------------------------------------------------------------
# PROGRAMA PRINCIPAL (MENÚ INTERACTIVO)
# ------------------------------------------------------------------------

def menu():
    """
    Objetivo: Muestra un menú interactivo por consola para que el usuario
              ingrese un mensaje y ejecute la simulación cuantas veces
              desee.
    Parámetros: Ninguno.
    Resultado: Bucle interactivo que llama a transmitir() con el mensaje
               ingresado por el usuario.
    Parte del proceso OSI: Punto de entrada del usuario (interfaz), no
               interviene directamente en una capa OSI.
    """
    # Título del programa.
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║   SIMULADOR DEL MODELO OSI - ENCAPSULAMIENTO/DESENCAPSULAMIENTO ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    # Bucle infinito: el menú se repite hasta que el usuario elija "Salir".
    while True:
        print("\nOpciones:")
        print("  1. Enviar un mensaje de PC-A a PC-B")
        print("  2. Salir")

        # input() lee lo que el usuario escribe por teclado.
        # strip() elimina espacios en blanco al inicio/final de la respuesta.
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            # Se solicita el mensaje que el usuario quiere transmitir.
            mensaje = input("\nIngrese el mensaje a transmitir desde PC-A: ")

            # Validación simple: no permitir mensajes vacíos.
            if mensaje.strip() == "":
                print("⚠ El mensaje no puede estar vacío.")
                continue  # Vuelve al inicio del bucle sin llamar a transmitir()

            # Se llama a la función principal que ejecuta toda la simulación.
            transmitir(mensaje)

        elif opcion == "2":
            # Se termina el bucle y el programa finaliza.
            print("\nSaliendo del simulador. ¡Hasta pronto!")
            break

        else:
            # Cualquier otra opción ingresada se considera inválida.
            print("⚠ Opción no válida. Intente nuevamente.")


# Este bloque asegura que menu() solo se ejecute si el archivo se corre
# directamente (por ejemplo, con "python3 simulador_osi.py"), y no si
# este archivo es importado como módulo desde otro programa.
if __name__ == "__main__":
    menu()