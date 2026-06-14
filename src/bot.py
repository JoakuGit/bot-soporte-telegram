"""Bot de Telegram para gestionar tickets de soporte tecnico nivel 1."""

import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from db import create_ticket, get_or_create_user, get_ticket_by_id, init_db
from states import (
    CONSULTANDO_TICKET,
    ERROR_ENTRADA,
    ESPERANDO_AREA,
    ESPERANDO_CATEGORIA,
    ESPERANDO_DESCRIPCION,
    ESPERANDO_NOMBRE,
    ESPERANDO_URGENCIA,
    MENU_PRINCIPAL,
    REGISTRANDO_TICKET,
    TICKET_CREADO,
    VALIDANDO_DATOS,
    clear_session,
    get_data,
    get_state,
    set_data,
    set_state,
    start_session,
)
from validators import (
    CATEGORIAS_PERMITIDAS,
    URGENCIAS_PERMITIDAS,
    validate_area,
    validate_category,
    validate_description,
    validate_name,
    validate_urgency,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

MENU_CREAR = "Crear ticket"
MENU_CONSULTAR = "Consultar ticket"
MENU_CANCELAR = "Cancelar"


def _telegram_id(update: Update) -> str:
    """Obtiene el id de Telegram como texto para usarlo como clave."""
    if update.effective_user is None:
        return "sin_usuario"
    return str(update.effective_user.id)


def _main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[MENU_CREAR], [MENU_CONSULTAR], [MENU_CANCELAR]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def _options_keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[option] for option in options],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def _show_main_menu(update: Update, text: str) -> None:
    """Muestra el menu principal y deja al usuario en estado de menu."""
    telegram_id = _telegram_id(update)
    set_state(telegram_id, MENU_PRINCIPAL)
    await update.message.reply_text(text, reply_markup=_main_menu_keyboard())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start: inicia la sesion y muestra el menu principal."""
    telegram_id = _telegram_id(update)
    start_session(telegram_id)

    message = (
        "Bienvenido al bot de Soporte Tecnico Interno de KodraSoft.\n\n"
        "Seleccione una opcion del menu principal."
    )
    await _show_main_menu(update, message)


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /cancelar: cancela cualquier carga en curso."""
    telegram_id = _telegram_id(update)
    clear_session(telegram_id)
    start_session(telegram_id)

    await _show_main_menu(
        update,
        "Operacion cancelada. Puede iniciar una nueva gestion desde el menu.",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Deriva cada mensaje de texto segun el estado actual del usuario."""
    if update.message is None or update.message.text is None:
        return

    telegram_id = _telegram_id(update)
    text = update.message.text.strip()

    if text == MENU_CANCELAR:
        await cancelar(update, context)
        return

    state = get_state(telegram_id)

    if state == MENU_PRINCIPAL:
        await _handle_main_menu(update, text)
    elif state == ESPERANDO_NOMBRE:
        await _handle_name(update, telegram_id, text)
    elif state == ESPERANDO_AREA:
        await _handle_area(update, telegram_id, text)
    elif state == ESPERANDO_CATEGORIA:
        await _handle_category(update, telegram_id, text)
    elif state == ESPERANDO_DESCRIPCION:
        await _handle_description(update, telegram_id, text)
    elif state == ESPERANDO_URGENCIA:
        await _handle_urgency(update, telegram_id, text)
    elif state == CONSULTANDO_TICKET:
        await _handle_ticket_query(update, telegram_id, text)
    else:
        await _show_main_menu(
            update,
            "No se reconoce el estado actual. Volvemos al menu principal.",
        )


async def _handle_main_menu(update: Update, text: str) -> None:
    telegram_id = _telegram_id(update)

    if text == MENU_CREAR:
        set_state(telegram_id, ESPERANDO_NOMBRE)
        await update.message.reply_text(
            "Ingrese su nombre:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    if text == MENU_CONSULTAR:
        set_state(telegram_id, CONSULTANDO_TICKET)
        await update.message.reply_text(
            "Ingrese el numero de ticket que desea consultar:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    await _show_main_menu(
        update,
        "Opcion invalida. Seleccione una opcion del menu principal.",
    )


async def _handle_name(update: Update, telegram_id: str, text: str) -> None:
    is_valid, name, error_message = validate_name(text)
    if not is_valid:
        await _send_validation_error(update, telegram_id, error_message, ESPERANDO_NOMBRE)
        return

    set_data(telegram_id, "nombre", name)
    set_state(telegram_id, ESPERANDO_AREA)
    await update.message.reply_text("Ingrese su area o sector:")


async def _handle_area(update: Update, telegram_id: str, text: str) -> None:
    is_valid, area, error_message = validate_area(text)
    if not is_valid:
        await _send_validation_error(update, telegram_id, error_message, ESPERANDO_AREA)
        return

    set_data(telegram_id, "area", area)
    set_state(telegram_id, ESPERANDO_CATEGORIA)
    await update.message.reply_text(
        "Seleccione la categoria del problema:",
        reply_markup=_options_keyboard(CATEGORIAS_PERMITIDAS),
    )


async def _handle_category(update: Update, telegram_id: str, text: str) -> None:
    is_valid, category, error_message = validate_category(text)
    if not is_valid:
        await _send_validation_error(
            update,
            telegram_id,
            error_message,
            ESPERANDO_CATEGORIA,
            _options_keyboard(CATEGORIAS_PERMITIDAS),
        )
        return

    set_data(telegram_id, "categoria", category)
    set_state(telegram_id, ESPERANDO_DESCRIPCION)
    await update.message.reply_text(
        "Describa el incidente con al menos 10 caracteres:",
        reply_markup=ReplyKeyboardRemove(),
    )


async def _handle_description(update: Update, telegram_id: str, text: str) -> None:
    is_valid, description, error_message = validate_description(text)
    if not is_valid:
        await _send_validation_error(update, telegram_id, error_message, ESPERANDO_DESCRIPCION)
        return

    set_data(telegram_id, "descripcion", description)
    set_state(telegram_id, ESPERANDO_URGENCIA)
    await update.message.reply_text(
        "Seleccione el nivel de urgencia:",
        reply_markup=_options_keyboard(URGENCIAS_PERMITIDAS),
    )


async def _handle_urgency(update: Update, telegram_id: str, text: str) -> None:
    is_valid, urgency, error_message = validate_urgency(text)
    if not is_valid:
        await _send_validation_error(
            update,
            telegram_id,
            error_message,
            ESPERANDO_URGENCIA,
            _options_keyboard(URGENCIAS_PERMITIDAS),
        )
        return

    set_data(telegram_id, "urgencia", urgency)
    await _register_ticket(update, telegram_id)


async def _send_validation_error(
    update: Update,
    telegram_id: str,
    error_message: str,
    return_state: str,
    reply_markup=None,
) -> None:
    """Representa el camino infeliz ERROR_ENTRADA y vuelve al dato requerido."""
    set_state(telegram_id, ERROR_ENTRADA)
    await update.message.reply_text(error_message, reply_markup=reply_markup)
    set_state(telegram_id, return_state)


async def _register_ticket(update: Update, telegram_id: str) -> None:
    """Valida el conjunto final, calcula prioridad y registra el ticket."""
    set_state(telegram_id, VALIDANDO_DATOS)
    data = get_data(telegram_id)

    # Gateway BPMN: si la urgencia es Alta, el caso queda marcado prioritario.
    priority = "Prioritario" if data["urgencia"] == "Alta" else "Normal"

    set_state(telegram_id, REGISTRANDO_TICKET)
    user_id = get_or_create_user(
        telegram_id=telegram_id,
        nombre=data["nombre"],
        area=data["area"],
    )
    ticket_id = create_ticket(
        id_usuario=user_id,
        categoria=data["categoria"],
        descripcion=data["descripcion"],
        urgencia=data["urgencia"],
        prioridad=priority,
    )

    set_state(telegram_id, TICKET_CREADO)
    response = (
        "Ticket creado correctamente.\n\n"
        f"Numero de ticket: {ticket_id}\n"
        f"Categoria: {data['categoria']}\n"
        f"Urgencia: {data['urgencia']}\n"
        f"Prioridad: {priority}\n"
        "Estado: Nuevo"
    )
    await update.message.reply_text(response, reply_markup=_main_menu_keyboard())
    set_state(telegram_id, MENU_PRINCIPAL)


async def _handle_ticket_query(update: Update, telegram_id: str, text: str) -> None:
    if not text.isdigit() or int(text) <= 0:
        await _send_validation_error(
            update,
            telegram_id,
            "Debe ingresar un numero de ticket valido.",
            CONSULTANDO_TICKET,
        )
        return

    ticket = get_ticket_by_id(int(text))
    if ticket is None:
        await _show_main_menu(
            update,
            "No se encontro un ticket con ese numero.",
        )
        return

    response = (
        "Detalle del ticket consultado:\n\n"
        f"Numero de ticket: {ticket['id_ticket']}\n"
        f"Usuario: {ticket['nombre']}\n"
        f"Area: {ticket['area']}\n"
        f"Categoria: {ticket['categoria']}\n"
        f"Urgencia: {ticket['urgencia']}\n"
        f"Prioridad: {ticket['prioridad']}\n"
        f"Estado: {ticket['estado']}\n"
        f"Fecha de creacion: {ticket['fecha_creacion']}"
    )
    await _show_main_menu(update, response)


def main() -> None:
    """Punto de entrada del bot."""
    load_dotenv()
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("Falta configurar BOT_TOKEN en el archivo .env")

    init_db()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancelar", cancelar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot de soporte iniciado.")
    asyncio.set_event_loop(asyncio.new_event_loop())
    application.run_polling()


if __name__ == "__main__":
    main()
