
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from new_ad import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ACTION, NEW_ANNOUNCEMENT, SEARCH, HELP, FAVORITES = range(5)

users = {}


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Мои объявления', 'Новое объявление', 'Поиск'], ['Помощь', 'Избранное']]
    update.message.reply_text(
        'Здравствуйте',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Главное меню'
        ),
    )

    return ACTION


def my_announsements(update: Update, context: CallbackContext):
    pass


def new_announsements(update: Update, context: CallbackContext):
     main_adding()


def search(update: Update, context: CallbackContext):
    pass


def help_message(update: Update, context: CallbackContext):
    pass


def favourites(update: Update, context: CallbackContext):
    pass


def main() -> None:
    updater = Updater("5194363749:AAH7UrS88vUQa2BgaAWCp-GMmn1m6wNB1s0")
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ACTION: [
                MessageHandler(Filters.regex('^Мои объявления$'), my_announsements),
                MessageHandler(Filters.regex('^Новое объявление$'), new_announsements),
                MessageHandler(Filters.regex('^Поиск$'), search),
                MessageHandler(Filters.regex('^Помощь$'), help_message),
                MessageHandler(Filters.regex('^Избранное$'), favourites)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
