import datetime

from sqlalchemy import create_engine, Column, Integer, Boolean, DateTime, exists
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from settings import DATABASE_URL

# Configure a Session class.
Session = sessionmaker()

# Create an engine which the Session will use for connections.
engine = create_engine(DATABASE_URL)

# Create a configured Session class.
Session.configure(bind=engine)

# Create a Session
session = Session()

# Create a base for the models to build upon.
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    subscribe = Column(Boolean, default=False)

    def __init__(self, user):
        self.user_id = user.id

    def exists(self):
        return session.query(exists().where(
            User.user_id == self.user_id)).scalar()

    def commit(self):
        session.add(self)
        session.commit()


class HackerSpace(Base):
    __tablename__ = "hackerspace"

    id = Column(Integer, primary_key=True)
    is_open = Column(Boolean)
    to_open = Column(DateTime, nullable=True)
    to_close = Column(DateTime, nullable=True)

    def __init__(self, is_open):
        self.is_open = is_open

    def commit(self):
        session.add(self)
        session.commit()

    def status(self):
        if self.is_open and self.to_open and self.to_open > datetime.datetime.now():
            return f'Хакерспейс откроется в {self.to_open.strftime("%a, %d %b %H:%M")}'
        elif not self.is_open and self.to_close and self.to_close > datetime.datetime.now():
            return f'Хакерспейс закроется в {self.to_close.strftime("%H:%M %d %b")}'
        else:
            return f'Хакерспейс сейчас {"открыт" if self.is_open else "закрыт"}'

    @classmethod
    def get_hs(cls):
        return session.query(HackerSpace).first()

    def update(self, is_open, to_open=None, to_close=None):
        self.is_open = is_open
        self.to_open = to_open
        self.to_close = to_close
        session.commit()
