# Bot de soporte tecnico nivel 1 - KodraSoft

Proyecto academico para simular la automatizacion de un proceso administrativo de soporte tecnico nivel 1 mediante un bot de Telegram.

La organizacion ficticia es **KodraSoft**, dentro del area de **Soporte Tecnico Interno**. El proceso inicia cuando un empleado abre el bot, selecciona la opcion de crear un ticket, carga los datos requeridos y recibe un numero de seguimiento.

## Stack utilizado

- Python 3.10+
- python-telegram-bot
- SQLite
- python-dotenv
- Archivo `.env` para guardar el token del bot

## Estructura del proyecto

```text
bot-soporte-telegram/
├── src/
│   ├── bot.py
│   ├── db.py
│   ├── states.py
│   └── validators.py
├── data/
│   └── soporte.db
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

El archivo `data/soporte.db` se crea automaticamente al iniciar el bot. Por eso no se versiona como archivo fijo del repositorio.

## Instalacion

Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## Obtener el token del bot con BotFather

1. Abrir Telegram y buscar `@BotFather`.
2. Enviar el comando `/newbot`.
3. Seguir las instrucciones: ingresar un nombre para el bot (ej. `Soporte Tecnico KodraSoft`) y un nombre de usuario que termine en `bot` (ej. `KodraSoftSoporteBot`).
4. BotFather devolvera un mensaje con el token del bot, similar a `123456789:AABhT8x8z...`.
5. Guardar ese token para usarlo en el archivo `.env`.

## Configuracion del .env

Copiar el archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

Editar `.env` y colocar el token real obtenido con BotFather:

```env
BOT_TOKEN=123456789:token_real_del_bot
```

## Como ejecutar el bot

Desde la raiz del proyecto:

```powershell
python src/bot.py
```

Al iniciar, el programa ejecuta `init_db()` y crea la base SQLite si no existe.

## Flujo funcional

1. El usuario envia `/start`.
2. El bot muestra el menu principal.
3. El usuario puede elegir `Crear ticket`, `Consultar ticket` o `Cancelar`.
4. Si elige `Crear ticket`, el bot solicita:
   - Nombre del usuario.
   - Area o sector.
   - Categoria del problema.
   - Descripcion del incidente.
   - Nivel de urgencia.
5. Si los datos son validos, se registra el ticket en SQLite.
6. El bot responde con numero de ticket, categoria, urgencia, prioridad y estado.
7. Si el usuario elige `Consultar ticket`, ingresa el numero y el bot devuelve el estado y datos principales.
8. El usuario puede cancelar la carga con `/cancelar` o con la opcion `Cancelar`.

## Categorias y urgencias permitidas

Categorias:

- Acceso
- Sistema
- Internet
- Equipo
- Otro

Urgencias:

- Baja
- Media
- Alta

## Reglas de validacion

- El nombre no puede estar vacio.
- El area no puede estar vacia.
- La categoria debe estar dentro de las opciones permitidas.
- La descripcion debe tener al menos 10 caracteres.
- La urgencia debe ser `Baja`, `Media` o `Alta`.

Si un dato es invalido, el bot informa el error y vuelve a pedir el mismo dato.

## Relacion con el BPMN TO-BE

El codigo representa el BPMN TO-BE mediante una maquina de estados simple:

- `INICIO`: el usuario abre el bot.
- `MENU_PRINCIPAL`: el usuario decide si crea o consulta un ticket.
- `ESPERANDO_NOMBRE`, `ESPERANDO_AREA`, `ESPERANDO_CATEGORIA`, `ESPERANDO_DESCRIPCION`, `ESPERANDO_URGENCIA`: tareas de captura de datos.
- `VALIDANDO_DATOS`: gateway equivalente a la pregunta "Datos validos?".
- `REGISTRANDO_TICKET`: tarea automatizada de registro en la base de datos.
- `TICKET_CREADO`: fin exitoso del proceso de alta.
- `CONSULTANDO_TICKET`: camino alternativo de consulta.
- `ERROR_ENTRADA`: camino infeliz cuando un dato no cumple las reglas.

Tambien existe un gateway de prioridad:

- Urgencia `Alta` genera prioridad `Prioritario`.
- Urgencia `Baja` o `Media` genera prioridad `Normal`.

## Base de datos

La tabla `usuarios` guarda los datos del empleado:

- `id_usuario`
- `telegram_id`
- `nombre`
- `area`

La tabla `tickets` guarda cada solicitud:

- `id_ticket`
- `id_usuario`
- `categoria`
- `descripcion`
- `urgencia`
- `prioridad`
- `estado`
- `fecha_creacion`

El estado inicial de cada ticket es `Nuevo`.

## Pruebas sugeridas

Casos felices:

- Crear ticket con urgencia `Alta` y verificar prioridad `Prioritario`.
- Crear ticket con urgencia `Media` y verificar prioridad `Normal`.
- Consultar un ticket existente por numero.

Caminos infelices:

- Ingresar nombre vacio.
- Ingresar area vacia.
- Ingresar categoria no permitida.
- Ingresar descripcion con menos de 10 caracteres.
- Ingresar urgencia no permitida.
- Consultar un numero de ticket inexistente.
- Cancelar la carga con `/cancelar` antes de finalizar.

## Consideraciones academicas

La solucion prioriza claridad y facilidad de defensa oral:

- `bot.py` contiene el flujo conversacional y los handlers de Telegram.
- `db.py` concentra la persistencia SQLite.
- `states.py` contiene la memoria temporal de la maquina de estados.
- `validators.py` concentra las reglas de negocio de validacion.
- La base de datos demuestra persistencia real de informacion.
- La maquina de estados demuestra memoria conversacional por usuario.
- Las decisiones de validacion y prioridad representan gateways del proceso BPMN.
