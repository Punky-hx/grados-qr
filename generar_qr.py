import os
import qrcode
from supabase import create_client

# 1. Credenciales de Supabase
SUPABASE_URL = "https://ahxfbaceyebvvdoponck.supabase.co/"
SUPABASE_KEY = "sb_publishable_HMa7MPcg5ORxuCKNk3nN8A_qDmwC6c6"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Crear una carpeta en tu computadora para guardar las imágenes
carpeta_qrs = "codigos_qr"
if not os.path.exists(carpeta_qrs):
    os.makedirs(carpeta_qrs)

print("🚀 Conectando a Supabase para descargar la lista de estudiantes...")

try:
    # 3. Traer los estudiantes de la base de datos
    response = supabase.table("estudiantes").select("id", "nombre").execute()
    estudiantes = response.data

    print(f"📊 Se encontraron {len(estudiantes)} estudiantes. Generando códigos...")

    # 4. Ciclo para crear el QR de cada estudiante
    for est in estudiantes:
        id_estudiante = est["id"]
        nombre_estudiante = est["nombre"]

        # Enlace real de la app desplegada en Streamlit Cloud
        url_qr = f"https://sacoi-q.streamlit.app/?id={id_estudiante}"

        # Configurar el diseño del QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url_qr)
        qr.make(fit=True)

        # Crear la imagen del QR (Blanco y Negro clásico)
        imagen_qr = qr.make_image(fill_color="black", back_color="white")

        # Guardar el archivo con el nombre del estudiante (quitando espacios raros)
        nombre_archivo = f"{id_estudiante}_{nombre_estudiante.replace(' ', '_')}.png"
        ruta_guardado = os.path.join(carpeta_qrs, nombre_archivo)
        imagen_qr.save(ruta_guardado)

        print(f"✅ QR Generado para: {nombre_estudiante} -> {ruta_guardado}")

    print("\n🎉 ¡Fábrica terminada! Todos los códigos QR están listos en la carpeta 'codigos_qr'")

except Exception as e:
    print(f"❌ Ocurrió un error: {e}")