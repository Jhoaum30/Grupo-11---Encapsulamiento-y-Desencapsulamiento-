"""
SIMULADOR VISUAL DEL MODELO OSI - Interfaz gráfica (tkinter)
Comunicación de Datos - UNEMI - Grupo 11
------------------------------------------------------------------
Muestra en una ventana el proceso de encapsulamiento (PC-A) y
desencapsulamiento (PC-B) de un mensaje a través de las 7 capas del
Modelo OSI, con cajas de colores que se van iluminando capa por capa
y dos "terminales" de texto que narran cada paso en tiempo real.
"""

import tkinter as tk
from tkinter import font as tkfont
import base64

# ----------------------------------------------------------------
# LÓGICA DE ENCAPSULAMIENTO / DESENCAPSULAMIENTO
# (misma lógica del simulador de consola, reutilizada aquí)
# ----------------------------------------------------------------

def capa_aplicacion(mensaje):
    return f"[APP-DATA]{mensaje}"

def capa_presentacion(pdu):
    cod = base64.b64encode(pdu.encode("utf-8")).decode("utf-8")
    return f"[PRES-HDR]{cod}"

def capa_sesion(pdu):
    return f"[SES-HDR|ID:0001]{pdu}"

def capa_transporte(pdu):
    return f"[TRANS-HDR|Puerto:5050->8080]{pdu}"

def capa_red(pdu):
    return f"[RED-HDR|IP:192.168.1.10->192.168.1.20]{pdu}"

def capa_enlace(pdu):
    return f"[ENLACE-HDR|MAC:AA:BB:CC->DD:EE:FF]{pdu}[FCS-OK]"

def capa_fisica(pdu):
    return base64.b64encode(pdu.encode("utf-8")).decode("utf-8")


def des_capa_fisica(bits):
    return base64.b64decode(bits.encode("utf-8")).decode("utf-8")

def des_capa_enlace(trama):
    return trama.replace("[FCS-OK]", "").split("]", 1)[1]

def des_capa_red(paquete):
    return paquete.split("]", 1)[1]

def des_capa_transporte(segmento):
    return segmento.split("]", 1)[1]

def des_capa_sesion(pdu):
    return pdu.split("]", 1)[1]

def des_capa_presentacion(pdu):
    cod = pdu.split("]", 1)[1]
    return base64.b64decode(cod.encode("utf-8")).decode("utf-8")

def des_capa_aplicacion(pdu):
    return pdu.replace("[APP-DATA]", "")


# Definición de las capas para recorrer y pintar en la interfaz
CAPAS_ENCAPS = [
    ("7", "APL", capa_aplicacion),
    ("6", "PRE", capa_presentacion),
    ("5", "SES", capa_sesion),
    ("4", "TRA", capa_transporte),
    ("3", "RED", capa_red),
    ("2", "ENL", capa_enlace),
    ("1", "FIS", capa_fisica),
]

CAPAS_DESENCAPS = [
    ("1", "FIS", des_capa_fisica),
    ("2", "ENL", des_capa_enlace),
    ("3", "RED", des_capa_red),
    ("4", "TRA", des_capa_transporte),
    ("5", "SES", des_capa_sesion),
    ("6", "PRE", des_capa_presentacion),
    ("7", "APL", des_capa_aplicacion),
]

COLOR_FONDO = "#0d1b2a"
COLOR_PANEL = "#14243a"
COLOR_TEXTO = "#e8eef4"
COLOR_ACENTO = "#3fa796"
COLOR_CAJA_EMISOR = "#3fa796"
COLOR_CAJA_RECEPTOR = "#4a7fb5"
COLOR_CAJA_ACTIVA = "#f2a541"
COLOR_TERMINAL_BG = "#081019"
COLOR_TERMINAL_TXT = "#6be675"


class SimuladorOSI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador Modelo OSI - Comunicación de Datos - Grupo 11")
        self.geometry("1150x700")
        self.configure(bg=COLOR_FONDO)
        self.resizable(False, False)

        self.cajas_emisor = {}
        self.cajas_receptor = {}
        self.en_ejecucion = False

        self._construir_encabezado()
        self._construir_barra_entrada()
        self._construir_capas()
        self._construir_terminales()

    # ------------------------------------------------------------
    def _construir_encabezado(self):
        f_titulo = tkfont.Font(family="Arial", size=18, weight="bold")
        f_sub = tkfont.Font(family="Arial", size=11)

        tk.Label(self, text="UNIVERSIDAD ESTATAL DE MILAGRO", font=f_titulo,
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=(14, 0))
        tk.Label(self, text="COMUNICACIÓN DE DATOS  •  GRUPO 11  •  Simulador del Modelo OSI",
                 font=f_sub, bg=COLOR_FONDO, fg=COLOR_ACENTO).pack(pady=(2, 10))

        nota = ("NOTA TÉCNICA: en el emisor (PC-A) el encapsulamiento recorre las capas "
                "7 → 1 (Aplicación hasta Física). En el receptor (PC-B) el desencapsulamiento "
                "recorre las capas 1 → 7 (Física hasta Aplicación) para reconstruir el mensaje.")
        panel = tk.Frame(self, bg=COLOR_PANEL, highlightbackground=COLOR_ACENTO, highlightthickness=1)
        panel.pack(fill="x", padx=20, pady=(0, 12))
        tk.Label(panel, text=nota, wraplength=1080, justify="center", font=("Arial", 9),
                 bg=COLOR_PANEL, fg=COLOR_TEXTO, padx=10, pady=8).pack()

    # ------------------------------------------------------------
    def _construir_barra_entrada(self):
        barra = tk.Frame(self, bg=COLOR_FONDO)
        barra.pack(fill="x", padx=20, pady=(0, 12))

        self.entrada_mensaje = tk.Entry(barra, font=("Arial", 11), width=55)
        self.entrada_mensaje.insert(0, "Mensaje de prueba - Grupo 11")
        self.entrada_mensaje.pack(side="left", ipady=4, padx=(0, 10))

        self.btn_enviar = tk.Button(barra, text="▶ ENVIAR", font=("Arial", 10, "bold"),
                                     bg=COLOR_ACENTO, fg="white", activebackground="#358c81",
                                     relief="flat", padx=14, pady=4, command=self.iniciar_transmision)
        self.btn_enviar.pack(side="left", padx=(0, 8))

        self.btn_reset = tk.Button(barra, text="⟲ REINICIAR", font=("Arial", 10, "bold"),
                                    bg="#5a6472", fg="white", activebackground="#454d58",
                                    relief="flat", padx=14, pady=4, command=self.reiniciar)
        self.btn_reset.pack(side="left")

    # ------------------------------------------------------------
    def _crear_fila_cajas(self, contenedor, capas, color_base, diccionario_cajas):
        fila = tk.Frame(contenedor, bg=COLOR_FONDO)
        fila.pack()
        for numero, nombre, _ in capas:
            caja = tk.Frame(fila, bg=color_base, width=68, height=54, highlightthickness=0)
            caja.pack(side="left", padx=4)
            caja.pack_propagate(False)
            tk.Label(caja, text=nombre, bg=color_base, fg="white",
                     font=("Arial", 10, "bold")).pack(expand=True)
            tk.Label(caja, text=numero, bg=color_base, fg="white",
                     font=("Arial", 7)).pack()
            diccionario_cajas[nombre] = caja

    def _construir_capas(self):
        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(fill="x", padx=20)

        col_izq = tk.Frame(contenedor, bg=COLOR_FONDO)
        col_izq.pack(side="left", expand=True)
        tk.Label(col_izq, text="PC-A · ENCAPSULAMIENTO", font=("Arial", 9, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_CAJA_EMISOR).pack(pady=(0, 4))
        self._crear_fila_cajas(col_izq, CAPAS_ENCAPS, COLOR_CAJA_EMISOR, self.cajas_emisor)

        col_centro = tk.Frame(contenedor, bg=COLOR_FONDO)
        col_centro.pack(side="left", padx=18)
        tk.Label(col_centro, text="CANAL", font=("Arial", 9, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=(20, 0))
        self.lbl_flecha = tk.Label(col_centro, text="— — ▶", font=("Arial", 14, "bold"),
                                    bg=COLOR_FONDO, fg="#666666")
        self.lbl_flecha.pack()

        col_der = tk.Frame(contenedor, bg=COLOR_FONDO)
        col_der.pack(side="left", expand=True)
        tk.Label(col_der, text="PC-B · DESENCAPSULAMIENTO", font=("Arial", 9, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_CAJA_RECEPTOR).pack(pady=(0, 4))
        self._crear_fila_cajas(col_der, CAPAS_DESENCAPS, COLOR_CAJA_RECEPTOR, self.cajas_receptor)

    # ------------------------------------------------------------
    def _construir_terminales(self):
        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=20, pady=14)

        marco_izq = tk.Frame(contenedor, bg=COLOR_FONDO)
        marco_izq.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(marco_izq, text="TERMINAL PC-A (ENCAPSULAMIENTO)", font=("Arial", 9, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor="w")
        self.txt_emisor = tk.Text(marco_izq, bg=COLOR_TERMINAL_BG, fg=COLOR_TERMINAL_TXT,
                                   font=("Consolas", 10), height=16, relief="flat")
        self.txt_emisor.pack(fill="both", expand=True, pady=(4, 0))
        self.txt_emisor.configure(state="disabled")

        marco_der = tk.Frame(contenedor, bg=COLOR_FONDO)
        marco_der.pack(side="left", fill="both", expand=True, padx=(8, 0))
        tk.Label(marco_der, text="TERMINAL PC-B (DESENCAPSULAMIENTO)", font=("Arial", 9, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(anchor="w")
        self.txt_receptor = tk.Text(marco_der, bg=COLOR_TERMINAL_BG, fg="#7fc4ff",
                                     font=("Consolas", 10), height=16, relief="flat")
        self.txt_receptor.pack(fill="both", expand=True, pady=(4, 0))
        self.txt_receptor.configure(state="disabled")

    # ------------------------------------------------------------
    def _escribir(self, widget, texto):
        widget.configure(state="normal")
        widget.insert("end", texto + "\n")
        widget.see("end")
        widget.configure(state="disabled")

    def _resaltar(self, caja_dict, nombre, activo):
        color = COLOR_CAJA_ACTIVA if activo else (
            COLOR_CAJA_EMISOR if caja_dict is self.cajas_emisor else COLOR_CAJA_RECEPTOR)
        caja = caja_dict[nombre]
        caja.configure(bg=color)
        for hijo in caja.winfo_children():
            hijo.configure(bg=color)

    # ------------------------------------------------------------
    def reiniciar(self):
        for widget in (self.txt_emisor, self.txt_receptor):
            widget.configure(state="normal")
            widget.delete("1.0", "end")
            widget.configure(state="disabled")
        for nombre in self.cajas_emisor:
            self._resaltar(self.cajas_emisor, nombre, activo=False)
        for nombre in self.cajas_receptor:
            self._resaltar(self.cajas_receptor, nombre, activo=False)
        self.btn_enviar.configure(state="normal")
        self.en_ejecucion = False

    def iniciar_transmision(self):
        if self.en_ejecucion:
            return
        mensaje = self.entrada_mensaje.get().strip()
        if not mensaje:
            self._escribir(self.txt_emisor, "⚠ Ingrese un mensaje antes de transmitir.")
            return

        self.reiniciar()
        self.en_ejecucion = True
        self.btn_enviar.configure(state="disabled")
        self.mensaje_original = mensaje
        self._escribir(self.txt_emisor, f">>> Mensaje a transmitir desde PC-A: {mensaje}\n")
        self._paso_encapsulamiento(0, mensaje)

    def _paso_encapsulamiento(self, indice, pdu_actual):
        if indice >= len(CAPAS_ENCAPS):
            self._escribir(self.txt_emisor, "\n>>> Bits listos. Transmitiendo por el canal...\n")
            self.bits_transmitidos = pdu_actual
            self.after(700, lambda: self._paso_desencapsulamiento(0, pdu_actual))
            return

        numero, nombre, funcion = CAPAS_ENCAPS[indice]
        pdu_nueva = funcion(pdu_actual)
        self._resaltar(self.cajas_emisor, nombre, activo=True)
        self._escribir(self.txt_emisor, f"[Capa {numero} - {nombre}] {pdu_nueva[:70]}")

        def continuar():
            self._resaltar(self.cajas_emisor, nombre, activo=False)
            self._paso_encapsulamiento(indice + 1, pdu_nueva)

        self.after(500, continuar)

    def _paso_desencapsulamiento(self, indice, pdu_actual):
        if indice >= len(CAPAS_DESENCAPS):
            mensaje_final = pdu_actual
            self._escribir(self.txt_receptor, "\n" + "=" * 46)
            if mensaje_final == self.mensaje_original:
                self._escribir(self.txt_receptor, f"✅ ÉXITO: Mensaje recuperado en PC-B: {mensaje_final}")
            else:
                self._escribir(self.txt_receptor, "❌ ERROR: el mensaje no coincide con el original.")
            self._escribir(self.txt_receptor, "=" * 46)
            self.btn_enviar.configure(state="normal")
            self.en_ejecucion = False
            return

        numero, nombre, funcion = CAPAS_DESENCAPS[indice]
        pdu_nueva = funcion(pdu_actual)
        self._resaltar(self.cajas_receptor, nombre, activo=True)
        self._escribir(self.txt_receptor, f"[Capa {numero} - {nombre}] {pdu_nueva[:70]}")

        def continuar():
            self._resaltar(self.cajas_receptor, nombre, activo=False)
            self._paso_desencapsulamiento(indice + 1, pdu_nueva)

        self.after(500, continuar)


if __name__ == "__main__":
    app = SimuladorOSI()
    app.mainloop()
