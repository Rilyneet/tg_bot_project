import logging
from ssl import ALERT_DESCRIPTION_CERTIFICATE_REVOKED
from database import addAd, userExists
import uuid
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

users = {}

logger = logging.getLogger(__name__)
SELECT_CATEGORY, ADD_TITLE, ADD_DESCRIPTION, SELECT_PHOTO, ADD_PRICE = range(10, 15)
ACTION = 0


def create_new_ad(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    users[user.id] = {}
    reply_keyboard = [['Книги', 'Значки', 'Майки']]

    update.message.reply_text(
        'Выберите категорию вашего товара',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Выбор категории'
        ),
    )

    return SELECT_CATEGORY


def select_category(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    users[user.id]['category'] = update.message.text
    logger.info("Пользователь %s: выбрал категорию %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Введите заголовок объявления',
        reply_markup=ReplyKeyboardRemove(),
    )

    return ADD_TITLE


def add_title(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    users[user.id]['title'] = update.message.text

    logger.info(
        "Title of %s: %s ", user.first_name, update.message.text)
    update.message.reply_text(
        'Продолжим, введите краткое описание '
    )

    return ADD_DESCRIPTION


def add_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    users[user.id]['description'] = update.message.text

    logger.info(
        "Description of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'А теперь пришлите картинку'
    )

    return SELECT_PHOTO


def skip_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    users[user.id]['description'] = ''
    logger.info("User %s did not send description.", user.first_name)
    update.message.reply_text(
        'Нет описания? Хотя бы пришлите картинку!'
    )

    return SELECT_PHOTO


def select_photo(update: Update, context: CallbackContext) -> int:
    print(update)
    user = update.message.from_user

    photo_file = update.message.photo[-1].get_file()
    print(photo_file)
    if not photo_file:
        photo_file = update.message.document[-1].get_file()

    filename = '/home/d/juliatg/images.jpg'
    photo_file.download(filename)
    user = update.message.from_user
    users[user.id]['image'] = filename

    logger.info("Photo of %s: %s", user.first_name, filename)
    update.message.reply_text(
        'Введите цену'
    )

    return ADD_PRICE


def skip_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Введите цену'
    )

    return ADD_PRICE


def price(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    users[user.id]['price'] = update.message.text

    logger.info("Цена %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Благодарим за заполнение, ваше объявление опубликовано')
    category = users[user.id]['category']
    title = users[user.id].get('title')
    description = users[user.id]['description']
    image = users[user.id].get('image', 'image')
    price = users[user.id]['price']
    author = user.id
    try:
        addAd(category, title, description, image, price, author)
    except Exception as e:
        print(e)
    users[user.id] = {}
    return ACTION

    # return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Вы можете вернуться к заполнению позже', reply_markup=ReplyKeyboardRemove()
    )

    return ACTION


new_ad_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex(
        '^Новое объявление$'), create_new_ad)],
    states={
        SELECT_CATEGORY: [MessageHandler(Filters.regex('^(Книги|Значки|Майки)$'), select_category)],
        ADD_TITLE: [
            MessageHandler(Filters.text, add_title),
        ],
        ADD_DESCRIPTION: [
            MessageHandler(Filters.text, add_description),
            CommandHandler('skip', skip_description),
        ],

        SELECT_PHOTO: [MessageHandler(Filters.photo | Filters.document, select_photo),
                       CommandHandler('skip', skip_photo)],

        ADD_PRICE: [MessageHandler(Filters.text & ~Filters.command, price)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
