"""Persistencia SQLite para usuarios y tickets de soporte."""

from datetime import datetime
from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "soporte.db"


def get_connection() -> sqlite3.Connection:
    """Abre una conexion SQLite y activa claves foraneas."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    """Crea la base de datos y sus tablas si todavia no existen."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                area TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                urgencia TEXT NOT NULL,
                prioridad TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Nuevo',
                fecha_creacion TEXT NOT NULL,
                FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
            )
            """
        )
        connection.commit()


def get_or_create_user(telegram_id: str, nombre: str, area: str) -> int:
    """Obtiene el usuario por telegram_id o lo crea si es la primera vez."""
    with get_connection() as connection:
        existing_user = connection.execute(
            "SELECT id_usuario FROM usuarios WHERE telegram_id = ?",
            (telegram_id,),
        ).fetchone()

        if existing_user:
            connection.execute(
                "UPDATE usuarios SET nombre = ?, area = ? WHERE telegram_id = ?",
                (nombre, area, telegram_id),
            )
            connection.commit()
            return int(existing_user["id_usuario"])

        cursor = connection.execute(
            """
            INSERT INTO usuarios (telegram_id, nombre, area)
            VALUES (?, ?, ?)
            """,
            (telegram_id, nombre, area),
        )
        connection.commit()
        return int(cursor.lastrowid)


def create_ticket(
    id_usuario: int,
    categoria: str,
    descripcion: str,
    urgencia: str,
    prioridad: str,
) -> int:
    """Registra un ticket nuevo y devuelve su numero de seguimiento."""
    fecha_creacion = datetime.now().isoformat(timespec="seconds")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                id_usuario,
                categoria,
                descripcion,
                urgencia,
                prioridad,
                estado,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, 'Nuevo', ?)
            """,
            (id_usuario, categoria, descripcion, urgencia, prioridad, fecha_creacion),
        )
        connection.commit()
        return int(cursor.lastrowid)


def get_ticket_by_id(id_ticket: int) -> dict | None:
    """Consulta un ticket por numero de seguimiento."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                tickets.id_ticket,
                tickets.categoria,
                tickets.descripcion,
                tickets.urgencia,
                tickets.prioridad,
                tickets.estado,
                tickets.fecha_creacion,
                usuarios.nombre,
                usuarios.area
            FROM tickets
            INNER JOIN usuarios ON usuarios.id_usuario = tickets.id_usuario
            WHERE tickets.id_ticket = ?
            """,
            (id_ticket,),
        ).fetchone()

    if row is None:
        return None
    return dict(row)