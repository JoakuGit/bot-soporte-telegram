"""Validaciones del proceso de soporte tecnico nivel 1."""

CATEGORIAS_PERMITIDAS = ["Acceso", "Sistema", "Internet", "Equipo", "Otro"]
URGENCIAS_PERMITIDAS = ["Baja", "Media", "Alta"]


def _normalize_option(value: str, allowed_values: list[str]) -> str | None:
    """Busca una opcion permitida ignorando mayusculas y espacios."""
    normalized_value = value.strip().lower()
    for allowed_value in allowed_values:
        if normalized_value == allowed_value.lower():
            return allowed_value
    return None


def validate_name(value: str) -> tuple[bool, str, str]:
    """Valida que el nombre no este vacio."""
    name = value.strip()
    if not name:
        return False, name, "El nombre no puede estar vacio. Ingrese su nombre."
    return True, name, ""


def validate_area(value: str) -> tuple[bool, str, str]:
    """Valida que el area o sector no este vacio."""
    area = value.strip()
    if not area:
        return False, area, "El area o sector no puede estar vacio. Ingrese su area."
    return True, area, ""


def validate_category(value: str) -> tuple[bool, str, str]:
    """Valida que la categoria pertenezca al listado permitido."""
    category = _normalize_option(value, CATEGORIAS_PERMITIDAS)
    if category is None:
        allowed_text = ", ".join(CATEGORIAS_PERMITIDAS)
        return False, "", f"Categoria invalida. Opciones permitidas: {allowed_text}."
    return True, category, ""


def validate_description(value: str) -> tuple[bool, str, str]:
    """Valida que la descripcion tenga suficiente detalle."""
    description = value.strip()
    if len(description) < 10:
        return False, description, "La descripcion debe tener al menos 10 caracteres."
    return True, description, ""


def validate_urgency(value: str) -> tuple[bool, str, str]:
    """Valida que la urgencia pertenezca al listado permitido."""
    urgency = _normalize_option(value, URGENCIAS_PERMITIDAS)
    if urgency is None:
        allowed_text = ", ".join(URGENCIAS_PERMITIDAS)
        return False, "", f"Urgencia invalida. Opciones permitidas: {allowed_text}."
    return True, urgency, ""