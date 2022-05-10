import logging
import requests
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

from telegram import LabeledPrice, ShippingOption, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
    ShippingQueryHandler,
    filters,
)

from new_ad import *
from database import *

PAYMENT_PROVIDER_TOKEN = '381764678:TEST:37069'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

ACTION, NEW_ANNOUNCEMENT, SEARCH, HELP, FAVORITES = range(5)
SELECT_CATEGORY, ADD_TITLE, ADD_DESCRIPTION, SELECT_PHOTO, ADD_PRICE = range(
    10, 15)

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


def show_ad(a):
    found = f"*{a.title}*\n{a.description}\n\nКатегория: {a.category}\nЦена: _{a.price}_"
    return found


def my_ads(update: Update, context: CallbackContext):
    ads = searchMy(update.message.from_user.id)

    for a in ads:
        found = show_ad(a)
        print(found)
        try:
           img = requests.get(a.image).content
           update.message.reply_photo(
             photo=img, caption=found, parse_mode='markdown')
        except Exception as e:
            print(e, img)
        else:
            pass

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
    if len(ads) == 0:
        update.message.reply_text('Ничего не найдено по вашему запросу')
    for a in ads:
        found = show_ad(a)
        keyboard = [
            [
                InlineKeyboardButton(
                    "В избранное", callback_data='favourite_' + str(a.id)),
                InlineKeyboardButton("Купить", callback_data='buy_' + str(a.id)),
            ]
        ]
        # reply_markup = InlineKeyboardMarkup(keyboard)
        # update.message.reply_text(found, parse_mode='markdown',reply_markup=InlineKeyboardMarkup(keyboard))
        try:
           img = requests.get(a.image).content
           update.message.reply_photo(
            photo=img, caption=found, parse_mode='markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            print(e)
        else:
            pass
    return ACTION


def help_message(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Если у вас возникли проблемы, позвоните по номеру 8(987)8311056, мы все уладим'
    )


def favourites(update: Update, context: CallbackContext):
    ads = searchFav(update.message.from_user.id)
    for a in ads:
        found = show_ad(a)
        print(found)
        img = requests.get(a.image).content
        update.message.reply_photo(
            photo=img, caption=found, parse_mode='markdown')


def favAd(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    print(query)
    user = query.message.chat.id
    data = query.data.split('_')
    command = data[0]
    param = data[1]

    if command == 'favourite':
        addFavourite(user, int(param))
        query.answer('Добавлено в избранное')
        return ACTION
    # elif command == 'buy':
    #    query.answer('Куплено', show_alert=True)
    #
    #    return ACTION


def buy_old(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""

    query = update.callback_query
    query.answer()
    update.message.reply_text("Куплено:")
    return ACTION


"""
add_handler(CommandHandler("noshipping", start_without_shipping_callback))

    # Optional handler if your product requires shipping
    application.add_handler(ShippingQueryHandler(shipping_callback))

    # Pre-checkout handler to final check
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
    )
"""


def start_buying_callback(
        update: Update, context: CallbackContext
) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id

    user = query.message.chat.id
    data = query.data.split('_')
    command = data[0]
    param = data[1]

    title = "Оплата покупки"
    description = "Оплатите покупку с помощью кредитной карты 1111 1111 1111 1026, 12/22, CVC 000"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    currency = "RUB"
    # price in dollars
    price = 100
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Test", price * 1000)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(
        chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices,
        need_name=True, need_email=True, need_shipping_address=True, )


# after (optional) shipping, it's the pre-checkout


def precheckout_callback(update: Update, context: CallbackContext) -> None:
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != "Custom-Payload":
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)


def successful_payment_callback(
        update: Update, context: CallbackContext
) -> None:
    """Confirms the successful payment."""
    # do something after successfully receiving payment?
    update.message.reply_text("Thank you for your payment!")


def main() -> None:
    token = '5194363749:AAH7UrS88vUQa2BgaAWCp-GMmn1m6wNB1s0'
    # token2 = '5392063749:AAEE6atvm54GhtGtU_JWlnrMYN6xU7W-p74'
    updater = Updater(token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('search', search),
                      CommandHandler('new', create_new_ad),

                      MessageHandler(Filters.regex('^Поиск$'), search),
                      CallbackQueryHandler(favAd, pattern='favourite'),
                      CallbackQueryHandler(start_buying_callback, pattern='buy'), ],
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
                CallbackQueryHandler(start_buying_callback)],
            SELECT_CATEGORY: [
                MessageHandler(Filters.regex('^(Книги|Подкасты|Подарочные сертификаты)$'), select_category)],
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

    dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dispatcher.add_handler(MessageHandler(
        Filters.successful_payment, successful_payment_callback))

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(new_ad_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
