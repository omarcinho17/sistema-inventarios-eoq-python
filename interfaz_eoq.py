"""
Interfaz grafica para los modelos de inventario EOQ.
Usa los cálculos de eoq_faltantes.py (el backend).

Ejecutar:  python3 interfaz_eoq.py
"""

import tkinter as tk
from tkinter import ttk, messagebox

from eoq_faltantes import (
    eoq_clasico, eoq_con_faltantes, eoq_produccion, eoq_produccion_faltantes,
    eoq_descuentos, eoq_seguridad, leer_niveles, a_numero,
)


AZUL = "#1f5fa8"
ROJO = "#b03a2e"
VERDE = "#2e7d32"

# campos de datos: clave  (texto, valor por defecto)
CAMPOS = {
    "D": ("Demanda anual (D)", 20000),
    "S": ("Costo de ordenar (S)", 40),
    "C": ("Costo unitario (C)", 14),
    "i": ("Tasa de mantener (i)", 0.2),
    "H": ("Costo mantener H (vacío = i·C)", ""),
    "Cf": ("Costo por faltante (Cf)", 20),
    "P": ("Tasa de producción anual (P)", 40000),
    "L": ("Tiempo de entrega L (días)", 5),
    "sigma": ("Desv. est. demanda diaria (σd)", 10),
    "nivel": ("Nivel de servicio", 0.95),
    "niveles": ("Precios  cantidad:precio", "0:14; 2000:13.5; 5000:13"),
    "dias": ("Días hábiles al año", 365),
}
CAMPOS_TEXTO = {"niveles"}
CAMPOS_CERO = {"L", "sigma"}  # pueden valer cero
CAMPOS_OPCIONALES = {"H"}     # pueden dejarse vacíos


def costo_H(d):
    """H directo si el usuario lo escribió; si no, H = i · C."""
    return d["H"] if d.get("H") else d["i"] * d["C"]


#  Formatos de resultados 

def unidades(r, clave):
    return f"{r[clave]:,.2f} u"


def redondeo(r, clave):
    return f"{r[clave + '_exacta']:.4f} ≈ {r[clave]} u"


def dinero(r, clave):
    return f"${r[clave]:,.2f}"


def en_dias(r, clave):
    return f"{r[clave]:.4f} días"


def tabla_descuentos(r):
    lineas = []
    for n in r["evaluacion"]:
        costo = f"${n['costo_total']:,.2f}" if "costo_total" in n else "—"
        marca = "◀" if n["minimo"] == r["minimo"] else " "
        lineas.append(f"≥{n['minimo']:<6g} ${n['precio']:<6g} Q={n['Q']:<8.2f} "
                      f"{n['estado']:<11} {costo} {marca}")
    return "\n".join(lineas)


# filas de resultados: (clave, texto, formato)  None = separador
SEP = None
FILA_Q = ("Q", "Q  (cantidad óptima)", redondeo)
FILA_SF = ("Sf", "Sf (faltante máximo)", redondeo)
FILA_IMAX = ("Imax", "Imax (inventario máximo)", unidades)
FILAS_COSTO = [
    ("costo_compra", "Costo de compra  D·C", dinero),
    ("costo_ordenar", "Costo de ordenar  S·D/Q", dinero),
    ("costo_mantener", "Costo de mantener", dinero),
]
FILA_FALTANTE = ("costo_faltante", "Costo de faltante", dinero)
FILA_TOTAL = ("costo_total", "COSTO TOTAL ANUAL", dinero)
FILA_D = ("d", "d  (demanda diaria)", lambda r, c: f"{r[c]:.4f} u/día")
FILA_N = ("N", "N  (pedidos al año)", lambda r, c: f"{r[c]:.4f}")
FILA_T = ("T", "T  (tiempo entre órdenes)", lambda r, c: f"{r[c]:.4f} ≈ {round(r[c])} días")


# perfiles para la grafica (un ciclo) 
# puntos: [(t, nivel)], marcas: [(nivel, texto)] en el eje Y,
# lineas: [(nivel, texto, color)] horizontales, tramos: [(t_ini, t_fin, texto, es_escasez)]

def perfil_clasico(r):
    lineas = [(r["R"], f"R={r['R']:.1f}", VERDE)] if r.get("R", 0) > 0 else []
    return {"puntos": [(0, r["Imax"]), (r["T"], 0)], "T": r["T"],
            "marcas": [(r["Imax"], f"Q={r['Imax']:.0f}"), (0, "0")], "lineas": lineas}


def perfil_faltantes(r):
    return {"puntos": [(0, r["Imax"]), (r["T"], -r["Sf_exacta"])], "T": r["T"],
            "marcas": [(r["Imax"], f"Imax={r['Imax']:.0f}"), (0, "0"), (-r["Sf_exacta"], f"-Sf={r['Sf']}")],
            "tramos": [(0, r["t1"], "t1", False), (r["t1"], r["T"], "t2", True)]}


def perfil_produccion(r):
    return {"puntos": [(0, 0), (r["t1"], r["Imax"]), (r["T"], 0)], "T": r["T"],
            "marcas": [(r["Imax"], f"Imax={r['Imax']:.0f}"), (0, "0")],
            "tramos": [(0, r["t1"], "t1", False), (r["t1"], r["T"], "t2", False)]}


def perfil_produccion_faltantes(r):
    t1, t2, t3, t4 = r["t1"], r["t2"], r["t3"], r["t4"]
    sf = r["Sf_exacta"]
    return {"puntos": [(0, -sf), (t4, 0), (t4 + t1, r["Imax"]),
                       (t4 + t1 + t2, 0), (r["T"], -sf)], "T": r["T"],
            "marcas": [(r["Imax"], f"Imax={r['Imax']:.0f}"), (0, "0"), (-sf, f"-Sf={r['Sf']}")],
            "tramos": [(0, t4, "t4", True), (t4, t4 + t1, "t1", False),
                       (t4 + t1, t4 + t1 + t2, "t2", False), (t4 + t1 + t2, r["T"], "t3", True)]}


def perfil_seguridad(r):
    return {"puntos": [(0, r["Imax"]), (r["T"], r["SS"])], "T": r["T"],
            "marcas": [(r["Imax"], f"Q+SS={r['Imax']:.0f}"), (0, "0")],
            "lineas": [(r["SS"], f"SS={r['SS']:.1f}", ROJO), (r["R"], f"R={r['R']:.1f}", VERDE)]}


# definicion de los modelos 

MODELOS = {
    "EOQ clásico (sin faltantes)": {
        "campos": ["D", "S", "C", "i", "H", "L", "dias"],
        "calcular": lambda d: eoq_clasico(d["D"], d["S"], costo_H(d), d["C"], d["dias"], d["L"]),
        "filas": [FILA_Q, FILA_IMAX, ("R", "R  (punto de reorden)", unidades), SEP,
                  *FILAS_COSTO, FILA_TOTAL, SEP, FILA_N, FILA_D, FILA_T],
        "perfil": perfil_clasico,
    },
    "EOQ con faltantes planeados": {
        "campos": ["D", "S", "C", "i", "H", "Cf", "dias"],
        "calcular": lambda d: eoq_con_faltantes(d["D"], d["S"], costo_H(d), d["Cf"], d["C"], d["dias"]),
        "filas": [FILA_Q, FILA_SF, FILA_IMAX, SEP, *FILAS_COSTO, FILA_FALTANTE, FILA_TOTAL, SEP,
                  FILA_N, FILA_D, FILA_T, ("t1", "t1 (dura el inventario)", en_dias),
                  ("t2", "t2 (tiempo de escasez)", en_dias)],
        "perfil": perfil_faltantes,
    },
    "EOQ de producción (sin faltantes)": {
        "campos": ["D", "S", "C", "i", "H", "P", "dias"],
        "calcular": lambda d: eoq_produccion(d["D"], d["S"], costo_H(d), d["C"], d["P"], d["dias"]),
        "filas": [FILA_Q, FILA_IMAX, SEP, *FILAS_COSTO, FILA_TOTAL, SEP,
                  FILA_N, FILA_D, ("p", "p  (producción diaria)", lambda r, c: f"{r[c]:.4f} u/día"), FILA_T,
                  ("t1", "t1 (tiempo produciendo)", en_dias),
                  ("t2", "t2 (solo consumiendo)", en_dias)],
        "perfil": perfil_produccion,
    },
    "EOQ de producción con faltantes": {
        "campos": ["D", "S", "C", "i", "H", "Cf", "P", "dias"],
        "calcular": lambda d: eoq_produccion_faltantes(d["D"], d["S"], costo_H(d), d["Cf"],
                                                       d["C"], d["P"], d["dias"]),
        "filas": [FILA_Q, FILA_SF, FILA_IMAX, SEP, *FILAS_COSTO, FILA_FALTANTE, FILA_TOTAL, SEP,
                  FILA_N, FILA_D, FILA_T, ("t1", "t1 (produce y acumula)", en_dias),
                  ("t2", "t2 (consume inventario)", en_dias),
                  ("t3", "t3 (acumula faltantes)", en_dias),
                  ("t4", "t4 (cubre faltantes)", en_dias)],
        "perfil": perfil_produccion_faltantes,
    },
    "EOQ con descuentos por cantidad": {
        "campos": ["D", "S", "i", "niveles", "dias"],
        "calcular": lambda d: eoq_descuentos(d["D"], d["S"], d["i"], d["niveles"], d["dias"]),
        "filas": [("Q", "Q  (cantidad a pedir)", lambda r, c: f"{r[c]:.4f} ≈ {round(r[c])} u"),
                  ("precio", "Precio unitario elegido", dinero),
                  ("H", "H = i · precio", dinero), SEP,
                  *FILAS_COSTO, FILA_TOTAL, SEP, FILA_N, FILA_T, SEP,
                  ("evaluacion", "Evaluación por nivel", lambda r, c: tabla_descuentos(r))],
        "perfil": perfil_clasico,
    },
    "EOQ con inventario de seguridad": {
        "campos": ["D", "S", "C", "i", "H", "L", "sigma", "nivel", "dias"],
        "calcular": lambda d: eoq_seguridad(d["D"], d["S"], costo_H(d), d["C"], d["dias"],
                                            d["L"], d["sigma"], d["nivel"]),
        "filas": [FILA_Q, ("z", "z  (valor de la normal)", lambda r, c: f"{r[c]:.4f}"),
                  ("sigma_L", "σL = σd·√L", lambda r, c: f"{r[c]:.4f} u"),
                  ("SS", "SS (inventario de seguridad)", unidades),
                  ("R", "R  (punto de reorden)", unidades), SEP,
                  *FILAS_COSTO, ("costo_seguridad", "Costo de seguridad  H·SS", dinero),
                  FILA_TOTAL, SEP, FILA_N, FILA_D, FILA_T],
        "perfil": perfil_seguridad,
    },
}


class InterfazEOQ:
    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Sistema de Inventario - Modelos EOQ")
        raiz.geometry("980x720")
        raiz.minsize(860, 640)

        self.entradas = {}
        self.etiquetas_resultado = {}
        self.resultado = None

        self._crear_selector()
        self.marco_datos = ttk.LabelFrame(self.raiz, text="Datos del problema", padding=12)
        self.marco_datos.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.marco_resultados = ttk.LabelFrame(self.raiz, text="Resultados", padding=12)
        self.marco_resultados.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self._crear_grafica()

        self.cambiar_modelo()

    # construccion de la ventana 

    def _crear_selector(self):
        marco = ttk.Frame(self.raiz, padding=(10, 10, 10, 0))
        marco.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(marco, text="Modelo:").pack(side="left")
        self.selector = ttk.Combobox(marco, values=list(MODELOS), state="readonly", width=40)
        self.selector.current(1)  # EOQ con faltantes, el que ya teníamos
        self.selector.pack(side="left", padx=8)
        self.selector.bind("<<ComboboxSelected>>", lambda _e: self.cambiar_modelo())

    def _crear_panel_datos(self):
        marco = self.marco_datos
        for hijo in marco.winfo_children():
            hijo.destroy()
        self.entradas = {}

        for fila, clave in enumerate(self.modelo["campos"]):
            texto, valor = CAMPOS[clave]
            ancho = 24 if clave in CAMPOS_TEXTO else 14
            ttk.Label(marco, text=texto).grid(row=fila, column=0, sticky="w", pady=4)
            entrada = ttk.Entry(marco, width=ancho, justify="right")
            entrada.insert(0, str(valor))
            entrada.grid(row=fila, column=1, pady=4, padx=(8, 0), sticky="e")
            entrada.bind("<Return>", lambda _e: self.calcular())
            self.entradas[clave] = entrada

        fila = len(self.modelo["campos"])
        self.etiqueta_H = ttk.Label(marco, text="", foreground="#555")
        self.etiqueta_H.grid(row=fila, column=0, columnspan=2, sticky="w", pady=(10, 4))

        botones = ttk.Frame(marco)
        botones.grid(row=fila + 1, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(botones, text="Calcular", command=self.calcular).pack(side="left", padx=4)
        ttk.Button(botones, text="Valores por defecto", command=self.restablecer).pack(side="left", padx=4)

    def _crear_panel_resultados(self):
        marco = self.marco_resultados
        for hijo in marco.winfo_children():
            hijo.destroy()
        self.etiquetas_resultado = {}

        for fila, definicion in enumerate(self.modelo["filas"]):
            if definicion is None:
                ttk.Separator(marco).grid(row=fila, column=0, columnspan=2, sticky="ew", pady=6)
                continue
            clave, texto, _ = definicion
            if clave == "evaluacion":
                # tabla de varias lineas debajo de su titulo
                ttk.Label(marco, text=texto).grid(row=fila, column=0, sticky="nw", pady=2)
                valor = ttk.Label(marco, text="—", font=("TkFixedFont", 10), justify="left")
                valor.grid(row=fila + 100, column=0, columnspan=2, sticky="w", pady=2)
                self.etiquetas_resultado[clave] = valor
                continue
            negrita = clave == "costo_total"
            fuente = ("TkDefaultFont", 11, "bold") if negrita else None
            ttk.Label(marco, text=texto, font=fuente).grid(row=fila, column=0, sticky="w", pady=2)
            valor = ttk.Label(marco, text="—", font=fuente)
            valor.grid(row=fila, column=1, sticky="e", padx=(16, 0), pady=2)
            self.etiquetas_resultado[clave] = valor

    def _crear_grafica(self):
        marco = ttk.LabelFrame(self.raiz, text="Comportamiento del inventario (2 ciclos)", padding=8)
        marco.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))

        self.lienzo = tk.Canvas(marco, height=220, background="white", highlightthickness=0)
        self.lienzo.pack(fill="both", expand=True)
        self.lienzo.bind("<Configure>", lambda _e: self._dibujar_grafica())

        self.raiz.columnconfigure(0, weight=1)
        self.raiz.columnconfigure(1, weight=2)
        self.raiz.rowconfigure(2, weight=1)

    # logica 

    def cambiar_modelo(self):
        self.modelo = MODELOS[self.selector.get()]
        self.resultado = None
        self._crear_panel_datos()
        self._crear_panel_resultados()
        self.calcular()

    def _leer_datos(self):
        datos = {}
        for clave in self.modelo["campos"]:
            texto = CAMPOS[clave][0]
            crudo = self.entradas[clave].get().strip()
            if clave in CAMPOS_TEXTO:
                datos[clave] = leer_niveles(crudo)
                continue
            if clave in CAMPOS_OPCIONALES and crudo == "":
                datos[clave] = None
                continue
            try:
                datos[clave] = a_numero(crudo)
            except ValueError:
                raise ValueError(f"'{texto}' debe ser un número.")
            if datos[clave] < 0 or (datos[clave] == 0 and clave not in CAMPOS_CERO):
                raise ValueError(f"'{texto}' debe ser mayor que cero.")
        return datos

    def calcular(self):
        try:
            datos = self._leer_datos()
            r = self.modelo["calcular"](datos)
        except ValueError as error:
            messagebox.showerror("Dato inválido", str(error))
            return

        if datos.get("H"):
            self.etiqueta_H.config(text=f"H = {datos['H']:g}  (dato directo)")
        elif "C" in datos:
            H = datos["i"] * datos["C"]
            self.etiqueta_H.config(text=f"H = i · C = {datos['i']:g} · {datos['C']:g} = {H:.2f}")
        else:
            self.etiqueta_H.config(text="H = i · C  (depende del precio de cada nivel)")

        self.resultado = r
        for definicion in self.modelo["filas"]:
            if definicion is None:
                continue
            clave, _, formato = definicion
            self.etiquetas_resultado[clave].config(text=formato(r, clave))

        self._dibujar_grafica()

    def restablecer(self):
        for clave in self.modelo["campos"]:
            self.entradas[clave].delete(0, tk.END)
            self.entradas[clave].insert(0, str(CAMPOS[clave][1]))
        self.calcular()

    def _dibujar_grafica(self):
        """dibuja el perfil del inventario del modelo elegido repetido en 2 ciclos"""
        lienzo = self.lienzo
        lienzo.delete("all")
        r = self.resultado
        if r is None:
            return

        ancho = lienzo.winfo_width()
        alto = lienzo.winfo_height()
        if ancho < 50 or alto < 50:
            return

        perfil = self.modelo["perfil"](r)
        puntos, T = perfil["puntos"], perfil["T"]
        lineas = perfil.get("lineas", [])
        niveles = [n for _, n in puntos] + [n for n, _, _ in lineas] + [0]
        tope, fondo = max(niveles), min(niveles)
        if tope == fondo or T <= 0:
            return

        margen_izq, margen_der, margen_sup, margen_inf = 80, 20, 15, 30
        ciclos = 2

        def x(t):
            return margen_izq + t / (ciclos * T) * (ancho - margen_izq - margen_der)

        def y(nivel):
            return margen_sup + (tope - nivel) / (tope - fondo) * (alto - margen_sup - margen_inf)

        # Ejes
        lienzo.create_line(margen_izq, margen_sup, margen_izq, alto - margen_inf, fill="#888")
        lienzo.create_line(margen_izq, y(0), ancho - margen_der, y(0), fill="#888")
        for nivel, texto in perfil["marcas"]:
            lienzo.create_text(margen_izq - 6, y(nivel), text=texto, anchor="e", font=("TkDefaultFont", 9))

        for c in range(ciclos):
            inicio = c * T
            ciclo = [(inicio + t, n) for t, n in puntos]
            for (ta, na), (tb, nb) in zip(ciclo, ciclo[1:]):
                self._rellenar(x, y, ta, na, tb, nb)
            lienzo.create_line(*[v for t, n in ciclo for v in (x(t), y(n))], fill=AZUL, width=2)
            if c < ciclos - 1 and ciclo[-1][1] != puntos[0][1]:
                lienzo.create_line(x(inicio + T), y(ciclo[-1][1]), x(inicio + T), y(puntos[0][1]),
                                   fill=AZUL, width=2, dash=(4, 3))

            for t_ini, t_fin, texto, es_escasez in perfil.get("tramos", []):
                medio = x(inicio + (t_ini + t_fin) / 2)
                if es_escasez:
                    lienzo.create_text(medio, y(0) - 12, text=texto, fill=ROJO)
                else:
                    lienzo.create_text(medio, y(0) + 12, text=texto, fill=AZUL)

        # lineas de referencia (punto de reorden, inventario de seguridad)
        for nivel, texto, color in lineas:
            lienzo.create_line(margen_izq, y(nivel), ancho - margen_der, y(nivel), fill=color, dash=(6, 4))
            lienzo.create_text(ancho - margen_der, y(nivel) - 2, text=texto, anchor="se",
                               fill=color, font=("TkDefaultFont", 9))

        # Marcas de tiempo en el eje X
        for k in range(ciclos + 1):
            lienzo.create_text(x(k * T), alto - margen_inf + 12,
                               text=f"{k * T:.1f} d", font=("TkDefaultFont", 9))

    def _rellenar(self, x, y, ta, na, tb, nb):
        """sombrea entre la curva y el eje: azul con inventario, rojo en escasez"""
        if na * nb < 0:
            tz = ta + (tb - ta) * na / (na - nb)  # cruce con el eje
            self._rellenar(x, y, ta, na, tz, 0)
            self._rellenar(x, y, tz, 0, tb, nb)
            return
        if na + nb == 0:
            return
        color = "#cfe3f7" if na + nb > 0 else "#f7d4cf"
        self.lienzo.create_polygon(x(ta), y(0), x(ta), y(na), x(tb), y(nb), x(tb), y(0),
                                   fill=color, outline="")


if __name__ == "__main__":
    raiz = tk.Tk()
    InterfazEOQ(raiz)
    raiz.mainloop()
