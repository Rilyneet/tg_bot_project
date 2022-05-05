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


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
SELECT_CATEGORY, SELECT_PHOTO, TITLE, FULL_DESCRIPTION = range(10, 14)
user_information = {}


def create_new_ad(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Категория1', 'Категория2', 'Категория3']]

    update.message.reply_text(
        'Выберите категорию вашего товара',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Выбор категории'
        ),
    )
    if update.message.from_user.id not in user_information:
        user_information[update.message.from_user.id] = {}
    user_information[update.message.from_user.id]['category'] = update.message.text

    return SELECT_CATEGORY


def select_category(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("category %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Пришлите изображение вашего товара',
        reply_markup=ReplyKeyboardRemove(),
    )
    if update.message.from_user.id not in user_information:
        user_information[update.message.from_user.id] = {}
    user_information[update.message.from_user.id]['photo'] = update.message.text

    return SELECT_PHOTO


def select_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Пришлите описание вашего товара'
    )
    if update.message.from_user.id not in user_information:
        user_information[update.message.from_user.id] = {}
    user_information[update.message.from_user.id]['description'] = update.message.text

    return TITLE


def skip_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Продолжим, добавьте описание вашего товара'
    )
    if update.message.from_user.id not in user_information:
        user_information[update.message.from_user.id] = {}
    user_information[update.message.from_user.id]['description'] = update.message.text

    return TITLE


def add_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(
        "Description of %s: %f / %f", user.first_name)
    update.message.reply_text(
        'Продолжим, по желанию напишите дополнение'
    )
    if update.message.from_user.id not in user_information:
        user_information[update.message.from_user.id] = {}
    user_information[update.message.from_user.id]['addition'] = update.message.text

    return FULL_DESCRIPTION


def skip_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'Продолжим, по желанию напишите дополнение'
    )
    if update.message.from_user.id not in user_information:
        user_information[update.message.from_user.id] = {}
    user_information[update.message.from_user.id]['addition'] = update.message.text
    return TITLE


def addition(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Благодарим за заполнение, ваше объявление опубликовано')

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Вы можете вернуться к заполнению позже', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


new_ad_handler = ConversationHandler(
    entry_points=[MessageHandler(Filters.regex('^Новое объявление$'), create_new_ad)],
    states={
        SELECT_CATEGORY: [MessageHandler(Filters.regex('^(Категория1|Категория2|Категория3)$'), select_category)],
        SELECT_PHOTO: [MessageHandler(Filters.photo, select_photo), CommandHandler('skip', skip_photo)],
        TITLE: [
            MessageHandler(Filters.text, add_description),
            CommandHandler('skip', skip_description),
        ],
        FULL_DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, addition)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)
