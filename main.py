import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, JobQueue
import datetime
from telegram.error import BadRequest, Conflict # Importamos errores específicos

# --- Configuración de Logging ---
# Configura el logging para que sea menos ruidoso y maneje los errores de forma más limpia.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO # Puedes cambiar a logging.DEBUG para más detalle si lo necesitas
)
# Silencia los logs de httpx (librería subyacente para peticiones HTTP) para evitar spam.
logging.getLogger("httpx").setLevel(logging.WARNING)

# --- Datos del Corán (Mantienen como estaban) ---
SURAH_NAMES = {
    1: "Al-Fatiha - الفاتحة", 2: "Al-Baqarah - البقرة", 3: "Ali-Imran - آل عمران", 4: "An-Nisa - النساء",
    5: "Al-Ma'idah - المائدة", 6: "Al-An'am - الأنعام", 7: "Al-A'raf - الأعراف", 8: "Al-Anfal - الأنفال",
    9: "At-Tawbah - التوبة", 10: "Yunus - يونس", 11: "Hud - هود", 12: "Yusuf - يوسف",
    13: "Ar-Ra'd - الرعد", 14: "Ibrahim - إبراهيم", 15: "Al-Hijr - الحجر", 16: "An-Nahl - النحل",
    17: "Al-Isra - الإسراء", 18: "Al-Kahf - الكهف", 19: "Maryam - مريم", 20: "Ta-Ha - طه",
    21: "Al-Anbiya - الأنبياء", 22: "Al-Hajj - الحج", 23: "Al-Mu'minun - المؤمنون", 24: "An-Nur - النور",
    25: "Al-Furqan - الفرقان", 26: "Ash-Shu'ara - الشعراء", 27: "An-Naml - النمل", 28: "Al-Qasas - القصص",
    29: "Al-Ankabut - العنكبut", 30: "Ar-Rum - الروم", 31: "Luqman - لقمان", 32: "As-Sajdah - السجدة",
    33: "Al-Ahzab - الأحزاب", 34: "Saba - سبأ", 35: "Fatir - فاطر", 36: "Ya-Sin - يس",
    37: "As-Saffat - الصافات", 38: "Sad - ص", 39: "Az-Zumar - الزمر", 40: "Ghafir - غافر",
    41: "Fussilat - فصلت", 42: "Ash-Shura - الشورى", 43: "Az-Zukhruf - الزخرف", 44: "Ad-Dukhan - الدخان",
    45: "Al-Jathiyah - الجاثية", 46: "Al-Ahqaf - الأحقاف", 47: "Muhammad - محمد", 48: "Al-Fath - الفتح",
    49: "Al-Hujurat - الحجرات", 50: "Qaf - ق", 51: "Adh-Dhariyat - الذاريات", 52: "At-Tur - الطور",
    53: "An-Najm - النجم", 54: "Al-Qamar - القمر", 55: "Ar-Rahman - الرحمن", 56: "Al-Waqi'ah - الواقعة",
    57: "Al-Hadid - الحديد", 58: "Al-Mujadila - المجادلة", 59: "Al-Hashr - الحشر", 60: "Al-Mumtahanah - الممتحنة",
    61: "As-Saff - الصف", 62: "Al-Jumu'ah - الجمعة", 63: "Al-Munafiqun - المنافقون", 64: "At-Taghabun - التغابن",
    65: "At-Talaq - الطلاق", 66: "At-Tahrim - التحريم", 67: "Al-Mulk - الملك", 68: "Al-Qalam - القلم",
    69: "Al-Haqqah - الحاقة", 70: "Al-Ma'arij - المعارج", 71: "Nuh - نوح", 72: "Al-Jinn - الجن",
    73: "Al-Muzzammil - المزّمّل", 74: "Al-Muddaththir - المدّثر", 75: "Al-Qiyamah - القيامة", 76: "Al-Insan - الإنسان",
    77: "Al-Mursalat - المرسلات", 78: "An-Naba - النبأ", 79: "An-Nazi'at - النازعات", 80: "Abasa - عبس",
    81: "At-Takwir - التكوير", 82: "Al-Infitar - الإنفطار", 83: "Al-Mutaffifin - المطفّفين", 84: "Al-Inshiqaq - الإنشقاق",
    85: "Al-Buruj - البروج", 86: "At-Tariq - الطارق", 87: "Al-A'la - الأعلى", 88: "Al-Ghashiyah - الغاشية",
    89: "Al-Fajr - الفجر", 90: "Al-Balad - البلد", 91: "Ash-Shams - الشمس", 92: "Al-Lail - الليل",
    93: "Ad-Duha - الضحى", 94: "Ash-Sharh - الشرح", 95: "At-Tin - التين", 96: "Al-'Alaq - العلق",
    97: "Al-Qadr - القدر", 98: "Al-Bayyinah - البيِّنة", 99: "Az-Zalzalah - الزلزلة", 100: "Al-'Adiyat - العاديات",
    101: "Al-Qari'ah - القارعة", 102: "At-Takathur - التكاثر", 103: "Al-Asr - العصر", 104: "Al-Humazah - الهمزة",
    105: "Al-Fil - الفيل", 106: "Quraysh - قريش", 107: "Al-Ma'un - الماعون", 108: "Al-Kawthar - الكوثر",
    109: "Al-Kafirun - الكافرون", 110: "An-Nasr - النصر", 111: "Al-Masad - المسد", 112: "Al-Ikhlas - الإخلاص",
    113: "Al-Falaq - الفلق", 114: "An-Nas - الناس",
}

QURAN_PLAN = [
    {"juz": 1, "start": {"surah": 1, "ayah": 1}, "end": {"surah": 2, "ayah": 141}},
    {"juz": 2, "start": {"surah": 2, "ayah": 142}, "end": {"surah": 2, "ayah": 252}},
    {"juz": 3, "start": {"surah": 2, "ayah": 253}, "end": {"surah": 3, "ayah": 92}},
    {"juz": 4, "start": {"surah": 3, "ayah": 93}, "end": {"surah": 4, "ayah": 23}},
    {"juz": 5, "start": {"surah": 4, "ayah": 24}, "end": {"surah": 4, "ayah": 147}},
    {"juz": 6, "start": {"surah": 4, "ayah": 148}, "end": {"surah": 5, "ayah": 81}},
    {"juz": 7, "start": {"surah": 5, "ayah": 82}, "end": {"surah": 6, "ayah": 110}},
    {"juz": 8, "start": {"surah": 6, "ayah": 111}, "end": {"surah": 7, "ayah": 87}},
    {"juz": 9, "start": {"surah": 7, "ayah": 88}, "end": {"surah": 8, "ayah": 40}},
    {"juz": 10, "start": {"surah": 8, "ayah": 41}, "end": {"surah": 9, "ayah": 92}},
    {"juz": 11, "start": {"surah": 9, "ayah": 93}, "end": {"surah": 11, "ayah": 5}},
    {"juz": 12, "start": {"surah": 11, "ayah": 6}, "end": {"surah": 12, "ayah": 52}},
    {"juz": 13, "start": {"surah": 12, "ayah": 53}, "end": {"surah": 14, "ayah": 52}},
    {"juz": 14, "start": {"surah": 15, "ayah": 1}, "end": {"surah": 16, "ayah": 128}},
    {"juz": 15, "start": {"surah": 17, "ayah": 1}, "end": {"surah": 18, "ayah": 74}},
    {"juz": 16, "start": {"surah": 18, "ayah": 75}, "end": {"surah": 20, "ayah": 135}},
    {"juz": 17, "start": {"surah": 21, "ayah": 1}, "end": {"surah": 22, "ayah": 78}},
    {"juz": 18, "start": {"surah": 23, "ayah": 1}, "end": {"surah": 25, "ayah": 20}},
    {"juz": 19, "start": {"surah": 25, "ayah": 21}, "end": {"surah": 27, "ayah": 55}},
    {"juz": 20, "start": {"surah": 27, "ayah": 56}, "end": {"surah": 29, "ayah": 45}},
    {"juz": 21, "start": {"surah": 29, "ayah": 46}, "end": {"surah": 33, "ayah": 30}},
    {"juz": 22, "start": {"surah": 33, "ayah": 31}, "end": {"surah": 36, "ayah": 27}},
    {"juz": 23, "start": {"surah": 36, "ayah": 28}, "end": {"surah": 39, "ayah": 31}},
    {"juz": 24, "start": {"surah": 39, "ayah": 32}, "end": {"surah": 41, "ayah": 46}},
    {"juz": 25, "start": {"surah": 41, "ayah": 47}, "end": {"surah": 45, "ayah": 37}},
    {"juz": 26, "start": {"surah": 46, "ayah": 1}, "end": {"surah": 51, "ayah": 30}},
    {"juz": 27, "start": {"surah": 51, "ayah": 31}, "end": {"surah": 57, "ayah": 29}},
    {"juz": 28, "start": {"surah": 58, "ayah": 1}, "end": {"surah": 66, "ayah": 12}},
    {"juz": 29, "start": {"surah": 67, "ayah": 1}, "end": {"surah": 77, "ayah": 50}},
    {"juz": 30, "start": {"surah": 78, "ayah": 1}, "end": {"surah": 114, "ayah": 6}}
]

# Almacenamiento de preferencias del usuario. En un entorno real, esto debería ser una base de datos.
user_preferences = {}

# --- Funciones de Utilidad ---

def get_juz_info(juz_number: int):
    """Obtiene la información de un Juz específico."""
    if 1 <= juz_number <= len(QURAN_PLAN):
        return QURAN_PLAN[juz_number - 1]
    return None

def calculate_current_juz(user_id: int):
    """Calcula el Juz actual para un usuario."""
    prefs = user_preferences.get(user_id)
    if not prefs:
        return 0 # No preferences, no juz

    mode = prefs['mode']
    start_date = prefs['start_date']
    hoy = datetime.date.today()

    if mode == 'daily':
        delta = (hoy - start_date).days
    else:  # weekly
        delta = ((hoy - start_date).days) // 7
    
    # Asegura que no se exceda el número de juzes
    return min(delta + 1, len(QURAN_PLAN))

async def send_juz_message(user_id: int, context: ContextTypes.DEFAULT_TYPE, juz_number: int, message_id_to_edit=None):
    """Envía el mensaje con la información del Juz."""
    juz_info = get_juz_info(juz_number)
    if not juz_info:
        await context.bot.send_message(chat_id=user_id, text="No se encontró información para este Juz.")
        return

    start_surah = juz_info['start']['surah']
    start_ayah = juz_info['start']['ayah']
    end_surah = juz_info['end']['surah']
    end_ayah = juz_info['end']['ayah']

    texto = (
        f"📖 *Juz {juz_number}* del Corán\n"
        f"Desde: *{SURAH_NAMES.get(start_surah, 'Sura desconocida')}* (Aya {start_ayah})\n"
        f"Hasta: *{SURAH_NAMES.get(end_surah, 'Sura desconocida')}* (Aya {end_ayah})\n\n"
        "¡Que Allah te facilite esta lectura! 🤲"
    )

    reply_markup = None
    if juz_number < len(QURAN_PLAN):
        keyboard = [[InlineKeyboardButton("He terminado, siguiente Juz ✅", callback_data=f'next_juz_{juz_number + 1}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

    if message_id_to_edit:
        try:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id_to_edit,
                text=texto,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except BadRequest as e:
            # Captura específicamente el error de "Message is not modified"
            if "Message is not modified" in str(e):
                logging.info(f"User {user_id}: Message content not modified for juz {juz_number}. No update needed.")
            else:
                logging.error(f"User {user_id}: Error editing message: {e}")
        except Exception as e:
            logging.error(f"User {user_id}: Unexpected error editing message: {e}")
    else:
        await context.bot.send_message(chat_id=user_id, text=texto, reply_markup=reply_markup, parse_mode='Markdown')

# --- Handlers de Comandos ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_name = user.first_name if user.first_name else "amigo"
    user_id = user.id

    welcome_text = (
        f"Assalamu alaikum, {user_name} 🙌\n"
        "Este bot te ayudará a leer el Corán según un plan diario o semanal.\n\n"
    )

    if user_id in user_preferences:
        keyboard = [
            [
                InlineKeyboardButton("Sí, cambiar modo", callback_data='change_mode'),
                InlineKeyboardButton("No, mantener modo", callback_data='keep_mode'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            welcome_text +
            "Ya estás en modo de lectura 📖.\n"
            "¿Quieres cambiar el modo de lectura?",
            reply_markup=reply_markup
        )
    else:
        keyboard = [
            [
                InlineKeyboardButton("📅 Lectura diaria", callback_data='mode_daily'),
                InlineKeyboardButton("📆 Lectura semanal", callback_data='mode_weekly'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            welcome_text +
            "Elige un modo de lectura:",
            reply_markup=reply_markup
        )

async def recordar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    prefs = user_preferences.get(user_id)

    if not prefs:
        await update.message.reply_text(
            "No tienes ningún plan de lectura activo. Usa /start para comenzar uno."
        )
        return

    mode = prefs['mode']
    current_juz = calculate_current_juz(user_id)
    juz_info = get_juz_info(current_juz)

    if not juz_info:
        await update.message.reply_text("Parece que ya has terminado el Corán o hay un error con el Juz.")
        return

    start_surah = juz_info['start']['surah']
    start_ayah = juz_info['start']['ayah']
    end_surah = juz_info['end']['surah']
    end_ayah = juz_info['end']['ayah']

    texto = (
        f"Tu progreso actual en modo *{'Diario 📅' if mode == 'daily' else 'Semanal 📆'}* es:\n\n"
        f"📖 *Juz {current_juz}* del Corán\n"
        f"Desde: *{SURAH_NAMES.get(start_surah, 'Sura desconocida')}* (Aya {start_ayah})\n"
        f"Hasta: *{SURAH_NAMES.get(end_surah, 'Sura desconocida')}* (Aya {end_ayah})"
    )
    
    if current_juz < len(QURAN_PLAN):
        keyboard = [[InlineKeyboardButton("He terminado, siguiente Juz ✅", callback_data=f'next_juz_{current_juz + 1}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(texto, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(texto + "\n\n¡Has completado el Corán! ¡Mashallah! 🎉", parse_mode='Markdown')


# --- Handlers de Botones (Callbacks) ---

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer() # Siempre responde a la callback query
    user_id = query.from_user.id
    message_id = query.message.message_id 

    if query.data == 'keep_mode':
        current_mode = user_preferences[user_id]['mode']
        await query.edit_message_text(
            f"👍 Mantenemos tu modo actual: *{'Diario 📅' if current_mode == 'daily' else 'Semanal 📆'}*.\n"
            "Usa /recordar para ver tu progreso.",
            parse_mode='Markdown'
        )
        return

    if query.data == 'change_mode':
        # Elimina cualquier tarea programada existente para este usuario
        if user_id in user_preferences and 'job_name' in user_preferences[user_id]:
            job_name = user_preferences[user_id]['job_name']
            current_jobs = context.job_queue.get_jobs_by_name(job_name)
            for job in current_jobs:
                job.schedule_removal()
            user_preferences[user_id].pop('job_name', None) # Limpia el nombre del job de las preferencias

        user_preferences.pop(user_id, None) # Limpia todas las preferencias del usuario
        keyboard = [
            [
                InlineKeyboardButton("📅 Lectura diaria", callback_data='mode_daily'),
                InlineKeyboardButton("📆 Lectura semanal", callback_data='mode_weekly'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Elige un nuevo modo de lectura:",
            reply_markup=reply_markup
        )
        return

    if query.data.startswith('mode_'):
        mode = query.data.split('_')[1]
        user_preferences[user_id] = {
            'mode': mode,
            'start_date': datetime.date.today(),
            'current_juz_completed': 0, # Mantiene un seguimiento del último juz completado
            'job_name': f'daily_weekly_reminder_{user_id}' # Nombre único para la tarea programada
        }
        await query.edit_message_text(
            f"✅ Has seleccionado *Lectura {mode.capitalize()}*.\n"
            "📅 Comenzamos hoy mismo.\n\n"
            "¡Que Allah te facilite la lectura! 🤲",
            parse_mode='Markdown'
        )
        
        # Programa el siguiente recordatorio basado en el modo seleccionado
        schedule_next_reminder(user_id, context.job_queue, mode)
        # Envía el primer juz inmediatamente
        await send_juz_message(user_id, context, 1) 

    elif query.data.startswith('next_juz_'):
        next_juz_number = int(query.data.split('_')[2])
        # Actualiza el juz completado del usuario
        user_preferences[user_id]['current_juz_completed'] = next_juz_number - 1 
        
        # Verifica si el usuario ha completado todos los juzes
        if next_juz_number > len(QURAN_PLAN):
            await query.edit_message_text("¡Mashallah! Has completado la lectura del Corán. 🎉", parse_mode='Markdown')
            # Si ha terminado, elimina las tareas programadas y las preferencias
            if 'job_name' in user_preferences[user_id]:
                job_name = user_preferences[user_id]['job_name']
                current_jobs = context.job_queue.get_jobs_by_name(job_name)
                for job in current_jobs:
                    job.schedule_removal()
                user_preferences[user_id].pop('job_name', None)
            user_preferences.pop(user_id, None) # Limpia las preferencias
        else:
            # Envía el siguiente juz, editando el mensaje anterior
            await send_juz_message(user_id, context, next_juz_number, query.message.message_id) 

# --- Funciones de Recordatorio Programado ---

async def send_scheduled_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Envía el recordatorio programado al usuario."""
    user_id = context.job.chat_id
    
    prefs = user_preferences.get(user_id)
    if not prefs:
        # Las preferencias del usuario podrían haber sido limpiadas, elimina la tarea
        context.job.schedule_removal()
        logging.info(f"Scheduled job for user {user_id} removed as preferences no longer exist.")
        return

    mode = prefs['mode']
    start_date = prefs['start_date']
    
    hoy = datetime.date.today()
    if mode == 'daily':
        delta = (hoy - start_date).days
    else: # weekly
        delta = ((hoy - start_date).days) // 7

    # Calcula el juz que DEBERÍA estar leyendo según el plan y la fecha
    next_scheduled_juz = min(delta + 1, len(QURAN_PLAN))

    # Si ya ha completado este juz o más, no envía el recordatorio.
    if next_scheduled_juz <= prefs.get('current_juz_completed', 0):
        logging.info(f"User {user_id} has already completed juz {next_scheduled_juz}. Skipping reminder.")
        return # Ya completó este juz o más, no es necesario recordarle

    logging.info(f"Sending scheduled reminder for user {user_id} to read juz {next_scheduled_juz}.")
    await send_juz_message(user_id, context, next_scheduled_juz)

def schedule_next_reminder(user_id: int, job_queue: JobQueue, mode: str):
    """Programa el próximo recordatorio de lectura."""
    job_name = f'daily_weekly_reminder_{user_id}'

    # Elimina cualquier tarea existente para este usuario para evitar duplicados o programaciones antiguas
    current_jobs = job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()
        logging.info(f"Removed old job: {job.name} for user {user_id}")

    if mode == 'daily':
        # Programa diariamente a las 10 AM
        job_queue.run_daily(
            send_scheduled_reminder,
            time=datetime.time(hour=10, minute=0, second=0),
            days=(0, 1, 2, 3, 4, 5, 6), # Todos los días
            chat_id=user_id,
            name=job_name
        )
        logging.info(f"Scheduled daily reminder for user {user_id} at 10:00 AM.")
    elif mode == 'weekly':
        # Programa semanalmente los lunes a las 10 AM (Lunes es 0 en datetime.weekday())
        job_queue.run_daily(
            send_scheduled_reminder,
            time=datetime.time(hour=10, minute=0, second=0),
            days=(0,), # Solo los lunes
            chat_id=user_id,
            name=job_name
        )
        logging.info(f"Scheduled weekly reminder for user {user_id} on Mondays at 10:00 AM.")
    user_preferences[user_id]['job_name'] = job_name # Guarda el nombre del job para futura eliminación


# --- Manejador de Errores Global ---

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Maneja y registra cualquier excepción que ocurra durante el procesamiento de actualizaciones."""
    # Registra la excepción completa para depuración (solo se verá en la consola del bot)
    logging.error("Exception while handling an update:", exc_info=context.error)

    # Mensaje genérico para el usuario
    user_message = "¡Uy! Algo salió mal. Por favor, intenta de nuevo o contacta a soporte si el problema persiste."

    # Manejo específico para el error de conflicto (múltiples instancias)
    if isinstance(context.error, Conflict):
        logging.warning("Conflict error detected: Another bot instance might be running. Please stop all other instances.")
        user_message = "¡Atención! Parece que hay otra instancia de mí misma intentando conectarse. Asegúrate de que solo tengo una copia ejecutándose. Si ves este mensaje repetidamente, reinicia la aplicación."
        
    # Manejo específico para el error "Message is not modified" (ya lo hemos manejado localmente)
    elif isinstance(context.error, BadRequest) and "Message is not modified" in str(context.error):
        logging.info("Attempted to edit message with identical content. No change needed (handled by `send_juz_message`).")
        return # No enviamos mensaje al usuario por esto, ya se maneja internamente.
    
    # Envía un mensaje al usuario solo si hay un chat efectivo y no es el error de mensaje no modificado
    if update and update.effective_chat:
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=user_message
            )
        except Exception as e:
            logging.error(f"Failed to send error message to user {update.effective_chat.id}: {e}")


# --- Función Principal ---

def main():
    # Asegúrate de reemplazar "TU_TOKEN_DE_BOT" con tu token real de Telegram.
    application = ApplicationBuilder().token("8093690763:AAGVzRsyJTIIZNB-snoO_1r-d9kM3oFZ944").build()

    # Registrar el manejador de errores global para capturar excepciones no manejadas
    application.add_error_handler(error_handler) 

    # Añadir los handlers de comandos y callbacks
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("recordar", recordar))
    application.add_handler(CallbackQueryHandler(button))

    # La JobQueue se inicializa automáticamente con ApplicationBuilder,
    # solo necesitamos asegurarnos de que la referencia esté disponible para usarla.
    application.job_queue 

    # Iniciar el bot en modo polling
    logging.info("Bot is starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()