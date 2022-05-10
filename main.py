import logging

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler,
    CallbackContext,
)

from new_ad import *
from database import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ACTION, NEW_ANNOUNCEMENT, SEARCH, HELP, FAVORITES = range(5)
SELECT_CATEGORY, ADD_TITLE, ADD_DESCRIPTION, SELECT_PHOTO, ADD_PRICE = range(10, 15)

users = {}


def start(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if not userExists(user_id):
        addUser(user_id)
    users[user_id] = {}
    reply_keyboard = [['Мои объявления', 'Новое объявление',
                       'Поиск'], ['Помощь', 'Избранное']]
    update.message.reply_text(
        'Вас приветствует p2p sell bot, ваши действия?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Главное меню'
        ),
    )

    return ACTION


def my_ads(update: Update, context: CallbackContext):
    ads = searchMy(update.message.from_user.id)
    for a in ads:
        found = f"*{a.title}*\n{a.description}\n\n{a.category}\n_{a.price}_"
        update.message.reply_text(found, parse_mode='markdown')


def search(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Что будем искать?'
    )
    user = update.message.from_user

    logger.info("search request %s: %s", user.first_name, update.message.text)
    return SEARCH


def search_ads(update: Update, context: CallbackContext):
    user = update.message.from_user
    query = update.message.text
    ads = searchAd(query)
    for a in ads:
        found = f"*{a.title}*\n{a.description}\n\n{a.category}\n_{a.price}_"
        keyboard = [
            [
                InlineKeyboardButton("В избранное", callback_data='favourite_' + str(a.id)),
                InlineKeyboardButton("Купить", callback_data='buy_' + str(a.id)),
            ]
        ]
        # reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(found, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    return ACTION


def help_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Если у вас возникли проблемы, позвоните по номеру 8(987)8311056, мы все уладим'
    )


def favourites(update: Update, context: CallbackContext):
    ads = searchFav(update.message.from_user.id)
    for a in ads:
        found = f"*{a.title}*\n{a.description}\n\n{a.category}\n_{a.price}_"
        update.message.reply_text(found, parse_mode='markdown')


def favAd(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    print(query)
    user = query.message.chat.id
    data = query.data.split('_')
    command = data[0]
    param = data[1]
    query.answer()
    if command == 'favourite':
        addFavourite(user, int(param))
        query.edit_message_text(
            text="Добавлено в избранное")
        return ACTION
    elif command == 'buy':
        query.edit_message_text(
            text="Куплено")
        return ACTION


def buy(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""

    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text="Куплено")
    return ACTION


def main() -> None:
    token = '5194363749:AAH7UrS88vUQa2BgaAWCp-GMmn1m6wNB1s0'
    updater = Updater(token)
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      MessageHandler(Filters.regex('^Поиск$'), search),
                      CallbackQueryHandler(favAd, pattern='favourite'),
                      CallbackQueryHandler(buy, pattern='buy'), ],
        states={
            ACTION: [
                MessageHandler(Filters.regex(
                    '^Мои объявления$'), my_ads),
                MessageHandler(Filters.regex(
                    '^Новое объявление$'), create_new_ad),
                MessageHandler(Filters.regex('^Поиск$'), search),
                MessageHandler(Filters.regex('^Помощь$'), help_message),
                MessageHandler(Filters.regex('^Избранное$'), favourites),
                CallbackQueryHandler(favAd),
                CallbackQueryHandler(buy, pattern='buy'), ],
            SELECT_CATEGORY: [MessageHandler(Filters.regex('^(Книги|Значки|Майки)$'), select_category)],
            ADD_TITLE: [MessageHandler(Filters.text, add_title), ],
            ADD_DESCRIPTION: [MessageHandler(Filters.text, add_description),
                              CommandHandler('skip', skip_description), ],
            SELECT_PHOTO: [MessageHandler(Filters.photo, select_photo),
                           CommandHandler('skip', skip_photo)],
            ADD_PRICE: [MessageHandler(Filters.text & ~Filters.command, price)],
            SEARCH: [MessageHandler(Filters.text & ~Filters.command, search_ads)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(new_ad_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
