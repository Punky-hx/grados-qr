"""Reporte de consola: asignación de asientos por estudiante.

Usa la MISMA lógica y el MISMO orden que la app (helpers.calcular_rangos,
orden curso → prioridad_orden), así lo que imprime coincide con lo que
ve cada familia al escanear su QR.
"""

from supabase import create_client, Client

from helpers import calcular_rangos, formatear_ubicacion

# Credenciales públicas (RLS: solo lectura)
SUPABASE_URL = "https://ahxfbaceyebvvdoponck.supabase.co/"
SUPABASE_KEY = "sb_publishable_HMa7MPcg5ORxuCKNk3nN8A_qDmwC6c6"

# Debe coincidir con SILLAS_POR_FILA de app.py
SILLAS_POR_FILA = 2

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def imprimir_asignacion():
    print("🔄 Conectando a Supabase en tiempo real...")

    # Mismo orden que la app: curso y luego prioridad
    response = (
        supabase.table("estudiantes")
        .select("*")
        .order("curso")
        .order("prioridad_orden")
        .execute()
    )
    estudiantes = response.data

    print(f"✅ ¡Conexión exitosa! Encontré {len(estudiantes)} estudiantes en la nube:\n")

    curso_actual = None
    for est, asiento_inicio, asiento_final in calcular_rangos(estudiantes):
        if est["curso"] != curso_actual:
            curso_actual = est["curso"]
            print(f"\n════════ CURSO {curso_actual} ════════")

        ubicacion = formatear_ubicacion(asiento_inicio, asiento_final, SILLAS_POR_FILA)
        total = asiento_final - asiento_inicio + 1
        print(f"🎓 {est['nombre']} | {total} cupos ({asiento_inicio}-{asiento_final})")
        print(f"🪑 {ubicacion}")
        print("-" * 45)


if __name__ == "__main__":
    imprimir_asignacion()
