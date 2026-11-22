# Sistema de inventario - modelos EOQ
# Investigacion de Operaciones
#
# Modelos:
#   1. EOQ clasico (sin faltantes)
#   2. EOQ con faltantes
#   3. EOQ de produccion (sin faltantes)
#   4. EOQ de produccion con faltantes
#   5. EOQ con descuentos por cantidad
#   6. EOQ con inventario de seguridad
#
# Variables:
#   D = demanda anual
#   S = costo de ordenar por pedido
#   C = costo unitario
#   i = tasa de mantener (fraccion de C)
#   H = costo de mantener por unidad al anio (H = i*C)
#   Cf = costo por faltante (por unidad al anio)
#   P = tasa de produccion anual (tiene que ser mayor que D)
#   L = tiempo de entrega en dias
#   sigma_d = desviacion estandar de la demanda diaria
#   nivel_servicio = prob. de no tener faltante (ej 0.95)
#   dias = dias habiles del anio

import math
import re
from statistics import NormalDist


def a_numero(texto):
    # acepta cosas como 20,000 o 0,2
    texto = str(texto).strip().replace(" ", "")
    if "," in texto:
        if "." in texto:
            texto = texto.replace(",", "")
        elif re.fullmatch(r"-?\d{1,3}(,\d{3})+", texto):
            texto = texto.replace(",", "")
        else:
            texto = texto.replace(",", ".")
    return float(texto)


def pedir_dato(mensaje, default):
    # si le das enter usa el valor por defecto
    texto = input(f"{mensaje} [{default}]: ").strip()
    if texto == "":
        return default
    return a_numero(texto)


# los calculos se hacen con Q sin redondear, el redondeo es nomas para mostrarlo

def eoq_clasico(D, S, H, C, dias, L=0):
    Qx = math.sqrt((2 * S * D) / H)
    Q = round(Qx)

    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Qx) / 2
    costo_total = costo_compra + costo_ordenar + costo_mantener

    d = D / dias   # demanda diaria
    N = D / Qx     # pedidos al anio
    T = Qx / d     # dias entre pedidos
    R = d * L      # punto de reorden

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
    Qx = math.sqrt((2 * S * D * (Cf + H)) / (H * Cf))
    Q = round(Qx)

    # faltante maximo
    Sx = (Qx * H) / (H + Cf)
    Sf = round(Sx)

    Imax = Qx - Sx

    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Imax ** 2) / (2 * Qx)
    costo_faltante = (Cf * Sx ** 2) / (2 * Qx)
    costo_total = costo_compra + costo_ordenar + costo_mantener + costo_faltante

    d = D / dias
    N = D / Qx
    T = Qx / d
    t1 = Imax / d   # tiempo con inventario
    t2 = Sx / d     # tiempo con faltante

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
        raise ValueError("P tiene que ser mayor que D")
    factor = 1 - D / P

    Qx = math.sqrt((2 * S * D) / (H * factor))
    Q = round(Qx)

    # se produce y se consume al mismo tiempo
    Imax = Qx * factor

    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Imax) / 2
    costo_total = costo_compra + costo_ordenar + costo_mantener

    d = D / dias
    p = P / dias
    N = D / Qx      # corridas al anio
    T = Qx / d
    t1 = Qx / p     # produciendo
    t2 = T - t1     # solo consumiendo

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
        raise ValueError("P tiene que ser mayor que D")
    factor = 1 - D / P

    Qx = math.sqrt((2 * S * D * (H + Cf)) / (H * Cf * factor))
    Q = round(Qx)

    Sx = (Qx * H * factor) / (H + Cf)
    Sf = round(Sx)

    Imax = Qx * factor - Sx

    costo_compra = D * C
    costo_ordenar = (S * D) / Qx
    costo_mantener = (H * Imax ** 2) / (2 * Qx * factor)
    costo_faltante = (Cf * Sx ** 2) / (2 * Qx * factor)
    costo_total = costo_compra + costo_ordenar + costo_mantener + costo_faltante

    d = D / dias
    p = P / dias
    N = D / Qx
    T = Qx / d
    t1 = Imax / (p - d)   # produce y acumula
    t2 = Imax / d         # consume inventario
    t3 = Sx / d           # se acumulan faltantes
    t4 = Sx / (p - d)     # produce para cubrir faltantes

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
    # "0:14; 2000:13.5; 5000:13" -> [(0,14), (2000,13.5), (5000,13)]
    niveles = []
    for parte in texto.split(";"):
        parte = parte.strip()
        if not parte:
            continue
        try:
            minimo, precio = parte.split(":")
            niveles.append((a_numero(minimo), a_numero(precio)))
        except ValueError:
            raise ValueError(f"Nivel mal escrito: '{parte}' (debe ser cantidad:precio)")
    if not niveles:
        raise ValueError("Falta poner al menos un nivel de precio")
    return sorted(niveles)


def eoq_descuentos(D, S, i, niveles, dias):
    evaluacion = []
    for k, (minimo, precio) in enumerate(niveles):
        if k + 1 < len(niveles):
            maximo = niveles[k + 1][0] - 1
        else:
            maximo = math.inf
        H = i * precio
        Q_exacta = math.sqrt((2 * S * D) / H)
        Q = Q_exacta

        if Q > maximo:
            # la Q se pasa del rango, este precio no aplica
            evaluacion.append({"minimo": minimo, "precio": precio, "H": H,
                               "Q_exacta": Q_exacta, "Q": round(Q), "estado": "no factible"})
            continue
        estado = "factible"
        if Q < minimo:
            Q = minimo   # se sube al minimo para que aplique el descuento
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
    mejor["Imax"] = mejor["Q"]
    mejor["d"] = d
    mejor["N"] = D / mejor["Q"]
    mejor["T"] = mejor["Q"] / d
    mejor["evaluacion"] = evaluacion
    return mejor


def eoq_seguridad(D, S, H, C, dias, L, sigma_d, nivel_servicio):
    if not 0 < nivel_servicio < 1:
        raise ValueError("El nivel de servicio va entre 0 y 1 (ej 0.95)")
    r = eoq_clasico(D, S, H, C, dias, L)

    # inventario de seguridad
    z = NormalDist().inv_cdf(nivel_servicio)
    sigma_L = sigma_d * math.sqrt(L)
    SS = z * sigma_L
    R = r["d"] * L + SS

    costo_seguridad = H * SS
    r["z"] = z
    r["sigma_L"] = sigma_L
    r["SS"] = SS
    r["R"] = R
    r["Imax"] = r["Q_exacta"] + SS
    r["costo_seguridad"] = costo_seguridad
    r["costo_total"] = r["costo_total"] + costo_seguridad
    return r


# ---------------- programa ----------------

def pedir_basicos(con_costo=True):
    D = pedir_dato("Demanda anual D", 20000)
    S = pedir_dato("Costo de ordenar S", 40)
    C = pedir_dato("Costo unitario C", 14) if con_costo else None
    i = pedir_dato("Tasa de mantener i", 0.2)
    dias = pedir_dato("Dias habiles al anio", 365)
    return D, S, C, i, dias


def imprimir_costos(r):
    print(f"Costo de compra     = ${r['costo_compra']:,.2f}")
    print(f"Costo de ordenar    = ${r['costo_ordenar']:,.2f}")
    print(f"Costo de mantener   = ${r['costo_mantener']:,.2f}")
    if "costo_faltante" in r:
        print(f"Costo de faltante   = ${r['costo_faltante']:,.2f}")
    if "costo_seguridad" in r:
        print(f"Costo inv seguridad = ${r['costo_seguridad']:,.2f}")
    print(f"COSTO TOTAL         = ${r['costo_total']:,.2f}")


def main():
    modelos = [
        "EOQ clasico (sin faltantes)",
        "EOQ con faltantes",
        "EOQ de produccion (sin faltantes)",
        "EOQ de produccion con faltantes",
        "EOQ con descuentos por cantidad",
        "EOQ con inventario de seguridad",
    ]
    print("=== Sistema de inventario ===")
    for n, nombre in enumerate(modelos, start=1):
        print(f"  {n}. {nombre}")
    opcion = int(pedir_dato("Elige un modelo", 2))
    print(f"\n--- {modelos[opcion - 1]} ---")
    print("(dale Enter para usar el valor por defecto)\n")

    if opcion == 5:
        D, S, _, i, dias = pedir_basicos(con_costo=False)
        texto = input("Niveles cantidad:precio [0:14; 2000:13.5; 5000:13]: ").strip()
        niveles = leer_niveles(texto or "0:14; 2000:13.5; 5000:13")
        r = eoq_descuentos(D, S, i, niveles, dias)
        print("\n--- Evaluacion por nivel ---")
        for n in r["evaluacion"]:
            if "costo_total" in n:
                costo = f"${n['costo_total']:,.2f}"
            else:
                costo = "-"
            print(f">={n['minimo']:g} a ${n['precio']:g}: Q={n['Q']:.2f} ({n['estado']})  CT={costo}")
        print(f"\nMejor opcion: pedir Q = {r['Q']:.2f} (aprox {round(r['Q'])} unidades) a ${r['precio']:g}")
        imprimir_costos(r)
        return

    D, S, C, i, dias = pedir_basicos()
    H = pedir_dato("Costo de mantener H (0 = calcularlo con i*C)", 0)
    if H > 0:
        print(f"\nH = {H:.2f}")
    else:
        H = i * C
        print(f"\nH = i*C = {i}*{C} = {H:.2f}")

    if opcion == 1:
        L = pedir_dato("Tiempo de entrega L (dias)", 5)
        r = eoq_clasico(D, S, H, C, dias, L)
    elif opcion == 2:
        Cf = pedir_dato("Costo por faltante Cf", 20)
        r = eoq_con_faltantes(D, S, H, Cf, C, dias)
    elif opcion == 3:
        P = pedir_dato("Tasa de produccion anual P", 40000)
        r = eoq_produccion(D, S, H, C, P, dias)
    elif opcion == 4:
        Cf = pedir_dato("Costo por faltante Cf", 20)
        P = pedir_dato("Tasa de produccion anual P", 40000)
        r = eoq_produccion_faltantes(D, S, H, Cf, C, P, dias)
    else:
        L = pedir_dato("Tiempo de entrega L (dias)", 5)
        sigma_d = pedir_dato("Desviacion estandar de la demanda diaria", 10)
        nivel = pedir_dato("Nivel de servicio", 0.95)
        r = eoq_seguridad(D, S, H, C, dias, L, sigma_d, nivel)

    print("\n--- Resultados ---")
    print(f"Q (cantidad optima)    = {r['Q_exacta']:.4f} (aprox {r['Q']} unidades)")
    if "Sf" in r:
        print(f"Sf (faltante maximo)   = {r['Sf_exacta']:.4f} (aprox {r['Sf']} unidades)")
    print(f"Imax (inv. maximo)     = {r['Imax']:.2f} unidades")
    if "SS" in r:
        print(f"z = {r['z']:.4f}  sigmaL = {r['sigma_L']:.4f}  SS = {r['SS']:.2f} unidades")
    if "R" in r:
        print(f"R (punto de reorden)   = {r['R']:.2f} unidades")
    print()
    imprimir_costos(r)
    print()
    print(f"d (demanda diaria)     = {r['d']:.4f} unidades/dia")
    print(f"T (tiempo entre ordenes) = {r['T']:.4f} (aprox {round(r['T'])} dias)")
    for clave in ("t1", "t2", "t3", "t4"):
        if clave in r:
            print(f"{clave} = {r[clave]:.4f} dias")


if __name__ == "__main__":
    main()