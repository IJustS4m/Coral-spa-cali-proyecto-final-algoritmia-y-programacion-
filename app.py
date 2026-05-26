import streamlit as st
import uuid
from datetime import datetime, timedelta
from database import (
    init_db,
    registrar_usuario,
    verificar_usuario,
    obtener_usuario,
    usuario_existe,
    crear_cita,
    obtener_citas_usuario,
    cancelar_cita,
    horarios_ocupados,
    obtener_estilistas,
    obtener_servicios,
)

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="CORAL SPA CALI",
    page_icon="spa.ico",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Estilos CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Jost:wght@300;400;500&display=swap');

:root {
    --bluesky:#2E8B8B;
    --dark: #1A1612;
    --gold: #C9A96E;
    --gold-light: #E8D5B0;
    --muted: #7A6F65;
    --border: #E0D8CE;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bluesky) !important;
    font-family: 'Jost', sans-serif;
    color: var(--cream) !important;
}

[data-testid="stMain"] {
    background-color: var(--bluesky) !important;
}

h1, h2, h3 {
    font-family: 'Cormorant Garamond', serif !important;
    color: var(--dark) !important;
}

.gs-banner {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2rem;
}

.gs-banner h1 {
    font-size: 3rem !important;
    font-weight: 300 !important;
    letter-spacing: 0.3em;
    margin: 0 !important;
    color: var(--dark) !important;
}

.gs-banner p {
    font-size: 0.75rem;
    letter-spacing: 0.25em;
    color: white;
    margin: 0.4rem 0 0;
    text-transform: uppercase;
    font-family: 'Jost', sans-serif;
}

.gs-section {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.6rem;
    font-weight: 300;
    letter-spacing: 0.1em;
    color: var(--dark);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
}

.gs-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 2px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.8rem;
}

.gs-card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--dark);
    margin-bottom: 0.2rem;
}

.gs-card-sub {
    font-size: 0.8rem;
    color: var(--muted);
    letter-spacing: 0.05em;
}

.gs-price {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem;
    color: #1A1612;
    font-weight: 400;
}

.gs-badge-ok {
    background: #EAF4EC;
    color: #2E7D3E;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Jost', sans-serif;
}

.gs-badge-cancel {
    background: #FDECEA;
    color: #C0392B;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Jost', sans-serif;
}

.gs-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

/* Botones */
.stButton > button {
    white-space: nowrap !important;
    font-size: 0.7rem !important;
    padding: 0.4rem 0.8rem !important;
    background-color: var(--dark) !important;
    color: #F2EBEB !important;
    border: none !important;
    border-radius: 1px !important;
    font-family: 'Jost', sans-serif !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    width: auto;
    transition: background 0.2s;
}

.stSelectbox > div > div > div {
    color: #1A1612 !important;
}

.stButton > button:hover {
    background-color: var(--gold) !important;
    color: var(--dark) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stNumberInput > div > div > input {
    border: 1px solid var(--border) !important;
    border-radius: 1px !important;
    background: white !important;
    font-family: 'Jost', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input {
    color: #1A1612 !important;
}
/* Ocultar elementos de streamlit */

.stTabs [data-baseweb="tab"] {
    color: #1A1612 !important;
    font-family: 'Jost', sans-serif !important;
}
.stColumns > div {
    padding: 0 8px !important;
}
#MainMenu, footer, header { visibility: hidden; }
.stTextInput label p, .stSelectbox label p {
    color: #1A1612 !important;
    opacity: 1 !important;
    visibility: visible !important;
}            
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

MESES = {1:"enero",2:"febrero",3:"marzo",4:"abril",5:"mayo",6:"junio",
         7:"julio",8:"agosto",9:"septiembre",10:"octubre",11:"noviembre",12:"diciembre"}

DIAS_SEMANA = {0:"Lunes",1:"Martes",2:"Miércoles",3:"Jueves",
               4:"Viernes",5:"Sábado",6:"Domingo"}

HORARIOS = ["9:00 AM","9:30 AM","10:00 AM","10:30 AM","11:00 AM","11:30 AM",
            "12:00 PM","12:30 PM","1:00 PM","1:30 PM","2:00 PM","2:30 PM",
            "3:00 PM","3:30 PM","4:00 PM","4:30 PM","5:00 PM","5:30 PM"]

# ── Helpers de datos ─────────────────────────────────────────────────────────
def fecha_es(d):
    return f"{DIAS_SEMANA[d.weekday()]}, {d.day} de {MESES[d.month]} de {d.year}"

def fechas_disponibles():
    fechas, dia = [], datetime.today() + timedelta(days=1)
    while len(fechas) < 14:
        if dia.weekday() != 6:
            fechas.append(fecha_es(dia))
        dia += timedelta(days=1)
    return fechas

def horarios_disponibles(estilista_id, fecha_str):
    ocupados = horarios_ocupados(estilista_id, fecha_str)
    return [h for h in HORARIOS if h not in ocupados]
# ── Session state ────────────────────────────────────────────────────────────
init_db()
SERVICIOS = obtener_servicios()
ESTILISTAS = obtener_estilistas()

if "usuario" not in st.session_state: st.session_state.usuario = None
if "pagina" not in st.session_state: st.session_state.pagina = "inicio"
if "reserva" not in st.session_state: st.session_state.reserva = {}

def ir(pagina): st.session_state.pagina = pagina

# ── Banner ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gs-banner">
    <h1>CORAL SPA CALI</h1>
    <p>Sistema de reservas para tus citas &amp; Reservas</p>
    <a href="https://www.instagram.com/coral_spacali/" target="_blank" style="
        display: inline-block;
        margin-top: 0.8rem;
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        color: #C2260A;
        text-decoration: none;
        font-family: 'Jost', sans-serif;
        text-transform: uppercase;
    ">Instagram</a>
</div>
""", unsafe_allow_html=True)

# ── Navegación superior (sesión activa) ──────────────────────────────────────
if st.session_state.usuario:
    u = st.session_state.usuario
    cols = st.columns([4, 1.5, 1.5, 1.5, 1.5, 1.5])
    cols[0].markdown(f"<div style='padding-top:8px;font-size:0.85rem;color:#7A6F65'>Hola, <b>{u['nombre']}</b></div>", unsafe_allow_html=True)
    if cols[1].button("Reservar"):  ir("reservar")
    if cols[2].button("Mis citas"): ir("mis_citas")
    if cols[3].button("Estilistas"):ir("estilistas")
    if cols[4].button("Perfil"):    ir("perfil")
    if cols[5].button("Salir"):
        st.session_state.usuario = None
        st.session_state.pagina = "inicio"
        st.rerun()
    st.markdown('<hr class="gs-divider">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: INICIO
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.pagina == "inicio" and not st.session_state.usuario:
    tab_login, tab_reg = st.tabs(["Iniciar sesión", "Crear cuenta"])

    with tab_login:
        st.markdown('<div class="gs-section">Iniciar sesión</div>', unsafe_allow_html=True)
        usuario_in = st.text_input("Usuario", key="li_user", label_visibility="visible")
        contra_in  = st.text_input("Contraseña", type="password", key="li_pw", label_visibility="visible")
        if st.button("Entrar", key="btn_login"):
            if not usuario_existe(usuario_in.lower()):
                st.error("Usuario no encontrado.")
            elif not verificar_usuario(usuario_in, contra_in):
                st.error("Contraseña incorrecta.")
            else:
                d = obtener_usuario(usuario_in.lower())
                st.session_state.usuario = d
                st.session_state.pagina = "inicio"
                st.rerun()
    with tab_reg:
        st.markdown('<div class="gs-section">Crear cuenta</div>', unsafe_allow_html=True)
        r_user = st.text_input("Usuario (4-20 caracteres alfanuméricos)", key="r_user")
        r_pw   = st.text_input("Contraseña (6-20 caracteres alfanuméricos)", type="password", key="r_pw")
        r_pw2  = st.text_input("Confirmar contraseña", type="password", key="r_pw2")
        r_nom  = st.text_input("Nombre completo", key="r_nom")
        r_tel  = st.text_input("Teléfono (solo dígitos)", key="r_tel")

        if st.button("Registrarse", key="btn_reg"):
            err = []
            if not r_user.isalnum() or not (4 <= len(r_user) <= 20):
                err.append("Usuario inválido (alfanumérico, 4-20 caracteres).")
            if not r_pw.isalnum() or not (6 <= len(r_pw) <= 20):
                err.append("Contraseña inválida (alfanumérica, 6-20 caracteres).")
            if r_pw != r_pw2:
                err.append("Las contraseñas no coinciden.")
            if len(r_nom.strip()) < 2:
                err.append("Nombre muy corto.")
            if not r_tel.isdigit() or len(r_tel) < 7:
                err.append("Teléfono inválido.")
            if usuario_existe(r_user.lower()):
                err.append("Ese usuario ya existe.")

            if err:
                for e in err: st.error(e)
            else:
                hoy = datetime.now()
                fecha_registro = f"{hoy.day} de {MESES[hoy.month]} de {hoy.year}"
                registrar_usuario(r_user, r_pw, r_nom, r_tel, fecha_registro)
                st.success(f"Cuenta creada exitosamente. Bienvenido/a, {r_nom}. Ya puede iniciar sesión.")
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: RESERVAR
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "reservar" and st.session_state.usuario:
    st.markdown('<div class="gs-section">Reservar una cita</div>', unsafe_allow_html=True)

    # Servicio
    st.markdown("**Servicio**")
    opciones_serv = [f"{s['nombre']}  —  ${int(s['precio']):,}  (~{s['duracion']})".replace(",", ".") for s in SERVICIOS]
    sel_serv = st.selectbox("Seleccione un servicio", opciones_serv, key="sel_serv", label_visibility="collapsed", index=None, placeholder="Elegir una opcion")
    servicio_sel = SERVICIOS[opciones_serv.index(sel_serv)] if sel_serv is not None else None

    st.markdown('<hr class="gs-divider">', unsafe_allow_html=True)

    # Estilista
    st.markdown("**Estilista**")
    opciones_est = [f"{e['nombre']}  ·  {e['calificacion']}/5  ·  {', '.join(e['especialidades'])}" for e in ESTILISTAS]
    sel_est = st.selectbox("Seleccione un estilista", opciones_est, key="sel_est", label_visibility="collapsed", index=None, placeholder="Elegir una opcion")
    estilista_sel = ESTILISTAS[opciones_est.index(sel_est)] if sel_est is not None else None

    st.markdown('<hr class="gs-divider">', unsafe_allow_html=True)

    # Fecha
    st.markdown("**Fecha**")
    fechas = fechas_disponibles()
    fecha_sel = st.selectbox("Seleccione una fecha", fechas, key="sel_fecha", label_visibility="collapsed", index=None, placeholder="Elegir una opcion")

    if servicio_sel is None or estilista_sel is None or fecha_sel is None:
        st.info("Por favor seleccione todas las opciones para continuar.")
        st.stop()

    st.markdown('<hr class="gs-divider">', unsafe_allow_html=True)

    # Hora
    st.markdown("**Hora**")
    horarios = horarios_disponibles(estilista_sel["id"], fecha_sel)
    if not horarios:
        st.warning(f"No hay horarios disponibles para {estilista_sel['nombre']} en esa fecha.")
    else:
        hora_sel = st.selectbox("Seleccione una hora", horarios, key="sel_hora", label_visibility="collapsed", index=None, placeholder="Elegir una opcion")

        st.markdown('<hr class="gs-divider">', unsafe_allow_html=True)

        # Resumen
        st.markdown("**Resumen de la reserva**")
        col1, col2 = st.columns(2)
        col1.markdown(f"**Servicio:** {servicio_sel['nombre']}")
        col1.markdown(f"**Estilista:** {estilista_sel['nombre']}")
        col2.markdown(f"**Fecha:** {fecha_sel}")
        col2.markdown(f"**Hora:** {hora_sel}")
        precio_fmt = f"{int(servicio_sel['precio']):,}".replace(",", ".")
        st.markdown(f"<div class='gs-price'>${precio_fmt} &nbsp;·&nbsp; ~{servicio_sel['duracion']}</div>", unsafe_allow_html=True)

        st.markdown("")
        if st.button("Confirmar reserva"):
            cita_id = crear_cita(
                usuario          = st.session_state.usuario["usuario"],
                estilista_id     = estilista_sel["id"],
                estilista_nombre = estilista_sel["nombre"],
                servicio_nombre  = servicio_sel["nombre"],
                precio           = servicio_sel["precio"],
                duracion         = servicio_sel["duracion"],
                fecha            = fecha_sel,
                hora             = hora_sel,
            )
            st.success(f"Cita reservada. ID de confirmación: **{cita_id}**") 
# MIS CITAS
elif st.session_state.pagina == "mis_citas" and st.session_state.usuario:
    st.markdown('<div class="gs-section">Mis citas</div>', unsafe_allow_html=True)
    citas = obtener_citas_usuario(st.session_state.usuario["usuario"])

    if not citas:
        st.info("Aún no tienes citas registradas.")
    else:
        for c in citas:
            badge = f"<span class='gs-badge-ok'>Confirmada</span>" if c["estado"] == "confirmada" else f"<span class='gs-badge-cancel'>Cancelada</span>"
            precio_fmt = f"{int(c['precio']):,}".replace(",", ".")
            st.markdown(f"""
            <div class="gs-card">
                <div class="gs-card-title">{c['servicio_nombre']} {badge}</div>
                <div class="gs-card-sub">Estilista: {c['estilista_nombre']}</div>
                <div class="gs-card-sub">Fecha: {c['fecha']} &nbsp;·&nbsp; Hora: {c['hora']}</div>
                <div class="gs-card-sub">ID: {c['id']}</div>
                <div class="gs-price" style="margin-top:6px">${precio_fmt} &nbsp;·&nbsp; ~{c['duracion']}</div>
            </div>
            """, unsafe_allow_html=True)

            if c["estado"] == "confirmada":
                if st.button(f"Cancelar cita", key=f"cancel_{c['id']}"):
                    cancelar_cita(c["id"], st.session_state.usuario["usuario"])
                    st.success("Cita cancelada.")
                    st.rerun()
# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: ESTILISTAS
 
elif st.session_state.pagina == "estilistas" and st.session_state.usuario:
    st.markdown('<div class="gs-section">Nuestros estilistas</div>', unsafe_allow_html=True)
    for est in ESTILISTAS:
        st.markdown(f"""
        <div class="gs-card">
            <div class="gs-card-title">{est['nombre']}</div>
            <div class="gs-card-sub">{est['calificacion']}/5.0 &nbsp;·&nbsp; {', '.join(est['especialidades'])}</div>
            <div style="margin-top:6px;font-size:0.88rem;color:#4A4A4A">{est['bio']}</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: CANCELAR CITA
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "cancelar" and st.session_state.usuario:
    st.markdown('<div class="gs-section">Cancelar una cita</div>', unsafe_allow_html=True)
    citas = cargar_citas()
    confirmadas = [c for c in citas
                   if c["usuario"]==st.session_state.usuario["usuario"] and c["estado"]=="confirmada"]
    if not confirmadas:
        st.info("No tiene citas activas para cancelar.")
    else:
        opciones = [f"{c['servicio']} con {c['estilista']} — {c['fecha']} {c['hora']} (ID: {c['id']})" for c in confirmadas]
        sel = st.selectbox("Seleccione la cita a cancelar", opciones)
        cita_a_cancelar = confirmadas[opciones.index(sel)]
        if st.button("Cancelar esta cita"):
            for c in citas:
                if c["id"] == cita_a_cancelar["id"]:
                    c["estado"] = "cancelada"
                    break
            guardar_citas(citas)
            st.success("Cita cancelada exitosamente.")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINA: PERFIL
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "perfil" and st.session_state.usuario:
    u = st.session_state.usuario
    st.markdown('<div class="gs-section">Mi perfil</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="gs-card">
        <div class="gs-card-title">{u['nombre']}</div>
        <div class="gs-card-sub" style="margin-top:8px">Usuario: {u['usuario']}</div>
        <div class="gs-card-sub">Teléfono: {u['telefono']}</div>
        <div class="gs-card-sub">Registrado el: {u['registro']}</div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# REDIRIGIR si está logueado y en "inicio"
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.pagina == "inicio" and st.session_state.usuario:
    ir("reservar")
    st.rerun()
