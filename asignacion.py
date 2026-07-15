import os
from supabase import create_client, Client

# Pegamos las credenciales de su proyecto de Supabase
SUPABASE_URL = "https://ahxfbaceyebvvdoponck.supabase.co/"
SUPABASE_KEY = "sb_publishable_HMa7MPcg5ORxuCKNk3nN8A_qDmwC6c6"

# Conectamos Python con la base de datos en la nube
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def probar_conexion_y_leer_estudiantes():
    print("🔄 Conectando a Supabase en tiempo real...")
    
    # Traemos los estudiantes ordenados por prioridad en la fila
    response = supabase.table("estudiantes").select("*").order("prioridad_orden").execute()
    estudiantes = response.data
    
    print(f"✅ ¡Conexión exitosa! Encontré {len(estudiantes)} estudiantes en la nube:\n")
    
    asiento_actual = 1
    
    for est in estudiantes:
        # 2 cupos base por estudiante
        total_asientos = 2 + est["cupos_adicionales"]
        asiento_final = asiento_actual + total_asientos - 1
        
        print(f"🎓 Estudiante: {est['nombre']} | Curso: {est['curso']}")
        print(f"🪑 Asientos asignados: Fila A (Del Asiento {asiento_actual} al {asiento_final})")
        print("-" * 45)
        
        # El contador se mueve para la siguiente familia
        asiento_actual = asiento_final + 1

if __name__ == "__main__":
    probar_conexion_y_leer_estudiantes()