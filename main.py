from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes, JobQueue
import datetime

# ... conserva tus diccionarios SURAH_NAMES y QURAN_PLAN

user_preferences = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_name = user.first_name or "amigo"
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

async def enviar_lectura(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    prefs = user_preferences.get(user_id)
    if not prefs:
        return  # No preferences set

    current_juz = prefs.get('current_juz', 1)
    if current_juz > 30:
        await context.bot.send_message(chat_id=user_id, text="Has completado todos los juz del Corán. ¡MashaAllah! 🎉")
        return

    start_surah = QURAN_PLAN[current_juz-1]['start']['surah']
    start_ayah = QURAN_PLAN[current_juz-1]['start']['ayah']
    end_surah = QURAN_PLAN[current_juz-1]['end']['surah']
    end_ayah = QURAN_PLAN[current_juz-1]['end']['ayah']

    texto = (
        f"📖 *Juz {current_juz}* del Corán\n"
        f"Desde: *{SURAH_NAMES.get(start_surah, 'Sura desconocida')}* (Aya {start_ayah})\n"
        f"Hasta: *{SURAH_NAMES.get(end_surah, 'Sura desconocida')}* (Aya {end_ayah})\n\n"
        "¿Quieres continuar con el siguiente juz?"
    )

    keyboard = [
        [
            InlineKeyboardButton("Sí", callback_data='continue_yes'),
            InlineKeyboardButton("No", callback_data='continue_no')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Marcar que estamos esperando respuesta para continuar
    prefs['awaiting_continue'] = True

    await context.bot.send_message(chat_id=user_id, text=texto, reply_markup=reply_markup, parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Comprobar si estamos esperando respuesta para continuar
    prefs = user_preferences.get(user_id, {})
    awaiting_continue = prefs.get('awaiting_continue', False)

    if awaiting_continue:
        if query.data == 'continue_yes':
            # Incrementar juz y enviar siguiente
            prefs['current_juz'] = prefs.get('current_juz', 1) + 1
            prefs['awaiting_continue'] = False
            await query.edit_message_text("¡Muy bien! Aquí tienes el siguiente juz:")
            await enviar_lectura(user_id, context)

        elif query.data == 'continue_no':
            prefs['awaiting_continue'] = False
            # Programar recordatorio según modo
            mode = prefs['mode']
            await query.edit_message_text("Entendido. Te recordaré continuar más tarde, in sha Allah.")

            # Usar JobQueue para programar recordatorio
            job_queue = context.job_queue
            chat_id = user_id

            # Primero cancelamos jobs anteriores si existieran para este usuario
            current_jobs = job_queue.get_jobs_by_name(str(chat_id))
            for job in current_jobs:
                job.schedule_removal()

            if mode == 'daily':
                # Programar recordatorio diario a las 10am
                now = datetime.datetime.now()
                next_run = now.replace(hour=10, minute=0, second=0, microsecond=0)
                if now > next_run:
                    next_run += datetime.timedelta(days=1)

                job_queue.run_daily(send_reminder, time=next_run.time(), days=(0,1,2,3,4,5,6), name=str(chat_id), context=chat_id)

            else:  # semanal
                # Programar recordatorio semanal los lunes a las 10am
                now = datetime.datetime.now()
                next_monday = now + datetime.timedelta((0 - now.weekday()) % 7)  # lunes próximo o hoy si es lunes
                next_run = next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
                if now > next_run:
                    next_run += datetime.timedelta(weeks=1)

                job_queue.run_daily(send_reminder, time=next_run.time(), days=(0,), name=str(chat_id), context=chat_id)

        else:
            # Si llega otro callback mientras se espera, ignorar o responder
            await query.answer("Por favor, responde Sí o No para continuar.")
        return

    # --- No estamos en espera de continuar, seguimos con los otros botones ---

    if query.data == 'keep_mode':
        current_mode = user_preferences[user_id]['mode']
        await query.edit_message_text(
            f"👍 Mantenemos tu modo actual: *{'Diario 📅' if current_mode == 'daily' else 'Semanal 📆'}*.\n"
            "Usa /recordar para ver tu progreso.",
            parse_mode='Markdown'
        )
        return

    if query.data == 'change_mode':
        user_preferences.pop(user_id, None)
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

    if query.data == 'mode_daily':
        user_preferences[user_id] = {
            'mode': 'daily',
            'start_date': datetime.date.today(),
            'current_day': 0,
            'current_juz': 1,
            'awaiting_continue': False,
        }
        await query.edit_message_text(
            "✅ Has seleccionado *Lectura diaria*.\n"
            "📅 Comenzamos hoy mismo.\n\n"
            "¡Que Allah te facilite la lectura! 🤲",
            parse_mode='Markdown'
        )
        await enviar_lectura(user_id, context)

    elif query.data == 'mode_weekly':
        user_preferences[user_id] = {
            'mode': 'weekly',
            'start_date': datetime.date.today(),
            'current_day': 0,
            'current_juz': 1,
            'awaiting_continue': False,
        }
        await query.edit_message_text(
            "✅ Has seleccionado *Lectura semanal*.\n"
            "📆 Comenzamos hoy mismo.\n\n"
            "¡Que Allah te facilite la lectura! 🤲",
            parse_mode='Markdown'
        )
        await enviar_lectura(user_id, context)

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.context
    prefs = user_preferences.get(user_id)
    if not prefs:
        return

    current_juz = prefs.get('current_juz', 1)
    if current_juz > 30:
        # Ya completó el Corán
        await context.bot.send_message(chat_id=user_id, text="¡Has completado la lectura del Corán, MashaAllah! 🎉")
        return

    start_surah = QURAN_PLAN[current_juz-1]['start']['surah']
    start_ayah = QURAN_PLAN[current_juz-1]['start']['ayah']
    end_surah = QURAN_PLAN[current_juz-1]['end']['surah']
    end_ayah = QURAN_PLAN[current_juz-1]['end']['ayah']

    texto = (
        f"⏰ Recordatorio de lectura 📖\n"
        f"Tu siguiente juz es el *Juz {current_juz}*:\n"
        f"Desde: *{SURAH_NAMES.get(start_surah, 'Sura desconocida')}* (Aya {start_ayah})\n"
        f"Hasta: *{SURAH_NAMES.get(end_surah, 'S
