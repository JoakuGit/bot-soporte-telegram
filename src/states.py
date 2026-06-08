"""Estados y sesiones temporales del bot.

La maquina de estados vive en memoria porque el Trabajo Practico pide una
solucion simple. Cada usuario queda identificado por su telegram_id.
"""

INICIO = "INICIO"
MENU_PRINCIPAL = "MENU_PRINCIPAL"
ESPERANDO_NOMBRE = "ESPERANDO_NOMBRE"
ESPERANDO_AREA = "ESPERANDO_AREA"
ESPERANDO_CATEGORIA = "ESPERANDO_CATEGORIA"
ESPERANDO_DESCRIPCION = "ESPERANDO_DESCRIPCION"
ESPERANDO_URGENCIA = "ESPERANDO_URGENCIA"
VALIDANDO_DATOS = "VALIDANDO_DATOS"
REGISTRANDO_TICKET = "REGISTRANDO_TICKET"
TICKET_CREADO = "TICKET_CREADO"
CONSULTANDO_TICKET = "CONSULTANDO_TICKET"
ERROR_ENTRADA = "ERROR_ENTRADA"


_sessions = {}


def start_session(telegram_id: str) -> None:
    """Crea o reinicia la sesion temporal de un usuario."""
    _sessions[telegram_id] = {
        "estado": INICIO,
        "datos": {},
    }


def get_session(telegram_id: str) -> dict:
    """Devuelve la sesion del usuario; si no existe, la crea."""
    if telegram_id not in _sessions:
        start_session(telegram_id)
    return _sessions[telegram_id]


def set_state(telegram_id: str, state: str) -> None:
    """Actualiza el estado actual de la conversacion."""
    session = get_session(telegram_id)
    session["estado"] = state


def get_state(telegram_id: str) -> str:
    """Obtiene el estado actual de la conversacion."""
    return get_session(telegram_id)["estado"]


def set_data(telegram_id: str, key: str, value: str) -> None:
    """Guarda un dato temporal hasta completar el ticket."""
    session = get_session(telegram_id)
    session["datos"][key] = value


def get_data(telegram_id: str) -> dict:
    """Devuelve los datos capturados hasta el momento."""
    return get_session(telegram_id)["datos"]


def clear_session(telegram_id: str) -> None:
    """Elimina la sesion temporal del usuario."""
    _sessions.pop(telegram_id, None)