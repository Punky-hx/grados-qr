import os
import qrcode
from PIL import Image
from supabase import create_client

from helpers import generar_token

# 1. Credenciales de Supabase
SUPABASE_URL = "https://ahxfbaceyebvvdoponck.supabase.co/"
SUPABASE_KEY = "sb_publishable_HMa7MPcg5ORxuCKNk3nN8A_qDmwC6c6"

# Logo de la marca (ponlo en assets/logo.png)
RUTA_LOGO = os.path.join("assets", "logo.png")
PROPORCION_LOGO = 0.22   # el logo ocupa ~22% del ancho del QR (máx recomendado 25%)
MARGEN_BLANCO = 0.10     # recuadro blanco extra alrededor del logo (10% del lado del logo)

carpeta_qrs = "codigos_qr"


def cargar_logo(ruta):
    """Carga el logo, recorta márgenes vacíos (transparentes) y lo devuelve en RGBA.

    Si no existe el archivo, devuelve None y los QR salen sin logo.
    """
    if not os.path.exists(ruta):
        print(f"⚠️  No se encontró el logo en '{ruta}'. Los QR saldrán SIN logo.")
        return None
    logo = Image.open(ruta).convert("RGBA")
    # Recortar bordes transparentes para que el logo no quede diminuto
    bbox = logo.getchannel("A").getbbox()
    if bbox:
        logo = logo.crop(bbox)
    return logo


def generar_qr_con_logo(url, ruta_salida, logo=None):
    """Genera un QR (corrección H) con el logo centrado sobre recuadro blanco."""
    qr = qrcode.QRCode(
        version=1,
        # Corrección ALTA: el logo tapa parte del código y H tolera ~30% de daño
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Crear la imagen del QR (Blanco y Negro clásico)
    imagen_qr = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    if logo is not None:
        ancho_qr = imagen_qr.size[0]

        # Escalar el logo manteniendo proporción: lado mayor = 22% del QR
        lado_max = int(ancho_qr * PROPORCION_LOGO)
        logo_red = logo.copy()
        logo_red.thumbnail((lado_max, lado_max), Image.LANCZOS)
        ancho_logo, alto_logo = logo_red.size

        # Recuadro blanco detrás del logo (el logo tiene fondo transparente)
        margen = int(max(ancho_logo, alto_logo) * MARGEN_BLANCO)
        caja_w = ancho_logo + 2 * margen
        caja_h = alto_logo + 2 * margen
        caja_blanca = Image.new("RGB", (caja_w, caja_h), "white")

        # Pegar recuadro blanco centrado y encima el logo (usando su alfa como máscara)
        x_caja = (ancho_qr - caja_w) // 2
        y_caja = (imagen_qr.size[1] - caja_h) // 2
        imagen_qr.paste(caja_blanca, (x_caja, y_caja))
        imagen_qr.paste(logo_red, (x_caja + margen, y_caja + margen), logo_red)

    imagen_qr.save(ruta_salida)


def main():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 2. Crear una carpeta en tu computadora para guardar las imágenes
    if not os.path.exists(carpeta_qrs):
        os.makedirs(carpeta_qrs)

    logo = cargar_logo(RUTA_LOGO)

    print("🚀 Conectando a Supabase para descargar la lista de estudiantes...")

    try:
        # 3. Traer los estudiantes de la base de datos
        response = supabase.table("estudiantes").select("id", "nombre", "token").execute()
        estudiantes = response.data

        # 3.5 Asegurar que cada estudiante tenga token aleatorio (idempotente:
        # si ya tiene, se conserva y su QR impreso sigue siendo válido)
        for est in estudiantes:
            if not est.get("token"):
                nuevo = generar_token()
                supabase.table("estudiantes").update({"token": nuevo}).eq("id", est["id"]).execute()
                est["token"] = nuevo
                print(f"🔑 Token asignado a: {est['nombre']}")

        print(f"📊 Se encontraron {len(estudiantes)} estudiantes. Generando códigos...")

        # 4. Ciclo para crear el QR de cada estudiante
        for est in estudiantes:
            id_estudiante = est["id"]
            nombre_estudiante = est["nombre"]

            # Enlace con token aleatorio (el id secuencial era adivinable)
            url_qr = f"https://sacoi-q.streamlit.app/?t={est['token']}"

            # Guardar el archivo con el nombre del estudiante (quitando espacios raros)
            nombre_archivo = f"{id_estudiante}_{nombre_estudiante.replace(' ', '_')}.png"
            ruta_guardado = os.path.join(carpeta_qrs, nombre_archivo)
            generar_qr_con_logo(url_qr, ruta_guardado, logo)

            print(f"✅ QR Generado para: {nombre_estudiante} -> {ruta_guardado}")

        print("\n🎉 ¡Fábrica terminada! Todos los códigos QR están listos en la carpeta 'codigos_qr'")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")


if __name__ == "__main__":
    main()
