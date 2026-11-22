"""
Sistema de inventario: modelos EOQ.
Investigación de Operaciones.

Modelos incluidos:
    1. EOQ clásico (sin faltantes)
    2. EOQ con faltantes planeados
    3. EOQ de producción (sin faltantes)
    4. EOQ de producción con faltantes
    5. EOQ con descuentos por cantidad
    6. EOQ con inventario de seguridad (demanda variable)

Variables de los modelos:
    D  = demanda anual (unidades/año)
    S  = costo de ordenar (por pedido)
    C  = costo unitario del producto
    i  = tasa de costo de mantener (fracción del costo unitario)
    H  = costo de mantener una unidad en inventario por año (H = i * C)
    Cf = costo por faltante (por unidad faltante por año)
    P  = tasa de producción anual (unidades/año), debe ser mayor que D
    L  = tiempo de entrega (días)
    sigma_d = desviación estándar de la demanda diaria
    nivel_servicio = probabilidad de no tener faltante durante L (ej. 0.95)
    dias = días hábiles del año
"""

import math
import re
from statistics import NormalDist


def a_numero(texto):
    """Convierte texto a número aceptando '20,000' (miles) y '0,2' (coma decimal)."""
    texto = str(texto).strip().replace(" ", "")
    if "," in texto:
        if "." in texto:
            texto = texto.replace(",", "")          # 20,000.50
        elif re.fullmatch(r"-?\d{1,3}(,\d{3})+", texto):
            texto = texto.replace(",", "")          # 20,000  /  1,250,000
        else:
            texto = texto.replace(",", ".")         # 0,2  /  13,5
    return float(texto)


def pedir_dato(mensaje, valor_por_defecto):
    """Pide un número al usuario; si presiona Enter, usa el valor por defecto."""
    texto = input(f"{mensaje} [{valor_por_defecto}]: ").strip()
    if texto == "":
        return valor_por_defecto
    return a_numero(texto)


# Nota: todos los cálculos usan los valores exactos (Q_exacta, Sf_exacta).
# Los valores redondeados (Q, Sf) son solo para mostrar "≈ unidades enteras".

def eoq_clasico(D, S, H, C, dias, L=0):
    # Cantidad óptima a pedir
    Qx = math.sqrt((2 * S * D) / H)
    Q = round(Qx)

    # Costo total anual = compra + ordenar + mantener
    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Qx) / 2
    costo_total = costo_compra + costo_ordenar + costo_mantener

    d = D / dias    # demanda diaria
    N = D / Qx      # número de pedidos al año
    T = Qx / d      # tiempo entre órdenes (días)
    R = d * L       # punto de reorden

    return {
        "Q_exacta": Qx, "Q": Q,
        "Imax": Qx,
        "costo_compra": costo_compra,
        "costo_ordenar": costo_ordenar,
        "costo_mantener": costo_mantener,
        "costo_total": costo_total,
        "d": d, "N": N, "T": T, "L": L, "R": R,
    }


def eoq_con_faltantes(D, S, H, Cf, C, dias):
    # Cantidad óptima a pedir
    Qx = math.sqrt((2 * S * D * (Cf + H)) / (H * Cf))
    Q = round(Qx)

    # Cantidad máxima faltante
    Sx = (Qx * H) / (H + Cf)
    Sf = round(Sx)

    # Inventario máximo
    Imax = Qx - Sx

    # Costo total anual = compra + ordenar + mantener + faltantes
    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Imax ** 2) / (2 * Qx)
    costo_faltante = (Cf * Sx ** 2) / (2 * Qx)
    costo_total = costo_compra + costo_ordenar + costo_mantener + costo_faltante

    # Tiempos del ciclo
    d = D / dias            # demanda diaria
    N = D / Qx              # número de pedidos al año
    T = Qx / d              # tiempo entre órdenes (días)
    t1 = Imax / d           # tiempo que dura el inventario (días)
    t2 = Sx / d             # tiempo de escasez, sin inventario (días)

    return {
        "Q_exacta": Qx, "Q": Q,
        "Sf_exacta": Sx, "Sf": Sf,
        "Imax": Imax, "N": N,
        "costo_compra": costo_compra,
        "costo_ordenar": costo_ordenar,
        "costo_mantener": costo_mantener,
        "costo_faltante": costo_faltante,
        "costo_total": costo_total,
        "d": d, "T": T, "t1": t1, "t2": t2,
    }


def eoq_produccion(D, S, H, C, P, dias):
    if P <= D:
        raise ValueError("La tasa de producción P debe ser mayor que la demanda D.")
    factor = 1 - D / P

    # Cantidad óptima a producir
    Qx = math.sqrt((2 * S * D) / (H * factor))
    Q = round(Qx)

    # Inventario máximo (se produce y se consume al mismo tiempo)
    Imax = Qx * factor

    # Costo total anual = compra + preparar + mantener
    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Imax) / 2
    costo_total = costo_compra + costo_ordenar + costo_mantener

    # Tiempos del ciclo
    d = D / dias    # demanda diaria
    p = P / dias    # producción diaria
    N = D / Qx      # corridas al año
    T = Qx / d      # tiempo entre corridas (días)
    t1 = Qx / p     # tiempo produciendo (días)
    t2 = T - t1     # tiempo solo consumiendo (días)

    return {
        "Q_exacta": Qx, "Q": Q,
        "Imax": Imax, "N": N,
        "costo_compra": costo_compra,
        "costo_ordenar": costo_ordenar,
        "costo_mantener": costo_mantener,
        "costo_total": costo_total,
        "d": d, "p": p, "T": T, "t1": t1, "t2": t2,
    }


def eoq_produccion_faltantes(D, S, H, Cf, C, P, dias):
    if P <= D:
        raise ValueError("La tasa de producción P debe ser mayor que la demanda D.")
    factor = 1 - D / P

    # Cantidad óptima a producir
    Qx = math.sqrt((2 * S * D * (H + Cf)) / (H * Cf * factor))
    Q = round(Qx)

    # Cantidad máxima faltante
    Sx = (Qx * H * factor) / (H + Cf)
    Sf = round(Sx)

    # Inventario máximo
    Imax = Qx * factor - Sx

    # Costo total anual = compra + preparar + mantener + faltantes
    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Imax ** 2) / (2 * Qx * factor)
    costo_faltante = (Cf * Sx ** 2) / (2 * Qx * factor)
    costo_total = costo_compra + costo_ordenar + costo_mantener + costo_faltante

    # Tiempos del ciclo
    d = D / dias            # demanda diaria
    p = P / dias            # producción diaria
    N = D / Qx              # corridas al año
    T = Qx / d              # tiempo entre corridas (días)
    t1 = Imax / (p - d)     # produciendo y acumulando inventario
    t2 = Imax / d           # consumiendo el inventario
    t3 = Sx / d             # acumulando faltantes
    t4 = Sx / (p - d)       # produciendo para cubrir faltantes

    return {
        "Q_exacta": Qx, "Q": Q,
        "Sf_exacta": Sx, "Sf": Sf,
        "Imax": Imax, "N": N,
        "costo_compra": costo_compra,
        "costo_ordenar": costo_ordenar,
        "costo_mantener": costo_mantener,
        "costo_faltante": costo_faltante,
        "costo_total": costo_total,
        "d": d, "p": p, "T": T, "t1": t1, "t2": t2, "t3": t3, "t4": t4,
    }


def leer_niveles(texto):
    """Convierte '0:14; 2000:13.5; 5000:13' en [(0, 14), (2000, 13.5), (5000, 13)]."""
    niveles = []
    for parte in texto.split(";"):
        parte = parte.strip()
        if not parte:
            continue
        try:
            minimo, precio = parte.split(":")
            niveles.append((a_numero(minimo), a_numero(precio)))
        except ValueError:
            raise ValueError(f"Nivel de precio inválido: '{parte}'. Usa el formato cantidad:precio.")
    if not niveles:
        raise ValueError("Debes indicar al menos un nivel de precio.")
    return sorted(niveles)


def eoq_descuentos(D, S, i, niveles, dias):
    """niveles = [(cantidad_minima, precio), ...] ordenados por cantidad mínima."""
    evaluacion = []
    for k, (minimo, precio) in enumerate(niveles):
        maximo = niveles[k + 1][0] - 1 if k + 1 < len(niveles) else math.inf
        H = i * precio
        Q_exacta = math.sqrt((2 * S * D) / H)
        Q = Q_exacta

        if Q > maximo:
            # Q cae arriba del rango: este precio no es alcanzable con su Q óptima
            evaluacion.append({"minimo": minimo, "precio": precio, "H": H,
                               "Q_exacta": Q_exacta, "Q": round(Q), "estado": "no factible"})
            continue
        estado = "factible"
        if Q < minimo:
            Q = minimo  # se ajusta al mínimo para obtener el descuento
            estado = "ajustada"

        costo_compra = D * precio
        costo_ordenar = (S * D) / Q
        costo_mantener = (H * Q) / 2
        evaluacion.append({
            "minimo": minimo, "precio": precio, "H": H,
            "Q_exacta": Q_exacta, "Q": Q, "estado": estado,
            "costo_compra": costo_compra,
            "costo_ordenar": costo_ordenar,
            "costo_mantener": costo_mantener,
            "costo_total": costo_compra + costo_ordenar + costo_mantener,
        })

    factibles = [n for n in evaluacion if n["estado"] != "no factible"]
    mejor = dict(min(factibles, key=lambda n: n["costo_total"]))

    d = D / dias
    mejor.update({
        "Imax": mejor["Q"],  # (Q exacta o el mínimo del nivel)
        "d": d, "N": D / mejor["Q"], "T": mejor["Q"] / d,
        "evaluacion": evaluacion,
    })
    return mejor


def eoq_seguridad(D, S, H, C, dias, L, sigma_d, nivel_servicio):
    if not 0 < nivel_servicio < 1:
        raise ValueError("El nivel de servicio debe estar entre 0 y 1 (ej. 0.95).")
    r = eoq_clasico(D, S, H, C, dias, L)

    # Inventario de seguridad para cubrir la variación de la demanda durante L
    z = NormalDist().inv_cdf(nivel_servicio)
    sigma_L = sigma_d * math.sqrt(L)
    SS = z * sigma_L
    R = r["d"] * L + SS

    costo_seguridad = H * SS
    r.update({
        "z": z, "sigma_L": sigma_L, "SS": SS, "R": R,
        "Imax": r["Q_exacta"] + SS,
        "costo_seguridad": costo_seguridad,
        "costo_total": r["costo_total"] + costo_seguridad,
    })
    return r


# ---------- Programa de consola ----------

def pedir_basicos(con_costo=True):
    D = pedir_dato("Demanda anual D", 20000)
    S = pedir_dato("Costo de ordenar S", 40)
    C = pedir_dato("Costo unitario C", 14) if con_costo else None
    i = pedir_dato("Tasa de mantener i", 0.2)
    dias = pedir_dato("Días hábiles al año", 365)
    return D, S, C, i, dias


def imprimir_costos(r):
    print(f"Costo de compra                      = ${r['costo_compra']:,.2f}")
    print(f"Costo de ordenar                     = ${r['costo_ordenar']:,.2f}")
    print(f"Costo de mantener                    = ${r['costo_mantener']:,.2f}")
    if "costo_faltante" in r:
        print(f"Costo de faltante                    = ${r['costo_faltante']:,.2f}")
    if "costo_seguridad" in r:
        print(f"Costo inventario de seguridad        = ${r['costo_seguridad']:,.2f}")
    print(f"COSTO TOTAL ANUAL                    = ${r['costo_total']:,.2f}")


def main():
    modelos = [
        "EOQ clásico (sin faltantes)",
        "EOQ con faltantes planeados",
        "EOQ de producción (sin faltantes)",
        "EOQ de producción con faltantes",
        "EOQ con descuentos por cantidad",
        "EOQ con inventario de seguridad",
    ]
    print("=== Sistema de inventario ===")
    for n, nombre in enumerate(modelos, start=1):
        print(f"  {n}. {nombre}")
    opcion = int(pedir_dato("Elige un modelo", 2))
    print(f"\n--- {modelos[opcion - 1]} ---")
    print("(Presiona Enter para usar el valor por defecto)\n")

    if opcion == 5:
        D, S, _, i, dias = pedir_basicos(con_costo=False)
        texto = input("Niveles cantidad:precio [0:14; 2000:13.5; 5000:13]: ").strip()
        niveles = leer_niveles(texto or "0:14; 2000:13.5; 5000:13")
        r = eoq_descuentos(D, S, i, niveles, dias)
        print("\n--- Evaluación por nivel ---")
        for n in r["evaluacion"]:
            costo = f"${n['costo_total']:,.2f}" if "costo_total" in n else "—"
            print(f"≥{n['minimo']:g} a ${n['precio']:g}: Q={n['Q']:.2f} ({n['estado']})  CT={costo}")
        print(f"\nMejor opción: pedir Q = {r['Q']:.2f} ≈ {round(r['Q'])} unidades a ${r['precio']:g}")
        imprimir_costos(r)
        return

    D, S, C, i, dias = pedir_basicos()
    H = pedir_dato("Costo de mantener H (0 = calcular i * C)", 0)
    if H > 0:
        print(f"\nH = {H:.2f} (dato directo)")
    else:
        H = i * C
        print(f"\nH = i * C = {i} * {C} = {H:.2f}")

    if opcion == 1:
        L = pedir_dato("Tiempo de entrega L (días)", 5)
        r = eoq_clasico(D, S, H, C, dias, L)
    elif opcion == 2:
        Cf = pedir_dato("Costo por faltante Cf", 20)
        r = eoq_con_faltantes(D, S, H, Cf, C, dias)
    elif opcion == 3:
        P = pedir_dato("Tasa de producción anual P", 40000)
        r = eoq_produccion(D, S, H, C, P, dias)
    elif opcion == 4:
        Cf = pedir_dato("Costo por faltante Cf", 20)
        P = pedir_dato("Tasa de producción anual P", 40000)
        r = eoq_produccion_faltantes(D, S, H, Cf, C, P, dias)
    else:
        L = pedir_dato("Tiempo de entrega L (días)", 5)
        sigma_d = pedir_dato("Desv. estándar de la demanda diaria", 10)
        nivel = pedir_dato("Nivel de servicio", 0.95)
        r = eoq_seguridad(D, S, H, C, dias, L, sigma_d, nivel)

    print("\n--- Resultados ---")
    print(f"Q    (cantidad óptima)     = {r['Q_exacta']:.4f} ≈ {r['Q']} unidades")
    if "Sf" in r:
        print(f"Sf   (faltante máximo)     = {r['Sf_exacta']:.4f} ≈ {r['Sf']} unidades")
    print(f"Imax (inventario máximo)   = {r['Imax']:.2f} unidades")
    if "SS" in r:
        print(f"z = {r['z']:.4f}   σL = {r['sigma_L']:.4f}   SS = {r['SS']:.2f} unidades")
    if "R" in r:
        print(f"R    (punto de reorden)    = {r['R']:.2f} unidades")
    print()
    imprimir_costos(r)
    print()
    print(f"d  (demanda diaria)          = {r['d']:.4f} unidades/día")
    print(f"T  (tiempo entre órdenes)    = {r['T']:.4f} ≈ {round(r['T'])} días")
    for clave in ("t1", "t2", "t3", "t4"):
        if clave in r:
            print(f"{clave}                          = {r[clave]:.4f} días")


if __name__ == "__main__":
    main()
