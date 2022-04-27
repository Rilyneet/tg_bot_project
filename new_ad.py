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

CATEGORY, PHOTO, NAME, DESCRIPTION, SEARCHRESULT = range(5)

users = {}


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Категория1', 'Категория2', 'Категория3']]

    update.message.reply_text(
        'Выберите категорию вашего товара',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Выбор категории'
        ),
    )

    return CATEGORY


def category(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user

    logger.info("category %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Пришлите изображение вашего товара',
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Пришлите описание вашего товара'
    )

    return NAME


def skip_photo(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text(
        'Продолжим, добавьте описание вашего товара'
    )

    return NAME


def description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info(
        "Description of %s: %f / %f", user.first_name)
    update.message.reply_text(
        'Продолжим, по желанию напишите дополнение'
    )

    return DESCRIPTION


def skip_description(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s did not send a location.", user.first_name)
    update.message.reply_text(
        'Продолжим, по желанию напишите дополнение'
    )

    return NAME


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


def main_adding() -> None:
    updater = Updater("5194363749:AAH7UrS88vUQa2BgaAWCp-GMmn1m6wNB1s0")
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CATEGORY: [MessageHandler(Filters.regex('^(Категория1|Категория2|Категория3)$'), category)],
            PHOTO: [MessageHandler(Filters.photo, photo), CommandHandler('skip', skip_photo)],
            NAME: [
                MessageHandler(Filters.text, description),
                CommandHandler('skip', skip_description),
            ],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, addition)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main_adding()
