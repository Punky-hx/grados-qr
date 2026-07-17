"""Funciones puras compartidas (asistencia, tokens y asignación de asientos).

Sin dependencias de Streamlit ni Supabase, para poder testearlas aisladas.
app.py y asignacion.py usan ESTA lógica de asientos: si cambia, cambia
para ambos y no pueden divergir.
"""

import secrets

SIN_CURSO = "Sin curso"
CUPOS_BASE = 2  # invitados base por graduando (el graduando se sienta aparte)


def generar_token():
    """Token aleatorio impredecible para el QR (reemplaza el id secuencial).

    token_urlsafe(8) → ~11 caracteres URL-safe, imposible de adivinar
    (a diferencia de id=1,2,3...).
    """
    return secrets.token_urlsafe(8)


def codigo_es_valido(ingresado, esperado):
    """True solo si el código ingresado no es vacío y coincide exacto con el esperado."""
    return bool(ingresado) and ingresado == esperado


def agrupar_por_curso(estudiantes):
    """Agrupa estudiantes por curso preservando el orden de aparición.

    Devuelve {curso: [estudiantes]}. Curso None o "" se agrupa bajo SIN_CURSO.
    """
    grupos = {}
    for est in estudiantes:
        curso = est.get("curso") or SIN_CURSO
        grupos.setdefault(curso, []).append(est)
    return grupos


def resumen_curso(estudiantes):
    """Devuelve (presentes, total) para una lista de estudiantes."""
    total = len(estudiantes)
    presentes = sum(1 for est in estudiantes if est.get("presente"))
    return presentes, total


def calcular_rangos(estudiantes, cupos_base=CUPOS_BASE):
    """Asigna rangos de asientos consecutivos a cada estudiante.

    Los estudiantes deben venir YA ordenados (curso, prioridad_orden).
    Devuelve [(estudiante, asiento_inicio, asiento_final), ...].
    """
    rangos = []
    asiento = 1
    for est in estudiantes:
        total = cupos_base + est.get("cupos_adicionales", 0)
        fin = asiento + total - 1
        rangos.append((est, asiento, fin))
        asiento = fin + 1
    return rangos


def calcular_ubicacion(numero_asiento, sillas_por_fila):
    """Convierte un número de asiento en (Fila Letra, Número de silla)."""
    letras = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
    indice_fila = (numero_asiento - 1) // sillas_por_fila
    if indice_fila < len(letras):
        fila_letra = f"Fila {letras[indice_fila]}"
    else:
        fila_letra = f"Fila {indice_fila + 1}"
    silla_num = ((numero_asiento - 1) % sillas_por_fila) + 1
    return fila_letra, silla_num


def formatear_ubicacion(asiento_inicio, asiento_final, sillas_por_fila):
    """Texto legible del rango de asientos, ej. 'Fila A (Sillas 1 a 3)'."""
    fila_inicio, silla_inicio = calcular_ubicacion(asiento_inicio, sillas_por_fila)
    fila_fin, silla_fin = calcular_ubicacion(asiento_final, sillas_por_fila)
    if fila_inicio == fila_fin:
        return f"{fila_inicio} (Sillas {silla_inicio} a {silla_fin})"
    return f"{fila_inicio} Silla {silla_inicio} hasta {fila_fin} Silla {silla_fin}"
