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
                MessageHandler(Filters.regex('^Новое объявление$'), create_new_ad),
                MessageHandler(Filters.regex('^Поиск$'), search),
                MessageHandler(Filters.regex('^Помощь$'), help_message),
                MessageHandler(Filters.regex('^Избранное$'), favourites)],

            SELECT_CATEGORY: [MessageHandler(Filters.regex('^(Категория1|Категория2|Категория3)$'), select_category)],
            SELECT_PHOTO: [MessageHandler(Filters.photo, select_photo), CommandHandler('skip', skip_photo)],
            TITLE: [
                MessageHandler(Filters.text, add_description),
                CommandHandler('skip', skip_description),
            ],
            FULL_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, addition)]

        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(new_ad_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()