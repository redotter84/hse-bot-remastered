from typing import List, Optional

from sqlalchemy import create_engine, Column, Integer, String
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


class SheetSubscription(Base):
    __tablename__ = 'sheetssubscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    sheet_id = Column(String(length=150))

    def __repr__(self) -> str:
        return f'<database.SheetsSubscription id: {self.id}, user_id: {self.user_id}, sheet_id: {self.sheet_id}>'


# ----------  TG  ----------


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
        .filter((TgSubscription.user_id == user_id) & (TgSubscription.chat_id == chat_id))\
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


# ----------  Sheets ----------


def create_sheet_subscription(user_id: int, sheet_id: str) -> SheetSubscription:
    subscription = get_sheet_subscription(user_id=user_id, sheet_id=sheet_id)
    if subscription is not None:
        return subscription

    subscription = SheetSubscription(user_id=user_id, sheet_id=sheet_id)
    session.add(subscription)
    session.commit()
    return subscription


def get_sheet_subscription(user_id: int, sheet_id: str) -> Optional[SheetSubscription]:
    return session.query(SheetSubscription)\
        .filter((SheetSubscription.user_id == user_id) & (SheetSubscription.sheet_id == sheet_id))\
        .first()


def get_sheet_subscriptions_by_user_id(user_id: int) -> List[SheetSubscription]:
    return session.query(SheetSubscription).where(SheetSubscription.user_id == user_id).all()


def get_sheet_subscriptions_by_sheet_id(sheet_id: str) -> List[SheetSubscription]:
    return session.query(SheetSubscription).where(SheetSubscription.sheet_id == sheet_id).all()


def get_unique_sheet_ids() -> List[str]:
    return list(map(lambda x: x[0], session.query(SheetSubscription.sheet_id).distinct()))


def delete_sheet_subscription(user_id: int, sheet_id: str) -> None:
    subscription = get_sheet_subscription(user_id=user_id, sheet_id=sheet_id)
    if subscription is None:
        raise ValueError(f"Sheet subscription with user_id={user_id} and sheet_id={sheet_id} does not exist.")

    session.delete(subscription)
    session.commit()


# ----------  Common  ----------


def migrate():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


Base.metadata.create_all(engine)
