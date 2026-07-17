"""Funciones puras para la sección de Asistencia.

Sin dependencias de Streamlit ni Supabase, para poder testearlas aisladas.
"""

import secrets

SIN_CURSO = "Sin curso"


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
