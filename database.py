from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///hse_assistant_tg.db")

Session = sessionmaker(bind=engine)

session = Session()
Base = declarative_base()


class TgSubscription(Base):
    __tablename__ = 'tgsubscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    chat_id = Column(Integer)

    def __repr__(self) -> str:
        return f'<database.TgSubscription id: {self.id}, user_id: {self.user_id}, chat_id: {self.chat_id}>'


def create_tg_subscription(user_id: int, chat_id: int) -> TgSubscription:
    subscription = get_tg_subscription(user_id=user_id, chat_id=chat_id)
    if subscription is not None:
        return subscription

    subscription = TgSubscription(user_id=user_id, chat_id=chat_id)
    session.add(subscription)
    session.commit()
    return subscription


def get_tg_subscription(user_id: int, chat_id: int) -> Optional[TgSubscription]:
    return session.query(TgSubscription)\
        .where(TgSubscription.user_id == user_id and TgSubscription.chat_id == chat_id)\
        .first()


def get_tg_subscriptions_by_user(user_id: int) -> List[TgSubscription]:
    return session.query(TgSubscription).where(TgSubscription.user_id == user_id).all()


def get_tg_subscriptions_by_chat(chat_id: int) -> List[TgSubscription]:
    return session.query(TgSubscription).where(TgSubscription.chat_id == chat_id).all()


def remove_tg_subscription(user_id: int, chat_id: int) -> None:
    subscription = get_tg_subscription(user_id=user_id, chat_id=chat_id)
    if subscription is None:
        raise ValueError(f'Subscription with user_id={user_id} and chat_id={chat_id} does not exist.')

    session.delete(subscription)
    session.commit()


def migrate():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


Base.metadata.create_all(engine)
