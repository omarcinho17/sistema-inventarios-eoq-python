#  Sistema de Inventarios EOQ en Python

Aplicación desarrollada en **Python** para resolver y visualizar diferentes modelos de inventario basados en la **Cantidad Económica de Pedido (EOQ)**.

El proyecto fue desarrollado como parte de la asignatura **Investigación de Operaciones** y permite ingresar los datos de cada problema, realizar los cálculos correspondientes y visualizar gráficamente el comportamiento del inventario.

---

## 📌 Modelos implementados

El sistema incluye seis modelos de inventario:

1. **EOQ clásico (sin faltantes)**
2. **EOQ con faltantes planeados**
3. **EOQ de producción (sin faltantes)**
4. **EOQ de producción con faltantes**
5. **EOQ con descuentos por cantidad**
6. **EOQ con inventario de seguridad**

Cada modelo utiliza los parámetros correspondientes y calcula automáticamente los resultados necesarios para analizar el inventario.

---

##  Características

- Interfaz gráfica desarrollada con **Tkinter**.
- Selección entre seis modelos EOQ.
- Captura de datos desde la interfaz.
- Validación de valores ingresados.
- Cálculo automático de cantidades óptimas.
- Cálculo de costos de inventario.
- Cálculo de tiempos entre órdenes o ciclos de producción.
- Cálculo de faltantes cuando el modelo lo requiere.
- Punto de reorden.
- Inventario de seguridad.
- Evaluación de descuentos por cantidad.
- Visualización gráfica del comportamiento del inventario.
- Representación de **dos ciclos de inventario**.
- Valores iniciales para facilitar las pruebas.

---

##  Variables principales

| Variable | Descripción |
|---|---|
| `D` | Demanda anual |
| `S` | Costo de ordenar |
| `C` | Costo unitario |
| `i` | Tasa anual de mantenimiento |
| `H` | Costo anual de mantenimiento por unidad |
| `Cf` | Costo por faltante |
| `P` | Tasa de producción anual |
| `L` | Tiempo de entrega |
| `σd` | Desviación estándar de la demanda diaria |
| `Q` | Cantidad óptima a pedir o producir |
| `Sf` | Faltante máximo |
| `Imax` | Inventario máximo |
| `R` | Punto de reorden |
| `SS` | Inventario de seguridad |

---

##  Estructura del proyecto

```text
sistema-inventarios-eoq-python/
│
├── eoq_faltantes.py
├── interfaz_eoq.py
└── README.md
```

### `eoq_faltantes.py`

Contiene la lógica matemática de los diferentes modelos de inventario.

Entre sus funciones se encuentran:

```text
eoq_clasico()
eoq_con_faltantes()
eoq_produccion()
eoq_produccion_faltantes()
eoq_descuentos()
eoq_seguridad()
```

También permite ejecutar los cálculos desde consola.

### `interfaz_eoq.py`

Contiene la interfaz gráfica de la aplicación.

Desde esta ventana el usuario puede:

- seleccionar el modelo EOQ;
- introducir los datos del problema;
- realizar los cálculos;
- consultar los resultados;
- restablecer los valores;
- visualizar la gráfica del inventario.

---

## Interfaz gráfica

La aplicación cuenta con tres áreas principales:

### Datos del problema

Permite ingresar los valores necesarios dependiendo del modelo seleccionado.

### Resultados

Muestra información como:

- cantidad óptima;
- inventario máximo;
- faltante máximo;
- costos;
- demanda diaria;
- tiempo entre órdenes;
- punto de reorden;
- inventario de seguridad.

### Gráfica de inventario

Representa visualmente el comportamiento del inventario durante **dos ciclos**, permitiendo observar periodos con inventario disponible y, cuando corresponde, periodos de escasez.

---

## Requisitos

Para ejecutar el proyecto se necesita:

- **Python 3**
- **Tkinter**
- Módulo `math`
- Módulo `statistics`

Los módulos matemáticos utilizados forman parte de la biblioteca estándar de Python.

---

##  Ejecución

Primero clona el repositorio:

```bash
git clone https://github.com/TU-USUARIO/sistema-inventarios-eoq-python.git
```

Entra a la carpeta:

```bash
cd sistema-inventarios-eoq-python
```

Después ejecuta la interfaz gráfica:

```bash
python interfaz_eoq.py
```

En algunos sistemas puede ser necesario utilizar:

```bash
python3 interfaz_eoq.py
```

También es posible ejecutar directamente el módulo de cálculos desde consola:

```bash
python eoq_faltantes.py
```

---

## 🔄 Funcionamiento general

El flujo principal del programa es:

```text
Inicio
   ↓
Seleccionar modelo EOQ
   ↓
Ingresar datos
   ↓
Validar información
   ↓
Ejecutar cálculos
   ↓
Mostrar resultados
   ↓
Generar gráfica
```

Si alguno de los datos introducidos no es válido, el sistema muestra un mensaje de error para que pueda corregirse antes de realizar nuevamente el cálculo.

---

##  Resultados

Dependiendo del modelo seleccionado, el programa puede obtener valores como:

```text
Q     → Cantidad óptima
Imax  → Inventario máximo
Sf    → Faltante máximo
R     → Punto de reorden
SS    → Inventario de seguridad
T     → Tiempo entre órdenes
```

Además se calculan diferentes componentes del costo:

```text
Costo de compra
Costo de ordenar
Costo de mantener
Costo de faltante
Costo de inventario de seguridad
Costo total anual
```

---

##  Objetivo

El objetivo del proyecto es implementar diferentes modelos de inventario EOQ dentro de una sola aplicación, facilitando tanto los cálculos como la interpretación de los resultados.

La separación entre la lógica matemática y la interfaz gráfica permite mantener una estructura más organizada y facilita futuras modificaciones al programa.

---

##  Tecnologías utilizadas

- Python
- Tkinter
- Programación modular
- Modelos matemáticos EOQ

---

## Contexto académico

Proyecto realizado para la materia:

**Investigación de Operaciones**

Tema:

**Modelos de Inventario EOQ**

El proyecto permite aplicar de forma práctica los conceptos matemáticos vistos en clase mediante una aplicación de escritorio.

---

## Licencia

Este proyecto fue desarrollado con fines educativos y académicos.