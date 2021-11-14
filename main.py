import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

import settings
import database as db
from tasks import send_text_to_subs


import logging
import locale

from functools import wraps

locale.setlocale(locale.LC_TIME, "ru_RU")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        chat_id = update.effective_chat.id
        if chat_id != settings.ADMIN_CHAT_ID:
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Подписаться на обновления", callback_data='1')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    user = db.User(update.effective_user)
    if not user.exists():
        user.commit()

    hs = db.HackerSpace.get_hs()
    update.message.reply_text(f'Привет, странник\n{hs.status()}',
                              reply_markup=reply_markup if not db.session.query(db.User).get(
                                  user.user_id).subscribe else None)


def subscribe_button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()
    db.session.query(db.User).filter_by(user_id=update.effective_user.id).update({db.User.subscribe: True})
    db.session.commit()

    query.message.edit_reply_markup(reply_markup=None)
    query.message.reply_text(
        text="Спасибо что подписался, теперь я буду уведомлять тебя о изменениях в работе спейса\nОтписаться можно командой /unsubscribe")


def status(update: Update, context: CallbackContext) -> None:
    hs = db.HackerSpace.get_hs()
    update.message.reply_text(hs.status())


@restricted
def open_hs(update: Update, context: CallbackContext) -> None:
    hs = db.HackerSpace.get_hs()
    if len(context.args) > 0:
        if context.args[0] == 'now':
            hs.update(is_open=True)
            send_text_to_subs.delay(text=hs.status())
            update.message.reply_text(
                f'Спейс открыт, уведомлено {db.session.query(db.User).filter_by(subscribe=True).count()} пользователей')
        else:
            try:
                open_time = datetime.datetime.strptime(' '.join(context.args), '%H:%M %m.%d').replace(
                    year=datetime.datetime.now().year)
                hs.update(is_open=True, to_open=open_time)
                send_text_to_subs.delay(text=hs.status())
                update.message.reply_text(
                    f'Спейс открыт, уведомлено {db.session.query(db.User).filter_by(subscribe=True).count()} пользователей')
            except:
                update.message.reply_text(f'Проверьте правильность ввода даты и попробуйте еще раз')



    else:
        update.message.reply_text(f'Введите время открытия в формате: <hh:mm> <dd.mm> \n"now" для мгновенного открытия')


@restricted
def close_hs(update: Update, context: CallbackContext) -> None:
    hs = db.HackerSpace.get_hs()
    if len(context.args) > 0:
        if context.args[0] == 'now':
            hs.update(is_open=False)
            send_text_to_subs.delay(text=hs.status())
            update.message.reply_text(
                f'Спейс закрыт, уведомлено {db.session.query(db.User).filter_by(subscribe=True).count()} пользователей')
        else:
            hs.update(is_open=False, to_close=datetime.datetime.now() + datetime.timedelta(hours=int(context.args[0])))
            send_text_to_subs.delay(text=hs.status())
            update.message.reply_text(
                f'Спейс закрыт, уведомлено {db.session.query(db.User).filter_by(subscribe=True).count()} пользователей')

    else:
        update.message.reply_text(f'Введите время до закрытия: /close <через X часов> \n"now" для мгновенного закрытия')


def subscribe(update: Update, context: CallbackContext) -> None:
    db.session.query(db.User).filter_by(user_id=update.effective_user.id).update({db.User.subscribe: True})
    db.session.commit()
    update.message.reply_text(
        text="Спасибо что подписался, теперь я буду уведомлять тебя о изменениях в работе спейса\nОтписаться можно командой /unsubscribe")


def unsubscribe(update: Update, context: CallbackContext) -> None:
    db.session.query(db.User).filter_by(user_id=update.effective_user.id).update({db.User.subscribe: False})
    db.session.commit()
    update.message.reply_text(
        text="Я больше не буду тревожить тебя уведомлениями\nЕсли передумаешь, всегда можешь нажать /subscribe")


def donate(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text="<a href='https://send.monobank.ua/jar/9rRiUNG8Tt'>MonoBank</a>", parse_mode=ParseMode.HTML)


def main() -> None:
    """Run the bot."""
    updater = Updater(settings.TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('donate', donate))
    dispatcher.add_handler(CommandHandler('subscribe', subscribe))
    dispatcher.add_handler(CommandHandler('unsubscribe', unsubscribe))
    dispatcher.add_handler(CommandHandler('status', status))
    dispatcher.add_handler(CommandHandler('open', open_hs))
    dispatcher.add_handler(CommandHandler('close', close_hs))

    dispatcher.add_handler(CallbackQueryHandler(subscribe_button))

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(settings.PORT),
                          url_path=settings.TOKEN,
                          webhook_url=settings.APP_URL + settings.TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
