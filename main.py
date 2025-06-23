from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import datetime

# Simulamos nombres de suras (solo ejemplo, debes poner los reales)
SURAH_NAMES = {
    1: "Al-Fatiha - الفاتحة",
    2: "Al-Baqarah - البقرة",
    3: "Ali-Imran - آل عمران",
    4: "An-Nisa - النساء",
    5: "Al-Ma'idah - المائدة",
    6: "Al-An'am - الأنعام",
    7: "Al-A'raf - الأعراف",
    8: "Al-Anfal - الأنفال",
    9: "At-Tawbah - التوبة",
    10: "Yunus - يونس",
    11: "Hud - هود",
    12: "Yusuf - يوسف",
    13: "Ar-Ra'd - الرعد",
    14: "Ibrahim - إبراهيم",
    15: "Al-Hijr - الحجر",
    16: "An-Nahl - النحل",
    17: "Al-Isra - الإسراء",
    18: "Al-Kahf - الكهف",
    19: "Maryam - مريم",
    20: "Ta-Ha - طه",
    21: "Al-Anbiya - الأنبياء",
    22: "Al-Hajj - الحج",
    23: "Al-Mu'minun - المؤمنون",
    24: "An-Nur - النور",
    25: "Al-Furqan - الفرقان",
    26: "Ash-Shu'ara - الشعراء",
    27: "An-Naml - النمل",
    28: "Al-Qasas - القصص",
    29: "Al-Ankabut - العنكبوت",
    30: "Ar-Rum - الروم",
    31: "Luqman - لقمان",
    32: "As-Sajdah - السجدة",
    33: "Al-Ahzab - الأحزاب",
    34: "Saba - سبأ",
    35: "Fatir - فاطر",
    36: "Ya-Sin - يس",
    37: "As-Saffat - الصافات",
    38: "Sad - ص",
    39: "Az-Zumar - الزمر",
    40: "Ghafir - غافر",
    41: "Fussilat - فصلت",
    42: "Ash-Shura - الشورى",
    43: "Az-Zukhruf - الزخرف",
    44: "Ad-Dukhan - الدخان",
    45: "Al-Jathiyah - الجاثية",
    46: "Al-Ahqaf - الأحقاف",
    47: "Muhammad - محمد",
    48: "Al-Fath - الفتح",
    49: "Al-Hujurat - الحجرات",
    50: "Qaf - ق",
    51: "Adh-Dhariyat - الذاريات",
    52: "At-Tur - الطور",
    53: "An-Najm - النجم",
    54: "Al-Qamar - القمر",
    55: "Ar-Rahman - الرحمن",
    56: "Al-Waqi'ah - الواقعة",
    57: "Al-Hadid - الحديد",
    58: "Al-Mujadila - المجادلة",
    59: "Al-Hashr - الحشر",
    60: "Al-Mumtahanah - الممتحنة",
    61: "As-Saff - الصف",
    62: "Al-Jumu'ah - الجمعة",
    63: "Al-Munafiqun - المنافقون",
    64: "At-Taghabun - التغابن",
    65: "At-Talaq - الطلاق",
    66: "At-Tahrim - التحريم",
    67: "Al-Mulk - الملك",
    68: "Al-Qalam - القلم",
    69: "Al-Haqqah - الحاقة",
    70: "Al-Ma'arij - المعارج",
    71: "Nuh - نوح",
    72: "Al-Jinn - الجن",
    73: "Al-Muzzammil - المزّمّل",
    74: "Al-Muddaththir - المدّثر",
    75: "Al-Qiyamah - القيامة",
    76: "Al-Insan - الإنسان",
    77: "Al-Mursalat - المرسلات",
    78: "An-Naba - النبأ",
    79: "An-Nazi'at - النازعات",
    80: "Abasa - عبس",
    81: "At-Takwir - التكوير",
    82: "Al-Infitar - الإنفطار",
    83: "Al-Mutaffifin - المطفّفين",
    84: "Al-Inshiqaq - الإنشقاق",
    85: "Al-Buruj - البروج",
    86: "At-Tariq - الطارق",
    87: "Al-A'la - الأعلى",
    88: "Al-Ghashiyah - الغاشية",
    89: "Al-Fajr - الفجر",
    90: "Al-Balad - البلد",
    91: "Ash-Shams - الشمس",
    92: "Al-Lail - الليل",
    93: "Ad-Duha - الضحى",
    94: "Ash-Sharh - الشرح",
    95: "At-Tin - التين",
    96: "Al-'Alaq - العلق",
    97: "Al-Qadr - القدر",
    98: "Al-Bayyinah - البيِّنة",
    99: "Az-Zalzalah - الزلزلة",
    100: "Al-'Adiyat - العاديات",
    101: "Al-Qari'ah - القارعة",
    102: "At-Takathur - التكاثر",
    103: "Al-Asr - العصر",
    104: "Al-Humazah - الهمزة",
    105: "Al-Fil - الفيل",
    106: "Quraysh - قريش",
    107: "Al-Ma'un - الماعون",
    108: "Al-Kawthar - الكوثر",
    109: "Al-Kafirun - الكافرون",
    110: "An-Nasr - النصر",
    111: "Al-Masad - المسد",
    112: "Al-Ikhlas - الإخلاص",
    113: "Al-Falaq - الفلق",
    114: "An-Nas - الناس",
}

# Simulación del plan de lectura (Juz con surah y ayah inicio y fin)
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

user_preferences = {}

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

async def enviar_lectura(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    prefs = user_preferences.get(user_id)
    if not prefs:
        return  # No hay preferencias guardadas, no hacer nada

    mode = prefs['mode']
    start_date = prefs['start_date']
    hoy = datetime.date.today()

    if mode == 'daily':
        delta = (hoy - start_date).days
    else:  # weekly
        delta = ((hoy - start_date).days) // 7

    if delta > 29:
        delta = 29

    juz = delta + 1
    prefs['current_day'] = delta

    start_surah = QURAN_PLAN[juz-1]['start']['surah']
    start_ayah = QURAN_PLAN[juz-1]['start']['ayah']
    end_surah = QURAN_PLAN[juz-1]['end']['surah']
    end_ayah = QURAN_PLAN[juz-1]['end']['ayah']

    texto = (
        f"📖 *Juz {juz}* del Corán\n"
        f"Desde: *{SURAH_NAMES.get(start_surah, 'Sura desconocida')}* (Aya {start_ayah})\n"
        f"Hasta: *{SURAH_NAMES.get(end_surah, 'Sura desconocida')}* (Aya {end_ayah})\n\n"
        "¡Que Allah te facilite esta lectura! 🤲"
    )

    await context.bot.send_message(chat_id=user_id, text=texto, parse_mode='Markdown')

async def recordar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    prefs = user_preferences.get(user_id)

    if not prefs:
        await update.message.reply_text(
            "No tienes ningún plan de lectura activo. Usa /start para comenzar uno."
        )
        return

    mode = prefs['mode']
    current_day = prefs.get('current_day', 0)
    juz = min(current_day + 1, 30)

    start_surah = QURAN_PLAN[juz-1]['start']['surah']
    start_ayah = QURAN_PLAN[juz-1]['start']['ayah']
    end_surah = QURAN_PLAN[juz-1]['end']['surah']
    end_ayah = QURAN_PLAN[juz-1]['end']['ayah']

    texto = (
        f"Tu progreso actual en modo *{'Diario 📅' if mode == 'daily' else 'Semanal 📆'}* es:\n\n"
        f"📖 *Juz {juz}* del Corán\n"
        f"Desde: *{SURAH_NAMES.get(start_surah, 'Sura desconocida')}* (Aya {start_ayah})\n"
        f"Hasta: *{SURAH_NAMES.get(end_surah, 'Sura desconocida')}* (Aya {end_ayah})"
    )

    await update.message.reply_text(texto, parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

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
        }
        await query.edit_message_text(
            "✅ Has seleccionado *Lectura semanal*.\n"
            "📆 Comenzamos hoy mismo.\n\n"
            "¡Que Allah te facilite la lectura! 🤲",
            parse_mode='Markdown'
        )
        await enviar_lectura(user_id, context)

def main():
    app = ApplicationBuilder().token("8093690763:AAGVzRsyJTIIZNB-snoO_1r-d9kM3oFZ944").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("recordar", recordar))  # Añadido el handler para /recordar
    app.add_handler(CallbackQueryHandler(button))

    app.run_polling()

if __name__ == '__main__':
    main()