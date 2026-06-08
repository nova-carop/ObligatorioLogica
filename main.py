import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# ==================================================
# CONEXIÓN CON PROLOG
# ==================================================
# Carpeta donde están los archivos .pl
PROLOG_DIR = os.path.dirname(os.path.abspath(os.getcwd()))

def llamar_prolog(archivo_pl, goal):
    """
    Llama a SWI-Prolog con un goal y devuelve el resultado como string.
    archivo_pl: nombre del archivo, ej: "vigenere.pl"
    goal: string con el goal de Prolog, ej: "cifrar(hola, sol, espanol, R), write(R)"
    """
    pl_path = os.path.join(PROLOG_DIR, archivo_pl)
    try:
        resultado = subprocess.run(
            ["swipl", "-q", "-g", goal, "-g", "halt", pl_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        if resultado.returncode != 0 or resultado.stdout.strip() == "":
            error = resultado.stderr.strip()
            return None, f"Error de Prolog: {error if error else 'sin resultado'}"
        return resultado.stdout.strip(), None
    except FileNotFoundError:
        return None, "SWI-Prolog no está instalado o no está en el PATH."
    except subprocess.TimeoutExpired:
        return None, "Prolog tardó demasiado."

def construir_goal(alg, op, texto, especial, idioma):
    """
    Arma el goal de Prolog según el algoritmo y operación.
    Los textos se envuelven en comillas simples para que Prolog los trate como atoms.
    """
    texto_pl   = f"'{texto.lower()}'"
    idioma_pl  = idioma  # espanol / ingles

    if alg == "cesar":
        desp = int(especial)
        if op == "cifrar":
            return "cesar.pl", f"cifrar_lista({texto_pl}, {desp}, {idioma_pl}, R), atomic_list_concat(R, Res), write(Res)"
        else:
            return "cesar.pl", f"descifrar_lista({texto_pl}, {desp}, {idioma_pl}, R), atomic_list_concat(R, Res), write(Res)"
    elif alg == "vigenere":
        clave_pl = f"'{especial.lower()}'"
        if op == "cifrar":
            return "vigenere.pl", f"cifrar({texto_pl}, {clave_pl}, {idioma_pl}, R), write(R)"
        else:
            return "vigenere.pl", f"descifrar({texto_pl}, {clave_pl}, {idioma_pl}, R), write(R)"
    elif alg == "playfair":
        clave_pl = f"'{especial.lower()}'"
        if op == "cifrar":
            return "playfair.pl", f"cifrar({texto_pl}, {clave_pl}, {idioma_pl}, R), write(R)"
        else:
            return "playfair.pl", f"descifrar({texto_pl}, {clave_pl}, {idioma_pl}, R), write(R)"

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================
BG       = "#1e1e2e"
BG2      = "#313244"
AZUL     = "#89b4fa"
TEXTO    = "#cdd6f4"
SUBTEXTO = "#a6adc8"

root = tk.Tk()
root.title("Sistema de Criptografía")
root.geometry("600x500")
root.configure(bg=BG)
root.resizable(False, False)

estado = {"idioma": None, "algoritmo": None, "operacion": None}

# ==================================================
# HELPERS
# ==================================================
def limpiar():
    for w in root.winfo_children():
        w.destroy()

def titulo(texto, sub=None):
    tk.Label(root, text="🪶 Sistema de Criptografía", font=("Segoe UI", 18, "bold"),
             bg=BG, fg=TEXTO).pack(pady=(25, 2))
    tk.Label(root, text="Cifrado César • Vigenère • Playfair", font=("Segoe UI", 9),
             bg=BG, fg=SUBTEXTO).pack()
    tk.Frame(root, bg=AZUL, height=2).pack(fill="x", padx=40, pady=10)
    tk.Label(root, text=texto, font=("Segoe UI", 14, "bold"), bg=BG, fg=TEXTO).pack(pady=(5, 0))
    if sub:
        tk.Label(root, text=sub, font=("Segoe UI", 9), bg=BG, fg=SUBTEXTO).pack()

def botones_navegacion(parent, label_siguiente, cmd_siguiente, cmd_volver=None):
    """Fila de botones: [← Volver]  [Siguiente →]"""
    frame = tk.Frame(parent, bg=BG)
    frame.pack(pady=10)
    if cmd_volver:
        tk.Button(frame, text="← Volver", command=cmd_volver,
                  font=("Segoe UI", 10), bg=BG2, fg=SUBTEXTO,
                  activebackground=BG2, activeforeground=AZUL,
                  relief="flat", padx=15, pady=6, cursor="hand2").pack(side="left", padx=5)
    tk.Button(frame, text=label_siguiente, command=cmd_siguiente,
              font=("Segoe UI", 10, "bold"), bg=AZUL, fg="black",
              activebackground="#74a8f5", relief="flat",
              padx=15, pady=6, cursor="hand2").pack(side="left", padx=5)

def boton_opcion(parent, texto, comando):
    tk.Button(parent, text=texto, command=comando,
              font=("Segoe UI", 12), bg=BG2, fg=TEXTO,
              activebackground=AZUL, activeforeground="black",
              relief="flat", padx=20, pady=10, width=20,
              cursor="hand2").pack(pady=6)

# ==================================================
# PANTALLA 1: IDIOMA
# ==================================================
def pantalla_idioma():
    limpiar()
    titulo("¿En qué idioma?", "Esto afecta si se incluye la Ñ o no")
    frame = tk.Frame(root, bg=BG)
    frame.pack(expand=True)
    boton_opcion(frame, "🇪🇸  Español", lambda: elegir_idioma("espanol"))
    boton_opcion(frame, "🇬🇧  Inglés",  lambda: elegir_idioma("ingles"))

def elegir_idioma(idioma):
    estado["idioma"] = idioma
    pantalla_algoritmo()

# ==================================================
# PANTALLA 2: ALGORITMO
# ==================================================
def pantalla_algoritmo():
    limpiar()
    titulo("¿Qué algoritmo?")
    frame = tk.Frame(root, bg=BG)
    frame.pack(expand=True)
    boton_opcion(frame, "🔐  César",    lambda: elegir_algoritmo("cesar"))
    boton_opcion(frame, "🔑  Vigenère", lambda: elegir_algoritmo("vigenere"))
    boton_opcion(frame, "🏰  Playfair", lambda: elegir_algoritmo("playfair"))
    botones_navegacion(root, "", None, pantalla_idioma)  # solo volver

def elegir_algoritmo(alg):
    estado["algoritmo"] = alg
    pantalla_operacion()

# ==================================================
# PANTALLA 3: OPERACIÓN
# ==================================================
def pantalla_operacion():
    limpiar()
    titulo("¿Qué querés hacer?")
    frame = tk.Frame(root, bg=BG)
    frame.pack(expand=True)
    boton_opcion(frame, "🔒  Cifrar",    lambda: elegir_operacion("cifrar"))
    boton_opcion(frame, "🔓  Descifrar", lambda: elegir_operacion("descifrar"))
    botones_navegacion(root, "", None, pantalla_algoritmo)  # solo volver

def elegir_operacion(op):
    estado["operacion"] = op
    pantalla_entrada()

# ==================================================
# PANTALLA 4: ENTRADA Y RESULTADO
# ==================================================
def pantalla_entrada():
    limpiar()

    alg = estado["algoritmo"]
    op  = estado["operacion"]
    titulo("Ingresá los datos", f"{alg.capitalize()} • {op.capitalize()}")

    frame = tk.Frame(root, bg=BG)
    frame.pack(fill="both", expand=True, padx=40)

    # Campo especial según algoritmo
    if alg == "cesar":
        tk.Label(frame, text="Desplazamiento:", font=("Segoe UI", 10),
                 bg=BG, fg=TEXTO, anchor="w").pack(fill="x", pady=(10,0))
        entry_especial = tk.Entry(frame, font=("Segoe UI", 11), bg=BG2, fg=TEXTO,
                                  insertbackground="white", relief="flat")
        entry_especial.insert(0, "3")
        entry_especial.pack(fill="x", ipady=5, pady=(2,8))
    else:
        tk.Label(frame, text="Clave:", font=("Segoe UI", 10),
                 bg=BG, fg=TEXTO, anchor="w").pack(fill="x", pady=(10,0))
        entry_especial = tk.Entry(frame, font=("Segoe UI", 11), bg=BG2, fg=TEXTO,
                                  insertbackground="white", relief="flat")
        entry_especial.pack(fill="x", ipady=5, pady=(2,8))

    # Texto entrada
    tk.Label(frame, text="Texto:", font=("Segoe UI", 10),
             bg=BG, fg=TEXTO, anchor="w").pack(fill="x")
    txt_entrada = tk.Text(frame, height=4, font=("Segoe UI", 11),
                          bg=BG2, fg=TEXTO, insertbackground="white", relief="flat")
    txt_entrada.pack(fill="x", pady=(2,8))

    # Resultado
    tk.Label(frame, text="Resultado:", font=("Segoe UI", 10),
             bg=BG, fg=TEXTO, anchor="w").pack(fill="x")
    txt_salida = tk.Text(frame, height=3, font=("Consolas", 11),
                         bg=BG2, fg=AZUL, insertbackground="white",
                         relief="flat", state="disabled")
    txt_salida.pack(fill="x", pady=(2,8))

    # Botones — volver desaparece al procesar
    frame_botones = tk.Frame(root, bg=BG)
    frame_botones.pack(pady=5)

    btn_volver = tk.Button(frame_botones, text="← Volver", command=pantalla_operacion,
                           font=("Segoe UI", 10), bg=BG2, fg=SUBTEXTO,
                           activebackground=BG2, activeforeground=AZUL,
                           relief="flat", padx=15, pady=6, cursor="hand2")
    btn_volver.pack(side="left", padx=5)

    def procesar():
        texto = txt_entrada.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Atención", "Ingresá un texto.")
            return

        especial = entry_especial.get().strip()
        if not especial:
            campo = "desplazamiento" if alg == "cesar" else "clave"
            messagebox.showwarning("Atención", f"Ingresá el {campo}.")
            return

        if alg == "cesar" and not especial.lstrip("-").isdigit():
            messagebox.showwarning("Atención", "El desplazamiento debe ser un número.")
            return

        # Llamada a Prolog
        archivo, goal = construir_goal(alg, op, texto, especial, estado["idioma"])
        resultado, error = llamar_prolog(archivo, goal)
        if error:
            messagebox.showerror("Error", error)
            return

        txt_salida.configure(state="normal")
        txt_salida.delete("1.0", tk.END)
        txt_salida.insert(tk.END, resultado)
        txt_salida.configure(state="disabled")

        # Ocultar volver una vez procesado
        btn_volver.pack_forget()

    tk.Button(frame_botones, text="🚀 Procesar", command=procesar,
              font=("Segoe UI", 10, "bold"), bg=AZUL, fg="black",
              activebackground="#74a8f5", relief="flat",
              padx=15, pady=6, cursor="hand2").pack(side="left", padx=5)

# ==================================================
# ARRANCAR
# ==================================================
pantalla_idioma()
root.mainloop()