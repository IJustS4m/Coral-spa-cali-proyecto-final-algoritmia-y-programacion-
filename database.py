import sqlite3
import hashlib
import os
import uuid
from datetime import datetime

#archivo de base de datos 
DB_DIR  = "data"
DB_PATH = os.path.join(DB_DIR, "coral_spa.db")



# CONEXIÓN
def _conectar() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row          # acceso tipo dict: fila["nombre"]
    conn.execute("PRAGMA foreign_keys = ON") # activa integridad referencial
    return conn



# crear tablas si no existen

def init_db() -> None:
    conn = _conectar()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario     TEXT PRIMARY KEY,
            contrasena  TEXT NOT NULL,
            nombre      TEXT NOT NULL,
            telefono    TEXT NOT NULL,
            registro    TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS estilistas (
            id              TEXT PRIMARY KEY,
            nombre          TEXT NOT NULL,
            calificacion    REAL NOT NULL,
            especialidades  TEXT NOT NULL,
            bio             TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre   TEXT    NOT NULL UNIQUE,
            precio   REAL    NOT NULL,
            duracion TEXT    NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id               TEXT PRIMARY KEY,
            usuario          TEXT NOT NULL,
            estilista_id     TEXT NOT NULL,
            estilista_nombre TEXT NOT NULL,
            servicio_nombre  TEXT NOT NULL,
            precio           REAL NOT NULL,
            duracion         TEXT NOT NULL,
            fecha            TEXT NOT NULL,
            hora             TEXT NOT NULL,
            estado           TEXT NOT NULL CHECK(estado IN ('confirmada','cancelada')),
            creada_el        TEXT NOT NULL,
            FOREIGN KEY (usuario)      REFERENCES usuarios(usuario),
            FOREIGN KEY (estilista_id) REFERENCES estilistas(id)
        )
    """)

    conn.commit()
    _poblar_estilistas(conn)
    _poblar_servicios(conn)
    conn.close()


# ── Datos iniciales de estilistas 
_ESTILISTAS_INICIALES = [
    ("est001", "Ana Arias Torres", 4.5,
     "Especialista en Manicure y Pedicure",
      "Experta en cuidado de uñas con más de 5 años de experiencia."),
    ("est002", "Maria Jose Araujo", 4.9,
     "Cortes masculinos,Degradados,Diseño de barba, Manicure y pedicure, entre otras cosas que se realizan en el spa",
     "Profesional integral del spa con amplia experiencia."),
    ("est003", "Diana Patricia torres Arias ", 5.0,
     "Cortes masculinos,Degradados,Diseño de barba, Manicure y pedicure, entre otras cosas que se realizan en el spa",
     "Profesional integral del spa con amplia experiencia."),
]

# ── Datos iniciales de servicios 
_SERVICIOS_INICIALES = [
    # Manicure y pedicure
("manicure manos",                              11000,  "45min"),
("manicure pies",                               13000,  "45min"),
("semi en manos",                               45000,  "1hora"),
("semi en pies",                                60000,  "1hora"),
("spa de manos",                                20000,  "30min"),
("spa de pies",                                 22000,  "30min"),
# Depilación con cera
("depilación cera - Axilas",                    13000,  "20min"),
("depilación cera - Bozo",                       6000,  "15min"),
("depilación cera - Cejas",                     10000,  "15min"),
("depilación cera - Bikini completo",           40000,  "30min"),
("depilación cera - Bikini parcial",            27000,  "20min"),
("depilación cera - Pierna completa",           50000,  "45min"),
("depilación cera - Pierna",                    23000,  "30min"),
# Sección facial
("diseño de cejas con henna",                   17000,  "30min"),
("pestañas",                                    17000,  "45min"),
("lifting de pestañas",                         70000,  "1hora"),
("microdermoabrasión",                          50000,  "45min"),
("limpieza facial profunda",                    90000,  "1hora"),
("hydrofacial",                                120000,  "1.5horas"),
("hydrofacial + limpieza facial",              140000,  "2horas"),
# Depilación láser
("depilación laser - Axilas",                   80000,  "30min"),
("depilación laser - Bikini",                  120000,  "45min"),
("depilación laser - Bozo",                     40000,  "20min"),
("depilación laser - Barba",                    60000,  "30min"),
("depilación laser - Pierna",                  100000,  "1hora"),
("depilación laser - Pecho",                    90000,  "45min"),
("depilación laser - Linea alba",               60000,  "20min"),
("depilacion laser - Patillas",                 60000,  "20min"),
# Sección corporal
("tratamiento reductor",                        50000,  "1hora"),
("tratamiento anticelulitis",                   60000,  "1hora"),
("anticelulitis piernas + tonificación glúteos",100000, "1hora"),
("drenaje post-operatorio",                    150000,  "1hora"),
("drenaje linfático",                           50000,  "1hora"),
("masajes terapéuticos",                        50000,  "1hora"),
# Masajes relajantes
("masaje relajante 1",                            25000,  "15min"),
("masaje relajante 2",                            90000,  "1hora"),
("masaje relajante 3",                            50000,  "2horas"),
("SPA",                                         120000,  "2horas"),

]


def _poblar_estilistas(conn: sqlite3.Connection) -> None:
    """Inserta los estilistas solo si la tabla está vacía."""
    if conn.execute("SELECT COUNT(*) FROM estilistas").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO estilistas VALUES (?,?,?,?,?)",
            _ESTILISTAS_INICIALES
        )
        conn.commit()


def _poblar_servicios(conn: sqlite3.Connection) -> None:
    """Inserta los servicios solo si la tabla está vacía."""
    if conn.execute("SELECT COUNT(*) FROM servicios").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO servicios (nombre, precio, duracion) VALUES (?,?,?)",
            _SERVICIOS_INICIALES
        )
        conn.commit()



# UTILIDADES INTERNAS

def _hash_pw(pw: str) -> str:
    """Devuelve el hash SHA-256 de una contraseña en texto plano."""
    return hashlib.sha256(pw.encode()).hexdigest()



# USUARIOS
def registrar_usuario(usuario: str, contrasena: str,
                      nombre: str, telefono: str,
                      fecha_registro: str) -> bool:  
    try:
        conn = _conectar()
        conn.execute(
            "INSERT INTO usuarios VALUES (?,?,?,?,?)",
            (usuario.lower(), _hash_pw(contrasena), nombre, telefono, fecha_registro)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # si el l usuario ya existe 
        return False
    finally:
        conn.close()


def verificar_usuario(usuario: str, contrasena: str) -> bool:
    """
    Comprueba si las credenciales son válidas.

    Retorna True si el usuario existe y la contraseña coincide.
    """
    conn = _conectar()
    fila = conn.execute(
        "SELECT contrasena FROM usuarios WHERE usuario = ?",
        (usuario.lower(),)
    ).fetchone()
    conn.close()

    if fila is None:
        return False                            # usuario no existe
    return fila["contrasena"] == _hash_pw(contrasena)


def obtener_usuario(usuario: str) -> dict | None:
    """
    Devuelve los datos públicos de un usuario como diccionario,
    o None si no existe.
    No incluye la contraseña.
    """
    conn = _conectar()
    fila = conn.execute(
        "SELECT usuario, nombre, telefono, registro FROM usuarios WHERE usuario = ?",
        (usuario.lower(),)
    ).fetchone()
    conn.close()

    if fila is None:
        return None
    return dict(fila)   # {"usuario": ..., "nombre": ..., "telefono": ..., "registro": ...}


def usuario_existe(usuario: str) -> bool:
    conn = _conectar()
    existe = conn.execute(
        "SELECT 1 FROM usuarios WHERE usuario = ?",
        (usuario.lower(),)
    ).fetchone() is not None
    conn.close()
    return existe

# CITAS


def crear_cita(usuario: str, estilista_id: str, estilista_nombre: str,
               servicio_nombre: str, precio: float, duracion: str,
               fecha: str, hora: str) -> str:
    """
    Registra una nueva cita confirmada.

    Retorna el ID de confirmación generado (ej. "GS-A1B2C3D4").
    """
    cita_id   = "GS-" + str(uuid.uuid4()).upper()[:8]
    creada_el = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = _conectar()
    conn.execute(
        """INSERT INTO citas
           (id, usuario, estilista_id, estilista_nombre,
            servicio_nombre, precio, duracion, fecha, hora, estado, creada_el)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (cita_id, usuario, estilista_id, estilista_nombre,
         servicio_nombre, precio, duracion, fecha, hora, "confirmada", creada_el)
    )
    conn.commit()
    conn.close()
    return cita_id


def obtener_citas_usuario(usuario: str) -> list[dict]:
    """
    Devuelve todas las citas (confirmadas y canceladas) de un usuario,
    ordenadas de más reciente a más antigua.
    """
    conn  = _conectar()
    filas = conn.execute(
        "SELECT * FROM citas WHERE usuario = ? ORDER BY creada_el DESC",
        (usuario,)
    ).fetchall()
    conn.close()
    return [dict(f) for f in filas]


def cancelar_cita(cita_id: str, usuario: str) -> bool:
    """
    Cambia el estado de una cita a "cancelada".
    Verifica que la cita pertenezca al usuario para mayor seguridad.

    Retorna True si se canceló, False si no se encontró o no pertenece al usuario.
    """
    conn = _conectar()
    cur  = conn.execute(
        "UPDATE citas SET estado = 'cancelada' WHERE id = ? AND usuario = ? AND estado = 'confirmada'",
        (cita_id, usuario)
    )
    conn.commit()
    filas_afectadas = cur.rowcount
    conn.close()
    return filas_afectadas > 0


def horarios_ocupados(estilista_id: str, fecha: str) -> set[str]:
    """
    Devuelve el conjunto de horarios ya reservados (confirmados) para
    un estilista en una fecha determinada.

    Uso en app.py:
        ocupados = horarios_ocupados(estilista_id, fecha_sel)
        libres   = [h for h in HORARIOS if h not in ocupados]
    """
    conn  = _conectar()
    filas = conn.execute(
        """SELECT hora FROM citas
           WHERE estilista_id = ? AND fecha = ? AND estado = 'confirmada'""",
        (estilista_id, fecha)
    ).fetchall()
    conn.close()
    return {f["hora"] for f in filas}


# ═══════════════════════════════════════════════════════════════════════════════
# CATÁLOGOS (estilistas y servicios)
# ═══════════════════════════════════════════════════════════════════════════════

def obtener_estilistas() -> list[dict]:
    """
    Devuelve la lista completa de estilistas.
    El campo 'especialidades' se convierte de texto CSV a lista Python.
    """
    conn  = _conectar()
    filas = conn.execute("SELECT * FROM estilistas ORDER BY calificacion DESC").fetchall()
    conn.close()

    resultado = []
    for f in filas:
        d = dict(f)
        d["especialidades"] = d["especialidades"].split(",")  # "a,b,c" → ["a","b","c"]
        resultado.append(d)
    return resultado


def obtener_servicios() -> list[dict]:
    """Devuelve la lista completa de servicios con precio y duración."""
    conn  = _conectar()
    filas = conn.execute("SELECT * FROM servicios ORDER BY id").fetchall()
    conn.close()
    return [dict(f) for f in filas]


# ═══════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA — solo para pruebas manuales
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Ejecutar este archivo directamente crea la base de datos y muestra
    # un resumen de las tablas creadas. Útil para verificar la instalación.
    print("Inicializando base de datos...")
    init_db()
    print(f"  ✓ Base de datos creada en: {DB_PATH}")

    conn = _conectar()
    tablas = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"  ✓ Tablas: {[t['name'] for t in tablas]}")

    n_est = conn.execute("SELECT COUNT(*) FROM estilistas").fetchone()[0]
    n_ser = conn.execute("SELECT COUNT(*) FROM servicios").fetchone()[0]
    print(f"  ✓ Estilistas cargados: {n_est}")
    print(f"  ✓ Servicios cargados:  {n_ser}")
    conn.close()
    print("Listo.")
