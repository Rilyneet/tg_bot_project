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

    reply_keyboard = [['Книги', 'Подкасты', 'Подарочные сертификаты']]

    update.message.reply_text(
        'Выберите категорию вашего товара',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Выбор категории'
        ),
    )

    return SELECT_CATEGORY


def select_category(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['category'] = update.message.text
    logger.info("Пользователь %s: выбрал категорию %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Введите заголовок объявления',
        reply_markup=ReplyKeyboardRemove(),
    )

    return ADD_TITLE


def add_title(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['title'] = update.message.text

    logger.info(
        "Title of %s: %s ", user.first_name, update.message.text)
    update.message.reply_text(
        'Продолжим, введите краткое описание '
    )

    return ADD_DESCRIPTION


def add_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['description'] = update.message.text

    logger.info(
        "Description of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'А теперь пришлите картинку'
    )

    return SELECT_PHOTO


def skip_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['description'] = ''
    logger.info("User %s did not send description.", user.first_name)
    update.message.reply_text(
        'Нет описания? Хотя бы пришлите картинку!'
    )

    return SELECT_PHOTO


def select_photo(update: Update, context: CallbackContext) -> int:
    print(update)
    user = update.message.from_user
    filename = str(uuid.uuid1())
    if len(update.message.photo) > 0:
        photo_file = update.message.photo[-1].get_file()
        print(photo_file)
        fn = photo_file.download(filename)
        print('fn', fn)
    elif update.message.document:
        photo_file = update.message.document[-1].get_file()
        fn = photo_file.download(filename)
        print('fn', fn)
    else:
        update.message.reply_text(
            'Вы не добавили картинку'
        )

    user = update.message.from_user
    context.user_data['image'] = photo_file['file_path']

    logger.info("Photo of %s: %s", user.first_name, fn)
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
    context.user_data['price'] = update.message.text
    reply_keyboard = [['Мои объявления', 'Новое объявление',
                       'Поиск'], ['Помощь', 'Избранное']]
    update.message.reply_text(
        'Благодарим за заполнение, ваше объявление опубликовано',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Главное меню'
        ),
    )

    logger.info("Цена %s: %s", user.first_name, update.message.text)

    category = context.user_data['category']
    title = context.user_data.get('title')
    description = context.user_data['description']
    image = context.user_data.get('image', 'image')
    price = context.user_data['price']
    author = user.id
    try:
        addAd(category, title, description, image, price, author)
    except Exception as e:
        print(e)
    return ACTION


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
        SELECT_CATEGORY: [MessageHandler(Filters.regex('^(Книги|Подкасты|Подарочные сертификаты)$'), select_category)],
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
