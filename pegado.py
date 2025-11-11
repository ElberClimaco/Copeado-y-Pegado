import keyboard
import time
import threading
import pyautogui
import customtkinter as ctk
import tkinter as tk

# --- Configuración ---
TIEMPO_LIMITE = 1.0  # segundos
ultimo_copia = 0
ultimo_pega = 0
timer_copia = None
timer_pega = None


# --- Notificación moderna (con animación tipo Windows toast) ---
def mostrar_notificacion(texto, color="#ffffff"):
    def _mostrar():
        root = tk.Tk()
        root.withdraw()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.0)
        root.wm_attributes("-toolwindow", True)
        root.configure(bg="#000000")

        # Tamaño compacto con sombra
        w, h = 150, 35
        frame = ctk.CTkFrame(root, width=w, height=h, corner_radius=15, fg_color="black")
        frame.pack()
        label = ctk.CTkLabel(frame, text=texto, text_color=color, font=("Segoe UI", 9, "bold"))
        label.place(relx=0.5, rely=0.5, anchor="center")

        root.update_idletasks()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        x, y_final = (sw - w) // 2, sh - 100
        y_inicio = y_final + 40  # empieza más abajo (efecto "sube")

        root.geometry(f"{w}x{h}+{x}+{y_inicio}")
        root.deiconify()

        # --- Animaciones ---
        def animar_subida(alpha=0.0, y=y_inicio):
            if alpha < 0.9:
                root.attributes("-alpha", alpha)
                root.geometry(f"{w}x{h}+{x}+{int(y)}")
                root.after(20, animar_subida, alpha + 0.1, y - 3)
            else:
                root.after(1200, fade_out, 0.9)

        def fade_out(alpha):
            if alpha > 0:
                root.attributes("-alpha", alpha)
                root.after(20, fade_out, alpha - 0.1)
            else:
                if root.winfo_exists():
                    root.destroy()

        animar_subida()
        root.mainloop()

    threading.Thread(target=_mostrar, daemon=True).start()


# --- Acciones ---
def copiar():
    pyautogui.hotkey("ctrl", "c")
    mostrar_notificacion("📋 Copiado", "#00ffff")


def pegar():
    pyautogui.hotkey("ctrl", "v")
    mostrar_notificacion("📥 Pegado", "#00ff7f")


# --- Manejadores ---
def manejar_copia(event):
    global ultimo_copia, timer_copia

    if keyboard.is_pressed("ctrl"):
        return

    if keyboard.is_pressed("shift"):
        keyboard.write(">")
        mostrar_notificacion("➡️ Escribiste >", "#ffd700")
        return

    ahora = time.time()

    if ahora - ultimo_copia <= TIEMPO_LIMITE:
        if timer_copia:
            timer_copia.cancel()
        copiar()
        ultimo_copia = 0
        return

    ultimo_copia = ahora

    def escribir_si_no_doble():
        if time.time() - ultimo_copia >= TIEMPO_LIMITE:
            keyboard.write("<")

    timer_copia = threading.Timer(TIEMPO_LIMITE, escribir_si_no_doble)
    timer_copia.start()


def manejar_pega(event):
    global ultimo_pega, timer_pega

    if keyboard.is_pressed("ctrl"):
        return

    if keyboard.is_pressed("shift"):
        keyboard.write("Z")
        return

    ahora = time.time()

    if ahora - ultimo_pega <= TIEMPO_LIMITE:
        if timer_pega:
            timer_pega.cancel()
        pegar()
        ultimo_pega = 0
        return

    ultimo_pega = ahora

    # --- Si no hay doble toque ---
    def escribir_si_no_doble():
        if time.time() - ultimo_pega >= TIEMPO_LIMITE:
            keyboard.write("z")

    # --- Si se presiona otra tecla antes ---
    def escribir_inmediato(evento):
        global timer_pega
        if timer_pega and timer_pega.is_alive():
            timer_pega.cancel()
            keyboard.write("z")
            keyboard.unhook(escribir_inmediato)

    timer_pega = threading.Timer(TIEMPO_LIMITE, escribir_si_no_doble)
    timer_pega.start()

    keyboard.hook(escribir_inmediato)


# --- Enganches ---
keyboard.on_press_key("<", manejar_copia, suppress=True)
keyboard.on_press_key("z", manejar_pega, suppress=True)

print("🟢 Script activo.")
print("   • Doble '<' rápido (≤1s) → Copiar (Ctrl+C)")
print("   • Doble 'z' rápido (≤1s) → Pegar (Ctrl+V)")
print("   • Shift + < → escribe '>'")
print("   • Shift + Z → escribe 'Z'")
print("   • Ctrl + Z → deshacer (normal)")
print("🔴 Ctrl+C para salir.")

keyboard.wait("ctrl+c")
