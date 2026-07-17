import streamlit as st
from supabase import create_client

from helpers import codigo_es_valido, agrupar_por_curso, resumen_curso

# ==========================================
# ⚙️ CONFIGURACIÓN LOGÍSTICA DEL EVENTO
# ==========================================
SILLAS_POR_FILA = 2         # Cambia esto según lo que diga el organizador (ej: 15, 20, 25)
MAX_CUPOS_EXTRAS = 5        # Límite total de cupos adicionales permitidos en el auditorio
# ==========================================

st.set_page_config(page_title="VIP Access - Grados", page_icon="🎓", layout="centered")

# Estilos base con fondo de gala diseñado por código CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background-color: #0f0e17;
        background-image:
            linear-gradient(135deg, hsla(253,16%,7%,1) 0%, transparent 60%),
            linear-gradient(225deg, hsla(225,39%,30%,0.4) 10%, transparent 70%),
            linear-gradient(45deg, hsla(339,49%,30%,0.25) 0%, transparent 60%),
            radial-gradient(at 50% 100%, hsla(250,24%,15%,1) 0%, transparent 100%);
        background-attachment: fixed;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


def get_supabase():
    """Cliente de solo lectura (key pública anon; RLS solo permite SELECT)."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def get_supabase_admin():
    """Cliente para escrituras (key secreta, salta RLS).

    La key vive SOLO en st.secrets (local y Streamlit Cloud), nunca en el repo.
    """
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_SERVICE_KEY"])


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


def render_aprobacion(supabase, token_escaneado):
    try:
        response = supabase.table("estudiantes").select("*").order("curso").order("prioridad_orden").execute()
        estudiantes = response.data

        asiento_actual = 1
        total_extras_usados = 0
        estudiante_encontrado = None

        for est in estudiantes:
            cupos_adicionales = est["cupos_adicionales"]
            total_extras_usados += cupos_adicionales

            total_asientos = 2 + cupos_adicionales  # 2 base + extras
            asiento_final = asiento_actual + total_asientos - 1

            if token_escaneado and est.get("token") == str(token_escaneado):
                fila_inicio, silla_inicio = calcular_ubicacion(asiento_actual, SILLAS_POR_FILA)
                fila_fin, silla_fin = calcular_ubicacion(asiento_final, SILLAS_POR_FILA)

                if fila_inicio == fila_fin:
                    ubicacion_final = f"{fila_inicio} (Sillas {silla_inicio} a {silla_fin})"
                else:
                    ubicacion_final = f"{fila_inicio} Silla {silla_inicio} hasta {fila_fin} Silla {silla_fin}"

                estudiante_encontrado = {
                    "id": est["id"],
                    "nombre": est["nombre"],
                    "curso": est["curso"],
                    "ubicacion": ubicacion_final,
                    "presente": est.get("presente", False),
                }

            asiento_actual = 1 + asiento_final

        # 📊 PANEL DE ALERTAS PARA DOCENTES / STAFF
        st.markdown("<p style='margin:0; font-size:12px; color:#a0aec0;'>MONITOR DE CAPACIDAD (CUPOS EXTRAS)</p>", unsafe_allow_html=True)
        porcentaje_uso = min(total_extras_usados / MAX_CUPOS_EXTRAS, 1.0)
        st.progress(porcentaje_uso)
        st.markdown(f"<p style='margin:0 0 15px 0; font-size:13px; color:#e2e8f0;'>Usados: <b>{total_extras_usados}</b> de {MAX_CUPOS_EXTRAS} permitidos</p>", unsafe_allow_html=True)

        if total_extras_usados >= MAX_CUPOS_EXTRAS:
            st.warning(f"⚠️ ¡ALERTA! Se ha alcanzado o superado el límite de cupos extras del auditorio ({total_extras_usados}/{MAX_CUPOS_EXTRAS}).")
        elif total_extras_usados >= (MAX_CUPOS_EXTRAS * 0.85):
            st.info("📉 Capacidad crítica: Más del 85% de los cupos extras han sido asignados.")

        st.markdown("<br><h2 style='text-align: center; color: #fdfae7; font-family: \"serif\"; letter-spacing: 2px;'>✨ CONTROL DE ACCESO ✨</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #a0aec0; font-size: 14px;'>Ceremonia de Graduación Oficial</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #2d3748;'>", unsafe_allow_html=True)

        if estudiante_encontrado:
            nombre = estudiante_encontrado["nombre"]
            curso = estudiante_encontrado["curso"]
            ubicacion = estudiante_encontrado["ubicacion"]

            html_vip = f'<div style="background-color: #fdfae7; padding: 30px; border-radius: 20px; box-shadow: 0px 10px 25px rgba(0,0,0,0.5); color: #1a1829; font-family: sans-serif; margin: 20px 0; text-align: center;"><span style="font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; color: #b59410;">Invitación Escaneada</span><h1 style="margin: 5px 0 0 0; color: #1a1829; font-size: 32px; font-weight: 700; text-align: center;">{nombre}</h1><p style="margin: 5px 0 0 0; font-size: 18px; color: #4a5568; font-weight: 500; text-align: center;">Curso: {curso}</p><div style="background-color: #1a1829; color: #fdfae7; padding: 20px; border-radius: 15px; margin-top: 25px; text-align: center;"><span style="font-size: 18px; font-weight: bold; letter-spacing: 1px;">🪑 PUESTOS ASIGNADOS</span><h2 style="margin: 10px 0 0 0; color: #fdfae7; font-size: 22px;">{ubicacion}</h2></div></div>'
            st.markdown(html_vip, unsafe_allow_html=True)

            # --- Registro de asistencia (staff) ---
            st.markdown("<hr style='border-color: #2d3748;'>", unsafe_allow_html=True)
            estado_placeholder = st.empty()

            codigo = st.text_input("Código de staff (para registrar ingreso)", type="password", key="cod_aprob")
            presente_actual = estudiante_encontrado["presente"]
            if codigo:
                if codigo_es_valido(codigo, st.secrets["STAFF_CODE"]):
                    if not presente_actual:
                        get_supabase_admin().table("estudiantes").update({"presente": True}).eq("id", estudiante_encontrado["id"]).execute()
                        presente_actual = True
                    st.success("✅ Ingreso registrado — Presente")
                else:
                    st.error("Código incorrecto")

            if presente_actual:
                estado_placeholder.markdown("<p style='text-align:center; color:#48bb78; font-weight:bold;'>🟢 Estado: PRESENTE</p>", unsafe_allow_html=True)
            else:
                estado_placeholder.markdown("<p style='text-align:center; color:#a0aec0;'>⚪ Estado: Ausente</p>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #fff5f5; color: #c53030; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #feb2b2;'><h3 style='margin:0;'>❌ Código No Válido</h3><p style='margin:5px 0 0 0; font-size:14px;'>El ID escaneado no coincide con ningún graduando en el sistema.</p></div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error técnico de conexión: {e}")


def render_asistencia(supabase):
    st.markdown("<br><h2 style='text-align: center; color: #fdfae7; font-family: \"serif\"; letter-spacing: 2px;'>📋 PANEL DE ASISTENCIA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #a0aec0; font-size: 14px;'>Solo staff</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #2d3748;'>", unsafe_allow_html=True)

    codigo = st.text_input("Código de staff", type="password", key="cod_panel")
    if not codigo_es_valido(codigo, st.secrets["STAFF_CODE"]):
        if codigo:
            st.error("Código incorrecto")
        else:
            st.info("Ingresa el código de staff para ver el panel.")
        return

    st.button("🔄 Actualizar")  # al hacer clic, Streamlit re-ejecuta y re-consulta

    try:
        response = supabase.table("estudiantes").select("*").order("curso").order("prioridad_orden").execute()
        estudiantes = response.data
    except Exception as e:
        st.error(f"Error técnico de conexión: {e}")
        return

    grupos = agrupar_por_curso(estudiantes)
    for curso, lista in grupos.items():
        presentes, total = resumen_curso(lista)
        st.markdown(f"<h3 style='color:#fdfae7;'>{curso} — {presentes}/{total} presentes</h3>", unsafe_allow_html=True)
        for est in lista:
            if est.get("presente", False):
                st.markdown(f"<p style='margin:2px 0; color:#e2e8f0;'>🟢 {est['nombre']} — <b>Presente</b></p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='margin:2px 0; color:#a0aec0;'>⚪ {est['nombre']} — Ausente</p>", unsafe_allow_html=True)


# ==========================================
# 🚦 RUTEO POR PARÁMETRO
# ==========================================
supabase = get_supabase()
query_params = st.query_params

if query_params.get("view") == "asistencia":
    render_asistencia(supabase)
else:
    # Solo se acepta el token aleatorio (?t=). El id secuencial ya no sirve.
    token_escaneado = query_params.get("t")
    render_aprobacion(supabase, token_escaneado)

st.markdown("<br><p style='text-align: center; color: #4a5568; font-size: 11px;'>Marya Logistics Platform &copy; 2026</p>", unsafe_allow_html=True)
