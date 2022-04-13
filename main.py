from telegram.ext import Updater, Filters
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def help(update, context):
    update.message.reply_text(
        "Я бот.")


def my_ads(update, context):
    update.message.reply_text("Мои объявления")


def new_ad(update, context):
    update.message.reply_text(
        "Новое объявление")


def second_submenu(bot, update):
    pass


def error(update, context):
    print(f'Update {update} caused error {context.error}')


def menu_handler(update, context):
    print(dir(update))
    update.message.reply_text('тут бот будет что-то писать')


token = '5194363749:AAF-Li9IZuKtBhBVK5Jg0BxzodLYZvz2yhY'
buttons = ['Мои объявления', 'Новое объявление', 'Поиск']
buttons2 = ['Помощь', 'Избранное']

updater = Updater(token, use_context=True)
updater.dispatcher.add_handler(MessageHandler(Filters.text(buttons + buttons2), menu_handler))
updater.dispatcher.add_handler(CommandHandler("address", address))
updater.dispatcher.add_handler(CommandHandler("help", help))
updater.dispatcher.add_error_handler(error)

updater.start_polling()
