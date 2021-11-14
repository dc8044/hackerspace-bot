from celery import Celery
from telegram import Bot

import database as db
import settings


celery_app = Celery('tasks', broker=settings.LOCAL_BROKER)


@celery_app.task
def send_text_to_subs(text):
    bot = Bot(settings.TOKEN)
    for user in db.session.query(db.User).filter_by(subscribe=True).all():
        try:
            bot.send_message(chat_id=user.user_id, text=text)
        except:
            pass
    return 'OK'
