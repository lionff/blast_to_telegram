import requests
from datetime import timedelta
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Замените 'YOUR_BOT_TOKEN' на ваш токен бота
TOKEN = ''

# Замените 'YOUR_CHAT_ID' на ваш ID чата
CHAT_ID = ''

# Замените 'ACCESS_TOKEN' на ваш токен из куков на blast.io
ACCESS_TOKEN = ''


def get_dashboard_data():
    cookies = {
        'accessToken': ACCESS_TOKEN,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
        'Accept': '*/*',
        'Accept-Language': 'en-CA,en-US;q=0.7,en;q=0.3',
        'Referer': 'https://blast.io/',
        'Content-Type': 'application/json',
        'Origin': 'https://blast.io',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',

    }

    response = requests.get('https://waitlist-api.prod.blast.io/v1/user/dashboard', cookies=cookies, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None


def get_spins_info(data):
    if data:
        spins_available = data.get('spins')
        # return f"Сейчас доступно {spins_available} спинов"
        return spins_available
    else:
        return "Не удалось получить данные о спинах"


def get_time_until_next_spin(data):
    if data and 'spinStats' in data:
        time_until_next_spin = data['spinStats'].get('timeUntilNextSpinSeconds')
        if time_until_next_spin is not None:
            formatted_time = timedelta(seconds=int(time_until_next_spin))
            return f"Следующий спин будет через {formatted_time}"
    return "Не удалось получить информацию о времени до следующего спина"


def start(update: Update, context: CallbackContext) -> None:
    message = "Привет! Чтобы получить информацию о спинах, используйте команду /spins."
    update.message.reply_text(message)


def spins(update: Update, context: CallbackContext) -> None:
    spins_data = get_spins_info(get_dashboard_data())
    f = [f'{k} = {v}' for k, v in spins_data.items()]
    date_spins = get_time_until_next_spin(get_dashboard_data())
    answer = 'Спинов нет' + '\n' + date_spins
    if spins_data:
        answer = ', '.join(f) + '\n' + date_spins
    context.bot.send_message(chat_id=update.message.chat_id, text=(answer), parse_mode=ParseMode.MARKDOWN)


def main() -> None:
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("spins", spins))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
