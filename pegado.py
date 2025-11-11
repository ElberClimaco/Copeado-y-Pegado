# ---------------------------- IMPORTACIÓN DE MÓDULOS ----------------------------

import keyboard        # Permite detectar y manejar eventos de teclado globales.
import time            # Se usa para medir tiempos y controlar intervalos.
import threading       # Permite ejecutar tareas en paralelo (por ejemplo, mostrar mensajes sin bloquear).
import pyautogui       # Permite controlar el teclado y el mouse (usado para enviar Ctrl+C y Ctrl+V).
import customtkinter as ctk  # Biblioteca moderna para interfaces Tkinter estilizadas.
import tkinter as tk   # Módulo gráfico estándar de Python (base de las ventanas).
from PIL import Image, ImageDraw, ImageTk  # PIL (Pillow) se usa para crear imágenes con bordes redondeados.


# ---------------------------- VARIABLES DE CONFIGURACIÓN ----------------------------

TIEMPO_LIMITE = 1.0   # Tiempo límite (en segundos) para detectar doble pulsación.
ultimo_copia = 0      # Guarda el tiempo de la última vez que se presionó "<".
ultimo_pega = 0       # Guarda el tiempo de la última vez que se presionó "z".
timer_copia = None    # Temporizador para la acción de copiar.
timer_pega = None     # Temporizador para la acción de pegar.
doble_pega = False    # Bandera para saber si se hizo doble pulsación de "z" (evita escribir "z" después de pegar).


# ---------------------------- FUNCIÓN DE NOTIFICACIÓN VISUAL ----------------------------
def mostrar_notificacion(texto, color="#ffffff"):
    """
    Muestra una notificación emergente moderna con bordes redondeados
    y efecto de transparencia (fade in/out), sin icono en la barra de tareas.
    """

    def _mostrar():  # Función interna que crea la ventana en un hilo independiente
        # Crear la ventana base
        root = tk.Tk()
        root.overrideredirect(True)           # Quita los bordes y botones de la ventana.
        root.attributes("-topmost", True)     # Hace que la ventana siempre esté sobre las demás.
        root.attributes("-transparentcolor", "gray17")  # Define un color como transparente real.
        root.wm_attributes("-toolwindow", True)          # Evita que aparezca en la barra de tareas.

        # Configuración del tamaño y radio de los bordes
        w, h, r = 160, 40, 20

        # --- Crear fondo con bordes redondeados usando Pillow (PIL) ---
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))       # Crea una imagen transparente.
        draw = ImageDraw.Draw(img)
        # Dibuja un rectángulo redondeado (negro translúcido con opacidad 200)
        draw.rounded_rectangle((0, 0, w, h), radius=r, fill=(0, 0, 0, 200))
        bg = ImageTk.PhotoImage(img)  # Convierte la imagen en formato usable por Tkinter.

        # --- Crear el Canvas transparente donde se mostrará la imagen ---
        canvas = tk.Canvas(root, width=w, height=h, highlightthickness=0, bg="gray17", bd=0)
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=bg)  # Dibuja la imagen redondeada como fondo.
        canvas.image = bg  # Guarda referencia para evitar que Python borre la imagen de memoria.

        # --- Agrega el texto centrado en la notificación ---
        canvas.create_text(
            w // 2, h // 2,
            text=texto,       # El texto a mostrar (por ejemplo: “📋 Copiado”)
            fill=color,       # Color del texto.
            font=("Segoe UI", 10, "bold")  # Fuente moderna.
        )

        # --- Posiciona la notificación en el centro inferior de la pantalla ---
        root.update_idletasks()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x, y = (sw - w) // 2, sh - 110  # Centrada horizontalmente, 110 px arriba del borde inferior.
        root.geometry(f"{w}x{h}+{x}+{y}")

        # --- Animación de aparición (fade in) y desaparición (fade out) ---
        def fade_in(alpha=0.0):
            """Aumenta la opacidad gradualmente."""
            if alpha < 0.95:
                root.attributes("-alpha", alpha)
                root.after(25, fade_in, alpha + 0.1)
            else:
                root.after(1000, fade_out, 0.95)  # Espera 1s y luego comienza a desaparecer.

        def fade_out(alpha):
            """Reduce la opacidad gradualmente hasta desaparecer."""
            if alpha > 0:
                root.attributes("-alpha", alpha)
                root.after(25, fade_out, alpha - 0.1)
            else:
                root.destroy()  # Destruye la ventana cuando termina la animación.

        fade_in()  # Inicia la animación.
        root.mainloop()  # Mantiene la ventana activa mientras está visible.

    # Inicia la función en un hilo separado (para no bloquear el programa principal).
    threading.Thread(target=_mostrar, daemon=True).start()


# ---------------------------- FUNCIONES DE ACCIÓN ----------------------------

def copiar():
    """Ejecuta Ctrl+C (copiar) y muestra una notificación."""
    pyautogui.hotkey("ctrl", "c")  # Simula la combinación de teclas Ctrl+C.
    mostrar_notificacion("📋 Copiado", "#00ffff")  # Muestra mensaje visual.


def pegar():
    """Ejecuta Ctrl+V (pegar) y muestra una notificación."""
    pyautogui.hotkey("ctrl", "v")  # Simula Ctrl+V.
    mostrar_notificacion("📥 Pegado", "#00ff7f")


# ---------------------------- MANEJADOR DE TECLA “<” (copiar) ----------------------------
def manejar_copia(event):
    """
    Detecta si la tecla '<' se presionó dos veces rápidamente para copiar,
    o una sola vez para escribir el carácter '<'.
    """
    global ultimo_copia, timer_copia

    # Evita interferir si el usuario usa Ctrl o Shift junto con la tecla.
    if keyboard.is_pressed("ctrl"):
        return
    if keyboard.is_pressed("shift"):
        keyboard.write(">")
        mostrar_notificacion("➡️ Escribiste >", "#ffd700")
        return

    ahora = time.time()  # Guarda el momento actual.

    # Si el intervalo entre dos pulsaciones es menor o igual al límite → COPIAR
    if ahora - ultimo_copia <= TIEMPO_LIMITE:
        if timer_copia:
            timer_copia.cancel()  # Cancela el temporizador de escritura normal.
        copiar()  # Ejecuta Ctrl+C
        ultimo_copia = 0
        return

    # Si es la primera pulsación → espera un segundo por posible doble toque.
    ultimo_copia = ahora
    timer_copia = threading.Timer(TIEMPO_LIMITE, lambda: keyboard.write("<"))
    timer_copia.start()


# ---------------------------- MANEJADOR DE TECLA “z” (pegar) ----------------------------
def manejar_pega(event):
    """
    Detecta si la tecla 'z' se presionó dos veces rápidamente para pegar,
    o una sola vez para escribir 'z'.
    """
    global ultimo_pega, timer_pega, doble_pega

    # Evita interferir con combinaciones de teclado (Ctrl+Z o Shift+Z)
    if keyboard.is_pressed("ctrl"):
        return
    if keyboard.is_pressed("shift"):
        keyboard.write("Z")
        return

    ahora = time.time()

    # Si se presiona dos veces rápido (dentro del TIEMPO_LIMITE) → PEGAR
    if ahora - ultimo_pega <= TIEMPO_LIMITE:
        if timer_pega:
            timer_pega.cancel()  # Cancela escritura normal.
        doble_pega = True        # Marca que se realizó un “doble toque”.
        pegar()                  # Ejecuta Ctrl+V
        ultimo_pega = 0
        return

    # Si no hubo doble toque, guarda el tiempo y espera posible segunda pulsación.
    ultimo_pega = ahora
    doble_pega = False

    # Si después de 1 segundo no hay segunda pulsación, se escribe “z”.
    def escribir_si_no_doble():
        if not doble_pega and time.time() - ultimo_pega >= TIEMPO_LIMITE:
            keyboard.write("z")

    timer_pega = threading.Timer(TIEMPO_LIMITE, escribir_si_no_doble)
    timer_pega.start()


# ---------------------------- ENGANCHE DE EVENTOS DE TECLADO ----------------------------

# Asocia la tecla '<' con la función manejar_copia.
keyboard.on_press_key("<", manejar_copia, suppress=True)

# Asocia la tecla 'z' con la función manejar_pega.
keyboard.on_press_key("z", manejar_pega, suppress=True)


# ---------------------------- MENSAJE DE ESTADO EN CONSOLA ----------------------------
print("🟢 Script activo.")
print("   • Doble '<' rápido (≤1s) → Copiar (Ctrl+C)")
print("   • Doble 'z' rápido (≤1s) → Pegar (Ctrl+V)")
print("   • Shift + < → escribe '>'")
print("   • Shift + Z → escribe 'Z'")
print("   • Ctrl + Z → deshacer (normal)")
print("🔴 Ctrl+C para salir.")


# ---------------------------- ESPERA INFINITA ----------------------------
keyboard.wait("ctrl+s")  # Mantiene el script corriendo hasta que se presione Ctrl+C para salir.

